"""Two separated barcode rows without bridging fragments."""
from pathlib import Path
import json,struct,math,random
import numpy as np
from refine_original_xbox_mastering import fingerprint
ROOT=Path(__file__).resolve().parents[1]
def update(path):
 raw=path.read_bytes();n=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+n]);blob=bytearray(raw[28+n:]);extra=g.setdefault('extras',{})
 if extra.get('originalXboxSeparatedTagsVersion')==1:return
 before=fingerprint(g,blob);measure=json.loads((ROOT/'work/xbox_original_security_measurements.json').read_text());tracks=[]
 def pattern(seed,arc):
  rng=random.Random(seed);cursor,end=arc;runs=[]
  while cursor<end:
   width=max(.32,rng.choice(measure['barcodeWidthSamplesDeg'])*rng.uniform(.94,1.06));stop=min(end,cursor+width)
   if stop-cursor>=.3:runs.append((cursor,stop))
   cursor=stop+max(.50,rng.choice(measure['barcodeGapSamplesDeg'])*rng.uniform(.94,1.06))
  return runs
 specs=[]
 for i,(prefix,key) in enumerate([('12_Original_Xbox_Mastering_Barcode_Outer_Track','outer'),('13_Original_Xbox_Mastering_Barcode_Inner_Track','inner')]):
  runs=pattern(measure['seed']+i,measure[key+'ArcDeg']);specs.append((prefix,measure[key+'TrackRadiusMm'],measure[key+'TrackHeightMm'],runs))
 # Keep the mesh count stable by assigning the former fragment mesh one real
 # tag from the outer row. There are no tags left in the radial gap.
 last=specs[0][3].pop();specs.append(('14_Original_Xbox_Mastering_Barcode_Middle_Group',specs[0][1],specs[0][2],[last]))
 def acc(data,kind):
  a=np.asarray(data,dtype='<f4');blob.extend(b'\0'*((-len(blob))%4));vi=len(g['bufferViews']);g['bufferViews'].append({'buffer':0,'byteOffset':len(blob),'byteLength':a.nbytes});blob.extend(a.tobytes());i=len(g['accessors']);g['accessors'].append({'bufferView':vi,'componentType':5126,'type':kind,'count':len(a),'min':a.min(axis=0).tolist(),'max':a.max(axis=0).tolist()});return i
 for name,radius,height,runs in specs:
  pos=[];norm=[];uv=[];tan=[]
  for start,end in runs:
   steps=max(1,math.ceil((end-start)/.25))
   for i in range(steps):
    a=math.radians(start+(end-start)*i/steps);b=math.radians(start+(end-start)*(i+1)/steps);corners=[(r*math.sin(t)/1000,-.00072,r*math.cos(t)/1000) for r,t in [(radius-height/2,a),(radius+height/2,a),(radius+height/2,b),(radius-height/2,b)]]
    for tri in [(0,2,1),(0,3,2)]:
     for k in tri:
      x,y,z=corners[k];pos.append((x,y,z));norm.append((0,-1,0));uv.append((.5-x/.12,.5-z/.12));tan.append((1,0,0,1))
  mesh=next(m for m in g['meshes'] if m['name']==name);material=mesh['primitives'][0]['material'];mesh['primitives']=[{'material':material,'attributes':{k:acc(a,t) for k,a,t in [('POSITION',pos,'VEC3'),('NORMAL',norm,'VEC3'),('TEXCOORD_0',uv,'VEC2'),('TANGENT',tan,'VEC4')]}}]
  tracks.append({'name':name,'radiusMm':radius,'heightMm':height,'arcDeg':[runs[0][0],runs[-1][1]],'barCount':len(runs),'runsDeg':runs})
 extra['originalXboxMasteringTracks']=tracks;extra['originalXboxSeparatedTagsVersion']=1
 assert before==fingerprint(g,blob)
 g['buffers'][0]['byteLength']=len(blob);j=json.dumps(g,separators=(',',':')).encode();j+=b' '*((-len(j))%4);blob.extend(b'\0'*((-len(blob))%4));path.write_bytes(struct.pack('<III',0x46546c67,2,28+len(j)+len(blob))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(blob),0x004e4942)+blob)
 print('Separated barcode tags: two rows, no bridging fragments, minimum 0.50 degree angular gaps.')
if __name__=='__main__':update(ROOT/'outputs/xbox-original-disc.glb')
