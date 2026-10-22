"""Fictional mould codes in shallow clear-plastic relief, not printed ink."""
import math
from original_xbox_vectors import text_paths,bounds
from shapely.geometry import Polygon,GeometryCollection
from shapely.ops import triangulate

CODES=[('NINTENDO',0),('IFPI 4A12',90),('B006C8',180),('2K38',270)]
def add_hub_codes(g,acc,clear):
 p=[];n=[];uv=[];tan=[]
 def vertex(x,y,z,normal):
  p.append((x/1000,y/1000,z/1000));n.append(normal);uv.append((.5-x/80,.5-z/80));tan.append((1,0,0,1))
 for text,angle in CODES:
  outlines=text_paths('C:/Windows/Fonts/arial.ttf',text,.63);x0,y0,x1,y1=bounds(outlines);shape=GeometryCollection()
  for path in outlines:
   points=[]
   for x,y in path:
    a=math.radians(angle)+(x-(x0+x1)/2)/9.05;r=9.05+y-(y0+y1)/2;points.append((r*math.sin(a),-r*math.cos(a)))
   if len(points)>2:shape=shape.symmetric_difference(Polygon(points).buffer(0))
  for tri in triangulate(shape):
   if not shape.covers(tri):continue
   points=list(tri.exterior.coords)[:3]
   # XZ triangles use reversed winding for their +Y face.
   for x,z in reversed(points):vertex(x,.688,z,(0,1,0))
  polygons=list(shape.geoms) if shape.geom_type=='MultiPolygon' else [shape]
  for poly in polygons:
   if poly.geom_type!='Polygon':continue
   for ring in [poly.exterior,*poly.interiors]:
    points=list(ring.coords)
    for (x,z),(xx,zz) in zip(points,points[1:]):
     length=math.hypot(xx-x,zz-z)
     if not length:continue
     normal=((zz-z)/length,0,-(xx-x)/length)
     for a,y,b in [(x,.66,z),(xx,.66,zz),(xx,.688,zz),(x,.66,z),(xx,.688,zz),(x,.688,z)]:vertex(a,y,b,normal)
 attrs={k:acc(data,typ) for k,data,typ in [('POSITION',p,'VEC3'),('NORMAL',n,'VEC3'),('TEXCOORD_0',uv,'VEC2'),('TANGENT',tan,'VEC4')]}
 g['meshes'].append({'name':'GameCube_fictional_mould_codes_28um_relief','primitives':[{'attributes':attrs,'material':clear}]});g['nodes'].append({'name':'Clear hub mould codes','mesh':len(g['meshes'])-1});g['scenes'][0]['nodes'].append(len(g['nodes'])-1)
 g['extras']['hubCodes']={'fictional':True,'values':[x[0] for x in CODES],'reliefMm':.028,'radiusMm':9.05}
