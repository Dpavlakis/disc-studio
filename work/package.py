from pathlib import Path
import base64,json,struct,zipfile,ast
root=Path(__file__).resolve().parents[1]/'outputs'
models={p.stem:base64.b64encode(p.read_bytes()).decode() for p in root.glob('*.glb')}
html='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Optical disc studio</title>
<script type="module" src="https://cdn.jsdelivr.net/npm/@google/model-viewer@4.0.0/dist/model-viewer.min.js"></script>
<style>body{margin:0;background:#15171d;color:#eee;font:16px system-ui}header{padding:24px;max-width:1000px;margin:auto}h1{font-size:28px;margin:0 0 12px}p{color:#bfc4d1}nav{display:flex;gap:12px;flex-wrap:wrap}button,label{padding:10px 16px;border:1px solid #5d6578;border-radius:6px;background:#252b38;color:white;font:inherit;cursor:pointer}button:focus-visible,label:focus-within{outline:2px solid #8dabff}input{max-width:240px}model-viewer{width:100%;height:68vh;min-height:360px;background:radial-gradient(#404755,#171a22)}#status{min-height:24px}</style>
<header><h1>Optical disc studio</h1><p>Drag to rotate · scroll to zoom · right drag to pan. Turn the disc to see its artwork.</p><nav>
<button data-finish="ps2-blue-disc">Blue CD</button><button data-finish="ps2-silver-disc">Silver DVD</button><button data-finish="ps2-gold-disc">Gold DVD</button><button data-finish="ps1-black-disc">Black CD</button>
<button id="front-view" type="button">Front view</button><button id="back-view" type="button">Back view</button><button id="download-png" type="button" disabled>Download PNG</button>
<label>Top artwork <input id="art" type="file" accept="image/*"></label><label><input id="show-art" type="checkbox" checked> Show artwork</label><button id="export">Download edited GLB</button></nav><p id="status" role="status">Loading. First use requires internet for the 3D viewer.</p></header>
<style>.disc-viewport{position:relative;width:100%;height:68vh;min-height:360px;overflow:hidden}.disc-viewport model-viewer{position:absolute;left:0;top:0;width:200%;height:200%;min-height:0;transform:scale(.5);transform-origin:top left}</style>
<div class="disc-viewport"><model-viewer id="disc" camera-controls camera-orbit="25deg 80deg 0.20m" field-of-view="35deg" environment-image="neutral" exposure="1.1" shadow-intensity="0" interaction-prompt="none" alt="Reflective optical disc with replaceable top artwork"></model-viewer></div>
<script>const models=MODELS; const v=document.getElementById('disc'); const s=document.getElementById('status');let artURL;
// Supersample at twice the displayed width/height and keep the native renderer
// at full resolution, including while orbiting. CSS downsamples the final image.
customElements.whenDefined('model-viewer').then(()=>{customElements.get('model-viewer').minimumRenderScale=1});
const pngButton=document.getElementById('download-png');
function saveBlob(blob,name){const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download=name;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),10000)}
async function setView(theta){await customElements.whenDefined('model-viewer');v.cameraTarget='0m 0.06m 0m';v.cameraOrbit=theta+'deg 90deg 0.23m';v.fieldOfView='35deg';await v.updateComplete;v.jumpCameraToGoal();s.textContent=theta===180?'Front view — artwork side.':'Back view — reflective underside.'}
document.getElementById('front-view').onclick=()=>setView(180);
document.getElementById('back-view').onclick=()=>setView(0);
pngButton.onclick=async()=>{pngButton.disabled=true;try{if(!v.loaded)throw new Error('Wait for the disc to finish loading.');await v.updateComplete;v.jumpCameraToGoal();await new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));const blob=await v.toBlob({mimeType:'image/png',idealAspect:false});if(!blob)throw new Error('The image could not be captured.');saveBlob(blob,'disc-view.png');s.textContent='PNG downloaded with a transparent background, using the current angle and artwork.'}catch(err){s.textContent='PNG export failed: '+err.message}finally{pngButton.disabled=!v.loaded}};
v.addEventListener('load',()=>{pngButton.disabled=false});
v.addEventListener('error',()=>{pngButton.disabled=true});
const showArt=document.getElementById('show-art');const artTextures=new WeakMap();
function updateArtwork(){if(!v.model)return;const m=v.model.materials.find(m=>m.name==='TOP_ART_REPLACE_THIS_TEXTURE');if(!m)return;const p=m.pbrMetallicRoughness;if(!artTextures.has(m))artTextures.set(m,p.baseColorTexture.texture);const enabled=showArt.checked;const bare=v.model.materials.find(m=>m.name.endsWith('_DATA_REFLECTIVE')).pbrMetallicRoughness;p.baseColorTexture.setTexture(enabled?artTextures.get(m):null);m.setAlphaMode(enabled?'OPAQUE':'BLEND');p.setBaseColorFactor(enabled?[1,1,1,1]:[1,1,1,0]);p.setMetallicFactor(0);p.setRoughnessFactor(.36);const badge=v.model.materials.find(m=>m.name==='TOP_PERMANENT_PS2_BRANDING');if(badge){badge.setAlphaMode(enabled?'MASK':'BLEND');badge.pbrMetallicRoughness.setBaseColorFactor([1,1,1,enabled?1:0])}}
async function applyArt(){if(!v.model)return;const m=v.model.materials.find(m=>m.name==='TOP_ART_REPLACE_THIS_TEXTURE');if(artURL){const t=await v.createTexture(artURL);artTextures.set(m,t)}updateArtwork()}
showArt.onchange=()=>{updateArtwork();s.textContent=showArt.checked?'Artwork shown.':'Artwork hidden. Your image is kept for when you turn it back on.'};
v.addEventListener('load',async()=>{await applyArt();s.textContent='Ready. Reflections change as you rotate the disc.'});v.addEventListener('error',()=>{s.textContent='Viewer could not load. Use the included GLB files in a 3D app.'});
document.querySelectorAll('[data-finish]').forEach(b=>b.onclick=()=>{s.textContent='Loading finish…';v.src='data:model/gltf-binary;base64,'+models[b.dataset.finish]});
document.getElementById('art').onchange=async e=>{if(!e.target.files[0])return;if(artURL)URL.revokeObjectURL(artURL);artURL=URL.createObjectURL(e.target.files[0]);try{await applyArt();s.textContent='Artwork replaced. Download edited GLB to keep it.'}catch(err){s.textContent='Could not apply artwork: '+err.message}};
document.getElementById('export').onclick=async()=>{try{const blob=await v.exportScene();const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download='custom-disc.glb';a.click();setTimeout(()=>URL.revokeObjectURL(url),10000)}catch(err){s.textContent='Export failed: '+err.message}};
v.src='data:model/gltf-binary;base64,'+models['ps2-blue-disc'];</script></html>'''
(root/'disc-preview.html').write_text(html.replace('MODELS',json.dumps(models)),encoding='utf-8')
(root/'READ-ME.txt').write_text('''OPTICAL DISC MODEL PACK

