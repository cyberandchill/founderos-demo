import os,sqlite3,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DB=Path(os.environ.get('FOUNDEROS_DB',ROOT/'data/business.sqlite'))
def connect():
 c=sqlite3.connect(DB,timeout=15);c.row_factory=sqlite3.Row;c.execute('PRAGMA foreign_keys=ON');return c
def rows(c,sql,args=()):return [dict(x) for x in c.execute(sql,args)]
def audit(c,kind,record_id,detail):
 c.execute('INSERT INTO audit(kind,record_id,detail) VALUES(?,?,?)',(kind,record_id,json.dumps(detail,sort_keys=True)))
SCHEMA='''
CREATE TABLE IF NOT EXISTS segments(id TEXT PRIMARY KEY,name TEXT,definition TEXT,status TEXT);
CREATE TABLE IF NOT EXISTS customers(id TEXT PRIMARY KEY,name TEXT,segment_id TEXT REFERENCES segments(id),prior_purchase TEXT);
CREATE TABLE IF NOT EXISTS products(id TEXT PRIMARY KEY,name TEXT,variant TEXT,price_cents INTEGER CHECK(price_cents>0));
CREATE TABLE IF NOT EXISTS creators(id TEXT PRIMARY KEY,name TEXT,niche TEXT,rate_cents INTEGER,status TEXT);
CREATE TABLE IF NOT EXISTS campaigns(id TEXT PRIMARY KEY,name TEXT,channel TEXT,status TEXT);
CREATE TABLE IF NOT EXISTS posts(id TEXT PRIMARY KEY,creator_id TEXT REFERENCES creators(id),campaign_id TEXT REFERENCES campaigns(id),published TEXT,views INTEGER,likes INTEGER,comments INTEGER,saves INTEGER,clicks INTEGER,watch_seconds REAL,hook TEXT,theme TEXT);
CREATE TABLE IF NOT EXISTS landings(id TEXT PRIMARY KEY,name TEXT,path TEXT);
CREATE TABLE IF NOT EXISTS traffic(id TEXT PRIMARY KEY,day TEXT,landing_id TEXT REFERENCES landings(id),campaign_id TEXT REFERENCES campaigns(id),post_id TEXT REFERENCES posts(id),sessions INTEGER CHECK(sessions>0));
CREATE TABLE IF NOT EXISTS orders(id TEXT PRIMARY KEY,day TEXT,customer_id TEXT REFERENCES customers(id),traffic_id TEXT REFERENCES traffic(id),revenue_cents INTEGER,subscription INTEGER CHECK(subscription IN (0,1)));
CREATE TABLE IF NOT EXISTS order_items(id TEXT PRIMARY KEY,order_id TEXT REFERENCES orders(id),product_id TEXT REFERENCES products(id),quantity INTEGER CHECK(quantity>0),unit_cents INTEGER);
CREATE TABLE IF NOT EXISTS attribution(order_id TEXT PRIMARY KEY REFERENCES orders(id),campaign_id TEXT REFERENCES campaigns(id),model TEXT);
CREATE TABLE IF NOT EXISTS flows(id TEXT PRIMARY KEY,name TEXT,segment_id TEXT REFERENCES segments(id),delivered INTEGER,opens INTEGER,clicks INTEGER,status TEXT);
CREATE TABLE IF NOT EXISTS proposals(id TEXT PRIMARY KEY,created TEXT DEFAULT CURRENT_TIMESTAMP,analysis TEXT,payload TEXT,digest TEXT,status TEXT CHECK(status IN ('PENDING','APPROVED','COMPLETED','REJECTED','FAILED')));
CREATE TABLE IF NOT EXISTS approvals(proposal_id TEXT PRIMARY KEY REFERENCES proposals(id),decision TEXT,source TEXT,approved_at TEXT DEFAULT CURRENT_TIMESTAMP);
CREATE TABLE IF NOT EXISTS concepts(id TEXT PRIMARY KEY,proposal_id TEXT REFERENCES proposals(id),title TEXT,body TEXT,source_post TEXT REFERENCES posts(id),status TEXT);
CREATE TABLE IF NOT EXISTS briefs(id TEXT PRIMARY KEY,proposal_id TEXT REFERENCES proposals(id),creator_id TEXT REFERENCES creators(id),title TEXT,body TEXT,status TEXT);
CREATE TABLE IF NOT EXISTS drafts(id TEXT PRIMARY KEY,proposal_id TEXT REFERENCES proposals(id),creator_id TEXT REFERENCES creators(id),subject TEXT,body TEXT,status TEXT CHECK(status='NOT SENT'));
CREATE TABLE IF NOT EXISTS assignments(id TEXT PRIMARY KEY,proposal_id TEXT REFERENCES proposals(id),creator_id TEXT REFERENCES creators(id),brief_id TEXT REFERENCES briefs(id),campaign_id TEXT REFERENCES campaigns(id),compensation_cents INTEGER,follow_up TEXT,status TEXT);
CREATE TABLE IF NOT EXISTS experiments(id TEXT PRIMARY KEY,proposal_id TEXT REFERENCES proposals(id),platform TEXT,title TEXT,hypothesis TEXT,variants TEXT,status TEXT);
CREATE TABLE IF NOT EXISTS tasks(id TEXT PRIMARY KEY,proposal_id TEXT REFERENCES proposals(id),platform TEXT,title TEXT,due TEXT,status TEXT);
CREATE TABLE IF NOT EXISTS email_drafts(id TEXT PRIMARY KEY,proposal_id TEXT REFERENCES proposals(id),segment_id TEXT REFERENCES segments(id),subject TEXT,body TEXT,status TEXT CHECK(status='NOT SENT'));
CREATE TABLE IF NOT EXISTS audit(seq INTEGER PRIMARY KEY,ts TEXT DEFAULT CURRENT_TIMESTAMP,kind TEXT,record_id TEXT,detail TEXT);
'''
def init():
 DB.parent.mkdir(parents=True,exist_ok=True)
 with connect() as c:c.executescript(SCHEMA)
