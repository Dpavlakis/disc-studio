"""PSX opaque black base, separate front label and optional centre print."""
from pathlib import Path
import copy
import json
import math
import struct
import numpy as np
from ps1_hub_profiles import profile as hub_profile


def refine_ps1(path):
    path = Path(path)
    raw = path.read_bytes()
    size = struct.unpack_from('<I', raw, 12)[0]
    g = json.loads(raw[20:20+size])
    if g.get('extras', {}).get('psxBlackSubstrateVersion') == 13:
        return
    binary_size = struct.unpack_from('<I', raw, 20+size)[0]
    blob = bytearray(raw[28+size:28+size+binary_size])
    mats = g['materials']
    black = {
        'baseColorFactor': [.0025, .0027, .0032, 1],
        'metallicFactor': 0, 'roughnessFactor': .085,
    }
    glossy = {
        'KHR_materials_clearcoat': {'clearcoatFactor': 1, 'clearcoatRoughnessFactor': .045},
        'KHR_materials_ior': {'ior': 1.58},
    }
    # The data area stays opaque; the white specular reflection comes from the
    # plastic surface, rather than raising the black substrate's base colour.
    for index in (1, 5, 9):
        mats[index]['pbrMetallicRoughness'] = copy.deepcopy(black)
        mats[index]['extensions'] = copy.deepcopy(glossy)
        mats[index].pop('alphaMode', None)
        mats[index].pop('alphaCutoff', None)
        # Match the PS2 track relief and tangent-driven reflection response,
        # while retaining the neutral-black PSX base colour and opaque body.
        mats[index]['pbrMetallicRoughness']['metallicFactor'] = .35
        mats[index]['pbrMetallicRoughness']['roughnessFactor'] = .115
        mats[index]['normalTexture'] = {'index': 1, 'scale': .25}
        mats[index]['extensions']['KHR_materials_anisotropy'] = {'anisotropyStrength': .83, 'anisotropyRotation': 0}
        mats[index]['extensions']['KHR_materials_clearcoat'] = {'clearcoatFactor': .65, 'clearcoatRoughnessFactor': .07}
    mats[1]['name'] = 'BLACK_DATA_REFLECTIVE'
    mats[5]['name'] = 'PS1_BLACK_INNER_SUBSTRATE'
    mats[9]['name'] = 'INNER_DISC_SUBSTRATE'
    # The centre is the same opaque black plastic as the disc body.
    hub = {
        'name': 'PS1_OPAQUE_BLACK_HUB',
        'pbrMetallicRoughness': copy.deepcopy(black),
        'extensions': copy.deepcopy(glossy),
    }
    mats[2] = copy.deepcopy(hub)
    mats[4] = copy.deepcopy(hub)
    mats[4]['name'] = 'PS1_BLACK_MOULDED_RINGS'
    # A very faint optical transmission, restricted to the moulded centre.
    # Keep alpha opaque so reflections and silhouettes remain well defined.
    for index in (2,4):
        mats[index]['extensions']['KHR_materials_transmission']={'transmissionFactor':.02}
    if 'KHR_materials_transmission' not in g['extensionsUsed']:
        g['extensionsUsed'].append('KHR_materials_transmission')
    for index in (3, 7, 8):
        mats[index]['pbrMetallicRoughness'] = copy.deepcopy(black)
        mats[index]['extensions'] = copy.deepcopy(glossy)
    mats[3]['name'] = 'PS1_BLACK_POLISHED_EDGE'
    # Reuse the unused PS2 band slot for the optional centre print. Its UVs
    # sample the same artwork and rotation as the outer label.
    mats[6] = {'name': 'PS1_CENTRE_PRINT', 'alphaMode': 'BLEND',
               'pbrMetallicRoughness': {'baseColorTexture': copy.deepcopy(mats[0]['pbrMetallicRoughness']['baseColorTexture']),
                                       'baseColorFactor': [1,1,1,0], 'metallicFactor': 0, 'roughnessFactor': .36}}
    foil_index = next((i for i,m in enumerate(mats) if m['name']=='PS1_FRONT_MASTERING_FOIL'),len(mats))
    foil = {'name': 'PS1_FRONT_MASTERING_FOIL', 'doubleSided': False,
            'pbrMetallicRoughness': {'baseColorFactor': [.55, .55, .55, 1], 'metallicFactor': 1, 'roughnessFactor': .115},
            'normalTexture': {'index': 1, 'scale': .25},
            'extensions': {'KHR_materials_anisotropy': {'anisotropyStrength': .83, 'anisotropyRotation': 0},
                           'KHR_materials_iridescence': {'iridescenceFactor': .14, 'iridescenceIor': 1.38, 'iridescenceThicknessMinimum': 380, 'iridescenceThicknessMaximum': 380},
                           'KHR_materials_clearcoat': {'clearcoatFactor': .15, 'clearcoatRoughnessFactor': .07}}}
    if foil_index == len(mats):
        mats.append(foil)
    else:
        mats[foil_index] = foil
    # Separate, high-resolution alpha marks preserve the foil's light response.
    image_index=next((i for i,image in enumerate(g['images']) if image.get('name')=='ps1-mastering-ring.png'),None)
    if image_index is None:
        image_path=path.parent/'ps1-mastering-ring.png'
        if not image_path.exists():
            import subprocess,sys
            subprocess.run([sys.executable,str(Path(__file__).with_name('make_ps1_matrix.py'))],check=True)
        image_bytes=image_path.read_bytes()
        while len(blob)%4:blob.append(0)
        g['bufferViews'].append({'buffer':0,'byteOffset':len(blob),'byteLength':len(image_bytes)})
        blob.extend(image_bytes)
        image_index=len(g['images']);g['images'].append({'name':'ps1-mastering-ring.png','bufferView':len(g['bufferViews'])-1,'mimeType':'image/png'})
        g['textures'].append({'source':image_index,'sampler':0})
    else:
        image_bytes=(path.parent/'ps1-mastering-ring.png').read_bytes()
        while len(blob)%4:blob.append(0)
        g['bufferViews'].append({'buffer':0,'byteOffset':len(blob),'byteLength':len(image_bytes)})
        blob.extend(image_bytes)
        g['images'][image_index]['bufferView']=len(g['bufferViews'])-1
    texture_index=next(i for i,texture in enumerate(g['textures']) if texture['source']==image_index)
    marking_index=next((i for i,m in enumerate(mats) if m['name']=='PS1_MASTERING_MARKS'),len(mats))
    marking={'name':'PS1_MASTERING_MARKS','alphaMode':'MASK','alphaCutoff':.35,
             'pbrMetallicRoughness':{'baseColorTexture':{'index':texture_index},'baseColorFactor':[1,1,1,1],'metallicFactor':.25,'roughnessFactor':.2}}
    if marking_index==len(mats):mats.append(marking)
    else:mats[marking_index]=marking
    for extension in ('KHR_materials_volume','KHR_materials_transmission'):
        if not any(extension in m.get('extensions',{}) for m in mats):
            g['extensionsUsed'] = [e for e in g['extensionsUsed'] if e != extension]

    def accessor(values, kind, integer=False):
        a = np.asarray(values, dtype='<u4' if integer else '<f4')
        while len(blob) % 4:
            blob.append(0)
        g['bufferViews'].append({'buffer': 0, 'byteOffset': len(blob), 'byteLength': a.nbytes})
        blob.extend(a.tobytes())
        obj = {'bufferView': len(g['bufferViews'])-1, 'componentType': 5125 if integer else 5126, 'count': len(a), 'type': kind}
        if not integer:
            obj.update(min=a.min(axis=0).tolist(), max=a.max(axis=0).tolist())
        g['accessors'].append(obj)
        return len(g['accessors'])-1

    def primitive(profile, material, front_uv=False, span=.12):
        p, n, uv, t, indices = [], [], [], [], []
        resolution = 2048
        for (ra, ya), (rb, yb) in zip(profile, profile[1:]):
            dr, dy = rb-ra, yb-ya
            length = math.hypot(dr, dy)
            base = len(p)
            for i in range(resolution+1):
                a = i*math.tau/resolution
                c, s = math.cos(a), math.sin(a)
                for r, y in ((ra, ya), (rb, yb)):
                    p.append((r*c, y, r*s))
                    n.append((dy/length*c, -dr/length, dy/length*s))
                    uv.append((.5+(-1 if front_uv else 1)*r*c/span, .5-r*s/span))
                    t.append((-s, 0, c, 1))
            for i in range(resolution):
                k = base+2*i
                for a, b, c in ((k, k+1, k+3), (k, k+3, k+2)):
                    cross = np.cross(np.array(p[b])-p[a], np.array(p[c])-p[a])
                    indices.extend((a,b,c) if np.dot(cross, n[a])>0 else (a,c,b))
        return {'attributes': {'POSITION': accessor(p, 'VEC3'), 'NORMAL': accessor(n, 'VEC3'),
                               'TEXCOORD_0': accessor(uv, 'VEC2'), 'TANGENT': accessor(t, 'VEC4')},
                'indices': accessor(indices, 'SCALAR', True), 'material': material}

    def smooth_lathe(points,material,front_uv=False):
        # Share radial rows and use smooth profile normals for rounded moulding.
        points=np.asarray(points);delta=np.gradient(points,axis=0)
        delta/=np.linalg.norm(delta,axis=1)[:,None]
        angles=np.linspace(0,math.tau,1025);c=np.cos(angles);s=np.sin(angles)
        p=np.stack((points[:,0,None]*c,np.broadcast_to(points[:,1,None],(len(points),1025)),points[:,0,None]*s),axis=-1).reshape(-1,3)
        n=np.stack((delta[:,1,None]*c,np.broadcast_to(-delta[:,0,None],(len(points),1025)),delta[:,1,None]*s),axis=-1).reshape(-1,3)
        uv=np.stack((.5+(-1 if front_uv else 1)*p[:,0]/.12,.5-p[:,2]/.12),axis=-1)
        tangent=np.tile(np.stack((-s,np.zeros_like(s),c,np.ones_like(s)),axis=-1),(len(points),1))
        indices=[]
        for row in range(len(points)-1):
            for i in range(1024):
                a=row*1025+i;b=a+1025
                for tri in ((a,b,b+1),(a,b+1,a+1)):
                    cross=np.cross(p[tri[1]]-p[tri[0]],p[tri[2]]-p[tri[0]])
                    indices.extend(tri if np.dot(cross,n[tri[0]])>0 else (tri[0],tri[2],tri[1]))
        return {'attributes':{'POSITION':accessor(p,'VEC3'),'NORMAL':accessor(n,'VEC3'),
                              'TEXCOORD_0':accessor(uv,'VEC2'),'TANGENT':accessor(tangent,'VEC4')},
                'indices':accessor(indices,'SCALAR',True),'material':material}

    meshes = {m['name']: m for m in g['meshes']}
    # The old 10-micrometre separation produced radial depth-buffer conflicts
    # with masked artwork. Give the ink layer a stable offset and closed lips.
    meshes['01_Replaceable_Art_Top']['primitives'] = [primitive([
        (.0587,.0006),(.0587,.00082),(.0195,.00082),(.0195,.0006)],0,True)]
    meshes['03_Outer_Bevel_Edge']['primitives'][0]['material'] = 3
    points=hub_profile('top',19.5,7.5)+hub_profile('bottom',7.5,10.8)
    meshes['04_Clear_Centre_Hub']['primitives'] = [smooth_lathe(points,2)]
    for j,(ri,ro) in enumerate(((10.8,12.5),(12.5,19.5),(19.5,22))):
        meshes['05_Moulded_Ring_'+str(j)]['primitives'] = [smooth_lathe(hub_profile('bottom',ri,ro),4)]
    centre_mesh = meshes.get('07_Top_PS2_Branding_Above_Artwork',meshes.get('07_Optional_PS1_Centre_Print'))
    centre_mesh['name'] = '07_Optional_PS1_Centre_Print'
    centre_mesh['primitives'] = [smooth_lathe([(r,y+.00002) for r,y in hub_profile('top',18.2,11.4)],6,True)]
    for node in g['nodes']:
        if node.get('name') == '07_Top_PS2_Branding_Above_Artwork':
            node['name'] = centre_mesh['name']
    # Silver extends under the entire label, including transparent print gaps.
    # Its uncovered inner annulus is the visible mastering area. It faces only
    # the artwork side; the underside and centre remain opaque black.
    meshes['06_Etched_Branding_Matrix_Ring']['primitives'] = [
        primitive([(.0587,.0006),(.0195,.0006)],foil_index),
        primitive([(.02198,.000625),(.01955,.000625)],marking_index,True,span=.044),
    ]
    meshes['14_Inner_Reflective_Substrate']['primitives'] = [primitive([(.022,-.0006),(.022,.0006)],9)]
    # Retire the old PS2 matrix pieces; they cut through the new curved hub
    # and produced intermittent bright marks along otherwise solid grooves.
    retired={i for i,node in enumerate(g['nodes']) if node.get('name','').startswith(('09_','10_','11_','12_','13_'))}
    for scene in g['scenes']:scene['nodes']=[i for i in scene['nodes'] if i not in retired]
    from ps1_silver_response import apply_xbox_silver_response
    apply_xbox_silver_response(g,blob,path.parent)
    g.setdefault('extras', {})['psxBlackSubstrateVersion'] = 13
    g['extras']['psxFinish'] = 'Opaque black disc and hub; separate silver or white front label; optional centre print at 11.4–18.2 mm leaves black inner and outer rings.'
    g['buffers'][0]['byteLength'] = len(blob)
    js = json.dumps(g,separators=(',',':')).encode()
    js += b' '*((-len(js))%4)
    blob += b'\0'*((-len(blob))%4)
    path.write_bytes(struct.pack('<III',0x46546c67,2,28+len(js)+len(blob))+
                     struct.pack('<II',len(js),0x4e4f534a)+js+struct.pack('<II',len(blob),0x004e4942)+blob)
    print('Refined PSX opaque black base, separate face and optional centre print:',path.name)


if __name__ == '__main__':
    refine_ps1(Path(__file__).resolve().parents[1]/'outputs/ps1-black-disc.glb')
