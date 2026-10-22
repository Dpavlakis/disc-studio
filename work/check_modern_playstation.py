from pathlib import Path
import json,struct,hashlib
import numpy as np
from PIL import Image,ImageDraw
from build_modern_playstation import load,ROOT
base,baseblob=load(ROOT/'outputs/ps2-silver-disc.glb')
def attr(g,b,p,key):
 a=g['accessors'][p['attributes'][key]];v=g['bufferViews'][a['bufferView']];o=v.get('byteOffset',0)+a.get('byteOffset',0);return bytes(b[o:o+v['byteLength']])
preview=Image.new('RGB',(1800,900),'#e8e8e5');d=ImageDraw.Draw(preview)
for ci,console in enumerate(['ps3','ps4']):
 path=ROOT/'outputs'/(console+'-silver-disc.glb');g,b=load(path);ex=g['extras'];assert ex['baseSha256'] in set(json.loads((ROOT/'work/ps2-silver-source-history.json').read_text())) | {hashlib.sha256((ROOT/'outputs/ps2-silver-disc.glb').read_bytes()).hexdigest()}
 for index in ([0,2,16,17] if console=='ps3' else [0,2,3,4,5,6,16,17]):
  for p,q in zip(g['meshes'][index]['primitives'],base['meshes'][index]['primitives']):
   for key in p['attributes']:assert attr(g,b,p,key)==attr(base,baseblob,q,key)
 if console in ['ps3','ps4']:
  p=g['meshes'][1]['primitives'][0];a=g['accessors'][p['attributes']['POSITION']];v=g['bufferViews'][a['bufferView']];face=np.frombuffer(b,dtype='<f4',count=a['count']*3,offset=v.get('byteOffset',0)).reshape(-1,3)
  assert abs(np.linalg.norm(face[:,[0,2]],axis=1).min()*1000-ex['securityOuterRadiusMm'])<.0001
 assert abs(np.linalg.norm(face[:,[0,2]],axis=1).max()*1000-58.4)<.0001
 rim=g['meshes'][9]['primitives'][-1];a=g['accessors'][rim['attributes']['POSITION']];v=g['bufferViews'][a['bufferView']];rp=np.frombuffer(b,dtype='<f4',count=a['count']*3,offset=v.get('byteOffset',0)).reshape(-1,3);rr=np.linalg.norm(rp[:,[0,2]],axis=1)*1000
 assert abs(rr.min()-58.4)<.0001 and abs(rr.max()-59.4)<.0001
 assert rim['material']==g['meshes'][7]['primitives'][0]['material']
 pbr=g['materials'][1]['pbrMetallicRoughness'];assert 'baseColorTexture' not in pbr and 'metallicRoughnessTexture' not in pbr
 xbox,_=load(ROOT/'outputs/xbox-original-disc.glb');mirror=next(m for m in xbox['materials'] if m['name']=='ORIGINAL_XBOX_TEST_PLAIN_REFLECTIVE_SILVER')
 for index in [g['meshes'][7]['primitives'][0]['material']]:
  assert {k:v for k,v in g['materials'][index].items() if k!='name'}=={k:v for k,v in mirror.items() if k!='name'}
 if console in ['ps3','ps4']:
  assert abs(ex['masteringTagHeightMm']-.62)<1e-8
  assert g['meshes'][13]['primitives'][0]['material']==g['meshes'][1]['primitives'][0]['material']==1
  assert g['meshes'][8]['primitives'][0]['material']==1
  runs=ex['masteringRunsDeg']
  assert min(a for a,b in runs)==43 and max(b for a,b in runs)==133
  assert all(43<=a<b<=133 for a,b in runs)
  assert max(b for a,b in runs)-min(a for a,b in runs)==90
  for mesh_index,source_name in [(14,'ORIGINAL_XBOX_REFERENCE_MASTERING_BARS')]:
   material=g['materials'][g['meshes'][mesh_index]['primitives'][0]['material']];source=next(m for m in xbox['materials'] if m['name']==source_name)
   assert {k:v for k,v in material.items() if k!='name'}=={k:v for k,v in source.items() if k!='name'}
 if console in ['ps3','ps4']:
  xbox,xboxblob=load(ROOT/'outputs/xbox-original-disc.glb');current=g['materials'][1];source=xbox['materials'][1]
  assert current['pbrMetallicRoughness']==source['pbrMetallicRoughness']
  assert current['extensions']['KHR_materials_anisotropy']==source['extensions']['KHR_materials_anisotropy']
  assert current['extensions']['KHR_materials_iridescence']['iridescenceFactor']==.85
  for local,original in [(current['normalTexture']['index'],source['normalTexture']['index']),(current['extensions']['KHR_materials_iridescence']['iridescenceThicknessTexture']['index'],source['extensions']['KHR_materials_iridescence']['iridescenceThicknessTexture']['index'])]:
   iv=g['bufferViews'][g['images'][g['textures'][local]['source']]['bufferView']];ov=xbox['bufferViews'][xbox['images'][xbox['textures'][original]['source']]['bufferView']]
   assert bytes(b[iv.get('byteOffset',0):iv.get('byteOffset',0)+iv['byteLength']])==bytes(xboxblob[ov.get('byteOffset',0):ov.get('byteOffset',0)+ov['byteLength']])
 assert ex['securityOuterRadiusMm']==(18.6 if console=='ps3' else 18.8) and ex['securityInnerRadiusMm']==(10.45 if console=='ps3' else 11.4)
 for m in g['meshes']:
  for p in m['primitives']:assert p['material'] not in [5,6,8,9],m['name']
 assert len(ex['securityPlacements'])==8
 for item in ex['securityPlacements']:
  if item['label']=='PS monogram':assert item['widthMm']==3.30
  if item['label']==console.upper():assert item['widthMm']==(7.15 if console=='ps3' else 6.71)

 if console=='ps4':
  assert any(item['label']=='Representative B4DL-132540B1' for item in ex['securityPlacements'])
  for lo,hi in [(66,69),(89,92),(110,113)]:assert not any(a<hi and b>lo for a,b in ex['masteringRunsDeg'])
  for item in ex['securityPlacements']:
   if item['label'] not in ['PS monogram','PS4']:continue
   assert item['radiusMm']==14.15
   inner_gap=item['radiusMm']-item['heightMm']/2-(ex['securityInnerRadiusMm']+.47)
   outer_gap=(ex['securityOuterRadiusMm']-1.25)-(item['radiusMm']+item['heightMm']/2)
   assert 1.5 < outer_gap/inner_gap < 2.7

 wordmarks=[x for x in ex['securityPlacements'] if x['label']==console.upper()];assert len(wordmarks)==3 and {x['angleDeg'] for x in wordmarks}=={60,180,300}
 for item in wordmarks:assert abs(item['widthMm']/item['heightMm']-item['nativeAspect'])<1e-9
 assert abs(ex['securityTextSourceAreaMm2']-ex['securityTriangleAreaMm2'])<1e-8
 for idx in [7,8,10,11,12,13,14,15]:
  for p in g['meshes'][idx]['primitives']:
   a=g['accessors'][p['attributes']['POSITION']];v=g['bufferViews'][a['bufferView']];points=np.frombuffer(b,dtype='<f4',count=a['count']*3,offset=v.get('byteOffset',0)).reshape(-1,3);assert np.linalg.norm(points[:,[0,2]],axis=1).max()<=(ex['securityOuterRadiusMm']+(.331 if idx==10 else .001))/1000;tri=points.reshape(-1,3,3);assert np.isfinite(points).all();assert (np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0])[:,1]<0).all()
 xcentre=450+ci*900;yc=450;scale=17
 d.ellipse((xcentre-380,yc-380,xcentre+380,yc+380),fill='#b5b8b2')
 for idx in [15,7,13,14,10,11,12,8]:
  p=g['meshes'][idx]['primitives'][0];a=g['accessors'][p['attributes']['POSITION']];v=g['bufferViews'][a['bufferView']];points=np.frombuffer(b,dtype='<f4',count=a['count']*3,offset=v.get('byteOffset',0)).reshape(-1,3)
  color={15:'#bfc2bc',7:'#c2c4bf',13:'#8a918a',14:'#d9ddd4',10:'#e5e8de',11:'#333833',12:'#e5e8de',8:'#7c847b'}[idx]
  for tri in points.reshape(-1,3,3):d.polygon([(xcentre+x*1000*scale,yc-z*1000*scale) for x,y,z in tri],fill=color)
 d.ellipse((xcentre-7.5*scale,yc-7.5*scale,xcentre+7.5*scale,yc+7.5*scale),fill='#e8e8e5')
 d.text((xcentre-15,20),console.upper(),fill='black')
 print(console+': inherited silver body intact, supplied SVG aspect ratios, six logos, native text fill and outward surfaces verified.')
preview.save(ROOT/'outputs/previews/ps3-ps4-security-layout.png')



