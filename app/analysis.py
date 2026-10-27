from app.db import connect,rows
from app.seed import END,START
from datetime import timedelta

def snapshot():
 with connect() as c:
  totals=dict(c.execute('SELECT count(*) orders,sum(revenue_cents) revenue_cents,sum(subscription) subscription_orders FROM orders').fetchone());totals['sessions']=c.execute('SELECT sum(sessions) FROM traffic').fetchone()[0];totals['aov_cents']=round(totals['revenue_cents']/totals['orders'],2);totals['conversion_pct']=round(totals['orders']/totals['sessions']*100,2)
  trend=rows(c,'SELECT day,count(*) orders,sum(revenue_cents) revenue_cents FROM orders GROUP BY day ORDER BY day')
  pages=rows(c,'''SELECT l.id,l.name,sum(t.sessions) sessions,(SELECT count(*) FROM orders o JOIN traffic tt ON o.traffic_id=tt.id WHERE tt.landing_id=l.id) orders,(SELECT sum(o.revenue_cents) FROM orders o JOIN traffic tt ON o.traffic_id=tt.id WHERE tt.landing_id=l.id) revenue_cents FROM landings l JOIN traffic t ON t.landing_id=l.id GROUP BY l.id''')
  for p in pages:p['conversion_pct']=round(p['orders']/p['sessions']*100,2)
  return {'window':[str(START),str(END)],'totals':totals,'trend':trend,'pages':pages,'products':rows(c,'SELECT p.id,p.name,p.variant,sum(i.quantity) units,sum(i.unit_cents*i.quantity) revenue_cents FROM products p JOIN order_items i ON p.id=i.product_id GROUP BY p.id'),'campaigns':rows(c,'SELECT ca.*,count(a.order_id) orders,coalesce(sum(o.revenue_cents),0) revenue_cents FROM campaigns ca LEFT JOIN attribution a ON a.campaign_id=ca.id LEFT JOIN orders o ON o.id=a.order_id GROUP BY ca.id')}

def creator_analysis():
 with connect() as c:
  result=[]
  for creator in rows(c,'SELECT * FROM creators ORDER BY id'):
   posts=rows(c,'SELECT * FROM posts WHERE creator_id=? ORDER BY published,id',(creator['id'],));recent=posts[-1];history=posts[:-1];base=sum(p['views'] for p in history)/len(history)
   commerce=dict(c.execute('SELECT count(*) orders,coalesce(sum(o.revenue_cents),0) revenue_cents FROM orders o JOIN traffic t ON o.traffic_id=t.id WHERE t.post_id=?',(recent['id'],)).fetchone())
   result.append({**creator,'post':recent,'baseline':base,'multiple':round(recent['views']/base,3),'history_ids':[p['id'] for p in history],'attribution':commerce,'engagement_pct':round((recent['likes']+recent['comments']+recent['saves'])/recent['views']*100,2),'ctr_pct':round(recent['clicks']/recent['views']*100,2)})
  return sorted(result,key=lambda r:(-r['multiple'],-r['attribution']['revenue_cents']))

def retention_analysis():
 split=str(END-timedelta(days=29))
 with connect() as c:
  rs=[]
  for s in rows(c,'SELECT * FROM segments WHERE status="ACTIVE"'):
   totals=dict(c.execute('''SELECT count(CASE WHEN o.day<? THEN 1 END) previous_orders,count(CASE WHEN o.day>=? THEN 1 END) recent_orders,count(DISTINCT CASE WHEN o.day<? THEN o.customer_id END) previous_buyers,count(DISTINCT CASE WHEN o.day>=? THEN o.customer_id END) recent_buyers FROM orders o JOIN customers cu ON cu.id=o.customer_id WHERE cu.segment_id=?''',(split,split,split,split,s['id'])).fetchone())
   rs.append({**s,**totals,'order_change_pct':round((totals['recent_orders']/totals['previous_orders']-1)*100,1) if totals['previous_orders'] else None})
  return {'periods':{'previous':[str(START),str(END-timedelta(days=30))],'recent':[split,str(END)]},'segments':rs,'flows':rows(c,'SELECT * FROM flows')}

def opportunities():
 s=snapshot();winner=creator_analysis()[0];pages=s['pages'];weak=min(pages,key=lambda x:x['conversion_pct']);reference=max((p for p in pages if p['id']!=weak['id']),key=lambda x:x['sessions']);seg=min(retention_analysis()['segments'],key=lambda x:x['order_change_pct'])
 # Scores are declared planning judgments, never measured or forecast dollars.
 opportunities=[{'id':'1','name':'Replicate a winning creator angle','finding':f"{winner['name']} / {winner['post']['id']}: {winner['post']['views']:,} views vs {winner['baseline']:,.0f} historical average ({winner['multiple']:g}×).",'evidence':winner,'impact':5,'confidence':4,'urgency':5,'effort':2}, {'id':'2','name':'Test a conversion leak','finding':f"{weak['name']}: {weak['sessions']:,} sessions, {weak['conversion_pct']}% purchase rate vs {reference['conversion_pct']}% on {reference['name']}.",'evidence':{'weak':weak,'reference':reference},'impact':5,'confidence':3,'urgency':4,'effort':3}, {'id':'3','name':'Recover repeat purchasing','finding':f"{seg['name']}: {seg['previous_orders']} → {seg['recent_orders']} orders across equal 30-day windows ({seg['order_change_pct']}%).",'evidence':seg,'impact':4,'confidence':4,'urgency':3,'effort':3}]
 for r in opportunities:r['priority_score']=round((r['impact']*.4+r['confidence']*.35+r['urgency']*.25)/r['effort'],3)
 return {'opportunities':sorted(opportunities,key=lambda r:-r['priority_score']),'scoring':'Planning rubric: (impact × .40 + confidence × .35 + urgency × .25) / effort; inputs 1–5, qualitative judgments. No impact forecast.','attribution':'All data synthetic. Last-touch association is not verified incremental revenue.'}

def reconcile():
 with connect() as c:
  checks={'foreign_keys':len(c.execute('PRAGMA foreign_key_check').fetchall())==0,'order_totals':c.execute('SELECT count(*) FROM orders o WHERE revenue_cents!=(SELECT sum(quantity*unit_cents) FROM order_items WHERE order_id=o.id)').fetchone()[0]==0,'one_attribution_per_order':c.execute('SELECT count(*) FROM attribution').fetchone()[0]==c.execute('SELECT count(*) FROM orders').fetchone()[0],'attribution_campaign':c.execute('SELECT count(*) FROM attribution a JOIN orders o ON o.id=a.order_id JOIN traffic t ON t.id=o.traffic_id WHERE a.campaign_id!=t.campaign_id').fetchone()[0]==0,'post_campaign':c.execute('SELECT count(*) FROM traffic t JOIN posts p ON p.id=t.post_id WHERE t.campaign_id!=p.campaign_id OR p.published>t.day').fetchone()[0]==0,'60_sales_days':c.execute('SELECT count(DISTINCT day) FROM orders').fetchone()[0]==60,'revenue_reconciles':c.execute('SELECT sum(revenue_cents) FROM orders').fetchone()[0]==c.execute('SELECT sum(i.quantity*i.unit_cents) FROM order_items i').fetchone()[0]}
  return checks
