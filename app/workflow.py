"""Ordinary local record utilities. Codex authors proposal JSON; no AI runtime."""
import hashlib,json
from datetime import date
from pydantic import BaseModel,ConfigDict,Field
from typing import Literal
from app.db import connect,rows,audit
class Artifact(BaseModel):
 model_config=ConfigDict(extra='forbid')
 table:Literal['concepts','briefs','drafts','assignments','experiments','tasks','segments','email_drafts']
 data:dict[str,str|int]
class Proposal(BaseModel):
 model_config=ConfigDict(extra='forbid')
 id:str=Field(pattern=r'^P[123]-[a-z0-9-]+$')
 analysis:dict
 artifacts:list[Artifact]=Field(min_length=1,max_length=50)
COLUMNS={'concepts':{'id','title','body','source_post','status'},'briefs':{'id','creator_id','title','body','status'},'drafts':{'id','creator_id','subject','body','status'},'assignments':{'id','creator_id','brief_id','campaign_id','compensation_cents','follow_up','status'},'experiments':{'id','platform','title','hypothesis','variants','status'},'tasks':{'id','platform','title','due','status'},'segments':{'id','name','definition','status'},'email_drafts':{'id','segment_id','subject','body','status'}}
def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'))
def validate(p):
 keys=[]
 for a in p.artifacts:
  if set(a.data)!=COLUMNS[a.table]:raise ValueError('Invalid artifact fields: '+a.table)
  if a.table in ['drafts','email_drafts'] and a.data['status']!='NOT SENT':raise ValueError('Messages must remain NOT SENT')
  if a.table=='assignments':
   if not isinstance(a.data['compensation_cents'],int) or a.data['compensation_cents']<0:raise ValueError('Invalid proposed compensation')
   date.fromisoformat(a.data['follow_up'])
  if a.table=='tasks':date.fromisoformat(a.data['due'])
  keys.append((a.table,a.data['id']))
 if len(set(keys))!=len(keys):raise ValueError('Duplicate artifact IDs')
 return p

def prepare(raw):
 p=validate(Proposal.model_validate(raw));payload=canonical(p.model_dump());digest=hashlib.sha256(payload.encode()).hexdigest()
 with connect() as c:
  old=c.execute('SELECT digest FROM proposals WHERE id=?',(p.id,)).fetchone()
  if old:
   if old['digest']!=digest:raise ValueError('Existing proposal differs; use a new ID')
   return {'id':p.id,'digest':digest,'status':'EXISTS'}
  c.execute('INSERT INTO proposals(id,analysis,payload,digest,status) VALUES(?,?,?,?,?)',(p.id,canonical(p.analysis),payload,digest,'PENDING'));audit(c,'proposal_prepared',p.id,{'digest':digest,'artifacts':len(p.artifacts),'author':'Codex conversation'})
 return {'id':p.id,'digest':digest,'status':'PENDING','artifacts':len(p.artifacts)}
def approve(ids,quote):
 expected={'1':['P1-growth-v1'],'2':['P2-conversion-v1'],'3':['P3-retention-v1'],'all':['P1-growth-v1','P2-conversion-v1','P3-retention-v1']}
 if quote.strip().lower() not in expected or sorted(ids)!=sorted(expected[quote.strip().lower()]):raise ValueError('Approval must match the selected action set')
 with connect() as c:
  for pid in ids:
   p=c.execute('SELECT * FROM proposals WHERE id=?',(pid,)).fetchone()
   if not p or p['status'] not in ['PENDING','APPROVED','COMPLETED']:raise ValueError('Proposal not pending')
   c.execute('INSERT OR IGNORE INTO approvals(proposal_id,decision,source) VALUES(?,?,?)',(pid,'APPROVED','User reply in Codex conversation: '+quote))
   if p['status']=='PENDING':c.execute('UPDATE proposals SET status=? WHERE id=?',('APPROVED',pid));audit(c,'approved',pid,{'quote':quote,'digest':p['digest'],'scope':'local mock records only'})
def reject(pid,reason='User rejected in Codex conversation'):
 with connect() as c:
  row=c.execute('SELECT status FROM proposals WHERE id=?',(pid,)).fetchone()
  if not row or row['status']!='PENDING':raise ValueError('Only pending proposals can be rejected')
  c.execute('UPDATE proposals SET status=? WHERE id=?',('REJECTED',pid));audit(c,'rejected',pid,{'reason':reason})
def execute(pid):
 with connect() as c:
  c.execute('BEGIN IMMEDIATE');r=c.execute('SELECT * FROM proposals WHERE id=?',(pid,)).fetchone()
  if not r:raise ValueError('Unknown proposal')
  if r['status']=='COMPLETED':return {'proposal':pid,'status':'COMPLETED','new_records':0,'duplicate_prevented':True}
  if r['status']!='APPROVED' or not c.execute('SELECT 1 FROM approvals WHERE proposal_id=? AND decision=?',(pid,'APPROVED')).fetchone():raise PermissionError('Explicit approval required')
  if hashlib.sha256(r['payload'].encode()).hexdigest()!=r['digest']:raise ValueError('Proposal digest mismatch')
  p=validate(Proposal.model_validate_json(r['payload']))
  for a in p.artifacts:
   data=dict(a.data)
   if a.table!='segments':data['proposal_id']=pid
   columns=list(data);c.execute(f"INSERT INTO {a.table} ({','.join(columns)}) VALUES ({','.join('?' for _ in columns)})",tuple(data.values()))
   audit(c,'record_created',data['id'],{'proposal':pid,'table':a.table,'status':data['status']})
  c.execute('UPDATE proposals SET status=? WHERE id=?',('COMPLETED',pid));audit(c,'execution_completed',pid,{'records':len(p.artifacts),'delivery':'NONE'})
 return {'proposal':pid,'status':'COMPLETED','new_records':len(p.artifacts),'delivery':'NONE'}
def verify(pid):
 with connect() as c:
  r=c.execute('SELECT * FROM proposals WHERE id=?',(pid,)).fetchone()
  if not r:raise ValueError('Unknown proposal')
  p=Proposal.model_validate_json(r['payload']);checks=[]
  for a in p.artifacts:
   record=c.execute(f'SELECT * FROM {a.table} WHERE id=?',(a.data['id'],)).fetchone()
   checks.append({'table':a.table,'id':a.data['id'],'exists':bool(record),'matches':bool(record) and all(record[k]==v for k,v in a.data.items()),'status':record['status'] if record else 'PENDING'})
  return {'proposal':pid,'status':r['status'],'approval':rows(c,'SELECT * FROM approvals WHERE proposal_id=?',(pid,)),'records':checks,'verified':r['status']=='COMPLETED' and all(x['matches'] for x in checks),'audit':rows(c,'SELECT * FROM audit WHERE record_id=? OR json_extract(detail,\'$.proposal\')=? ORDER BY seq',(pid,pid))}
