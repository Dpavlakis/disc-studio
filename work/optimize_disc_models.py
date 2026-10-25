"""Lossless indexed runtime models, verified against expanded source triangles."""
from pathlib import Path
import copy,hashlib,json,struct,time,io
import numpy as np
from PIL import Image
from embed_default_labels import ROOT,load
DTYPES={5120:'i1',5121:'u1',5122:'<i2',5123:'<u2',5125:'<u4',5126:'<f4'}
WIDTHS={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}
VERSION=2

def array(g,b,index):
 a=g['accessors'][index];v=g['bufferViews'][a['bufferView']]
 assert 'sparse' not in a and not v.get('byteStride')
 return np.frombuffer(b,dtype=DTYPES[a['componentType']],count=a['count']*WIDTHS[a['type']],offset=v.get('byteOffset',0)+a.get('byteOffset',0)).reshape(a['count'],-1)

def signature(g,b):
 result=[]
 for mesh in g['meshes']:
  for p in mesh['primitives']:
   index=array(g,b,p['indices']).ravel() if 'indices' in p else np.arange(g['accessors'][p['attributes']['POSITION']]['count'])
   h=hashlib.sha256()
   for name,ai in sorted(p['attributes'].items()):
    h.update(name.encode());h.update(array(g,b,ai)[index].tobytes())
    h.update(str(bool(g['accessors'][ai].get('normalized',False))).encode())
   result.append((mesh['name'],p.get('mode',4),p['material'],len(index),h.hexdigest()))
 return result

def image_bytes(g,b,i):
 v=g['bufferViews'][g['images'][i]['bufferView']];o=v.get('byteOffset',0)
 return bytes(b[o:o+v['byteLength']])

