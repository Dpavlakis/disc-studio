"""Verify approved placeholder assets and preserve the existing disc files."""
from pathlib import Path
import hashlib,json,re,base64,struct
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
expected=json.loads((ROOT/'work/default-label-model-hashes.json').read_text())
assert expected=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'outputs').glob('*.glb')}
html=(ROOT/'outputs/studio.html').read_text(encoding='utf-8')
labels=json.loads(re.search(r'const defaultLabels=(\{.*?\});let activeSystem=',html).group(1))
for system,asset in {'ps1':'ps1','ps2':'ps2','ps3':'ps3','ps4':'ps4','xbox':'xbox','xbox360':'x360','gamecube':'gc','ps2Branding':'ps2-branding'}.items():
 path=ROOT/'outputs/default-labels'/(asset+'.png')
 assert labels[system]=='data:image/png;base64,'+base64.b64encode(path.read_bytes()).decode()
 image=Image.open(path);assert image.size==(1200,1200)
 # Physical hub and hole are not painted into these cover images.
 if system!='ps2Branding':assert image.getpixel((600,600))[3]==255
assert "let url=artURL||defaultLabels[system]" in html
assert all(text not in html for text in ['GC-07','Expanded controls','THE MATERIAL COLLECTION','OPTICAL / MATERIAL STUDY','LOCAL WORKSPACE'])
assert 'print-intensity' not in html and 'print-dot-size' not in html
print('Seven approved placeholder covers and separate PS2 footer embedded; sidebar copy simplified; all ten model files unchanged.')
