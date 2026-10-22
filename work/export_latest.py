from pathlib import Path
import zipfile, json, struct
root=Path('outputs')
models=sorted(p for p in root.glob('*.glb') if not p.stem.endswith('-preview'))
assert len(models)==10
textures=['label-art.png','groove-normal.png','hub-branding.png','hub-metal-roughness.png','disc-substrate-marks.png','disc-substrate-roughness.png','top-ps2-branding.png']
textures += ['ps1-mastering-ring.png','gamecube-mastering-details.png','gamecube-label-panel.png','gamecube-label-foil.png']
textures += ['ps-modern-outer-microetch.png','printed-ink-normal.png','printed-ink-roughness.png']
textures += [p.name for p in root.glob('ps[34]-label-template.png')]
textures += [p.name for p in root.glob('xbox360-*.png')]
textures += [p.name for p in root.glob('xbox-original-*.png')]
with zipfile.ZipFile(root/'latest-disc-models.zip','w',zipfile.ZIP_DEFLATED) as archive:
 for p in models:
  data=p.read_bytes()
  magic,version,size=struct.unpack_from('<III',data)
  assert magic==0x46546c67 and version==2 and size==len(data)
  n=struct.unpack_from('<I',data,12)[0]
  model=json.loads(data[20:20+n]);assert len(model['meshes'])==(13 if p.name=='gamecube-disc.glb' else 22 if p.name=='xbox360-test.glb' else (20 if p.name.startswith('xbox') else (18 if p.name.startswith(('ps2-','ps3-','ps4-')) else 17)))
  archive.writestr(p.name,data)
 for name in textures:archive.write(root/name,'textures/'+name)
 for p in (root/'xbox360-headers').glob('*.png'):archive.write(p,'xbox360-headers/'+p.name)
 for p in (root/'branding-source').iterdir():
  if p.is_file() and p.suffix in ('.svg','.ttf'):archive.write(p,'branding-source/'+p.name)
 archive.writestr('READ-ME.txt','LATEST OPTICAL DISC MODELS\n\nTen self-contained GLB models including an 80 mm GameCube mini disc: PS3/PS4 silver Blu-ray, PS2 blue/silver/gold, PS1 near-black, Xbox 360 silver, and a separate Xbox 360 – Test foil experiment, and Original Xbox.\nAll textures are embedded; import the GLBs directly into your 3D application.\nExternal texture copies and the supplied SVG branding are included for editing.\n\nGameCube: 80 mm diameter; other discs: 120 mm diameter. All: 15 mm center hole, upright orientation, spindle at origin; units are meters.\nPS2 models contain 18 mesh parts (PS1 has 17), including replaceable artwork, separate PS2 label band,\nclear hub and rim, smooth geometric rings and geometric barcode.\\nOriginal Xbox has 20 parts. Xbox 360 has 20 parts (Test has 22), its own holographic center ring, supplied Xbox branding and X360 font.\n\nReplace Base Color in TOP_ART_REPLACE_THIS_TEXTURE with square artwork.\nAlpha-masked PNG artwork is supported by the preview app.\nThe model contains the placeholder label; personal game artwork is not included.\nOptional glTF iridescence, clearcoat, anisotropy and transmission support varies by renderer.\nViewer zoom, studio lights, supersampling and PNG export are app settings,\nnot features embedded in the GLB files.\n')
with zipfile.ZipFile(root/'latest-disc-models.zip') as archive:
 assert archive.testzip() is None
 print('Verified export:',len(archive.namelist()),'files;', (root/'latest-disc-models.zip').stat().st_size,'bytes')





