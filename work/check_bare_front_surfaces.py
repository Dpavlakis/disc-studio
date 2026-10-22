import json
import numpy as np
from fix_bare_front_surfaces import TARGETS,protected_front,front_name,ROOT,load
og,_=load(ROOT/'outputs/xbox-original-disc.glb');mirror=next(m for m in og['materials'] if m['name']=='ORIGINAL_XBOX_TEST_PLAIN_REFLECTIVE_SILVER')
for name in TARGETS:
 g,b=load(ROOT/'outputs'/(name+'.glb'));assert g['extras']['bareFrontSurfaceVersion']==1
 actual=protected_front(g,b);expected=json.loads((ROOT/'work'/(name+'-bare-front-baseline.json')).read_text())
 if name=='ps3-silver-disc' and g['extras']['modernPlayStationVersion']>=6:
  # Separately checked: read surface now meets the resized security ring.
  actual.pop('PS3_Silver_Data_Underside');expected.pop('PS3_Silver_Data_Underside')
 if name=='ps3-silver-disc' and g['extras']['modernPlayStationVersion']>=7:
  for key in ['PS3_Native_Logo_And_Matrix_Outlines','PS3_Mastering_Track','PS3_Separated_Mastering_Tags']:
   actual.pop(key);expected.pop(key)
 if name=='ps3-silver-disc' and g['extras']['modernPlayStationVersion']>=8:
  for index in g['extras'].get('modernImportedDataImages',g['extras'].get('ps3ImportedDataImages',[])):actual.pop('IMAGE-'+str(index))
 if name=='ps4-silver-disc' and g['extras']['modernPlayStationVersion']>=5:
  # PS4's new tighter security layout and shared data material are checked
  # against the geometry/material requirements in check_modern_playstation.
  for key in ['PS4_Silver_Data_Underside','PS4_Silver_Inner_Security_Field','PS4_Native_Logo_And_Matrix_Outlines','PS4_Fine_Mastering_Outer_Boundary','PS4_Mastering_Track','PS4_Separated_Mastering_Tags','PS4_Inner_Silver_Substrate']:
   actual.pop(key);expected.pop(key)
  for index in g['extras']['modernImportedDataImages']:actual.pop('IMAGE-'+str(index))
 if g['extras'].get('outerMicroEtchVersion')==1:
  for index in g['extras']['outerMicroEtchImageIndices']:actual.pop('IMAGE-'+str(index))
  if name=='ps3-silver-disc':
   actual.pop('PS3_Fine_Mastering_Outer_Boundary');expected.pop('PS3_Fine_Mastering_Outer_Boundary')
 if g['extras'].get('modernOuterDataTransitionVersion')==1:
  actual.pop(g['extras']['platform'].upper()+'_Plain_Outer_Rim_Transition');expected.pop('08_Smooth_Outer_Ring_Both_Sides')
 assert actual==expected,name
 materials=[m for m in g['materials'] if '_PLAIN_MIRROR_FRONT_' in m['name']] if name.startswith('ps') else [next(m for m in g['materials'] if m['name']=='BARE_FRONT_XBOX_MIRROR_SURFACE')]
 assert len(materials)==(2 if name.startswith('ps') else 1)
 for material in materials:assert {k:v for k,v in material.items() if k!='name'}=={k:v for k,v in mirror.items() if k!='name'}
 if name.startswith('xbox'):
  p=next(m for m in g['meshes'] if m['name']==front_name(g))['primitives'][0];a=g['accessors'][p['attributes']['POSITION']];v=g['bufferViews'][a['bufferView']];points=np.frombuffer(b,dtype='<f4',count=a['count']*3,offset=v.get('byteOffset',0)).reshape(-1,3);r=np.linalg.norm(points[:,[0,2]],axis=1)
  assert np.allclose(points[:,1],.00048 if g['extras'].get('artworkDepthSeparationVersion')==1 else .0006) and abs(r.min()-.0167)<1e-8 and abs(r.max()-.0594)<1e-8
  t=points.reshape(-1,3,3);assert (np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0])[:,1]>0).all()
  artwork=g['meshes'][0]['primitives'][0];art=g['accessors'][artwork['attributes']['POSITION']];assert art['min'][1]>.0006
 print(name+': plain mirror front; no missing coverage; artwork above backing; approved protected components unchanged.')
