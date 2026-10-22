"""Check centred geometry and watertight opaque laminate in every shipped model."""
from pathlib import Path
from collections import Counter
import json,struct,math
import numpy as np
root=Path(__file__).resolve().parents[1]
for path in (root/'outputs').glob('*.glb'):
 b=path.read_bytes();n=struct.unpack_from('<I',b,12)[0];g=json.loads(b[20:20+n]);binary=b[28+n:]
 def read(i):
  a=g['accessors'][i];v=g['bufferViews'][a['bufferView']];assert a['componentType']==5126 and 'byteStride' not in v
  width={'VEC2':2,'VEC3':3,'VEC4':4}[a['type']];return np.frombuffer(binary,dtype='<f4',count=a['count']*width,offset=v.get('byteOffset',0)+a.get('byteOffset',0)).reshape((-1,width))
 core=next(m for m in g['meshes'] if m['name']=='SOLID_DISC_LAMINATE_BODY')['primitives'][0];mat=g['materials'][core['material']]
 assert 'normalTexture' not in mat and 'extensions' not in mat;assert mat['alphaMode']=='OPAQUE';assert not mat.get('extensions',{}).get('KHR_materials_transmission',{}).get('transmissionFactor',0)
 pos=read(core['attributes']['POSITION']);norm=read(core['attributes']['NORMAL']);tri=pos.reshape((-1,3,3));cross=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);assert np.all(np.einsum('ij,ij->i',cross,norm[::3])>0)
 edges=Counter()
 for t in tri:
  points=[tuple(np.round(v.astype(float),8)) for v in t]
  for i in range(3):edges[tuple(sorted((points[i],points[(i+1)%3])))]+=1
 assert set(edges.values())=={2},'Laminate has an open/nonmanifold edge'
 lo=pos.min(axis=0);hi=pos.max(axis=0);assert np.allclose(lo+hi,0,atol=1e-8);assert math.isclose(float(hi[1]-lo[1]),.0008,abs_tol=1e-8)
 assert g['extras']['spindleCentered']
 def matrix(node):
  assert 'matrix' not in node
  x,y,z,w=node.get('rotation',[0,0,0,1]);r=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
  result=np.eye(4);result[:3,:3]=r@np.diag(node.get('scale',[1,1,1]));result[:3,3]=node.get('translation',[0,0,0]);return result
 bounds=[]
 def walk(index,parent):
  node=g['nodes'][index];world=parent@matrix(node)
  if 'mesh' in node:
   for p in g['meshes'][node['mesh']]['primitives']:
    points=read(p['attributes']['POSITION']);wp=points@world[:3,:3].T+world[:3,3];bounds.extend([wp.min(axis=0),wp.max(axis=0)])
  for child in node.get('children',[]):walk(child,world)
 for node in g['scenes'][g.get('scene',0)]['nodes']:walk(node,np.eye(4))
 bounds=np.array(bounds);centre=(bounds.min(axis=0)+bounds.max(axis=0))/2
 assert abs(centre[0])<1e-6 and abs(centre[1])<1e-6,(path.name,centre)
 print(path.name,': centred spindle; watertight body; outward faces; opaque core')
html=(root/'outputs/studio.html').read_text(encoding='utf-8');assert 'camera-target="0m 0m 0m"' in html;assert '0m 0.06m 0m' not in html
from html.parser import HTMLParser
class Buttons(HTMLParser):
 def __init__(self):super().__init__();self.buttons={};self.active=None
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='button' and 'data-system' in a:self.active=a['data-system'];self.buttons[self.active]=False;assert a.get('aria-label')
  if tag=='img' and self.active:self.buttons[self.active]=a.get('src','').startswith('data:image/svg+xml;base64,')
 def handle_endtag(self,tag):
  if tag=='button':self.active=None
parser=Buttons();parser.feed(html);assert len(parser.buttons)==7 and all(parser.buttons.values())
print('Seven labelled SVG console buttons and centred camera target verified.')
