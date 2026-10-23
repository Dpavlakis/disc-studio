"""Verify the extra variant matches the data material and preserves its source."""
import copy,hashlib,json
from build_xbox_disc_matched import ROOT,TARGET
from embed_default_labels import load,geometry
source=ROOT/'outputs/xbox-original-disc.glb';g,b=load(source)
variant=ROOT/'outputs'/(TARGET+'.glb');v,vb=load(variant)
assert v['extras']['discMatchedXboxVersion']==2
assert v['extras']['discMatchedXboxSourceSha256']==hashlib.sha256(source.read_bytes()).hexdigest()
assert vb[:len(b)]==b
assert len(v['meshes'])==len(g['meshes'])==20
actual_geometry=geometry(v,vb)
assert all(actual_geometry[i]==value for i,value in geometry(g,b).items())
for i,mesh in enumerate(g['meshes']):
 for j,p in enumerate(mesh['primitives']):
  q=copy.deepcopy(v['meshes'][i]['primitives'][j])
  if p['material'] in [16,17]:assert q['material']==1;q['material']=p['material']
  assert q==p
for i in [7,11]:
 assert len(v['meshes'][i]['primitives'])==2
 overlay=v['meshes'][i]['primitives'][1];material=copy.deepcopy(v['materials'][overlay['material']])
 assert overlay['attributes']['TEXCOORD_1']==g['meshes'][i]['primitives'][0]['attributes']['TEXCOORD_0']
 assert material.pop('alphaMode')=='MASK';assert material.pop('alphaCutoff')==.5
 info=material['pbrMetallicRoughness'].pop('baseColorTexture');assert info['texCoord']==1
 material['name']=g['materials'][1]['name'];assert material==g['materials'][1]
assert len(v['extras']['discMatchedXboxMasteringMeshes'])==4
html=(ROOT/'outputs/studio.html').read_text(encoding='utf-8')
assert 'data-finish="'+TARGET+'" data-platform="xbox"' in html
print('Extra Xbox variant: exact disc optical response on branding and security marks, independent mask/full-disc UVs, original geometry and source preserved.')
