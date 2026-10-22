"""Check PSX optical layers, through-hole, winding and reproducible refinement."""
import hashlib
import json
from pathlib import Path
import struct
import numpy as np
from refine_ps1 import refine_ps1
from ps1_hub_profiles import height

root = Path(__file__).resolve().parents[1]/'outputs'
path = root/'ps1-black-disc.glb'
raw = path.read_bytes()
size = struct.unpack_from('<I',raw,12)[0]
g = json.loads(raw[20:20+size])
binary = raw[28+size:]
assert len(raw) == struct.unpack_from('<I',raw,8)[0]
assert len(g['meshes']) == 16
mats = g['materials']
for i in (1,2,3,4,5,7,8,9):
    m = mats[i]
    assert m.get('alphaMode','OPAQUE') == 'OPAQUE'
    assert max(m['pbrMetallicRoughness']['baseColorFactor'][:3]) < .005
    assert m['pbrMetallicRoughness']['metallicFactor'] == (.35 if i in (1,5,9) else 0)
    assert m['extensions'].get('KHR_materials_transmission',{}).get('transmissionFactor',0)==(.02 if i in (2,4) else 0)
    assert 'KHR_materials_iridescence' not in m['extensions']
    assert 'baseColorTexture' not in m['pbrMetallicRoughness']
for i in (1,5,9):
    assert mats[i]['normalTexture']['scale'] == .25
    assert mats[i]['extensions']['KHR_materials_anisotropy']['anisotropyStrength'] == .83
hub = mats[2]
assert hub.get('alphaMode','OPAQUE') == 'OPAQUE'
assert 'KHR_materials_transmission' in g['extensionsUsed']
assert 'KHR_materials_volume' not in g['extensionsUsed']
assert all(m.get('extensions',{}).get('KHR_materials_transmission',{}).get('transmissionFactor',0)==(.02 if i in (2,4) else 0) for i,m in enumerate(mats))
assert all('KHR_materials_volume' not in m.get('extensions',{}) for m in mats)
assert mats[6]['pbrMetallicRoughness']['baseColorFactor'][3] == 0
assert mats[6]['name'] == 'PS1_CENTRE_PRINT'
assert mats[6]['pbrMetallicRoughness']['baseColorTexture'] == mats[0]['pbrMetallicRoughness']['baseColorTexture']
foil_index = next(i for i,m in enumerate(mats) if m['name']=='PS1_FRONT_MASTERING_FOIL')
assert mats[foil_index]['pbrMetallicRoughness']['metallicFactor'] == 1
assert not mats[foil_index]['doubleSided']
assert mats[foil_index]['normalTexture']['scale']==.07
assert mats[foil_index]['extensions']['KHR_materials_anisotropy']['anisotropyStrength']==.95
assert mats[foil_index]['extensions']['KHR_materials_iridescence']['iridescenceFactor']==.85
assert 'iridescenceThicknessTexture' in mats[foil_index]['extensions']['KHR_materials_iridescence']
active={i for scene in g['scenes'] for i in scene['nodes']}
assert all(i not in active for i,node in enumerate(g['nodes']) if node.get('name','').startswith(('09_','10_','11_','12_','13_')))

def read(index):
    a = g['accessors'][index]
    view = g['bufferViews'][a['bufferView']]
    width = {'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']]
    return np.frombuffer(binary,dtype={5126:'<f4',5125:'<u4'}[a['componentType']],
                         count=a['count']*width,offset=view.get('byteOffset',0)+a.get('byteOffset',0)).reshape(-1,width)

for mesh in g['meshes']:
    for primitive in mesh['primitives']:
        p = read(primitive['attributes']['POSITION'])
        radius = np.linalg.norm(p[:,[0,2]],axis=1)
        assert radius.min() >= .007499, mesh['name']
        if mesh['name'] == '04_Clear_Centre_Hub':
            assert abs(radius.max()-.0195)<1e-7
            assert abs(radius.min()-.0075)<1e-7
        if mesh['name'] == '01_Replaceable_Art_Top':
            assert abs(radius.min()-.0195)<1e-7
            assert abs(p[:,1].max()-.00082)<1e-8
            assert p[:,1].max()-.000625>.00019
        if mesh['name'] == '07_Optional_PS1_Centre_Print':
            assert abs(radius.min()-.0114)<1e-7
            assert abs(radius.max()-.0182)<1e-7
            assert radius.min()>.0075 and radius.max()<.0195
            assert np.allclose(p[:,1],.00062+height(radius*1000,'top')/1000,atol=1e-8)
        if mesh['name'].startswith('05_Moulded_Ring_'):
            assert np.allclose(p[:,1],-.0006-height(radius*1000,'bottom')/1000,atol=1e-8)
            assert np.isclose(np.linalg.norm(read(primitive['attributes']['NORMAL']),axis=1),1).all()
        if mesh['name'] in ('01_Replaceable_Art_Top','07_Optional_PS1_Centre_Print'):
            uv = read(primitive['attributes']['TEXCOORD_0'])
            assert np.allclose(uv, .5-p[:,[0,2]]/.12,atol=1e-7)
        if mesh['name'] in ('06_Etched_Branding_Matrix_Ring','14_Inner_Reflective_Substrate'):
            assert radius.min()>=.019499
        if primitive['material'] == foil_index:
            assert abs(radius.max()-.0587)<1e-7
            assert np.allclose(p[:,1],.0006)
            assert np.all(read(primitive['attributes']['NORMAL'])[:,1]>.99)
        if 'indices' in primitive:
            triangles = read(primitive['indices']).reshape(-1,3)
            normals = read(primitive['attributes']['NORMAL'])
            cross = np.cross(p[triangles[:,1]]-p[triangles[:,0]],p[triangles[:,2]]-p[triangles[:,0]])
            assert np.all(np.sum(cross*normals[triangles[:,0]],axis=1)>0),mesh['name']
before = {p.name:hashlib.sha256(p.read_bytes()).digest() for p in root.glob('*.glb')}
refine_ps1(path)
assert before == {p.name:hashlib.sha256(p.read_bytes()).digest() for p in root.glob('*.glb')}
print('Verified 2% transmission restricted to the black hub and moulded rings; silver and data surfaces opaque, open hole, approved relief, outward winding, artwork UVs and idempotence.')
