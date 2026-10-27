from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib
ROOT=Path(__file__).resolve().parents[1];SRC=ROOT/'evidence/screenshots-original/pitch-simple';OUT=ROOT/'evidence/carousel-ready/pitch-simple';OUT.mkdir(exist_ok=True)
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf';BOLD='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
def font(n,b=False):return ImageFont.truetype(BOLD if b else FONT,n)
slides=[('01-find-the-winner','Find the content\nworth repeating.','84,000 views versus a 12,000-view creator baseline.'),('02-create-five-ideas','Turn a winner into\nfive fresh ideas.','Five original concepts, saved in the content workspace.'),('03-prepare-outreach','Get creator outreach\nready to review.','Three personalized messages, saved as unsent drafts.'),('04-approval-to-results','One approval.\nThe prep is done.','Briefs, assignments and follow-ups saved across the tools.')]
manifest=[]
for i,(name,title,sentence) in enumerate(slides,1):
 im=Image.new('RGB',(1080,1350),'#10292e');d=ImageDraw.Draw(im);d.text((50,33),'CODEX × YOUR BUSINESS TOOLS',font=font(22,True),fill='#85e9c8');d.text((932,33),f'{i:02} / 04',font=font(20,True),fill='#85e9c8')
 for j,line in enumerate(title.split('\n')):d.text((50,88+j*77),line,font=font(64,True),fill='white')
 source=SRC/(name+'-card.png');pic=Image.open(source).convert('RGB');pic.thumbnail((980,900),Image.Resampling.LANCZOS);im.paste(pic,((1080-pic.width)//2,285))
 d.text((50,1230),sentence,font=font(24),fill='#e5f0eb');d.text((50,1300),'LOCAL POC · SYNTHETIC DATA',font=font(22,True),fill='#85e9c8')
 out=OUT/(name+'.png');im.save(out)
 manifest.append({'file':str(out.relative_to(ROOT)),'source':str(source.relative_to(ROOT)),'size':[1080,1350],'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'proof':'Unchanged screenshot of real read-only platform view, populated from the persisted approved demo; headline and supporting sentence outside capture.','not_claimed':'No real integration, sent message, new campaign launch or business performance.'})
(ROOT/'evidence/pitch-carousel-manifest.json').write_text(json.dumps(manifest,indent=2));print('Four 1080x1350 pitch images exported.')
