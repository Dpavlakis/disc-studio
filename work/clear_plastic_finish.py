"""Optical clear plastic, preserving all geometry and reflective disc materials."""
import json,struct
from pathlib import Path

def apply_clear_plastic_finish(g):
 changed=[]
 for material in g['materials']:
  if 'KHR_materials_transmission' not in material.get('extensions',{}):continue
  # Transmission carries light through a full surface; alpha blending had
  # reduced its reflections and made overlapping plastic look flat/tinted.
  material['alphaMode']='OPAQUE';material.pop('alphaCutoff',None)
  material['pbrMetallicRoughness']={'baseColorFactor':[1,1,1,1],'metallicFactor':0,'roughnessFactor':.025}
  material['extensions']={'KHR_materials_transmission':{'transmissionFactor':1},'KHR_materials_ior':{'ior':1.58},'KHR_materials_volume':{'thicknessFactor':.0012,'attenuationColor':[1,1,1]},'KHR_materials_clearcoat':{'clearcoatFactor':.25,'clearcoatRoughnessFactor':.025}}
  changed.append(material['name'])
 if changed:
  for extension in ['KHR_materials_transmission','KHR_materials_ior','KHR_materials_volume','KHR_materials_clearcoat']:
   if extension not in g.setdefault('extensionsUsed',[]):g['extensionsUsed'].append(extension)
 return changed

def update_model(path):
 raw=path.read_bytes();size=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+size]);binary=raw[28+size:]
 original=json.dumps(g,sort_keys=True)
 geometry=json.dumps({key:g[key] for key in ['meshes','nodes','accessors','bufferViews']},sort_keys=True)
 changed=apply_clear_plastic_finish(g)
 if not changed:return
 if original==json.dumps(g,sort_keys=True) and len(binary)%4==0:return
 assert geometry==json.dumps({key:g[key] for key in ['meshes','nodes','accessors','bufferViews']},sort_keys=True)
 j=json.dumps(g,separators=(',',':')).encode();j+=b' '*((-len(j))%4)
 padded=binary+b'\0'*((-len(binary))%4)
 path.write_bytes(struct.pack('<III',0x46546c67,2,28+len(j)+len(padded))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(padded),0x004e4942)+padded)
 check=path.read_bytes();n=struct.unpack_from('<I',check,12)[0];assert check[28+n:28+n+len(binary)]==binary
 print(path.name+': clear plastic updated; geometry and binary assets unchanged ('+', '.join(changed)+').')

if __name__=='__main__':
 root=Path(__file__).resolve().parents[1]/'outputs'
 for path in root.glob('*.glb'):
  if path.name.startswith(('ps2-','xbox-','xbox360-')) or path.name=='gamecube-disc.glb':update_model(path)
