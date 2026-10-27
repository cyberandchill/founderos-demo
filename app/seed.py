from datetime import date,timedelta
import random
from app.db import init,connect,audit
END=date(2026,10,27);START=END-timedelta(days=59)
def seed():
 init();rng=random.Random(731)
 with connect() as c:
  if c.execute('SELECT count(*) FROM creators').fetchone()[0]:return
  c.executemany('INSERT INTO segments VALUES(?,?,?,?)',[('S_REPEAT','Established customers','Synthetic prior purchase before the 60-day observation window','ACTIVE'),('S_NEW','First-window customers','No synthetic purchases before observation window','ACTIVE')])
  for i in range(120):c.execute('INSERT INTO customers VALUES(?,?,?,?)',(f'CU{i:03}',f'Demo Customer {i+1:03}','S_REPEAT' if i<60 else 'S_NEW','2026-07-15' if i<60 else None))
  c.executemany('INSERT INTO products VALUES(?,?,?,?)',[('P1','Evening journal','Midnight',3900),('P2','Wind-down kit','Standard',5900),('P3','Sleep mask','Slate',2900)])
  c.executemany('INSERT INTO campaigns VALUES(?,?,?,?)',[('C_ROUTINE','Evening ritual','Organic creator','ACTIVE'),('C_RESET','Room reset','Organic creator','ACTIVE'),('C_EMAIL','Lifecycle reminders','Email','ACTIVE')])
  c.executemany('INSERT INTO landings VALUES(?,?,?)',[('L_ROUTINE','Routine collection','/routine'),('L_KIT','Wind-down product','/wind-down-kit'),('L_MASK','Mask product','/sleep-mask')])
  names=['Maya Vale','Jules Rowan','Alex Cove','Riley Stone','Sage Ellis','Casey Reed','Emery Lane','Avery Hart','Jordan Moss','Quinn Ash','Drew Sky','Morgan Lake']
  for i,name in enumerate(names):
   creator=f'CR{i+1:02}';c.execute('INSERT INTO creators VALUES(?,?,?,?,?)',(creator,'Demo '+name,'Evening routines' if i%3==0 else 'Lifestyle / recovery',18000+i*2300,'AVAILABLE'))
   base=12000 if i==0 else rng.randrange(7,24)*1000
   historical=[9000,11000,12000,13000,15000] if i==0 else [int(base*rng.uniform(.65,1.35)) for _ in range(5)]
   for j in range(6):
    views=historical[j] if j<5 else (84000 if i==0 else int(base*rng.uniform(.75,1.8)))
    published=START+timedelta(days=[0,10,20,30,42,57][j]);campaign='C_ROUTINE' if i%2==0 else 'C_RESET'
    c.execute('INSERT INTO posts VALUES(?,?,?,?,?,?,?,?,?,?,?,?)',(f'V{i+1:02}-{j+1}',creator,campaign,str(published),views,int(views*rng.uniform(.03,.07)),int(views*.002),int(views*rng.uniform(.008,.025)),int(views*rng.uniform(.006,.018)),round(rng.uniform(9,22),1),'Phone away. Lights low. One repeatable ritual.' if i==0 and j==5 else rng.choice(['A calmer bedside setup','Three things before bed','My evening reset']),'Nighttime routines and recovery' if i%2==0 else 'Bedroom reset'))
  count=0
  for d in range(60):
   day=START+timedelta(days=d)
   for land in ['L_ROUTINE','L_KIT','L_MASK']:
    for camp in ['C_ROUTINE','C_RESET','C_EMAIL']:
     sessions=rng.randint(95,190) if land=='L_ROUTINE' else rng.randint(35,105)
     tid=f'T{d:02}-{land}-{camp}'
     candidates=[r[0] for r in c.execute('SELECT id FROM posts WHERE campaign_id=? AND published<=?',(camp,str(day)))];post=rng.choice(candidates) if candidates else None
     c.execute('INSERT INTO traffic VALUES(?,?,?,?,?,?)',(tid,str(day),land,camp,post,sessions))
     rate={'L_ROUTINE':.009,'L_KIT':.030,'L_MASK':.025}[land]*(1.13 if camp=='C_EMAIL' else 1)
     n=sum(rng.random()<rate for _ in range(sessions))
     for _ in range(n):
      count+=1;oid=f'O{count:05}';customer=rng.randrange(0,60) if rng.random()<(.60 if d<30 else .20) else rng.randrange(60,120)
      products=[rng.choice([('P1',3900),('P2',5900),('P3',2900)])]
      if rng.random()<.18:products.append(('P3',2900))
      total=sum(p[1] for p in products)
      c.execute('INSERT INTO orders VALUES(?,?,?,?,?,?)',(oid,str(day),f'CU{customer:03}',tid,total,int(rng.random()<.17)))
      for j,(pid,price) in enumerate(products):c.execute('INSERT INTO order_items VALUES(?,?,?,?,?)',(f'{oid}-{j}',oid,pid,1,price))
      c.execute('INSERT INTO attribution VALUES(?,?,?)',(oid,camp,'SYNTHETIC: one last-touch traffic record; 100% of order revenue; no incremental-lift claim'))
  c.executemany('INSERT INTO flows VALUES(?,?,?,?,?,?,?)',[('F_WELCOME','Welcome / product orientation','S_NEW',1100,530,86,'ACTIVE'),('F_CHECKOUT','Checkout reminder','S_NEW',460,172,39,'ACTIVE'),('F_REORDER','Repeat routine reminder','S_REPEAT',780,225,28,'ACTIVE')])
  audit(c,'seed','dataset',{'start':str(START),'end':str(END),'creators':12,'posts':72,'orders':count,'random_seed':731})
if __name__=='__main__':seed()
