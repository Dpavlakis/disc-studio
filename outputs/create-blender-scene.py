"""Blender: open Scripting, load this file, Run Script. Save alongside the GLBs."""
import bpy, math
from pathlib import Path
ROOT=Path(__file__).resolve().parent
# Add to the existing scene without deleting its contents.
bpy.ops.import_scene.gltf(filepath=str(ROOT/'ps2-blue-disc.glb'))
parts=list(bpy.context.selected_objects)
for ob in parts:
 if ob.type=='MESH':
  # glTF import converts Y-up to Blender Z-up.
  for face in ob.data.polygons: face.use_smooth=False
data=next(o for o in parts if o.name.startswith('02_Blue'))
mat=data.data.materials[0]; mat.use_nodes=True
nt=mat.node_tree; nt.nodes.clear(); n=nt.nodes; l=nt.links
out=n.new('ShaderNodeOutputMaterial'); out.location=(700,0)
bs=n.new('ShaderNodeBsdfPrincipled'); bs.location=(400,0)
bs.inputs['Metallic'].default_value=.92; bs.inputs['Roughness'].default_value=.115
bs.inputs['Coat Weight'].default_value=1; bs.inputs['Coat Roughness'].default_value=.07
bs.inputs['Anisotropic IOR Level'].default_value=.8
layer=n.new('ShaderNodeLayerWeight'); layer.location=(-600,150)
ramp=n.new('ShaderNodeValToRGB'); ramp.location=(-350,160)
cr=ramp.color_ramp; cr.elements.remove(cr.elements[1])
for i,(p,c) in enumerate([(0,(.008,.012,.25,1)),(.3,(.018,.01,.6,1)),(.59,(.08,.012,.38,1)),(.7,(.008,.19,.4,1)),(.8,(.015,.025,.52,1)),(1,(.008,.012,.3,1))]):
 e=cr.elements[0] if i==0 else cr.elements.new(p); e.position=p; e.color=c
l.new(layer.outputs['Facing'],ramp.inputs[0]); l.new(ramp.outputs[0],bs.inputs['Base Color'])
tex=n.new('ShaderNodeTexImage'); tex.image=bpy.data.images.load(str(ROOT/'groove-normal.png'),check_existing=True); tex.image.colorspace_settings.name='Non-Color'; tex.location=(-350,-200)
norm=n.new('ShaderNodeNormalMap'); norm.inputs['Strength'].default_value=.25; norm.location=(0,-200)
l.new(tex.outputs['Color'],norm.inputs['Color']); l.new(norm.outputs['Normal'],bs.inputs['Normal'])
tangent=n.new('ShaderNodeTangent'); tangent.direction_type='RADIAL'; tangent.axis='Y'; tangent.location=(0,-400)
l.new(tangent.outputs['Tangent'],bs.inputs['Tangent']); l.new(bs.outputs[0],out.inputs[0])
# Readable material presets: duplicate the material to keep multiple finishes in a scene.
mat['finish_presets']='Blue: current ramp. Silver: disconnect ramp, RGB .72 .74 .78; Gold: .68 .45 .14; Black: .009 .006 .014.'
world=bpy.context.scene.world or bpy.data.worlds.new('Disc studio'); bpy.context.scene.world=world; world.use_nodes=True
world.node_tree.nodes['Background'].inputs[0].default_value=(.15,.15,.18,1)
world.node_tree.nodes['Background'].inputs[1].default_value=.5
from mathutils import Vector
def aim(ob,point): ob.rotation_euler=(Vector(point)-ob.location).to_track_quat('-Z','Y').to_euler()
for name,loc,power,size in [('Long softbox',(.06,-.10,.12),8,.10),('Rim softbox',(-.08,-.08,.10),5,.07)]:
 light=bpy.data.lights.new(name,'AREA'); light.energy=power; light.shape='RECTANGLE'; light.size=size; light.size_y=.012
 ob=bpy.data.objects.new(name,light); bpy.context.collection.objects.link(ob); ob.location=loc; aim(ob,(0,0,.06))
camdata=bpy.data.cameras.new('Underside camera'); cam=bpy.data.objects.new('Underside camera',camdata); bpy.context.collection.objects.link(cam)
cam.location=(.10,-.22,.10); aim(cam,(0,0,.06)); camdata.type='ORTHO'; camdata.ortho_scale=.155; bpy.context.scene.camera=cam
scene=bpy.context.scene; scene.render.engine='CYCLES'; scene.cycles.samples=64
scene.render.resolution_x=1200; scene.render.resolution_y=1200; scene.render.resolution_percentage=100
for image in bpy.data.images:
 if image.source=='FILE': image.pack()
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'ps2-disc-studio.blend'))
print('Saved ps2-disc-studio.blend. Top art material: TOP_ART_REPLACE_THIS_TEXTURE')
