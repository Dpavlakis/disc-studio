"""An extra Xbox finish: original shapes, disc-matched security marks."""
from pathlib import Path
import copy,json,struct,hashlib,io
import numpy as np
from PIL import Image
from embed_default_labels import load,ROOT

TARGET='xbox-original-disc-matched'
def build():
 source=ROOT/'outputs/xbox-original-disc.glb';target=ROOT/'outputs'/(TARGET+'.glb')
 sha=hashlib.sha256(source.read_bytes()).hexdigest()
 if target.exists():
  old,_=load(target)
  if old.get('extras',{}).get('discMatchedXboxSourceSha256')==sha and old['extras'].get('discMatchedXboxVersion')==6:return
 g,raw=load(source);blob=bytearray(raw);data=copy.deepcopy(g['materials'][1])
 def attr(primitive,key):
  a=g['accessors'][primitive['attributes'][key]];v=g['bufferViews'][a['bufferView']]
  width={'VEC2':2,'VEC3':3,'VEC4':4}[a['type']]
  return np.frombuffer(blob,dtype='<f4',count=a['count']*width,offset=v.get('byteOffset',0)+a.get('byteOffset',0)).reshape(-1,width).copy()
 def accessor(array,kind):
  a=np.asarray(array,dtype='<f4');blob.extend(b'\0'*((-len(blob))%4));vi=len(g['bufferViews'])
  g['bufferViews'].append({'buffer':0,'byteOffset':len(blob),'byteLength':a.nbytes});blob.extend(a.tobytes())
  i=len(g['accessors']);g['accessors'].append({'bufferView':vi,'componentType':5126,'count':len(a),'type':kind,'min':a.min(axis=0).tolist(),'max':a.max(axis=0).tolist()});return i
 # Use the data face's full-disc UV convention for its groove/thickness maps.
 face=g['meshes'][1]['primitives'][0];pos=attr(face,'POSITION');uv=attr(face,'TEXCOORD_0')
 projection=np.linalg.lstsq(np.column_stack((pos[:,0],pos[:,2],np.ones(len(pos)))),uv,rcond=None)[0]
 masks=[];pattern_masks=[]
 for mesh_index,side in [(7,'front'),(11,'rear')]:
  base=g['meshes'][mesh_index]['primitives'][0]
  mask=Image.open(ROOT/'work'/('xbox-vector-'+side+'.png')).convert('L')
  rgba=Image.new('RGBA',mask.size,'white');rgba.putalpha(mask);out=io.BytesIO();rgba.save(out,format='PNG',optimize=True);png=out.getvalue()
  blob.extend(b'\0'*((-len(blob))%4));vi=len(g['bufferViews']);g['bufferViews'].append({'buffer':0,'byteOffset':len(blob),'byteLength':len(png)});blob.extend(png)
  ii=len(g['images']);g['images'].append({'bufferView':vi,'mimeType':'image/png','name':'xbox-disc-matched-'+side+'-mask.png'})
  ti=len(g['textures']);g['textures'].append({'source':ii,'sampler':g['textures'][0].get('sampler',0)})
  material=copy.deepcopy(data);material['name']='XBOX_DISC_MATCHED_'+side.upper()+'_BRANDING';material['alphaMode']='MASK';material['alphaCutoff']=.5
  material['pbrMetallicRoughness']['baseColorTexture']={'index':ti,'texCoord':1}
  mi=len(g['materials']);g['materials'].append(material)
  points=attr(base,'POSITION');normals=attr(base,'NORMAL');points+=normals*.00004
  full_uv=np.column_stack((points[:,0],points[:,2],np.ones(len(points))))@projection
  overlay=copy.deepcopy(base);overlay['material']=mi
  overlay['attributes']['POSITION']=accessor(points,'VEC3');overlay['attributes']['TEXCOORD_0']=accessor(full_uv,'VEC2')
  overlay['attributes']['TEXCOORD_1']=base['attributes']['TEXCOORD_0']
  g['meshes'][mesh_index]['primitives'].append(overlay);masks.append(ii)
  # Pale silver pattern, separate from the disc-textured branding above it.
  size=mask.width
  yy,xx=np.indices((size,size),dtype=np.float32);xx-=size/2;yy-=size/2
  radius=np.hypot(xx,yy)*.034/size;degrees=np.degrees(np.arctan2(xx,-yy))
  annulus=(radius>.0112)&(radius<.0162)
  panels=(np.abs((degrees-90+180)%360-180)<20)|(np.abs((degrees-270+180)%360-180)<20)
  squares=((np.floor((degrees+20)/(40/6))+np.floor((radius-.0112)/(.005/3)))%2)*panels*annulus
  contours=np.asarray(Image.open(ROOT/'work/xbox-vector-contours.png').convert('L'),dtype=np.float32)
  lines=np.clip((contours-140)/41,0,1)*(~panels)*annulus
  pattern=(np.maximum(lines,squares)*(1-np.asarray(mask,dtype=np.float32)/255)*255).astype('uint8')
  rgba=Image.new('RGBA',mask.size,'white');rgba.putalpha(Image.fromarray(pattern));out=io.BytesIO();rgba.save(out,format='PNG',optimize=True);png=out.getvalue()
  blob.extend(b'\0'*((-len(blob))%4));vi=len(g['bufferViews']);g['bufferViews'].append({'buffer':0,'byteOffset':len(blob),'byteLength':len(png)});blob.extend(png)
  ii=len(g['images']);g['images'].append({'bufferView':vi,'mimeType':'image/png','name':'xbox-pale-pattern-'+side+'.png'});pattern_masks.append(ii)
  ti=len(g['textures']);g['textures'].append({'source':ii,'sampler':g['textures'][0].get('sampler',0)})
  pale=copy.deepcopy(g['materials'][6]);pale['name']='XBOX_PALE_'+side.upper()+'_PATTERN_AND_SQUARES';pale['alphaMode']='BLEND';pale['doubleSided']=True
  pale['pbrMetallicRoughness'].update({'baseColorFactor':[.86,.86,.85,.10],'roughnessFactor':.12,'baseColorTexture':{'index':ti}})
  pale['extensions']['KHR_materials_iridescence']['iridescenceFactor']=.10
  mi=len(g['materials']);g['materials'].append(pale)
  pale_overlay=copy.deepcopy(base);pale_overlay['material']=mi
  pale_overlay['attributes']['POSITION']=accessor(attr(base,'POSITION')+normals*.00002,'VEC3')
  g['meshes'][mesh_index]['primitives'].append(pale_overlay)

 # Native dashes and serial outlines use the full-disc UV convention.
 mastering=[]
 for mesh in g['meshes']:
  for primitive in mesh['primitives']:
   if primitive['material'] in [16,17]:
    primitive['material']=1;mastering.append(mesh['name'])
 g.setdefault('extras',{}).update({'discMatchedXboxSourceSha256':sha,'discMatchedXboxVersion':6,'discMatchedXboxMaskImages':masks,'discMatchedXboxPatternImages':pattern_masks,'discMatchedXboxMasteringMeshes':sorted(set(mastering))})
 assert bytes(blob[:len(raw)])==raw
 g['buffers'][0]['byteLength']=len(blob);j=json.dumps(g,separators=(',',':')).encode();j+=b' '*((-len(j))%4);blob.extend(b'\0'*((-len(blob))%4))
 target.write_bytes(struct.pack('<III',0x46546c67,2,28+len(j)+len(blob))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(blob),0x004e4942)+blob)
 print('Extra Xbox variant built: disc-matched branding, security dashes and serial text; lighter silver geometric pattern and checker squares.')
if __name__=='__main__':build()
