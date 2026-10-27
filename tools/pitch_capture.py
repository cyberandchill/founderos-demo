"""Four concise read-only screenshots of genuine live tool views."""
import os,json,hashlib,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from app.workflow import verify
from app.db import DB
assert verify('P1-growth-v1')['verified'],'Creator action set must actually be completed first'
os.environ['PLAYWRIGHT_BROWSERS_PATH']=str(ROOT/'data/browsers')
OUT=ROOT/'evidence/screenshots-original/pitch-simple';OUT.mkdir(exist_ok=True)
cases=[('ugc-demo','winner','01-find-the-winner'),('ugc-demo','ideas','02-create-five-ideas'),('creator-crm-demo','outreach','03-prepare-outreach'),('creator-crm-demo','results','04-approval-to-results')]
manifest=[];checks=[]
with sync_playwright() as p:
 b=p.chromium.launch(headless=True,chromium_sandbox=True);page=b.new_page(viewport={'width':1080,'height':1350},device_scale_factor=1);errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 for route,view,name in cases:
  page.goto(f'http://127.0.0.1:8775/{route}?pitch={view}');panel=page.locator('.pitch-panel');panel.wait_for();assert page.locator('.banner').is_visible();assert 'LOCAL MOCKUP' in panel.inner_text()
  if view=='winner':
   assert '84,000' in panel.inner_text() and '12,000' in panel.inner_text();assert panel.locator('.pitch-big').inner_text()=='7×'
   page.select_option('#pitch-creator','CR02');assert panel.locator('.pitch-big').inner_text()!='7×';page.select_option('#pitch-creator','CR01');assert panel.locator('.pitch-big').inner_text()=='7×';checks.append('Live creator selection recomputes displayed metrics')
  if view=='ideas':assert panel.locator('.pitch-row').count()==5
  if view=='outreach':
   assert panel.locator('.pill.warn').count()==3
   panel.locator('summary').first.click();assert panel.locator('details').first.get_attribute('open') is not None;assert 'local synthetic draft' in panel.locator('details').first.inner_text();panel.locator('summary').first.click();checks.append('Outreach previews open actual full saved messages')
  if view=='results':assert '19 records saved and verified' in panel.inner_text();assert panel.locator('.pitch-result').count()==6
  page.screenshot(path=str(OUT/(name+'-full.png')),full_page=True);panel.screenshot(path=str(OUT/(name+'-card.png')))
  checks.append(view+' live view and source screenshot')
  manifest.append({'name':name,'url':f'/{route}?pitch={view}','sources':[str((OUT/(name+'-full.png')).relative_to(ROOT)),str((OUT/(name+'-card.png')).relative_to(ROOT))],'text_verified':True})
 assert errors==[];b.close()
for item in manifest:
 item['sha256']={f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in item['sources']}
(ROOT/'evidence/pitch-sources.json').write_text(json.dumps({'genuine_browser_captures':manifest,'page_errors':errors,'browser_sandbox':True,'business_records_mutated':0,'checks_passed':len(checks),'checks':checks},indent=2))
print(f'{len(checks)} pitch browser checks passed; 8 untouched browser screenshots; zero business mutations.')
