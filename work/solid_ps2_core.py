"""Close the PS2 core under the removable label and beside the clear hub."""
from pathlib import Path
import json
import struct
import math
import copy
import numpy as np


def close_ps2_core(path):
    path=Path(path)
    raw=path.read_bytes()
    size=struct.unpack_from('<I',raw,12)[0]
    g=json.loads(raw[20:20+size])
    mesh=next(m for m in g['meshes'] if m['name']=='Closed_Outer_Laminate_Edge')
    if mesh.get('extras',{}).get('solidPS2CoreVersion')==4:
        return
    length=struct.unpack_from('<I',raw,20+size)[0]
    blob=bytearray(raw[28+size:28+size+length])
    material=mesh['primitives'][0]['material']
    def backing(source,name):
        index=next((i for i,m in enumerate(g['materials']) if m['name']==name),len(g['materials']))
        mat=copy.deepcopy(g['materials'][source]);mat['name']=name;mat['doubleSided']=False;mat['alphaMode']='OPAQUE';mat.pop('alphaCutoff',None)
        if index==len(g['materials']):g['materials'].append(mat)
        else:g['materials'][index]=mat
        return index
    # Use the existing optical finishes, not the plain edge material, on faces.
    data_material=backing(1,'PS2_FRONT_DATA_BACKING')
    matrix_material=backing(9,'PS2_FRONT_MATRIX_BACKING')
    # The removable artwork must have an opaque substrate beneath it. Close
    # the inner wall down to the existing mastering film's lower surface too.
    profiles=[((.0594,-.0006),(.0594,.0006),material),
              ((.0590,.0006),(.022,.0006),data_material),
              ((.022,.00035),(.0114,.00035),matrix_material),
              ((.022,.0006),(.022,.00035),material),
              ((.0594,.0006),(.0593,.0006),data_material),
              ((.0114,.00035),(.0114,-.0009),material)]
    p,n,uv,t,indices=[],[],[],[],[]
    groups=[]
    for (ra,ya),(rb,yb),face_material in profiles:
        first_index=len(indices)
        dr,dy=rb-ra,yb-ya
        distance=math.hypot(dr,dy)
        base=len(p)
        for i in range(2049):
            a=i*math.tau/2048
            c,s=math.cos(a),math.sin(a)
            for r,y in ((ra,ya),(rb,yb)):
                p.append((r*c,y,r*s));n.append((dy/distance*c,-dr/distance,dy/distance*s))
                uv.append((.5+r*c/.12,.5-r*s/.12));t.append((-s,0,c,-1 if dr<0 and dy==0 else 1))
        for i in range(2048):
            k=base+2*i
            for a,b,c in ((k,k+1,k+3),(k,k+3,k+2)):
                cross=np.cross(np.array(p[b])-p[a],np.array(p[c])-p[a])
                indices.extend((a,b,c) if np.dot(cross,n[a])>0 else (a,c,b))
        groups.append((first_index,len(indices),face_material))

    def accessor(values,kind,integer=False):
        array=np.asarray(values,dtype='<u4' if integer else '<f4')
        while len(blob)%4:blob.append(0)
        g['bufferViews'].append({'buffer':0,'byteOffset':len(blob),'byteLength':array.nbytes})
        blob.extend(array.tobytes())
        a={'bufferView':len(g['bufferViews'])-1,'componentType':5125 if integer else 5126,'count':len(array),'type':kind}
        if not integer:a.update(min=array.min(axis=0).tolist(),max=array.max(axis=0).tolist())
        g['accessors'].append(a)
        return len(g['accessors'])-1

    attrs={'POSITION':accessor(p,'VEC3'),'NORMAL':accessor(n,'VEC3'),'TEXCOORD_0':accessor(uv,'VEC2'),'TANGENT':accessor(t,'VEC4')}
    mesh['primitives']=[{'attributes':attrs,'indices':accessor(indices[start:end],'SCALAR',True),'material':face_material}
                         for start,end,face_material in groups]
    def read(index):
        a=g['accessors'][index];view=g['bufferViews'][a['bufferView']]
        width={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']]
        return np.frombuffer(blob,dtype={5126:'<f4',5125:'<u4'}[a['componentType']],count=a['count']*width,
                             offset=view.get('byteOffset',0)+a.get('byteOffset',0)).reshape(-1,width).copy()
    # Reproduce the complete mastering construction, not just its colour map.
    # Compress it behind the removable label; both sides retain the same UVs,
    # so the lettering and barcode read as a physical reverse of one another.
    for detail in g['meshes']:
        name=detail['name']
        if not (name.startswith('05_Moulded_Ring_') or name.startswith(('06_','09_','10_','11_','12_','13_'))):continue
        originals=[pr for pr in detail['primitives'] if not pr.get('extras',{}).get('ps2MirroredRear')]
        reflected=[]
        for original in originals:
            arrays={key:read(index) for key,index in original['attributes'].items()}
            count=len(arrays['POSITION'])
            indices_array=read(original['indices']).reshape(-1,3) if 'indices' in original else np.arange(count,dtype='<u4').reshape(-1,3)
            arrays['POSITION'][:,1]=-arrays['POSITION'][:,1]-(0 if name.startswith('05_') else .00025)
            arrays['NORMAL'][:,1]*=-1
            if 'TANGENT' in arrays:
                arrays['TANGENT'][:,1]*=-1;arrays['TANGENT'][:,3]*=-1
            reflected.append({'attributes':{key:accessor(values,'VEC'+str(values.shape[1])) for key,values in arrays.items()},
                              'indices':accessor(indices_array[:,[0,2,1]].reshape(-1),'SCALAR',True),
                              'material':original['material'],'extras':{'ps2MirroredRear':True}})
        detail['primitives']=originals+reflected
    mesh.setdefault('extras',{})['solidPS2CoreVersion']=4
    g['buffers'][0]['byteLength']=len(blob)
    js=json.dumps(g,separators=(',',':')).encode();js+=b' '*((-len(js))%4)
    blob+=b'\0'*((-len(blob))%4)
    path.write_bytes(struct.pack('<III',0x46546c67,2,28+len(js)+len(blob))+
                     struct.pack('<II',len(js),0x4e4f534a)+js+struct.pack('<II',len(blob),0x004e4942)+blob)
    print('Closed label backing, outer wall and inner core wall:',path.name)


if __name__=='__main__':
    root=Path(__file__).resolve().parents[1]/'outputs'
    for name in ('ps2-blue-disc.glb','ps2-silver-disc.glb','ps2-gold-disc.glb'):
        close_ps2_core(root/name)
