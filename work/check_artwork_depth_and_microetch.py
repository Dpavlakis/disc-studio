import math
import numpy as np
from fix_artwork_depth import TARGETS,load,ROOT
for name in TARGETS:
 g,b=load(ROOT/'outputs'/(name+'.glb'));assert g['extras']['artworkDepthSeparationVersion']==1
 art=next(p for m in g['meshes'] for p in m['primitives'] if g['materials'][p['material']]['name']=='TOP_ART_REPLACE_THIS_TEXTURE');ay=g['accessors'][art['attributes']['POSITION']]['min'][1]
 if name.startswith('xbox'):mesh=next(m for m in g['meshes'] if 'Exposed_Silver_Between_Artwork' in m['name'])
 else:mesh=next(m for m in g['meshes'] if m['name']=='Closed_Outer_Laminate_Edge')
 maximum=max(g['accessors'][p['attributes']['POSITION']]['max'][1] for p in mesh['primitives']);assert abs(maximum-.00048)<1e-8 and ay-maximum>.000129
 assert maximum>.0004
 # Conservative 24-bit depth-buffer separation over the viewer camera range.
 near,far=.01,10
 def depth(distance):return far/(far-near)-far*near/(far-near)/distance
 for distance in [.065,.12,.23,.5,1.0]:assert abs(depth(distance-ay)-depth(distance-maximum))*(2**24-1)>20
 print(name+': artwork/backing gap 0.13 mm; stable depth separation across camera distances 65–1000 mm.')
for console in ['ps3','ps4']:
 g,b=load(ROOT/'outputs'/(console+'-silver-disc.glb'));e=g['extras'];assert e['outerMicroEtchVersion']==1 and e['outerMicroEtchOpacity']==.12
 primitive=g['meshes'][10]['primitives'][1];m=g['materials'][primitive['material']];assert m['alphaMode']=='BLEND' and m['pbrMetallicRoughness']['baseColorTexture']['texCoord']==1
 texture=g['textures'][m['pbrMetallicRoughness']['baseColorTexture']['index']];assert g['samplers'][texture['sampler']]['minFilter']==9987
 a=g['accessors'][primitive['attributes']['POSITION']];v=g['bufferViews'][a['bufferView']];points=np.frombuffer(b,dtype='<f4',count=a['count']*3,offset=v.get('byteOffset',0)).reshape(-1,3);r=np.linalg.norm(points[:,[0,2]],axis=1)*1000
 assert abs(r.min()-(e['securityOuterRadiusMm']+.025))<.0001 and abs(r.max()-(e['securityOuterRadiusMm']+.33))<.0001
 print(console+': faint .305 mm etched fringe, independent UVs, mip filtering, correct ring position.')
