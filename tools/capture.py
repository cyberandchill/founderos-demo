import os,json,hashlib,argparse,sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT));os.environ['PLAYWRIGHT_BROWSERS_PATH']=str(ROOT/'data/browsers')
parser=argparse.ArgumentParser();parser.add_argument('--after',action='store_true');args=parser.parse_args()
original=ROOT/'evidence/screenshots-original';logs=ROOT/'evidence/test-results';checks=[];manifest=[]
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True,chromium_sandbox=True);context=browser.new_context(viewport={'width':1280,'height':1000},device_scale_factor=1);page=context.new_page();errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
 for route,short in [('shopify-demo','shopify'),('ugc-demo','ugc'),('creator-crm-demo','crm'),('klaviyo-demo','klaviyo')]:
  page.goto(f'http://127.0.0.1:8775/{route}');page.locator('#evidence-card').wait_for();assert page.locator('.banner').inner_text()=='LOCAL POC · SYNTHETIC DATA · NO LIVE INTEGRATIONS';page.screenshot(path=str(original/f'{short}-overview.png'),full_page=True);page.locator('#evidence-card').screenshot(path=str(original/f'{short}-evidence-card.png'));checks.append(route+' rendering + source capture')
  links=page.locator('#nav a').evaluate_all('(els)=>els.map(a=>a.href)')
  for link in links:
   page.goto(link);page.locator('#content > *').first.wait_for();assert len(page.locator('#content').inner_text())>5
  checks.append(short+' navigation tabs')
 page.goto('http://127.0.0.1:8775/creator-crm-demo?tab=Creator%20directory');page.locator('#filter').fill('Maya');assert page.locator('tbody tr:visible').count()==1;checks.append('CRM live filter')
 page.goto('http://127.0.0.1:8775/shopify-demo?tab=Experiments');page.locator('#new-experiment').click();assert page.locator('#editor').is_visible();page.get_by_role('button',name='Cancel',exact=True).click();checks.append('Local draft modal opens without writing')
 if args.after:
  page.goto('http://127.0.0.1:8775/creator-crm-demo?tab=Execution%20proof');page.locator('#execution-proof').wait_for();assert page.locator('#execution-proof .row .warn').count()>=3;page.screenshot(path=str(original/'approved-execution-full.png'),full_page=True);page.locator('#execution-proof').screenshot(path=str(original/'approved-execution-card.png'));checks.append('Approved execution and NOT SENT evidence visible')
  for tab,name in [('Campaign assignments','assignments'),('Outreach drafts','outreach'),('Tasks','followups')]:
   page.goto('http://127.0.0.1:8775/creator-crm-demo?tab='+tab.replace(' ','%20'));page.locator('tbody tr').first.wait_for();page.screenshot(path=str(original/f'{name}.png'),full_page=True)
  checks.append('Created artifacts visible in three CRM views')
 assert not errors
 (logs/('browser-after.json' if args.after else 'browser-before.json')).write_text(json.dumps({'checks_passed':len(checks),'checks':checks,'page_errors':errors,'sandbox_enabled':True,'viewport':[1280,1000],'note':'Read-only checks and canceled draft modal; no approval simulated.'},indent=2))
 context.close();browser.close()
for f in original.glob('*.png'):manifest.append({'path':str(f.relative_to(ROOT)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'origin':'Unedited Playwright full-page or DOM element screenshot from live localhost app','synthetic':True})
(ROOT/'evidence/screenshot-sources.json').write_text(json.dumps(manifest,indent=2));print(f'{len(checks)} browser checks passed; {len(manifest)} untouched captures.')
