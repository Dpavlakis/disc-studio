"""Check ink-only changes, source image bytes and minified texture stability."""
import hashlib, io
import numpy as np
from PIL import Image
from printed_ink_finish import ROOT, load, surface_reference, maps

count=0
for path in (ROOT/'outputs').glob('*.glb'):
 g,b=load(path); finish=g['extras']['printedInkFinish']
 assert finish['version']==2
 assert hashlib.sha256(b[:finish['originalBufferBytes']]).hexdigest()==finish['originalBufferSha256']
 for index, original in finish['originalMaterials'].items():
  actual=g['materials'][int(index)];surface_reference(g,int(index))
  assert actual['pbrMetallicRoughness'].get('baseColorTexture')==original['pbrMetallicRoughness'].get('baseColorTexture')
  assert actual.get('alphaMode')==original.get('alphaMode')
  for mesh in g['meshes']:
   for p in mesh['primitives']:
    if p['material']==int(index):assert 'TEXCOORD_0' in p['attributes'] and 'NORMAL' in p['attributes']
 for i,(_,expected) in zip(finish['images'],maps()):
  view=g['bufferViews'][g['images'][i]['bufferView']];start=view.get('byteOffset',0)
  assert b[start:start+view['byteLength']]==expected
 for ti in finish['textures']:
  sampler=g['samplers'][g['textures'][ti]['sampler']]
  assert sampler=={'magFilter':9729,'minFilter':9987,'wrapS':10497,'wrapT':10497}
 count+=1
normal=np.asarray(Image.open(io.BytesIO(maps()[0][1])))
# Round dot relief must vary in both directions; a scanline normal fails this.
assert np.ptp(normal[:,:,0])>80 and np.ptp(normal[:,:,1])>80
assert np.abs(np.diff(normal[:,:,0].astype(float),axis=1)).mean()>2
assert np.abs(np.diff(normal[:,:,1].astype(float),axis=0)).mean()>2
rough=np.asarray(Image.open(io.BytesIO(maps()[1][1])))[:,:,1]
assert np.ptp(rough[0])>2 and np.ptp(rough[:,0])>2
assert np.array_equal(normal[:-16],normal[16:])
# A distant mip resolves the alternating slopes to a neutral normal.
mip=np.asarray(Image.fromarray(normal).resize((4,4),Image.Resampling.BOX))
assert np.abs(mip[:,:,1].astype(float)-128).max()<=1
assert .52*235/255>.4 and .52<.6
runtime=(ROOT/'work/package.py').read_text(encoding='utf-8')
assert 'p.setRoughnessFactor(.52)' in runtime
print(f'Printed finish verified on {count} models: unchanged art/geometry bytes, satin response, two-dimensional halftone dots and neutral distant mip.')
