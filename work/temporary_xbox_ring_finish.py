"""Temporary original Xbox ring inspection finish; --restore restores its mirror material."""
from pathlib import Path
import json,struct,copy,sys
p=Path(__file__).resolve().parents[1]/'outputs/xbox-original-disc.glb'
r=p.read_bytes();n=struct.unpack_from('<I',r,12)[0];g=json.loads(r[20:20+n]);b=r[28+n:]
band=next(m for m in g['meshes'] if m['name']=='10_Original_Xbox_Back_Mastering_Band');primitive=band['primitives'][0];extras=g.setdefault('extras',{})
if '--restore' in sys.argv:
 if 'originalXboxInspectionOriginalMaterial' in extras:primitive['material']=extras.pop('originalXboxInspectionOriginalMaterial')
 extras.pop('originalXboxBlackRingInspection',None)
else:
 extras.setdefault('originalXboxInspectionOriginalMaterial',primitive['material'])
 name='TEMP_ORIGINAL_XBOX_BLACK_SECURITY_RING'
 index=next((i for i,m in enumerate(g['materials']) if m['name']==name),None)
 if index is None:
  index=len(g['materials']);g['materials'].append({'name':name,'pbrMetallicRoughness':{'baseColorFactor':[.004,.004,.004,1],'metallicFactor':0,'roughnessFactor':.85}})
 primitive['material']=index;extras['originalXboxBlackRingInspection']=True
j=json.dumps(g,separators=(',',':')).encode();j+=b' '*((-len(j))%4)
p.write_bytes(struct.pack('<III',0x46546c67,2,28+len(j)+len(b))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(b),0x004e4942)+b)
print('Original Xbox security ring inspection finish:', 'mirror restored' if '--restore' in sys.argv else 'temporary black; bars and centre preserved')