Open disc-preview.html in a browser. First use needs internet for the viewer library.
Select Blue, Silver, Gold or Black. Drag to inspect the light response. Choose a square image under Top artwork, then Download edited GLB to save your customized model.

MODELS
ps2-blue-disc.glb: cobalt blue underside matching the supplied references.
ps2-silver-disc.glb: silver finish.
ps2-gold-disc.glb: gold finish.
ps1-black-disc.glb: glossy near-black finish.
All files embed their textures and use meters: 120 mm diameter, 15 mm center hole, 1.2 mm nominal thickness (moulded rings extend slightly).
Fifteen separate parts: top artwork, underside, edge, hub, three moulded rings and an independent etched branding/matrix ring, plus the PS2 label band above the replaceable artwork and a solid dark perimeter ring visible from both sides, plus three smooth matrix boundary/separator rings and geometric barcode backing/bars. Discs stand upright on the rim at Y=0 in glTF. Artwork faces -Z; reflective underside faces +Z.

INNER BRANDING
The underside has an independent metallic etched ring with repeated PlayStation wordmarks and PS monograms rendered from your supplied SVG files and representative matrix/barcode marks. It remains in place when top art changes. The logo shapes come from the supplied SVGs; the ring layout is recreated rather than scanned from a particular pressing. Original SVGs are included in branding-source. The placeholder matrix text is illustrative.

REPLACE ART IN A 3D APP
Assign your image to Base Color in TOP_ART_REPLACE_THIS_TEXTURE. UVs are already set up as a centered square. Use a 2048x2048 or larger square image. Printed artwork is clipped at 48.92% of image width, leaving the reflective rim and clear bevel exposed and the label inner radius is 9.5%. The hole and clear hub are real geometry, so the image need not contain a cutout. Keep image orientation as supplied; rotate the texture if your artwork needs a different alignment.
label-art.png is a placeholder/template. Changing it alone does NOT update the embedded GLB: reassign the image in your 3D app, or use the browser preview and export.

LIGHT RESPONSE
Blue metallic material, glossy clearcoat, concentric micro-normal texture, radial anisotropy and glTF iridescence. Use an HDRI/studio environment with bright strip lights for reflections. Rainbow response is an artistic approximation of optical-disc diffraction, not a spectral diffraction simulation. Exact blue appearance depends on lighting, exposure and renderer. Apps without the optional glTF material extensions show a simpler blue metallic surface. Hub transmission may also vary by renderer.

BLENDER
In Blender 4.x or later, open the Scripting workspace, load create-blender-scene.py from this folder, then Run Script. Keep the GLBs and PNGs beside it. It imports the blue model, builds an editable view-dependent underside material, adds lights and a camera, packs images, and saves ps2-disc-studio.blend beside the files. Existing scene objects are preserved. Render with F12. The Blender setup script has been syntax checked but was not run here because Blender is unavailable. Browser viewer is the portable preview.
''',encoding='utf-8')
for p in root.glob('*.glb'):
 b=p.read_bytes(); magic,ver,total=struct.unpack_from('<III',b); assert magic==0x46546c67 and total==len(b)
 size=struct.unpack_from('<I',b,12)[0]; g=json.loads(b[20:20+size]); assert len(g['meshes'])==15
 for mesh in g['meshes']:
  attrs=mesh['primitives'][0]['attributes']; assert all(g['accessors'][a]['count']==g['accessors'][attrs['POSITION']]['count'] for a in attrs.values())
 print(p.name, 'validated', len(g['meshes']), 'meshes')
ast.parse((root/'create-blender-scene.py').read_text())
with zipfile.ZipFile(root/'optical-disc-pack.zip','w',zipfile.ZIP_DEFLATED) as z:
 for p in root.rglob('*'):
  if p.is_file() and p.suffix!='.zip':z.write(p,p.relative_to(root))
print('Packaged', (root/'optical-disc-pack.zip').stat().st_size, 'bytes')
