from pathlib import Path
import json,struct,math,zipfile,hashlib
import numpy as np
from refine_original_xbox_mastering import fingerprint,ALLOWED
root=Path(__file__).resolve().parents[1]
p=root/'outputs/xbox-original-disc.glb'
raw=p.read_bytes();n=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+n]);b=raw[28+n:]
current=fingerprint(g,b);expected=json.loads((root/'work/original_xbox_security_baseline.json').read_text())
if g.get('extras',{}).get('bareFrontSurfaceVersion')==1:
 front='07b_Original_Xbox_Exposed_Silver_Between_Artwork_And_Clear_Rim';current.pop(front);expected.pop(front)
assert current==expected, 'Approved centre or assets changed'
measure=json.loads((root/'work/xbox_original_security_measurements.json').read_text())
def positions(primitive):
 a=g['accessors'][primitive['attributes']['POSITION']];v=g['bufferViews'][a['bufferView']];return np.frombuffer(b,dtype='<f4',count=a['count']*3,offset=v.get('byteOffset',0)+a.get('byteOffset',0)).reshape(-1,3)
for track in g['extras']['originalXboxMasteringTracks']:
 mesh=next(m for m in g['meshes'] if m['name']==track['name']);points=positions(mesh['primitives'][0]);r=np.linalg.norm(points[:,[0,2]],axis=1)*1000
 assert abs(r.min()-(track['radiusMm']-track['heightMm']/2))<.0001
 assert abs(r.max()-(track['radiusMm']+track['heightMm']/2))<.0001
 assert np.allclose(points[:,1],-.00072)
 assert track['barCount']>=1
 if 'Outer' in track['name']:assert track['radiusMm']==measure['outerTrackRadiusMm']
 if 'Inner' in track['name']:assert track['radiusMm']==measure['innerTrackRadiusMm']
for mesh in g['meshes']:
 if mesh['name'] not in ALLOWED:continue
 for primitive in mesh['primitives']:
  t=positions(primitive).reshape(-1,3,3);cross=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);assert np.isfinite(t).all();assert (cross[:,1]<0).all(),mesh['name']
band=next(m for m in g['meshes'] if m['name']=='10_Original_Xbox_Back_Mastering_Band');assert len(band['primitives'])==2
assert len(positions(band['primitives'][1]))>300
material=g['materials'][band['primitives'][0]['material']]
if g.get('extras',{}).get('originalXboxBlackRingInspection'):
 assert material['name']=='TEMP_ORIGINAL_XBOX_BLACK_SECURITY_RING'
 assert material['pbrMetallicRoughness']['baseColorFactor']==[.004,.004,.004,1]
 material=g['materials'][g['extras']['originalXboxInspectionOriginalMaterial']]
assert material['pbrMetallicRoughness']['metallicFactor']==1 and material['pbrMetallicRoughness']['roughnessFactor']<.1
print('Verified original Xbox measured security tracks, outward geometry, reflective band and reference lettering; approved original Xbox centre/assets unchanged.')

assert g['extras']['originalXboxCleanMasteringTextVersion']==5
sizes={round(item['glyphHeightMm'],2) for item in g['extras']['originalXboxMasteringTypography']}
assert sizes=={.78,.36,.56,.55}
assert abs(g['extras']['originalXboxTextAreaMm2']-g['extras']['originalXboxTextTriangleAreaMm2'])<1e-8
tracks=g['extras']['originalXboxMasteringTracks']
outer=sorted(tracks[0]['runsDeg']+tracks[2]['runsDeg'])
for runs in [outer,tracks[1]['runsDeg']]:
 for previous,following in zip(runs,runs[1:]):assert following[0]-previous[1] >= .4999
assert tracks[0]['radiusMm']-tracks[0]['heightMm']/2-(tracks[1]['radiusMm']+tracks[1]['heightMm']/2)>.4
assert tracks[2]['radiusMm']==tracks[0]['radiusMm']
print('Verified full letter fill, four glyph sizes, separated suffixes, and clear angular/radial gaps between tags.')

labels=g['extras']['originalXboxMasteringTypography']
code=next(item for item in labels if item['text']=='DS01234-MS-L0')
stamp=next(item for item in labels if item['text']=='01' and item['glyphHeightMm']>.5)
assert code['radiusMm']==18.6 and code['angleDeg']==-12
assert stamp['radiusMm']==20 and stamp['angleDeg']==1
first=next(item for item in labels if item['text']=='DS01234-MS-L1')
assert code['radiusMm'] < first['radiusMm']
assert code['angleDeg']-code['arcDeg']/2 > first['angleDeg']+first['arcDeg']/2
