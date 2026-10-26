"""Verify runtime meshes preserve the source render data and reduce file size."""
import hashlib,json,io,gzip,base64
from pathlib import Path
from PIL import Image
from optimize_disc_models import ROOT,load,signature,image_bytes

report=json.loads((ROOT/'outputs/model-optimization-report.json').read_text())
assert len(report['models'])==12
for row in report['models']:
 source=ROOT/'outputs'/row['model'];target=ROOT/'outputs/optimized-models'/row['model']
 g,b=load(source);v,vb=load(target);meta=v['extras']['runtimeOptimization']
 assert meta['sourceSha256']==hashlib.sha256(source.read_bytes()).hexdigest()
 assert signature(g,b)==signature(v,vb)
 for key in ['materials','textures','samplers','nodes','scenes']:assert g.get(key)==v.get(key),(source.name,key)
 assert target.stat().st_size<source.stat().st_size
 for i in range(len(g['images'])):
  original=image_bytes(g,b,i);runtime=image_bytes(v,vb,i)
  if i in row['runtimeBrandingImagesResized']:
   assert source.stem=='gamecube-disc'
   assert max(Image.open(io.BytesIO(runtime)).size)<=2048
  else:assert original==runtime,(source.name,'image',i)
html=(ROOT/'outputs/studio.html').read_text(encoding='utf-8')
payloads=json.loads(html.split('<script>const models=',1)[1].split('; const v=',1)[0])
assert len(payloads)==12
for name,payload in payloads.items():
 assert payload.startswith('gzip:')
 assert gzip.decompress(base64.b64decode(payload[5:]))==(ROOT/'outputs/optimized-models'/f'{name}.glb').read_bytes()
package=(ROOT/'work/package.py').read_text(encoding='utf-8')
assert "for p in optimized_root.glob('*.glb')" in package
assert "gzip.compress(p.read_bytes()" in package
assert 'new DecompressionStream' in html
assert 'id="export"' not in html
assert "v.exportScene(" not in html
assert 'id="download-png"' in html
assert report['optimizedBytes']<report['sourceBytes']*.65
print('All twelve optimized models: exact expanded triangle attributes, unchanged materials/transforms/visible artwork, smaller files, optimized studio inputs and PNG-only studio verified.')
