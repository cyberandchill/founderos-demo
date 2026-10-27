from pathlib import Path
import tarfile,hashlib,sqlite3,datetime,json,subprocess,os
ROOT=Path(__file__).resolve().parents[1];archive_dir=ROOT/'archives';archive_dir.mkdir(exist_ok=True)
# SQLite backup API yields a consistent snapshot while the local service is running.
with sqlite3.connect(ROOT/'data/business.sqlite') as source,sqlite3.connect(ROOT/'data/restore-snapshot.sqlite') as target:source.backup(target)
exclude={'.venv','tmp','browsers','archives','__pycache__','.pytest_cache','.git'}
files=[p for p in ROOT.rglob('*') if p.is_file() and not any(x in exclude for x in p.relative_to(ROOT).parts) and p.name not in ['business.sqlite','server.log','server.pid']]
checks={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
path=archive_dir/('founderos-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'.tar.gz')
with tarfile.open(path,'w:gz') as t:
 for p in files:t.add(p,arcname='founderos-lucas-demo/'+str(p.relative_to(ROOT)),recursive=False)
restore=ROOT/'tmp/archive-restore'/path.name.removesuffix('.tar.gz');restore.mkdir(parents=True,exist_ok=False)
with tarfile.open(path) as t:
 assert all(m.isfile() and not Path(m.name).is_absolute() and '..' not in Path(m.name).parts for m in t.getmembers());t.extractall(restore,filter='data')
base=restore/'founderos-lucas-demo'
assert all(hashlib.sha256((base/name).read_bytes()).hexdigest()==digest for name,digest in checks.items())
with sqlite3.connect(base/'data/restore-snapshot.sqlite') as c:assert c.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
env={**os.environ,'FOUNDEROS_DB':str(base/'data/restore-snapshot.sqlite'),'PYTHONPATH':str(base)}
p=subprocess.run([str(ROOT/'.venv/bin/python'),str(base/'tools/cli.py'),'reconcile'],env=env,cwd=base,capture_output=True,text=True,check=True);assert all(json.loads(p.stdout).values())
workflow_checks=[]
with sqlite3.connect(base/'data/restore-snapshot.sqlite') as restored:
 completed=[r[0] for r in restored.execute("SELECT id FROM proposals WHERE status='COMPLETED'")]
for pid in completed:
 check=subprocess.run([str(ROOT/'.venv/bin/python'),str(base/'tools/cli.py'),'verify','--id',pid],env=env,cwd=base,capture_output=True,text=True,check=True)
 assert json.loads(check.stdout)[0]['verified'];workflow_checks.append(pid)
result={'restored_completed_workflows':workflow_checks,'archive':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'files_verified':len(checks),'checks_passed':5 if workflow_checks else 4,'checks':['all archive member paths safe','every restored file hash matches','restored SQLite integrity ok','restored reconciliation command passed']+(['restored completed workflows independently verified'] if workflow_checks else []),'snapshot':'data/restore-snapshot.sqlite','restore_root':str(base)}
(ROOT/'evidence/test-results/archive.json').write_text(json.dumps(result,indent=2));path.with_suffix(path.suffix+'.sha256').write_text(result['sha256']+'  '+path.name+'\n');print(json.dumps(result,indent=2))
