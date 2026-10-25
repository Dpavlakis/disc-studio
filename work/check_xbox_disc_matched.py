"""Verify the extra variant matches the data material and preserves its source."""
import copy,hashlib,json,io
import numpy as np
from PIL import Image
from build_xbox_disc_matched import ROOT,TARGET
from embed_default_labels import load,geometry
source=ROOT/'outputs/xbox-original-disc.glb';g,b=load(source)
variant=ROOT/'outputs'/(TARGET+'.glb');v,vb=load(variant)
assert v['extras']['discMatchedXboxVersion']==7
assert v['extras']['discMatchedXboxSourceSha256']==hashlib.sha256(source.read_bytes()).hexdigest()
assert vb[:len(b)]==b
assert len(v['meshes'])==len(g['meshes'])==20
actual_geometry=geometry(v,vb)
assert all(actual_geometry[i]==value for i,value in geometry(g,b).items())
for i,mesh in enumerate(g['meshes']):
 for j,p in enumerate(mesh['primitives']):
  q=copy.deepcopy(v['meshes'][i]['primitives'][j])
  if p['material'] in [16,17]:
   assert q['material']==1;q['material']=p['material']
  assert q==p
for i in [7,11]:
 assert len(v['meshes'][i]['primitives'])==3
 overlay=v['meshes'][i]['primitives'][1];material=copy.deepcopy(v['materials'][overlay['material']])
 assert overlay['attributes']['TEXCOORD_1']==g['meshes'][i]['primitives'][0]['attributes']['TEXCOORD_0']
 assert material.pop('alphaMode')=='MASK';assert material.pop('alphaCutoff')==.5
 info=material['pbrMetallicRoughness'].pop('baseColorTexture');assert info['texCoord']==1
 material['name']=g['materials'][1]['name'];assert material==g['materials'][1]
assert len(v['extras']['discMatchedXboxMasteringMeshes'])==4
assert v['materials'][:len(g['materials'])]==g['materials']
for image_index,side in zip(v['extras']['discMatchedXboxMaskImages'],['front','rear']):
 view=v['bufferViews'][v['images'][image_index]['bufferView']];start=view.get('byteOffset',0)
 actual=np.asarray(Image.open(io.BytesIO(vb[start:start+view['byteLength']])).getchannel('A'))
 expected=np.asarray(Image.open(ROOT/'work'/('xbox-vector-'+side+'.png')).convert('L'))
 assert np.array_equal(actual,expected), 'Only the supplied X/Xbox/genuine branding mask may have the new finish.'
html=(ROOT/'outputs/studio.html').read_text(encoding='utf-8')
assert 'data-finish="'+TARGET+'" data-platform="xbox"' in html
print('Extra Xbox variant: exact disc optical response on branding, security dashes and serial text, with the lighter geometric pattern kept separate, independent mask/full-disc UVs, original geometry and source preserved.')

for mesh_index,image_index in zip([7,11],v['extras']['discMatchedXboxPatternImages']):
 p=v['meshes'][mesh_index]['primitives'][2];m=v['materials'][p['material']]
 assert m['alphaMode']=='BLEND' and 'alphaCutoff' not in m
 assert m['pbrMetallicRoughness']['baseColorFactor']==[.86,.86,.85,.20]
 assert m['pbrMetallicRoughness']['roughnessFactor']==.12
 assert m['extensions']['KHR_materials_iridescence']['iridescenceFactor']==.10
 view=v['bufferViews'][v['images'][image_index]['bufferView']];start=view.get('byteOffset',0)
 alpha=np.asarray(Image.open(io.BytesIO(vb[start:start+view['byteLength']])).getchannel('A'))
 h,w=alpha.shape
 # Both side panels must contain visible squares, not empty sectors.
 assert np.count_nonzero(alpha[h//2-80:h//2+80,int(w*.83):int(w*.97)]>128)>1000
 assert np.count_nonzero(alpha[h//2-80:h//2+80,int(w*.03):int(w*.17)]>128)>1000
 assert np.count_nonzero(alpha[:h//3]>128)>1000
print('Pale silver pattern lines and both checkerboard panels verified independently of the disc-textured lettering.')
