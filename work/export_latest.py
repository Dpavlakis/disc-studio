from pathlib import Path
import zipfile, json, struct
root=Path('outputs')
models=sorted(root.glob('*.glb'))
assert len(models)==5
textures=['label-art.png','groove-normal.png','hub-branding.png','hub-metal-roughness.png','disc-substrate-marks.png','disc-substrate-roughness.png','top-ps2-branding.png']
textures += [p.name for p in root.glob('xbox360-*.png')]
with zipfile.ZipFile(root/'latest-disc-models.zip','w',zipfile.ZIP_DEFLATED) as archive:
 for p in models:
  data=p.read_bytes()
  magic,version,size=struct.unpack_from('<III',data)
  assert magic==0x46546c67 and version==2 and size==len(data)
  n=struct.unpack_from('<I',data,12)[0]
  model=json.loads(data[20:20+n]);assert len(model['meshes'])==16
  archive.writestr(p.name,data)
 for name in textures:archive.write(root/name,'textures/'+name)
 for p in (root/'branding-source').iterdir():
  if p.is_file() and p.suffix in ('.svg','.ttf'):archive.write(p,'branding-source/'+p.name)
 archive.writestr('READ-ME.txt','LATEST OPTICAL DISC MODELS\n\nFive self-contained GLB models: PS2 blue/silver/gold, PS1 near-black, and Xbox 360 silver.\nAll textures are embedded; import the GLBs directly into your 3D application.\nExternal texture copies and the supplied SVG branding are included for editing.\n\n120 mm diameter, 15 mm center hole, upright orientation; units are meters.\nPS models contain 16 mesh parts, including replaceable artwork, separate PS2 label band,\nclear hub and rim, smooth geometric rings and geometric barcode.\\nXbox 360 has 16 parts, its own holographic center ring, supplied Xbox branding and X360 font.\n\nReplace Base Color in TOP_ART_REPLACE_THIS_TEXTURE with square artwork.\nAlpha-masked PNG artwork is supported by the preview app.\nThe model contains the placeholder label; personal game artwork is not included.\nOptional glTF iridescence, clearcoat, anisotropy and transmission support varies by renderer.\nViewer zoom, studio lights, supersampling and PNG export are app settings,\nnot features embedded in the GLB files.\n')
with zipfile.ZipFile(root/'latest-disc-models.zip') as archive:
 assert archive.testzip() is None
 print('Verified export:',len(archive.namelist()),'files;', (root/'latest-disc-models.zip').stat().st_size,'bytes')




