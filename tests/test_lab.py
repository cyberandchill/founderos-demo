import json,socket,sqlite3,subprocess,os
from pathlib import Path
import pytest
from app import db
from app.seed import seed
from app.analysis import snapshot,creator_analysis,retention_analysis,opportunities,reconcile
from app import workflow
ROOT=Path(__file__).resolve().parents[1]
@pytest.fixture(autouse=True)
def isolated(tmp_path,monkeypatch):
 monkeypatch.setattr(db,'DB',tmp_path/'business.sqlite');seed()
def raw(n=1):return json.loads((ROOT/'docs'/f"P{n}-{'growth' if n==1 else 'conversion' if n==2 else 'retention'}-v1.json").read_text())
def test_seed_idempotent():
 seed()
 with db.connect() as c:
  assert c.execute('SELECT count(*) FROM creators').fetchone()[0]==12
  assert c.execute('SELECT count(*) FROM posts').fetchone()[0]==72
  assert c.execute('SELECT count(DISTINCT day) FROM orders').fetchone()[0]==60
@pytest.mark.parametrize('check',['foreign_keys','order_totals','one_attribution_per_order','attribution_campaign','post_campaign','60_sales_days','revenue_reconciles'])
def test_reconciliation(check):assert reconcile()[check]
def test_metrics():
 s=snapshot();t=s['totals'];assert t['revenue_cents']==sum(x['revenue_cents'] for x in s['products']);assert t['orders']==sum(x['orders'] for x in s['pages']);assert t['conversion_pct']==round(t['orders']/t['sessions']*100,2)
def test_baseline():
 w=creator_analysis()[0];assert w['id']=='CR01';assert w['baseline']==12000;assert w['post']['views']==84000;assert w['multiple']==7;assert len(w['history_ids'])==5
 assert all(x['multiple']>=y['multiple'] for x,y in zip(creator_analysis(),creator_analysis()[1:]))
def test_opportunities():
 o=opportunities()['opportunities'];assert [r['id'] for r in o]==['1','2','3'];assert o[1]['evidence']['weak']['conversion_pct']<o[1]['evidence']['reference']['conversion_pct'];assert o[2]['evidence']['order_change_pct']<0
def test_prepare_no_mutations():
 workflow.prepare(raw());workflow.prepare(raw())
 with db.connect() as c:assert c.execute('SELECT count(*) FROM drafts').fetchone()[0]==0;assert c.execute('SELECT count(*) FROM proposals').fetchone()[0]==1
@pytest.mark.parametrize('n',[1,2,3])
def test_workflow(n):
 p=raw(n);workflow.prepare(p);pid=p['id']
 with pytest.raises(PermissionError):workflow.execute(pid)
 assert not workflow.verify(pid)['verified']
 workflow.approve([pid],str(n));r=workflow.execute(pid);assert r['new_records']==len(p['artifacts']);assert workflow.verify(pid)['verified'];assert workflow.execute(pid)['new_records']==0
 assert all(x['matches'] for x in workflow.verify(pid)['records'])
def test_all():
 ids=[]
 for n in [1,2,3]:p=raw(n);workflow.prepare(p);ids.append(p['id'])
 workflow.approve(ids,'all')
 for pid in ids:workflow.execute(pid)
 with db.connect() as c:
  assert c.execute('SELECT count(*) FROM tasks').fetchone()[0]==10
  assert c.execute('SELECT count(*) FROM drafts WHERE status="NOT SENT"').fetchone()[0]==3
  assert c.execute('SELECT count(*) FROM email_drafts WHERE status="NOT SENT"').fetchone()[0]==3
 assert reconcile()['foreign_keys']
def test_rejection():
 p=raw();workflow.prepare(p);workflow.reject(p['id'])
 with pytest.raises(PermissionError):workflow.execute(p['id'])
 with pytest.raises(ValueError):workflow.approve([p['id']],'1')
def test_approval_scope():
 workflow.prepare(raw())
 with pytest.raises(ValueError):workflow.approve(['P1-growth-v1'],'all')
 with pytest.raises(ValueError):workflow.approve(['P1-growth-v1'],'yes')
