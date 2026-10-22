"""Verify GameCube rear geometry against recorded photo proportions."""
from pathlib import Path
import json,struct,numpy as np
ROOT=Path(__file__).resolve().parents[1];m=json.loads((ROOT/'work/gamecube_reference_measurements.json').read_text());raw=(ROOT/'outputs/gamecube-disc.glb').read_bytes();n=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+n]);blob=raw[28+n:]
def read(i,w):
 a=g['accessors'][i];v=g['bufferViews'][a['bufferView']];return np.frombuffer(blob,dtype='<f4',count=a['count']*w,offset=v.get('byteOffset',0)+a.get('byteOffset',0)).reshape(-1,w)
for name,expected,centre in [('GAMECUBE_REAR_MOULDED_CLEAR_LETTERING',m['hubGlyphHeightMm'],m['hubTextRadiusMm']),('GAMECUBE_REAR_VECTOR_MASTERING_TEXT',m['matrixGlyphHeightMm'],21.05)]:
 primitive=next(p for mesh in g['meshes'] for p in mesh['primitives'] if g['materials'][p['material']]['name']==name);pos=read(primitive['attributes']['POSITION'],3);r=np.hypot(pos[:,0],pos[:,2])*1000
 assert pos[:,1].max()<0
 assert abs(float((r.min()+r.max())/2)-centre)<.04,(name,r.min(),r.max())
 assert abs(float(r.max()-r.min())-expected)<.05,(name,r.max()-r.min(),expected)
 if 'MOULDED' in name:assert r.min()>7.5
primitive=next(mesh for mesh in g['meshes'] if mesh['name']=='Irregular_security_bars')['primitives'][0];pos=read(primitive['attributes']['POSITION'],3).reshape(-1,3,3);rear=pos[(pos[:,:,1]<0).all(axis=1)];r=np.hypot(rear[:,:,0],rear[:,:,2])*1000;assert abs(float(r.max()-r.min())-m['barcodeHeightMm'])<.005
angles=np.degrees(np.arctan2(rear[:,:,0],rear[:,:,2]))%360;assert np.all(angles>=m['barcodeArcDeg'][0]-.001) and np.all(angles<=m['barcodeArcDeg'][1]+.001)
intervals=sorted(zip(angles.min(axis=1),angles.max(axis=1)));merged=[]
for a,b in intervals:
 if merged and a<=merged[-1][1]+.0001:merged[-1][1]=max(merged[-1][1],b)
 else:merged.append([a,b])
widths=np.array([b-a for a,b in merged]);gaps=np.array([merged[i+1][0]-merged[i][1] for i in range(len(merged)-1)]);assert abs(np.median(widths)/np.median(m['barcodeWidthsDeg'])-1)<.2;assert abs(np.median(gaps)/np.median(m['barcodeGapsDeg'])-1)<.2
for item in g['extras']['rearMasteringTypography']:assert abs(item['angleDeg']-m['matrixWordAnglesDeg'][item['text']])<.001
print('Verified measured glyph heights/radii, word placement, barcode height/arc, and sampled width/gap proportions.')

# Matched X/Z geometry reverses naturally when viewed from the opposite side.
def primitive_named(name):return next(p for mesh in g['meshes'] for p in mesh['primitives'] if g['materials'][p['material']]['name']==name)
def matched(rear,front,offset):
 rp=read(rear['attributes']['POSITION'],3);fp=read(front['attributes']['POSITION'],3);expected=rp.reshape(-1,3,3)[:,[0,2,1],:].reshape(-1,3).copy();expected[:,1]=-expected[:,1]+offset
 assert fp.shape==expected.shape and np.allclose(fp,expected,atol=1e-9)
 normal=read(front['attributes']['NORMAL'],3);tri=fp.reshape(-1,3,3);cross=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);assert np.all(np.einsum('ij,ij->i',cross,normal[::3])>=-1e-12)
matched(primitive_named('GAMECUBE_REAR_VECTOR_MASTERING_TEXT'),primitive_named('GAMECUBE_FRONT_THROUGH_MASTERING_TEXT'),.0001)
matched(primitive_named('GAMECUBE_REAR_POLISHED_SECURITY_BOUNDARY'),primitive_named('GAMECUBE_FRONT_THROUGH_SECURITY_BOUNDARY'),.0001)
hubs=[p for mesh in g['meshes'] for p in mesh['primitives'] if g['materials'][p['material']]['name']=='GAMECUBE_REAR_MOULDED_CLEAR_LETTERING'];rear=next(p for p in hubs if read(p['attributes']['POSITION'],3)[:,1].max()<0);front=next(p for p in hubs if read(p['attributes']['POSITION'],3)[:,1].min()>0);matched(rear,front,0)
primitive=next(mesh for mesh in g['meshes'] if mesh['name']=='Irregular_security_bars')['primitives'][0];pos=read(primitive['attributes']['POSITION'],3);rp=pos[pos[:,1]<0].reshape(-1,3,3)[:,[0,2,1],:].reshape(-1,3).copy();rp[:,1]=-rp[:,1]+.000105;assert np.allclose(rp,pos[pos[:,1]>0],atol=1e-9)
xraw=(ROOT/'outputs/xbox-original-disc.glb').read_bytes();xn=struct.unpack_from('<I',xraw,12)[0];xg=json.loads(xraw[20:20+xn]);xm=next(v for v in xg['materials'] if v['name']=='ORIGINAL_XBOX_TEST_PLAIN_REFLECTIVE_SILVER');gm=next(v for v in g['materials'] if v['name']=='GAMECUBE_SILVER_SECURITY_BACKING')
assert gm['pbrMetallicRoughness']==xm['pbrMetallicRoughness'] and gm['extensions']==xm['extensions']
print('Verified mirrored front/rear glyphs, hub mould text, rings and barcode positions; reverse band matches the Xbox reflective silver material.')
