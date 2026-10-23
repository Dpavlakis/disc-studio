"""Verify approved placeholder assets and preserve the existing disc files."""
from pathlib import Path
import hashlib,json,re,base64,struct
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
expected=json.loads((ROOT/'work/default-label-model-hashes.json').read_text())
assert expected=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'outputs').glob('*.glb') if p.name in expected}
html=(ROOT/'outputs/studio.html').read_text(encoding='utf-8')
for system,asset in {'ps1':'ps1','ps2':'ps2','ps3':'ps3','ps4':'ps4','xbox':'xbox','xbox360':'x360','gamecube':'gc','ps2Branding':'ps2-branding'}.items():
 path=ROOT/'outputs/default-labels'/(asset+'.png')
 image=Image.open(path);assert image.size==(1200,1200)
 # Physical hub and hole are not painted into these cover images.
 if system!='ps2Branding':assert image.getpixel((600,600))[3]==255
assert "let url=artURL;let texture;" in html
assert all(text not in html for text in ['GC-07','Expanded controls','THE MATERIAL COLLECTION','OPTICAL / MATERIAL STUDY','LOCAL WORKSPACE'])
assert 'print-intensity' not in html and 'print-dot-size' not in html
print('Seven approved placeholder covers and separate PS2 footer embedded; sidebar copy simplified; all ten approved model files match their recorded cover update.')

# The initial native cover must equal the approved image before any async UI work.
from embed_default_labels import SYSTEMS,load
for name,key in SYSTEMS.items():
 g,b=load(ROOT/'outputs'/(name+'.glb'))
 for m in g['materials']:
  if m['name'] not in {'TOP_ART_REPLACE_THIS_TEXTURE','TOP_PERMANENT_PS2_BRANDING'}:continue
  asset='ps2-branding' if m['name']=='TOP_PERMANENT_PS2_BRANDING' else key
  texture=g['textures'][m['pbrMetallicRoughness']['baseColorTexture']['index']]
  view=g['bufferViews'][g['images'][texture['source']]['bufferView']];o=view.get('byteOffset',0)
  assert b[o:o+view['byteLength']]==(ROOT/'outputs/default-labels'/(asset+'.png')).read_bytes()
print('Native models contain the approved starter covers; old embedded placeholders cannot flash during loading.')
