from pathlib import Path
import json,math
import numpy as np
from refine_xbox360_mastering import read,protected,ALLOWED,ROOT
from PIL import Image,ImageDraw
measure=json.loads((ROOT/'work/xbox360_security_measurements.json').read_text())
for name in ['xbox360-silver-disc','xbox360-test']:
 g,b=read(ROOT/'outputs'/(name+'.glb'));extra=g['extras'];assert extra['xbox360MasteringReferenceVersion']==1
 current=protected(g,b);expected=json.loads((ROOT/'work'/(name+'-mastering-baseline.json')).read_text())
 if extra.get('bareFrontSurfaceVersion')==1:
  front='07b_Xbox360_Exposed_Silver_Between_Artwork_And_Clear_Rim';current.pop(front);expected.pop(front)
 assert current==expected
 def points(p):
  a=g['accessors'][p['attributes']['POSITION']];v=g['bufferViews'][a['bufferView']];return np.frombuffer(b,dtype='<f4',count=a['count']*3,offset=v.get('byteOffset',0)+a.get('byteOffset',0)).reshape(-1,3)
 assert extra['xbox360ExcludedPunchedStamps']==['60','14']
 assert not {'60','14'} & {item['text'] for item in extra['xbox360MasteringTypography']}
 assert abs(extra['xbox360MasteringLetterAreaMm2']-extra['xbox360MasteringTriangleAreaMm2'])<1e-8
 tracks=extra['xbox360MasteringTracks'];outer=sorted(tracks[0]['runsDeg']+tracks[2]['runsDeg']);inner=tracks[1]['runsDeg']
 for key,runs in [('outer',outer),('inner',inner)]:
  assert runs[0][0]==measure[key+'ArcDeg'][0] and runs[-1][1]<=measure[key+'ArcDeg'][1]
  for previous,following in zip(runs,runs[1:]):assert following[0]-previous[1]>=.4499
 for track in tracks:
  mesh=next(m for m in g['meshes'] if m['name']==track['name']);r=np.linalg.norm(points(mesh['primitives'][0])[:,[0,2]],axis=1)*1000
  assert abs(r.min()-(track['radiusMm']-track['heightMm']/2))<.0001
  assert abs(r.max()-(track['radiusMm']+track['heightMm']/2))<.0001
 for mesh in g['meshes']:
  if mesh['name'] not in ALLOWED:continue
  for p in mesh['primitives']:
   triangles=points(p).reshape(-1,3,3);assert np.isfinite(triangles).all();assert (np.cross(triangles[:,1]-triangles[:,0],triangles[:,2]-triangles[:,0])[:,1]<0).all()
 if name=='xbox360-silver-disc':
  im=Image.new('RGB',(1400,1400),'#888888');d=ImageDraw.Draw(im)
  for mesh in g['meshes']:
   if mesh['name'] not in ALLOWED:continue
   for p in mesh['primitives']:
    color='#262626' if mesh['name']=='10_Xbox360_Back_Mastering_Band' else '#d0d0c9'
    for tri in points(p).reshape(-1,3,3):d.polygon([(700+x*30000,700-z*30000) for x,y,z in tri],fill=color)
  im.save(ROOT/'work/xbox360-security-geometry-check.png')
 print(name+': measured sectors, separated tags, full text, excluded stamps and preserved centre verified.')
