"""An extra Xbox 360 finish: disc-matched marks and pale original swirl pattern."""
from pathlib import Path
import copy,json,struct,hashlib,io
import numpy as np
from PIL import Image,ImageDraw,ImageFont
import math
from embed_default_labels import load,ROOT

TARGET='xbox360-disc-matched'
def build():
 source=ROOT/'outputs/xbox360-test.glb';target=ROOT/'outputs'/(TARGET+'.glb')
 sha=hashlib.sha256(source.read_bytes()).hexdigest()
 if target.exists():
  old,_=load(target)
  if old.get('extras',{}).get('discMatchedXbox360SourceSha256')==sha and old['extras'].get('discMatchedXbox360Version')==1:return
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
 # Reproduce the approved Xbox 360 glyph mask at its existing positions.
 S=4096;C=S/2;scale=S/.12
 lettering=Image.new('L',(S,S));font=ImageFont.truetype(str(ROOT/'outputs/branding-source/X360.ttf'),100)
 def stamp(tile,angle):
  tile=tile.rotate(-angle,resample=Image.Resampling.BICUBIC,expand=True)
  rad=math.radians(angle);x=C+math.sin(rad)*.0137*scale;y=C-math.cos(rad)*.0137*scale
  lettering.paste(tile,(round(x-tile.width/2),round(y-tile.height/2)),tile)
 logo=Image.open(ROOT/'work/xbox-logo.png').convert('RGBA').resize((145,145),Image.Resampling.LANCZOS).getchannel('A')
 for angle in range(0,360,90):stamp(logo,angle)
 for center in [45,135,225,315]:
  advances=[font.getlength(ch) for ch in 'XBOX 360'];factor=180/math.pi/(.0137*scale);angle=center-sum(advances)*factor/2
  for ch,width in zip('XBOX 360',advances):
   tile=Image.new('L',(140,160));bounds=font.getbbox(ch)
   ImageDraw.Draw(tile).text((70-(bounds[0]+bounds[2])/2,80-(bounds[1]+bounds[3])/2),ch,font=font,fill=255)
   stamp(tile,angle+width*factor/2);angle+=width*factor
 lettering=lettering.resize((2048,2048),Image.Resampling.LANCZOS)
 masks=[];pattern_masks=[]
 for mesh_index,side in [(7,'front'),(11,'rear')]:
  base=g['meshes'][mesh_index]['primitives'][0]
  mask=lettering.copy()
  rgba=Image.new('RGBA',mask.size,'white');rgba.putalpha(mask);out=io.BytesIO();rgba.save(out,format='PNG',optimize=True);png=out.getvalue()
  blob.extend(b'\0'*((-len(blob))%4));vi=len(g['bufferViews']);g['bufferViews'].append({'buffer':0,'byteOffset':len(blob),'byteLength':len(png)});blob.extend(png)
  ii=len(g['images']);g['images'].append({'bufferView':vi,'mimeType':'image/png','name':'xbox360-disc-matched-'+side+'-mask.png'})
  ti=len(g['textures']);g['textures'].append({'source':ii,'sampler':g['textures'][0].get('sampler',0)})
  material=copy.deepcopy(data);material['name']='XBOX360_DISC_MATCHED_'+side.upper()+'_BRANDING';material['alphaMode']='MASK';material['alphaCutoff']=.5
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
  xx*=.12/size;yy*=.12/size
  radius=np.hypot(xx,yy);azimuth=np.arctan2(yy,xx)
  annulus=(radius>.01115)&(radius<.01625)
  waves=np.zeros_like(radius);weights=np.zeros_like(radius)
  # Same twelve overlapping circular cells as the original 360 foil.
  for i in range(12):
   angle=i*math.tau/12;cr=.0137+.00065*math.sin(i*2.3)
   distance=np.hypot(xx-cr*math.cos(angle),yy-cr*math.sin(angle));weight=np.exp(-(distance/.00315)**4)
   waves+=weight*np.sin(distance*math.tau/.00032);weights+=weight
  waves/=np.maximum(weights,1e-6)
  lines=np.clip((waves-.25)/.75,0,1)
  pattern=(lines*annulus*(1-np.asarray(mask,dtype=np.float32)/255)*255).astype('uint8')
  rgba=Image.new('RGBA',mask.size,'white');rgba.putalpha(Image.fromarray(pattern));out=io.BytesIO();rgba.save(out,format='PNG',optimize=True);png=out.getvalue()
  blob.extend(b'\0'*((-len(blob))%4));vi=len(g['bufferViews']);g['bufferViews'].append({'buffer':0,'byteOffset':len(blob),'byteLength':len(png)});blob.extend(png)
  ii=len(g['images']);g['images'].append({'bufferView':vi,'mimeType':'image/png','name':'xbox360-pale-pattern-'+side+'.png'});pattern_masks.append(ii)
  ti=len(g['textures']);g['textures'].append({'source':ii,'sampler':g['textures'][0].get('sampler',0)})
  pale=copy.deepcopy(g['materials'][6]);pale['name']='XBOX360_PALE_'+side.upper()+'_SWIRL_PATTERN';pale['alphaMode']='MASK';pale['alphaCutoff']=.5;pale['doubleSided']=True
  pale['pbrMetallicRoughness'].update({'baseColorFactor':[.97,.97,.96,1],'roughnessFactor':.24,'baseColorTexture':{'index':ti}})
  pale['extensions']['KHR_materials_iridescence']['iridescenceFactor']=.03
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
 g.setdefault('extras',{}).update({'discMatchedXbox360SourceSha256':sha,'discMatchedXbox360Version':1,'discMatchedXbox360MaskImages':masks,'discMatchedXbox360PatternImages':pattern_masks,'discMatchedXbox360MasteringMeshes':sorted(set(mastering))})
 assert bytes(blob[:len(raw)])==raw
 g['buffers'][0]['byteLength']=len(blob);j=json.dumps(g,separators=(',',':')).encode();j+=b' '*((-len(j))%4);blob.extend(b'\0'*((-len(blob))%4))
 target.write_bytes(struct.pack('<III',0x46546c67,2,28+len(j)+len(blob))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(blob),0x004e4942)+blob)
 print('Extra Xbox 360 variant built: disc-matched branding, security dashes and serial text; pale original circular swirls.')
if __name__=='__main__':build()
