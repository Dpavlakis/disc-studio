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
 image=Image.open(path);assert image.size==(4096,4096)
 # Physical hub and hole are not painted into these cover images.
 if system!='ps2Branding':assert image.getpixel((2048,2048))[3]==255
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

# Covers retain fractional edge coverage, not binary stair-step boundaries.
import numpy as np
ps3=np.asarray(Image.open(ROOT/'outputs/default-labels/ps3.png'))
xs=np.arange(400,3700);ys=np.rint((375-45*(xs/4096))*4096/1200).astype(int)
samples=np.concatenate([ps3[ys+dy,xs,0] for dy in [-1,0,1]])
assert np.count_nonzero((samples>60)&(samples<200))>100
xbox=np.asarray(Image.open(ROOT/'outputs/default-labels/xbox.png').convert('RGB'))
green=(xbox[:,:,1].astype(int)>xbox[:,:,0].astype(int)*1.4)&(xbox[:,:,0]>60)
assert green[int(4096*.65):].sum()>1000
assert green[int(4096*.29):int(4096*.36)].sum()==0
svg=(ROOT/'outputs/branding-source/default-labels/templates/gc.svg').read_text()
assert 'y="386"' in svg and 'y="414"' in svg and 'y="851"' not in svg
print('4096px cover antialiasing, lower Xbox accent and visible GameCube text placement verified.')