def optimize(source,destination):
 sha=hashlib.sha256(source.read_bytes()).hexdigest()
 if destination.exists():
  prior,_=load(destination)
  meta=prior.get('extras',{}).get('runtimeOptimization',{})
  if meta.get('version')==VERSION and meta.get('sourceSha256')==sha:return meta['report']
 start=time.perf_counter();g,b=load(source);original=copy.deepcopy(g);before=signature(g,b)
 assert not g.get('animations') and not g.get('skins')
 groups={}
 for mesh in g['meshes']:
  for p in mesh['primitives']:
   assert p.get('mode',4)==4 and not p.get('targets')
   groups.setdefault(tuple(sorted(p['attributes'].items())),[]).append(p)
 blob=bytearray();views=[];accessors=[];cache={};vertices_before=vertices_after=0
 def view(data):
  blob.extend(b'\0'*((-len(blob))%4));i=len(views);views.append({'buffer':0,'byteOffset':len(blob),'byteLength':len(data)});blob.extend(data);return i
 def accessor(values,prototype,kind=None):
  a=np.ascontiguousarray(values);meta={k:v for k,v in prototype.items() if k not in {'bufferView','byteOffset','count','min','max'}}
  if kind:meta.update(type='SCALAR',componentType=kind)
  raw=a.tobytes();key=(json.dumps(meta,sort_keys=True),hashlib.sha256(raw).digest())
  if key in cache:return cache[key]
  i=len(accessors);meta.update(bufferView=view(raw),count=len(a))
  if a.size:meta.update(min=a.reshape(len(a),-1).min(axis=0).tolist(),max=a.reshape(len(a),-1).max(axis=0).tolist())
  accessors.append(meta);cache[key]=i;return i
 for key,primitives in groups.items():
  arrays=[array(original,b,ai) for _,ai in key];count=len(arrays[0]);vertices_before+=count
  records=np.ascontiguousarray(np.concatenate([a.view('u1').reshape(count,-1) for a in arrays],axis=1))
  indices=[array(original,b,p['indices']).ravel().astype(np.int64) if 'indices' in p else np.arange(count) for p in primitives]
  used=np.unique(np.concatenate(indices))
  packed=np.ascontiguousarray(records[used]);_,first,inverse=np.unique(packed.view(np.dtype((np.void,packed.shape[1]))).ravel(),return_index=True,return_inverse=True)
  # Keep unique vertices in first-use order for coherent GPU reads and compression.
  order=np.argsort(first);chosen=used[first[order]];lookup=np.empty(len(order),dtype=np.int64);lookup[order]=np.arange(len(order))
  remap=np.empty(count,dtype=np.int64);remap[used]=lookup[inverse];vertices_after+=len(chosen)
  attributes={name:accessor(a[chosen],original['accessors'][ai]) for (name,ai),a in zip(key,arrays)}
  component=5123 if len(chosen)<=65535 else 5125
  for p,index in zip(primitives,indices):
   p['attributes']=attributes.copy();p['indices']=accessor(remap[index].astype(DTYPES[component]).reshape(-1,1),{},component)
 # Preserve every texture. Only the invisible, superseded GameCube branding
 # placeholders use smaller runtime images; live SVG branding replaces them.
 resized=[]
 branding_images=set()
 if source.stem=='gamecube-disc':
  for m in g['materials']:
   if m['name'] in {'GAMECUBE_LABEL_PANEL','GAMECUBE_LABEL_FOIL'}:
    slot=m['pbrMetallicRoughness'].get('baseColorTexture')
    if slot:branding_images.add(g['textures'][slot['index']]['source'])
 for i,img in enumerate(g['images']):
  raw=image_bytes(original,b,i)
  if i in branding_images:
   im=Image.open(io.BytesIO(raw))
   if max(im.size)>2048:
    im.thumbnail((2048,2048),Image.Resampling.LANCZOS);out=io.BytesIO();im.save(out,format='PNG',optimize=True);raw=out.getvalue();resized.append(i)
  img['bufferView']=view(raw)
 g['accessors']=accessors;g['bufferViews']=views;g['buffers'][0]['byteLength']=len(blob)
 assert signature(g,blob)==before,'Expanded triangle attributes changed'
 assert g['materials']==original['materials'] and g['nodes']==original['nodes'] and g['scenes']==original['scenes']
 for i in range(len(g['images'])):
  if i not in resized:assert image_bytes(g,blob,i)==image_bytes(original,b,i)
 report={'model':source.name,'sourceBytes':source.stat().st_size,'vertexRecordsBefore':vertices_before,'vertexRecordsAfter':vertices_after,'triangleAttributesExact':True,'runtimeBrandingImagesResized':resized}
 g.setdefault('extras',{})['runtimeOptimization']={'version':VERSION,'sourceSha256':sha,'report':report}
 def encode():
  j=json.dumps(g,separators=(',',':')).encode();j+=b' '*((-len(j))%4);padded=blob+b'\0'*((-len(blob))%4)
  return struct.pack('<III',0x46546c67,2,28+len(j)+len(padded))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(padded),0x004e4942)+padded
 report['optimizedBytes']=len(encode());report['savedPercent']=round(100*(1-report['optimizedBytes']/report['sourceBytes']),1)
 # Adding the final report changes JSON length by a few bytes.
 report['optimizedBytes']=len(encode());report['optimizedBytes']=len(encode())
 destination.parent.mkdir(parents=True,exist_ok=True);destination.write_bytes(encode())
 final,fb=load(destination);assert signature(final,fb)==before
 print(f"{source.name}: {source.stat().st_size/1048576:.2f} -> {destination.stat().st_size/1048576:.2f} MiB; exact triangles verified ({time.perf_counter()-start:.1f}s)",flush=True)
 return report

def build_all():
 output=ROOT/'outputs/optimized-models';reports=[]
 for source in sorted((ROOT/'outputs').glob('*.glb')):reports.append(optimize(source,output/source.name))
 result={'method':'Exact vertex indexing; no simplification or quantization','models':reports,'sourceBytes':sum(r['sourceBytes'] for r in reports),'optimizedBytes':sum((output/r['model']).stat().st_size for r in reports)}
 (ROOT/'outputs/model-optimization-report.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
 return output
if __name__=='__main__':build_all()