def test_tamper():
 p=raw();workflow.prepare(p);workflow.approve([p['id']],'1')
 with db.connect() as c:c.execute('UPDATE proposals SET payload=? WHERE id=?',(json.dumps({**p,'analysis':{}}),p['id']))
 with pytest.raises(ValueError):workflow.execute(p['id'])
 with db.connect() as c:assert c.execute('SELECT count(*) FROM concepts').fetchone()[0]==0
def test_atomic_failure():
 p=raw();p['artifacts'][-1]['data']['id']='G-CON1';p['artifacts'][-1]['table']='concepts';p['artifacts'][-1]['data']=dict(p['artifacts'][0]['data']);p['artifacts'][-1]['data']['id']='BAD-FK';p['artifacts'][-1]['data']['source_post']='MISSING';workflow.prepare(p);workflow.approve([p['id']],'1')
 with pytest.raises(sqlite3.IntegrityError):workflow.execute(p['id'])
 with db.connect() as c:assert c.execute('SELECT count(*) FROM concepts').fetchone()[0]==0
 assert workflow.verify(p['id'])['status']=='APPROVED'
def test_no_delivery(monkeypatch):
 def denied(*a,**kw):raise AssertionError('Network attempted')
 monkeypatch.setattr(socket.socket,'connect',denied);monkeypatch.setattr(socket,'create_connection',denied)
 p=raw();workflow.prepare(p);workflow.approve([p['id']],'1');workflow.execute(p['id']);assert workflow.verify(p['id'])['verified']
 with db.connect() as c:assert {r[0] for r in c.execute('SELECT status FROM drafts')}=={'NOT SENT'}
def test_invalid_payload():
 p=raw();p['artifacts'][0]['table']='orders'
 with pytest.raises(Exception):workflow.prepare(p)
 p=raw();next(a for a in p['artifacts'] if a['table']=='drafts')['data']['status']='SENT'
 with pytest.raises(ValueError):workflow.prepare(p)
@pytest.mark.parametrize('route',['shopify-demo','ugc-demo','creator-crm-demo','klaviyo-demo'])
def test_pages(route):
 from fastapi.testclient import TestClient
 from app.main import app
 c=TestClient(app);r=c.get('/'+route);assert r.status_code==200;assert 'NO LIVE INTEGRATIONS' in r.text;assert '__PLATFORM__' not in r.text
 assert c.get('/api/state').status_code==200

def test_local_writes():
 from fastapi.testclient import TestClient
 from app.main import app
 c=TestClient(app);p={'id':'MANUAL-testing','platform':'Shopify','title':'Product clarity','hypothesis':'Clear product choices improve navigation','variants':'A / B'}
 assert c.post('/api/experiments',json=p).status_code==403
 h={'X-Local-POC':'1'};assert c.post('/api/experiments',json=p,headers=h).status_code==200;assert c.post('/api/experiments',json=p,headers=h).json()['duplicate_prevented']
 assert c.post('/api/status',json={'table':'experiments','id':p['id'],'status':'IN REVIEW'},headers=h).status_code==200
 with db.connect() as conn:assert conn.execute('SELECT status FROM experiments WHERE id=?',(p['id'],)).fetchone()[0]=='IN REVIEW'
 assert c.post('/api/status',json={'table':'orders','id':'x','status':'COMPLETED'},headers=h).status_code==422
 assert c.post('/api/send',headers=h).status_code==404
 assert c.get('/api/state',headers={'Host':'evil.example'}).status_code==400
def test_campaign_cohort_flow_link():
 with db.connect() as c:
  r=c.execute('SELECT count(*) FROM attribution a JOIN orders o ON o.id=a.order_id JOIN customers cu ON cu.id=o.customer_id JOIN flows f ON f.segment_id=cu.segment_id WHERE a.campaign_id=? AND f.id=?',('C_ROUTINE','F_REORDER')).fetchone()[0]
  assert r>0
