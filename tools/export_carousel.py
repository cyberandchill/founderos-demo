"""Truthful layout of unchanged browser crops; no generated UI or statuses."""
from pathlib import Path
import json,hashlib,textwrap
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'evidence/screenshots-original';OUT=ROOT/'evidence/carousel-ready'
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def font(n,bold=False):return ImageFont.truetype(BOLD if bold else FONT,n)
def canvas(headline,sentence):
 im=Image.new('RGB',(1080,1350),'#10292e');d=ImageDraw.Draw(im);d.text((50,29),'FOUNDEROS / CODEX + LOCAL BUSINESS TOOLS',font=font(17,True),fill='#78e6c3')
 y=69
 for line in headline.split('\n'):d.text((50,y),line,font=font(51,True),fill='white');y+=63
 d.text((50,1248),sentence,font=font(19),fill='#d1e4df');d.text((50,1300),'LOCAL POC · SYNTHETIC DATA',font=font(19,True),fill='#78e6c3');return im
manifest=[]
im=canvas('Four platforms.\nOne clear decision.','Shared records connect the creator signal to business context.')
y=225;paths=[]
for short in ['ugc','shopify','crm','klaviyo']:
 p=SRC/f'{short}-evidence-card.png';pic=Image.open(p).convert('RGB');pic.thumbnail((980,240),Image.Resampling.LANCZOS);im.paste(pic,(50,y));y+=pic.height+15;paths.append(str(p.relative_to(ROOT)))
out=OUT/'02-multiplatform-intelligence.png';im.save(out);manifest.append({'export':str(out.relative_to(ROOT)),'sources':paths,'proof':'Live shared records across four local mock platforms; the retention cohort is a separate opportunity, not a causal consequence of the creator outlier.','layout':'Resized screenshot crops pasted without changing contents.'})
p=SRC/'approved-execution-card.png'
if p.exists():
 im=canvas('One approval.\nThe work gets done.','Approved locally. Drafts remain unsent. Every write is recorded.')
 pic=Image.open(p).convert('RGB');pic.thumbnail((980,1000),Image.Resampling.LANCZOS);im.paste(pic,((1080-pic.width)//2,225));out=OUT/'03-approved-execution.png';im.save(out);manifest.append({'export':str(out.relative_to(ROOT)),'sources':[str(p.relative_to(ROOT))],'proof':'User approval, actual persisted briefs / drafts / assignments / tasks, and SQLite write count. No message delivery.','layout':'Unchanged browser screenshot resized on annotated canvas.'})
for m in manifest:m['sha256']=hashlib.sha256((ROOT/m['export']).read_bytes()).hexdigest()
(ROOT/'evidence/carousel-manifest.json').write_text(json.dumps(manifest,indent=2));print(json.dumps(manifest,indent=2))
