import json
from pathlib import Path
from fastapi import FastAPI,HTTPException,Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel,Field
from typing import Literal
from app.seed import seed
from app.db import connect,rows,audit
from app.analysis import snapshot,creator_analysis,retention_analysis,opportunities
seed();app=FastAPI(title='FounderOS local business tools — mockups only')
ROUTES={'shopify-demo':'shopify','ugc-demo':'ugc','creator-crm-demo':'crm','klaviyo-demo':'klaviyo'}
@app.middleware('http')
async def local_only(request:Request,call_next):
 if request.headers.get('host','').split(':')[0] not in ['127.0.0.1','localhost','testserver']:return HTMLResponse('Local host required',400)
 if request.method not in ['GET','HEAD'] and request.headers.get('x-local-poc')!='1':return HTMLResponse('Local mutation header required',403)
 return await call_next(request)
@app.get('/api/state')
def state():
 with connect() as c:
  tables=['creators','posts','campaigns','flows','segments','concepts','briefs','drafts','assignments','experiments','tasks','email_drafts','proposals','approvals','audit']
  d={t:rows(c,f'SELECT * FROM {t}'+(' ORDER BY seq DESC LIMIT 40' if t=='audit' else '')) for t in tables}
  for p in d['proposals']:p.pop('payload');p['analysis']=json.loads(p['analysis'])
  d['campaign_segments']=rows(c,'SELECT a.campaign_id,cu.segment_id,count(*) orders,sum(o.revenue_cents) revenue_cents FROM attribution a JOIN orders o ON o.id=a.order_id JOIN customers cu ON cu.id=o.customer_id GROUP BY a.campaign_id,cu.segment_id')
  d['orders']=rows(c,'SELECT o.*,cu.name customer,l.name landing FROM orders o JOIN customers cu ON cu.id=o.customer_id JOIN traffic t ON t.id=o.traffic_id JOIN landings l ON l.id=t.landing_id ORDER BY day DESC LIMIT 100')
  d['customers']=rows(c,'SELECT cu.*,count(o.id) orders,coalesce(sum(o.revenue_cents),0) revenue_cents FROM customers cu LEFT JOIN orders o ON o.customer_id=cu.id GROUP BY cu.id')
 return {**d,'snapshot':snapshot(),'leaderboard':creator_analysis(),'retention':retention_analysis(),'opportunities':opportunities()}
class StatusUpdate(BaseModel):
 table:Literal['tasks','experiments','assignments']
 id:str=Field(min_length=1,max_length=80)
 status:Literal['PENDING','IN REVIEW','COMPLETED','DRAFTED']
@app.post('/api/status')
def status(u:StatusUpdate):
 with connect() as c:
  r=c.execute(f'SELECT * FROM {u.table} WHERE id=?',(u.id,)).fetchone()
  if not r:raise HTTPException(404,'Unknown record')
  c.execute(f'UPDATE {u.table} SET status=? WHERE id=?',(u.status,u.id));audit(c,'status_changed',u.id,{'table':u.table,'from':r['status'],'to':u.status})
 return {'updated':u.id,'status':u.status}
class LocalExperiment(BaseModel):
 platform:Literal['Shopify','UGC','CRM','Klaviyo']
 id:str=Field(pattern=r'^MANUAL-[a-zA-Z0-9-]{3,60}$')
 title:str=Field(min_length=3,max_length=200)
 hypothesis:str=Field(min_length=10,max_length=1500)
 variants:str=Field(min_length=3,max_length=2000)
@app.post('/api/experiments')
def experiment(u:LocalExperiment):
 with connect() as c:
  old=c.execute('SELECT * FROM experiments WHERE id=?',(u.id,)).fetchone()
  if old:
   if any(old[k]!=v for k,v in u.model_dump().items()):raise HTTPException(409,'ID already used')
   return {'id':u.id,'duplicate_prevented':True}
  c.execute('INSERT INTO experiments(id,platform,title,hypothesis,variants,status) VALUES(?,?,?,?,?,?)',(u.id,u.platform,u.title,u.hypothesis,u.variants,'DRAFTED'));audit(c,'manual_experiment_drafted',u.id,u.model_dump())
 return {'id':u.id,'status':'DRAFTED'}
@app.get('/{route}',response_class=HTMLResponse)
def page(route:str):
 if route not in ROUTES:raise HTTPException(404,'Use /shopify-demo, /ugc-demo, /creator-crm-demo or /klaviyo-demo')
 return (Path(__file__).with_name('index.html').read_text()).replace('__PLATFORM__',ROUTES[route])
@app.get('/',response_class=HTMLResponse)
def index():return '<a href="/shopify-demo">Shopify — LOCAL MOCKUP</a> · <a href="/ugc-demo">UGC Analytics — LOCAL MOCKUP</a> · <a href="/creator-crm-demo">Creator CRM — LOCAL MOCKUP</a> · <a href="/klaviyo-demo">Klaviyo — LOCAL MOCKUP</a>'
