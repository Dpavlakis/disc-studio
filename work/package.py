from pathlib import Path
import base64,json,struct,zipfile,ast,re,gzip
root=Path(__file__).resolve().parents[1]/'outputs'
from build_modern_playstation import build as build_modern_ps
for console in ['ps3','ps4']:build_modern_ps(console)
from clear_plastic_finish import update_model
from repair_disc_body import repair
for current_model in root.glob('*.glb'):repair(current_model)
for plastic_model in root.glob('*.glb'):
 if plastic_model.name.startswith(('ps2-','ps3-','ps4-','xbox-','xbox360-')) or plastic_model.name=='gamecube-disc.glb':update_model(plastic_model)
from soften_gamecube_security import soften
soften(root/'gamecube-disc.glb')
from refine_gamecube_underside import refine
refine(root/'gamecube-disc.glb')
from resize_gamecube_rear_text import resize
resize(root/'gamecube-disc.glb')
from sync_gamecube_security_sides import synchronize
synchronize(root/'gamecube-disc.glb')
from refine_original_xbox_mastering import refine as refine_xbox_mastering
refine_xbox_mastering(root/'xbox-original-disc.glb')
from clean_original_xbox_mastering_text import update as clean_xbox_text
clean_xbox_text(root/'xbox-original-disc.glb')
from separate_original_xbox_tags import update as separate_xbox_tags
separate_xbox_tags(root/'xbox-original-disc.glb')
from refine_xbox360_mastering import update as refine_360_mastering
for name in ['xbox360-silver-disc.glb','xbox360-test.glb']:refine_360_mastering(root/name)
from fix_bare_front_surfaces import update as fix_bare_front,TARGETS as bare_front_targets
for name in bare_front_targets:fix_bare_front(root/(name+'.glb'))
from fix_artwork_depth import update as fix_ink_depth,TARGETS as ink_depth_targets
for name in ink_depth_targets:fix_ink_depth(root/(name+'.glb'))
from add_modern_playstation_microetch import update as add_ps_microetch
for key in ['ps3','ps4']:add_ps_microetch(root/(key+'-silver-disc.glb'))
from refine_ps1 import update_centre_transparency
update_centre_transparency(root/'ps1-black-disc.glb')
from embed_default_labels import update as embed_approved_cover
for current_model in root.glob('*.glb'):embed_approved_cover(current_model)
from match_gamecube_security_material import update as match_gc_security
match_gc_security(root/'gamecube-disc.glb')
from build_xbox_disc_matched import build as build_disc_matched_xbox
build_disc_matched_xbox()
from build_xbox360_disc_matched import build as build_disc_matched_360
build_disc_matched_360()
from optimize_disc_models import build_all as optimize_runtime_models
optimized_root=optimize_runtime_models()
models={p.stem:'gzip:'+base64.b64encode(gzip.compress(p.read_bytes(),compresslevel=3,mtime=0)).decode() for p in optimized_root.glob('*.glb') if not p.stem.endswith('-preview')}
lightmaps={str(i):'data:application/octet-stream;base64,'+base64.b64encode((root/'lighting'/f'{i}-softbox.hdr').read_bytes()).decode() for i in range(1,5)}
environment_presets=json.loads((root/'lighting/environments.json').read_text(encoding='utf-8'))
for key,preset in environment_presets.items():
 lightmaps[key]='data:application/octet-stream;base64,'+base64.b64encode((root/'lighting'/preset['file']).read_bytes()).decode()
