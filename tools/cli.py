import sys,json,argparse
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app.seed import seed
from app.analysis import snapshot,creator_analysis,retention_analysis,opportunities,reconcile
from app.workflow import prepare,approve,execute,verify,reject

def main():
 p=argparse.ArgumentParser();p.add_argument('command',choices=['seed','snapshot','creators','retention','opportunities','reconcile','prepare','approve','execute','verify','reject']);p.add_argument('--file');p.add_argument('--id',action='append',default=[]);p.add_argument('--approval-text');a=p.parse_args();seed()
 if a.command=='seed':out={'seeded':True}
 elif a.command=='snapshot':out=snapshot()
 elif a.command=='creators':out=creator_analysis()
 elif a.command=='retention':out=retention_analysis()
 elif a.command=='opportunities':out=opportunities()
 elif a.command=='reconcile':out=reconcile()
 elif a.command=='prepare':out=prepare(json.loads(Path(a.file).read_text()))
 elif a.command=='approve':approve(a.id,a.approval_text or '');out={'approved':a.id}
 elif a.command=='execute':out=[execute(x) for x in a.id]
 elif a.command=='verify':out=[verify(x) for x in a.id]
 else:out=[reject(x) for x in a.id]
 print(json.dumps(out,indent=2))
if __name__=='__main__':main()
