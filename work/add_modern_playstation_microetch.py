"""Faint mip-filtered micro-etch just outside modern PlayStation mastering rings."""
from pathlib import Path
import json,struct,copy,math,random,io
import numpy as np
from PIL import Image
from build_modern_playstation import load,ROOT

def update(path):
 g,blob=load(path);extra=g.setdefault('extras',{})
 if extra.get('outerMicroEtchVersion')==1:return
 width,height=8192,64;rng=random.Random(314159);alpha=np.zeros(width);cursor=0
 while cursor<width:
  stroke=rng.randint(1,3);alpha[cursor:cursor+stroke]=rng.uniform(.4,1.0)*255;cursor+=stroke+rng.randint(2,5)
 fade=np.sin(np.linspace(0,math.pi,height))**1.8;rgba=np.full((height,width,4),255,np.uint8);rgba[:,:,3]=np.uint8(fade[:,None]*alpha[None,:]);im=Image.fromarray(rgba);im.save(ROOT/'outputs/ps-modern-outer-microetch.png');out=io.BytesIO();im.save(out,format='PNG');data=out.getvalue();blob.extend(b'\0'*((-len(blob))%4));vi=len(g['bufferViews']);g['bufferViews'].append({'buffer':0,'byteOffset':len(blob),'byteLength':len(data)});blob.extend(data);image_index=len(g['images']);g['images'].append({'bufferView':vi,'mimeType':'image/png'});sampler=len(g.setdefault('samplers',[]));g['samplers'].append({'magFilter':9729,'minFilter':9987,'wrapS':10497,'wrapT':33071});tex=len(g['textures']);g['textures'].append({'sampler':sampler,'source':image_index})
 material=copy.deepcopy(g['materials'][1]);material['name']=extra['platform'].upper()+'_SUBTLE_OUTER_MICROETCH';material['alphaMode']='BLEND';material['doubleSided']=False;pbr=material['pbrMetallicRoughness'];pbr['baseColorTexture']={'index':tex,'texCoord':1};pbr['baseColorFactor']=[.68,.68,.68,.12];pbr['roughnessFactor']=.17;mi=len(g['materials']);g['materials'].append(material)
 outer=extra['securityOuterRadiusMm']/1000;ri,ro=outer+.000025,outer+.00033;pos=[];norm=[];uv=[];polar=[];tan=[]
 for i in range(2048):
  corners=[]
  for r,t,u,v in [(ri,i*math.tau/2048,i/2048,0),(ro,i*math.tau/2048,i/2048,1),(ro,(i+1)*math.tau/2048,(i+1)/2048,1),(ri,(i+1)*math.tau/2048,(i+1)/2048,0)]:corners.append((r*math.sin(t),-.00073,r*math.cos(t),u,v))
  for k in [0,2,1,0,3,2]:
   x,y,z,u,v=corners[k];pos.append((x,y,z));norm.append((0,-1,0));uv.append((.5-x/.12,.5-z/.12));polar.append((u,v));tan.append((1,0,0,1))
 def acc(data,kind):
  a=np.asarray(data,dtype='<f4');blob.extend(b'\0'*((-len(blob))%4));v=len(g['bufferViews']);g['bufferViews'].append({'buffer':0,'byteOffset':len(blob),'byteLength':a.nbytes});blob.extend(a.tobytes());i=len(g['accessors']);g['accessors'].append({'bufferView':v,'componentType':5126,'count':len(a),'type':kind,'min':a.min(axis=0).tolist(),'max':a.max(axis=0).tolist()});return i
 p={'material':mi,'attributes':{key:acc(a,t) for key,a,t in [('POSITION',pos,'VEC3'),('NORMAL',norm,'VEC3'),('TEXCOORD_0',uv,'VEC2'),('TEXCOORD_1',polar,'VEC2'),('TANGENT',tan,'VEC4')]}}
 g['meshes'][10]['primitives'].append(p);extra['outerMicroEtchVersion']=1;extra['outerMicroEtchImageIndices']=[image_index];extra['outerMicroEtchWidthMm']=.305;extra['outerMicroEtchOpacity']=.12
 g['buffers'][0]['byteLength']=len(blob);j=json.dumps(g,separators=(',',':')).encode();j+=b' '*((-len(j))%4);blob.extend(b'\0'*((-len(blob))%4));path.write_bytes(struct.pack('<III',0x46546c67,2,28+len(j)+len(blob))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(blob),0x004e4942)+blob)
 print(path.name+': faint outer micro-etch added with distance filtering.')
if __name__=='__main__':
 for key in ['ps3','ps4']:update(ROOT/'outputs'/(key+'-silver-disc.glb'))