backgrounds={key:'data:image/jpeg;base64,'+base64.b64encode((root/'lighting'/preset['background']['file']).read_bytes()).decode() for key,preset in environment_presets.items()}
environment_controls_js=(root.parent/'work/environment_controls.js').read_text(encoding='utf-8').replace('LIGHTMAPS',json.dumps(lightmaps)).replace('BACKGROUNDS',json.dumps(backgrounds)).replace('ENVIRONMENT_PRESETS',json.dumps(environment_presets))
header_cuts={'classic': 372, 'live-classic': 372, 'live-wordmark': 363, 'no-live': 363, 'live-wide': 363, 'live-split': 363, 'kinect': 362, 'green-waves': 374}
headers={key:{'url':'data:image/png;base64,'+base64.b64encode((root/'xbox360-headers'/f'{key}.png').read_bytes()).decode(),'cut':cut} for key,cut in header_cuts.items()}
artwork_controls_js=(root.parent/'work/artwork_controls.js').read_text(encoding='utf-8')
disc_object_rotation_js=(root.parent/'work/disc_object_rotation.js').read_text(encoding='utf-8')
ps1_label_controls_js=(root.parent/'work/ps1_label_controls.js').read_text(encoding='utf-8')
gamecube_label_js=(root.parent/'work/gamecube_label_controls.js').read_text(encoding='utf-8').replace('GC_BRANDING_ASSETS',(root/'branding-source/gamecube-label/assets.json').read_text(encoding='utf-8'))
header_js=(root.parent/'work/xbox360_headers.js').read_text(encoding='utf-8').replace('XBOX_HEADERS',json.dumps(headers)).replace('XBOX_DEFAULT_ART',json.dumps('data:image/png;base64,'+base64.b64encode((root/'default-labels/x360.png').read_bytes()).decode()))
html='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Optical disc studio</title>
<script type="module" src="https://cdn.jsdelivr.net/npm/@google/model-viewer@4.0.0/dist/model-viewer.min.js"></script>
<style>body{margin:0;background:#15171d;color:#eee;font:16px system-ui}header{padding:24px;max-width:1000px;margin:auto}h1{font-size:28px;margin:0 0 12px}p{color:#bfc4d1}nav{display:flex;gap:12px;flex-wrap:wrap}button,label{padding:10px 16px;border:1px solid #5d6578;border-radius:6px;background:#252b38;color:white;font:inherit;cursor:pointer}button:focus-visible,label:focus-within{outline:2px solid #8dabff}input{max-width:240px}model-viewer{width:100%;height:68vh;min-height:360px;background:radial-gradient(#404755,#171a22)}#status{min-height:24px}</style>
<header><h1>Optical disc studio</h1><nav aria-label="Console sections" class="system-nav"><button data-system="ps1" aria-pressed="false">PS1</button><button data-system="ps2" aria-pressed="true">PS2</button><button data-system="xbox360" aria-pressed="false">Xbox 360</button></nav><p id="system-context">PS2 · Drag to rotate · scroll to zoom · middle drag rotates disc · right drag pans.</p><nav>
<button data-finish="ps2-blue-disc" data-platform="ps2">Blue CD</button><button data-finish="ps2-silver-disc" data-platform="ps2">Silver DVD</button><button data-finish="ps2-gold-disc" data-platform="ps2">Gold DVD</button><button data-finish="ps1-black-disc" data-platform="ps1" hidden>Black CD</button>
<button data-finish="xbox360-silver-disc" data-platform="xbox360" hidden>Silver DVD · Holographic hub</button><button data-finish="xbox360-test" data-platform="xbox360" hidden>Xbox 360 – Test</button>
<button id="front-view" type="button">Front view</button><button id="back-view" type="button">Back view</button><button id="download-png" type="button" disabled>Download PNG</button>
<button id="zoom-out" type="button" aria-label="Zoom out">−</button><label>Zoom <input id="zoom" type="range" min="0.5" max="12" value="1" step="0.1"><output id="zoom-value">1.0×</output></label><button id="zoom-in" type="button" aria-label="Zoom in">+</button><button id="fit-view" type="button">Fit disc</button><button id="fullscreen" type="button">Full screen</button>
<label>Lights <select id="lights"><option value="neutral">Studio</option><option value="1">1 softbox</option><option value="2">2 softboxes</option><option value="3">3 softboxes</option><option value="4">4 softboxes</option></select></label><label>Brightness <input id="brightness" type="range" min="0.3" max="2" value="1.1" step="0.05"></label>
<label data-platform="xbox360" hidden>Xbox header <select id="xbox-header"><option value="none">None</option><option value="classic">Classic</option><option value="live-classic">Xbox Live · Classic</option><option value="live-rings">Xbox Live · Rings</option><option value="live-wide">Xbox Live · Wide</option><option value="green-waves">Green waves</option><option value="kinect">Kinect</option></select></label><label>Top artwork <input id="art" type="file" accept="image/*"></label><label><input id="show-art" type="checkbox" checked> Show artwork</label></nav><p id="status" role="status">Loading. First use requires internet for the 3D viewer.</p></header>
<style>html{height:100%}body{min-height:100vh;min-height:100dvh;display:flex;flex-direction:column}header{box-sizing:border-box;max-width:none;width:100%;padding:12px 18px}h1{font-size:20px;margin:0 0 5px}header p{font-size:13px;margin:5px 0 9px}nav{gap:7px}button,label{font-size:13px;padding:7px 10px}label{display:inline-flex;align-items:center;gap:7px}input[type=range]{width:110px}select{background:#252b38;color:#eee;border:1px solid #68748b;border-radius:4px;padding:4px}output{min-width:34px}#status{margin:7px 0 0;min-height:18px}.disc-viewport{position:relative;width:100%;flex:1;min-height:520px;overflow:hidden}.disc-viewport model-viewer{position:absolute;left:0;top:0;width:200%;height:200%;min-height:0;transform:scale(.5);transform-origin:top left}.disc-viewport:fullscreen{width:100vw;height:100vh;background:#171a22}@media(max-width:600px){header{padding:10px}.disc-viewport{min-height:65vh}input[type=range]{width:90px}}</style>
<div class="disc-viewport"><model-viewer id="disc" camera-controls camera-orbit="180deg 90deg 0.23m" camera-target="0m 0m 0m" min-camera-orbit="auto auto 0.065m" max-camera-orbit="auto auto 1m" min-field-of-view="2deg" max-field-of-view="60deg" field-of-view="35deg" environment-image="neutral" exposure="1.1" shadow-intensity="0" interaction-prompt="none" alt="Reflective optical disc with replaceable top artwork"></model-viewer></div>
<script>const models=MODELS; const v=document.getElementById('disc'); const s=document.getElementById('status');let artURL;
let activeSystem='ps1';const systemState={ps3:{finish:'ps3-silver-disc',art:null,artRotation:0,branding:true},ps4:{finish:'ps4-silver-disc',art:null,artRotation:0,branding:true},gamecube:{finish:'gamecube-disc',art:null,artRotation:0,branding:true},ps1:{finish:'ps1-black-disc',art:null,artRotation:0,branding:true,labelStyle:'silver'},ps2:{finish:'ps2-blue-disc',art:null,artRotation:0,branding:true},xbox360:{finish:'xbox360-disc-matched',art:null,artRotation:0,branding:true},xbox:{finish:'xbox-original-disc-matched',art:null,artRotation:0,branding:true}};
const emptySystem=document.createElement('div');emptySystem.className='empty-system';emptySystem.hidden=true;emptySystem.innerHTML='<h2>Xbox 360</h2><p>Next in the collection.</p><p>The Xbox 360 disc model has not been added yet.</p>';document.querySelector('.disc-viewport').append(emptySystem);
const systemStyle=document.createElement('style');systemStyle.textContent='[hidden]{display:none!important}.system-nav{margin:10px 0}.system-nav button{min-width:70px}.system-nav button[aria-pressed=true]{background:#e7eaf1;color:#15171d;border-color:#e7eaf1}.empty-system{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:24px}.empty-system h2{font-size:32px;margin:0 0 10px}.empty-system p{margin:5px}';document.head.append(systemStyle);
const finishStorageKey='discStudio.finishes.v1';
function restoreFinishes(){
 try{
  const saved=JSON.parse(localStorage.getItem(finishStorageKey)||'{}');
  for(const [system,state] of Object.entries(systemState)){
   const finish=saved?.[system];
   if(typeof finish==='string'&&models[finish]&&[...document.querySelectorAll('[data-finish]')].some(b=>b.dataset?.platform===system&&b.dataset.finish===finish))state.finish=finish;
  }
 }catch(error){}
}
function saveFinishes(){
 try{localStorage.setItem(finishStorageKey,JSON.stringify(Object.fromEntries(Object.entries(systemState).map(([system,state])=>[system,state.finish]))))}catch(error){}
}
restoreFinishes();
MODEL_LOADING_SCRIPT
function markFinish(){document.querySelectorAll('[data-finish]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.finish===systemState[activeSystem].finish)))}
function chooseSystem(system){activeSystem=system;markFinish();const ready=Boolean(systemState[system]);document.querySelectorAll('[data-system]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.system===system)));document.querySelectorAll('[data-platform]').forEach(b=>b.hidden=b.dataset.platform!==system||b.dataset.reference==='true');v.style.visibility=ready?'visible':'hidden';emptySystem.hidden=ready;for(const id of ['front-view','back-view','download-png','zoom-out','zoom','zoom-in','fit-view','art','show-art'])document.getElementById(id).disabled=!ready;document.getElementById('system-context').textContent=ready?({ps1:'PS1',ps2:'PS2',ps3:'PS3',ps4:'PS4',xbox360:'Xbox 360',xbox:'Original Xbox',gamecube:'GameCube · 80 mm'}[system])+' · Drag to rotate · scroll to zoom · middle drag rotates disc · right drag pans.':'Xbox 360 · Ready for the next disc model';document.getElementById('art').value='';if(ready){artURL=systemState[system].art;s.textContent='Loading '+({ps1:'PS1',ps2:'PS2',ps3:'PS3',ps4:'PS4',xbox360:'Xbox 360',xbox:'Original Xbox',gamecube:'GameCube · 80 mm'}[system])+' disc…';setDiscModel(systemState[system].finish);if(!modelPreparationPending)document.getElementById('download-png').disabled=!v.loaded}else{s.textContent='Xbox 360 section prepared. Switch to PS1 or PS2 to use the current models.'}syncArtworkControls()}
document.querySelectorAll('[data-system]').forEach(b=>b.onclick=()=>chooseSystem(b.dataset.system));
ENVIRONMENT_CONTROLS_SCRIPT
DISC_OBJECT_ROTATION_SCRIPT
document.getElementById('brightness').oninput=e=>{v.exposure=Number(e.target.value)};
const zoom=document.getElementById('zoom');const zoomValue=document.getElementById('zoom-value');
function changeZoom(value){value=Math.max(.5,Math.min(12,value));zoom.value=value;zoomValue.textContent=value.toFixed(1)+'×';v.fieldOfView=(2*Math.atan(Math.tan(35*Math.PI/360)/value)*180/Math.PI)+'deg'}
zoom.oninput=()=>changeZoom(Number(zoom.value));document.getElementById('zoom-in').onclick=()=>changeZoom(Number(zoom.value)*1.35);document.getElementById('zoom-out').onclick=()=>changeZoom(Number(zoom.value)/1.35);
document.getElementById('fit-view').onclick=()=>{resetDiscRotation();const orbit=v.getCameraOrbit();v.cameraTarget='0m 0m 0m';v.cameraOrbit=orbit.theta+'rad '+orbit.phi+'rad 0.23m';changeZoom(1)};
document.getElementById('fullscreen').onclick=async()=>{try{if(document.fullscreenElement)await document.exitFullscreen();else await document.querySelector('.disc-viewport').requestFullscreen()}catch(err){s.textContent='Full screen is unavailable in this browser.'}};
// Supersample at twice the displayed width/height and keep the native renderer
// at full resolution, including while orbiting. CSS downsamples the final image.
customElements.whenDefined('model-viewer').then(()=>{customElements.get('model-viewer').minimumRenderScale=1;return applyEnvironment()});
const pngButton=document.getElementById('download-png');
function saveBlob(blob,name){const url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download=name;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),10000)}
async function setView(theta){await customElements.whenDefined('model-viewer');resetDiscRotation();v.cameraTarget='0m 0m 0m';v.cameraOrbit=theta+'deg 90deg 0.23m';changeZoom(1);await v.updateComplete;v.jumpCameraToGoal();s.textContent=theta===180?'Front view — artwork side.':'Back view — reflective underside.'}
document.getElementById('front-view').onclick=()=>setView(180);
document.getElementById('back-view').onclick=()=>setView(0);
pngButton.onclick=async()=>{pngButton.disabled=true;try{if(!v.loaded)throw new Error('Wait for the disc to finish loading.');await waitForArtwork();transparentCapture=true;syncEnvironmentBackground();await v.updateComplete;v.jumpCameraToGoal();await new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));const blob=await v.toBlob({mimeType:'image/png',idealAspect:false});if(!blob)throw new Error('The image could not be captured.');saveBlob(blob,'disc-view.png');s.textContent='PNG downloaded with a transparent background, using the current angle and artwork.'}catch(err){s.textContent='PNG export failed: '+err.message}finally{transparentCapture=false;syncEnvironmentBackground();pngButton.disabled=!v.loaded}};
v.addEventListener('load',()=>{if(!modelPreparationPending)pngButton.disabled=false});
v.addEventListener('error',()=>{pngButton.disabled=true});
const showArt=document.getElementById('show-art');const artTextures=new WeakMap();
function updateArtwork(){if(!v.model)return;const m=v.model.materials.find(m=>m.name==='TOP_ART_REPLACE_THIS_TEXTURE');if(!m)return;const p=m.pbrMetallicRoughness;if(!artTextures.has(m))artTextures.set(m,p.baseColorTexture.texture);const enabled=showArt.checked;p.baseColorTexture.setTexture(enabled?artTextures.get(m):null);m.setAlphaMode(enabled&&activeSystem!=='gamecube'?'MASK':'BLEND');p.setBaseColorFactor(enabled?[1,1,1,activeSystem==='gamecube'?.94:1]:[1,1,1,0]);p.setMetallicFactor(0);p.setRoughnessFactor(.36);const badge=v.model.materials.find(m=>m.name==='TOP_PERMANENT_PS2_BRANDING');if(badge){badge.setAlphaMode('BLEND');badge.pbrMetallicRoughness.setBaseColorFactor([1,1,1,systemState[activeSystem].branding!==false?1:0])}applyPS1LabelStyle()}
XBOX_HEADER_SCRIPT
PS1_LABEL_CONTROLS_SCRIPT
GAMECUBE_LABEL_SCRIPT
ARTWORK_CONTROLS_SCRIPT
async function applyArt(){
 if(!v.model)return;const revision=++artworkRevision;const model=v.model;
 const m=model.materials.find(m=>m.name==='TOP_ART_REPLACE_THIS_TEXTURE');if(!m)return;
 if(!originalArtTextures.has(m))originalArtTextures.set(m,m.pbrMetallicRoughness.baseColorTexture.texture);
 const system=activeSystem;const state=systemState[system];const angle=state.artRotation||0;const header=state.header;
 let url=artURL;let texture;
 const fixedHeader=system==='xbox360'&&header!=='none'?header:null;
 if((url||fixedHeader)&&typeof v.createCanvasTexture==='function'){
  const inputs=await readLiveArtwork(url,fixedHeader);
  if(revision!==artworkRevision||v.model!==model)return;
  texture=paintLiveArtwork(m,inputs,angle,state.artCoverage||100);
 }else{
  if(url&&(angle||(state.artCoverage||100)!==100))url=await rotateUploadedArtwork(url,angle,state.artCoverage||100);
  if(fixedHeader)url=await composeXboxArtwork(url,fixedHeader);
  texture=url?await v.createTexture(url):originalArtTextures.get(m);
  if(revision!==artworkRevision||v.model!==model)return;
 }
 if(artTextures.get(m)!==texture)artTextures.set(m,texture);updateArtwork();
 await applyGCLabel();
}
showArt.onchange=()=>{updateArtwork();s.textContent=showArt.checked?'Artwork shown.':'Artwork hidden. Your image is kept for when you turn it back on.'};
v.addEventListener('load',async event=>{if(modelPreparationPending||(event.detail?.url&&String(event.detail.url)!==v.src))return;const model=v.model,system=activeSystem;syncArtworkControls();try{await requestArtworkUpdate();await waitForArtwork();await v.updateComplete;if(model!==v.model||system!==activeSystem)return;v.style.visibility='visible';s.textContent='Ready. Reflections change as you rotate the disc.'}catch(error){if(model===v.model&&system===activeSystem)v.style.visibility='visible';s.textContent='Could not apply artwork: '+error.message}});v.addEventListener('error',()=>{s.textContent='The disc could not load. Refresh the studio to try again.'});
document.querySelectorAll('[data-finish]').forEach(b=>b.onclick=()=>{systemState[activeSystem].finish=b.dataset.finish;saveFinishes();markFinish();s.textContent='Loading finish…';setDiscModel(b.dataset.finish)});
document.getElementById('art').onchange=async e=>{if(!e.target.files[0])return;if(artURL){artworkImageCache.delete(artURL);URL.revokeObjectURL(artURL)}artURL=URL.createObjectURL(e.target.files[0]);systemState[activeSystem].art=artURL;systemState[activeSystem].artRotation=0;systemState[activeSystem].artCoverage=100;syncArtworkControls();try{await requestArtworkUpdate();s.textContent='Artwork replaced. Download edited GLB to keep it.'}catch(err){s.textContent='Could not apply artwork: '+err.message}};
chooseSystem('ps1');</script></html>'''
html=re.sub(r'<header>.*?</header>',(root.parent/'work/studio_header.html').read_text(encoding='utf-8'),html,count=1,flags=re.S)
html=html.replace('<div class="disc-viewport">','<div class="disc-viewport"><div class="stage-help">Drag to rotate<span>·</span>Scroll to zoom<span>·</span>Middle-drag: disc rotation<span>·</span>Right-drag: pan</div>')
html=html.replace('<script>const models=','<style>'+(root.parent/'work/studio.css').read_text(encoding='utf-8')+'</style><script>const models=')
(root/'studio.html').write_text(html.replace('MODELS',json.dumps(models)).replace('MODEL_LOADING_SCRIPT',(root.parent/'work/model_loading.js').read_text(encoding='utf-8')).replace('ENVIRONMENT_CONTROLS_SCRIPT',environment_controls_js).replace('DISC_OBJECT_ROTATION_SCRIPT',disc_object_rotation_js).replace('XBOX_HEADER_SCRIPT',header_js).replace('PS1_LABEL_CONTROLS_SCRIPT',ps1_label_controls_js).replace('GAMECUBE_LABEL_SCRIPT',gamecube_label_js).replace('ARTWORK_CONTROLS_SCRIPT',artwork_controls_js),encoding='utf-8')
print('Updated office-background studio saved as studio.html')
(root/'READ-ME.txt').write_text('''OPTICAL DISC MODEL PACK

Open studio.html in a browser. First use needs internet for the viewer library.
Select Blue, Silver, Gold or Black. Drag to inspect the light response. Choose a square image under Top artwork, use Artwork rotation to align it, and turn off Show PlayStation 2 branding if your image already contains that band. Use Save transparent PNG to save an image of your customized disc. The browser studio does not offer GLB downloads.

MODELS
ps2-blue-disc.glb: cobalt blue underside matching the supplied references.
ps2-silver-disc.glb: silver finish.
ps3-silver-disc.glb / ps4-silver-disc.glb: PS2 silver body with separate PS3/PS4 security layouts and supplied SVG wordmarks. Three console wordmarks alternate with three PS monograms. No PS2 top band. Matrix codes are representative.
ps2-gold-disc.glb: gold finish.
gamecube-disc.glb: 80 mm diameter, 15 mm centre hole, 1.2 mm nominal body. Silver rainbow read side, clear front with a thin black outer rim, dark mastering marks beneath uploaded artwork. GameCube artwork uses 94% ink opacity to let underlying security details show subtly. The separate GameCube branding layer includes a configurable lower colour panel, two seal variants, E/T rating selection and an editable four-character game code. Security pattern and hub details are reconstructed from reference photographs, not exact encoded data.\nps1-black-disc.glb: opaque glossy black disc and centre hub, with a 15 mm open hole. PSX label construction offers a silver face over black, a white face with a black centre, or extra printing inside the centre ring. Uploaded artwork is shared by the outer and optional centre print, with matching rotation. The inner hole surround and outer centre ring remain black. The silver/white face and centre-print visibility are saved in edited GLB exports. No PS2 label band or PS2 inner-ring logos are used. Only the black hub and moulded rings have a 40% light transmission; the silver face, barcode marks and data surface remain opaque.\nxbox360-silver-disc.glb: silver Xbox 360 model with holographic center, supplied Xbox SVG and X360 font.
All files embed their textures and use meters: 120 mm diameter, 15 mm center hole, 1.2 mm nominal thickness (moulded rings extend slightly).
PS model parts include: top artwork, underside, edge, hub, three moulded rings and an independent etched branding/matrix ring, plus the PS2 label band above the replaceable artwork and a solid dark perimeter ring visible from both sides, plus three smooth matrix boundary/separator rings and geometric barcode backing/bars. Discs are upright with their spindle centred at the glTF origin. Artwork faces -Z; reflective underside faces +Z.

INNER BRANDING
The underside has an independent metallic etched ring with repeated PlayStation wordmarks and PS monograms rendered from your supplied SVG files and representative matrix/barcode marks. It remains in place when top art changes. The logo shapes come from the supplied SVGs; the ring layout is recreated rather than scanned from a particular pressing. Original SVGs are included in branding-source. The placeholder matrix text is illustrative.

REPLACE ART IN A 3D APP
For PS1, the outer label starts at a 19.5 mm radius over the black hub. The optional centre-print annulus covers radii 11.4 to 18.2 mm, sampling the same full-disc artwork; black rings remain visible on either side. The plastic data surface is opaque; the black hub and moulded rings have 2% optical transmission.
Assign your image to Base Color in TOP_ART_REPLACE_THIS_TEXTURE. UVs are already set up as a centered square. Use a 2048x2048 or larger square image. Printed artwork is clipped at 48.92% of image width. The label inner radius is 9.5% of image width for PS2, 16.25% for PS1, and 14.42% for Xbox 360. The rim and centre remain separate geometry. Xbox 360 top artwork begins outside its holographic band. The hole is real geometry, so the image need not contain a cutout. Keep image orientation as supplied; rotate the texture if your artwork needs a different alignment.
label-art.png is a placeholder/template. Changing it alone does NOT update the embedded GLB: reassign the image in your 3D app, or use the browser preview and export.

LIGHT RESPONSE
The Environment menu keeps all studio softbox options and adds five photographic environments with separate 8K backgrounds and 2K HDR lighting: living room, office, garden, forest and sunset waterfront. Select one to light the disc; Show 360° surroundings also displays the panorama behind it. Choose your own panorama accepts Radiance .hdr or a 2:1 equirectangular JPG/PNG. LDR photos provide less highlight range than HDR. Lighting and surroundings are preview settings, not embedded in exported GLBs. Transparent PNG export excludes the surroundings. Included HDRIs are CC0 assets from Poly Haven; see lighting/ENVIRONMENT-CREDITS.txt for sources.
Blue metallic material, glossy clearcoat, concentric micro-normal texture, radial anisotropy and glTF iridescence. Use an HDRI/studio environment with bright strip lights for reflections. Rainbow response is an artistic approximation of optical-disc diffraction, not a spectral diffraction simulation. Exact blue appearance depends on lighting, exposure and renderer. Apps without the optional glTF material extensions show a simpler blue metallic surface. Hub transmission may also vary by renderer.

BLENDER
In Blender 4.x or later, open the Scripting workspace, load create-blender-scene.py from this folder, then Run Script. Keep the GLBs and PNGs beside it. It imports the blue model, builds an editable view-dependent underside material, adds lights and a camera, packs images, and saves ps2-disc-studio.blend beside the files. Existing scene objects are preserved. Render with F12. The Blender setup script has been syntax checked but was not run here because Blender is unavailable. Browser viewer is the portable preview.
''',encoding='utf-8')
for p in root.glob('*.glb'):
 if p.stem.endswith('-preview'):continue
 b=p.read_bytes(); magic,ver,total=struct.unpack_from('<III',b); assert magic==0x46546c67 and total==len(b)
 size=struct.unpack_from('<I',b,12)[0]; g=json.loads(b[20:20+size]); assert len(g['meshes'])==(13 if p.name=='gamecube-disc.glb' else 22 if p.name in {'xbox360-test.glb','xbox360-disc-matched.glb'} else (20 if p.name.startswith('xbox') else (18 if p.name.startswith(('ps2-','ps3-','ps4-')) else 17)))
 for mesh in g['meshes']:
  attrs=mesh['primitives'][0]['attributes']; assert all(g['accessors'][a]['count']==g['accessors'][attrs['POSITION']]['count'] for a in attrs.values())
 print(p.name, 'validated', len(g['meshes']), 'meshes')
ast.parse((root/'create-blender-scene.py').read_text())
with zipfile.ZipFile(root/'optical-disc-pack.zip','w',zipfile.ZIP_DEFLATED) as z:
 allowed_folders={'branding-source','lighting','xbox360-headers','default-labels'}
 for p in root.rglob('*'):
  rel=p.relative_to(root)
  if not p.is_file() or p.suffix=='.zip':continue
  if p.suffix=='.html' and p.name!='studio.html':continue
  if len(rel.parts)>1 and rel.parts[0] not in allowed_folders:continue
  if p.name.startswith('007-') or p.name=='disc-cleanup-report.csv':continue
  z.write(optimized_root/p.name if p.suffix=='.glb' and len(rel.parts)==1 else p,rel)
print('Packaged', (root/'optical-disc-pack.zip').stat().st_size, 'bytes')






