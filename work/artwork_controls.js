const angleSlider=document.getElementById('art-angle');
const angleNumber=document.getElementById('art-angle-number');
const brandingToggle=document.getElementById('show-branding');
const printTextureToggle=document.getElementById('print-texture');
const printIntensity=document.getElementById('print-intensity');
const printIntensityValue=document.getElementById('print-intensity-value');
const printDotSize=document.getElementById('print-dot-size');
const printDotSizeValue=document.getElementById('print-dot-size-value');
const printPatterns=new Map();
const printedBandStates=new WeakMap();
const ps2PrintedBandURL='PS2_PRINTED_BAND_URL';
function printStrength(){return systemState[activeSystem].printTexture===false?0:(systemState[activeSystem].printIntensity??75)/100}
function dotScale(){return (systemState[activeSystem].printDotSize??250)/100}
function drawPrintedDots(ctx,size){
 const strength=printStrength();if(!strength||typeof ctx.createPattern!=='function')return;
 let tile=printPatterns.get(strength);
 if(!tile){
  tile=document.createElement('canvas');tile.width=tile.height=32;
  const ink=tile.getContext('2d');
  // A diagonal dot screen adds gentle ink-density variation on dark and light art.
  // source-atop below preserves the uploaded image's transparency exactly.
  for(const [x,y] of [[8,8],[24,24]]){
   ink.fillStyle='rgba(0,0,0,'+(.12*strength)+')';ink.beginPath();ink.arc(x,y,5,0,Math.PI*2);ink.fill();
   ink.fillStyle='rgba(255,255,255,'+(.09*strength)+')';ink.beginPath();ink.arc(x+1,y+1,3.8,0,Math.PI*2);ink.fill();
  }
  printPatterns.set(strength,tile);
 }
 const extent=8192/dotScale();
 ctx.save();ctx.globalCompositeOperation='source-atop';ctx.scale(size/extent,size/extent);
 ctx.fillStyle=ctx.createPattern(tile,'repeat');ctx.fillRect(0,0,extent,extent);ctx.restore();
}
async function applyPrintedBand(){
 if(activeSystem!=='ps2'||!v.model||typeof v.createCanvasTexture!=='function')return;
 // Older preview implementations still support the material-only finish.
 const outer=v.model.materials.find(m=>m.name==='TOP_ART_REPLACE_THIS_TEXTURE');
 const live=liveArtworkTextures.get(outer);
 if(typeof live?.canvas.getContext('2d').createPattern!=='function')return;
 const model=v.model,material=model.materials.find(m=>m.name==='TOP_PERMANENT_PS2_BRANDING');if(!material)return;
 const settings=printStrength()+':'+dotScale();if(printedBandStates.get(material)===settings)return;
 const base=await cachedArtworkImage(ps2PrintedBandURL);
 if(v.model!==model||activeSystem!=='ps2'||settings!==printStrength()+':'+dotScale())return;
 material.pbrMetallicRoughness.baseColorTexture.setTexture(paintLiveArtwork(material,{base},0));
 printedBandStates.set(material,settings);
}
const printedSurfaceTextures=new WeakMap();
function applyPrintTexture(){
 if(!v.model)return;
 const enabled=printStrength()>0;
 for(const material of v.model.materials){
  if(!['TOP_ART_REPLACE_THIS_TEXTURE','TOP_PERMANENT_PS2_BRANDING'].includes(material.name))continue;
  const p=material.pbrMetallicRoughness;
  // Retain the embedded maps so off/on never re-uploads or edits artwork.
  if(!printedSurfaceTextures.has(material))printedSurfaceTextures.set(material,{
   normal:material.normalTexture?.texture||null,
   roughness:p.metallicRoughnessTexture?.texture||null,
   anisotropy:material.anisotropyStrength??0
  });
  const saved=printedSurfaceTextures.get(material);
  material.normalTexture?.setTexture(enabled?saved.normal:null);
  p.metallicRoughnessTexture?.setTexture(enabled?saved.roughness:null);
  p.setRoughnessFactor?.(enabled?.52:material.name==='TOP_PERMANENT_PS2_BRANDING'?.38:.36);
  material.setAnisotropyStrength?.(enabled?saved.anisotropy:0);
 }
}
printTextureToggle.onchange=()=>{
 systemState[activeSystem].printTexture=printTextureToggle.checked;
 applyPrintTexture();
 syncArtworkControls();requestLiveArtworkUpdate().catch(error=>{s.textContent='Could not update print texture: '+error.message});
 s.textContent=printTextureToggle.checked?'Print texture on · Satin ink finish.':'Print texture off · Smooth artwork finish.';
};
printIntensity.oninput=()=>{
 const value=Number(printIntensity.value);if(!Number.isFinite(value))return;
 systemState[activeSystem].printIntensity=Math.max(0,Math.min(200,value));
 printIntensityValue.textContent=systemState[activeSystem].printIntensity+'%';
 applyPrintTexture();
 requestLiveArtworkUpdate().catch(error=>{s.textContent='Could not update print texture: '+error.message});
};
printDotSize.oninput=()=>{
 const value=Number(printDotSize.value);if(!Number.isFinite(value))return;
 systemState[activeSystem].printDotSize=Math.max(50,Math.min(400,value));
 printDotSizeValue.textContent=systemState[activeSystem].printDotSize+'%';
 requestLiveArtworkUpdate().catch(error=>{s.textContent='Could not update dot size: '+error.message});
};
const coverageSlider=document.getElementById('art-coverage');
const coverageNumber=document.getElementById('art-coverage-number');
const artworkImageCache=new Map();
const liveArtworkTextures=new WeakMap();
let artworkUpdate=Promise.resolve();
let artworkFrameQueued=false,liveArtworkTask;
function syncArtworkControls(){
 const state=systemState[activeSystem];const hasArt=Boolean(state&&state.art);
 const value=state&&state.artRotation||0;
 angleSlider.value=String(value);
 if(document.activeElement!==angleNumber)angleNumber.value=String(value);
 const coverage=state&&state.artCoverage||100;
 coverageSlider.value=String(coverage);
 if(document.activeElement!==coverageNumber)coverageNumber.value=String(coverage);
 for(const id of ['art-coverage','art-coverage-number','art-coverage-reset'])document.getElementById(id).disabled=!hasArt;
 for(const id of ['art-angle','art-angle-number','art-turn-left','art-turn-right','art-angle-reset'])document.getElementById(id).disabled=!hasArt;
 brandingToggle.checked=!state||state.branding!==false;
 printTextureToggle.checked=!state||state.printTexture!==false;
 printTextureToggle.disabled=!state;
 printIntensity.value=String(state?.printIntensity??75);
 printIntensityValue.textContent=printIntensity.value+'%';
 printIntensity.disabled=!state||state.printTexture===false;
 printDotSize.value=String(state?.printDotSize??250);
 printDotSizeValue.textContent=printDotSize.value+'%';
 printDotSize.disabled=!state||state.printTexture===false;
 if(activeSystem==='ps1')ps1LabelStyle.value=state.labelStyle||'silver';
 if(activeSystem==='gamecube')syncGCLabelControls();
}
function requestArtworkUpdate(){
 const pending=applyArt();artworkUpdate=pending;return pending;
}
async function waitForArtwork(){
 let pending;do{pending=artworkUpdate;await pending}while(pending!==artworkUpdate);
}
function requestLiveArtworkUpdate(){
 if(!artworkFrameQueued){
  artworkFrameQueued=true;
  liveArtworkTask=new Promise((resolve,reject)=>requestAnimationFrame(()=>{
   artworkFrameQueued=false;applyArt().then(resolve,reject);
  }));
  artworkUpdate=liveArtworkTask;
 }
 return liveArtworkTask;
}
function cachedArtworkImage(url){
 if(!artworkImageCache.has(url))artworkImageCache.set(url,readArtworkImage(url).catch(error=>{artworkImageCache.delete(url);throw error}));
 return artworkImageCache.get(url);
}
async function readLiveArtwork(art,header){
 const config=header&&header!=='none'?xboxHeaders[header]:null;
 if(header&&header!=='none'&&!config)throw new Error('Unknown Xbox header.');
 const [base,headerImage]=await Promise.all([cachedArtworkImage(art||xboxDefaultArt),config?cachedArtworkImage(config.url):null]);
 return {base,headerImage,config};
}
function paintLiveArtwork(material,inputs,angle,coverage=100){
 let live=liveArtworkTextures.get(material);
 if(!live){const texture=v.createCanvasTexture();live={texture,canvas:texture.source.element};liveArtworkTextures.set(material,live)}
 const {canvas,texture}=live;
 const size=Math.min(4096,Math.max(2048,inputs.base.width,inputs.base.height));
 if(canvas.width!==size||canvas.height!==size)canvas.width=canvas.height=size;
 const ctx=canvas.getContext('2d');
 // model-viewer 4.0 canvas textures retain Three.js flipY=true, unlike
 // createTexture uploads. Counter-flip the canvas so both paths look alike.
 ctx.setTransform(1,0,0,-1,0,size);ctx.clearRect(0,0,size,size);
 ctx.imageSmoothingEnabled=true;ctx.imageSmoothingQuality='high';
 ctx.save();ctx.translate(size/2,size/2);ctx.rotate(angle*Math.PI/180);
 const coveredSize=size*coverage/100;
 ctx.drawImage(inputs.base,-coveredSize/2,-coveredSize/2,coveredSize,coveredSize);ctx.restore();
 if(inputs.headerImage)drawXboxHeader(ctx,inputs.headerImage,inputs.config,size);
 drawPrintedDots(ctx,size);
 texture.source.update();return texture;
}
async function rotateUploadedArtwork(url,angle,coverage=100){
 if(!url||(!angle&&coverage===100))return url;
 if(!artworkImageCache.has(url))artworkImageCache.set(url,readArtworkImage(url).catch(error=>{artworkImageCache.delete(url);throw error}));
 const image=await artworkImageCache.get(url);
 const size=Math.min(4096,Math.max(2048,image.width,image.height));
 const canvas=document.createElement('canvas');canvas.width=canvas.height=size;
 const ctx=canvas.getContext('2d');ctx.imageSmoothingEnabled=true;ctx.imageSmoothingQuality='high';
 ctx.translate(size/2,size/2);ctx.rotate(angle*Math.PI/180);
 const coveredSize=size*coverage/100;
 ctx.drawImage(image,-coveredSize/2,-coveredSize/2,coveredSize,coveredSize);
 return canvas.toDataURL('image/png');
}
async function setArtworkAngle(value){
 value=Number(value);if(!Number.isFinite(value)||!systemState[activeSystem].art)return;
 const system=activeSystem;
 value=((value+180)%360+360)%360-180;
 value=Math.round(value*10)/10;
 systemState[system].artRotation=value;syncArtworkControls();
 try{await requestLiveArtworkUpdate();if(activeSystem===system&&systemState[system].artRotation===value)s.textContent='Artwork angle: '+value+'°. Download edited GLB to keep it.'}
 catch(error){if(activeSystem===system&&systemState[system].artRotation===value)s.textContent='Could not rotate artwork: '+error.message}
}
angleSlider.oninput=()=>setArtworkAngle(angleSlider.value);
angleNumber.oninput=()=>{if(angleNumber.value!=='')return setArtworkAngle(angleNumber.value)};
angleNumber.onchange=angleNumber.oninput;
angleNumber.onblur=()=>{angleNumber.value=String(systemState[activeSystem].artRotation||0)};
document.getElementById('art-turn-left').onclick=()=>setArtworkAngle((systemState[activeSystem].artRotation||0)-90);
document.getElementById('art-turn-right').onclick=()=>setArtworkAngle((systemState[activeSystem].artRotation||0)+90);
document.getElementById('art-angle-reset').onclick=()=>setArtworkAngle(0);
async function setArtworkCoverage(value){
 value=Number(value);if(!Number.isFinite(value)||!systemState[activeSystem].art)return;
 const system=activeSystem;value=Math.round(Math.max(80,Math.min(120,value))*10)/10;
 systemState[system].artCoverage=value;syncArtworkControls();
 try{await requestLiveArtworkUpdate();if(activeSystem===system&&systemState[system].artCoverage===value)s.textContent='Artwork coverage: '+value+'%. Larger values extend the image towards the rim.'}
 catch(error){if(activeSystem===system)s.textContent='Could not adjust artwork coverage: '+error.message}
}
coverageSlider.oninput=()=>setArtworkCoverage(coverageSlider.value);
coverageNumber.oninput=()=>{if(coverageNumber.value!=='')return setArtworkCoverage(coverageNumber.value)};
coverageNumber.onchange=coverageNumber.oninput;
coverageNumber.onblur=()=>{coverageNumber.value=String(systemState[activeSystem].artCoverage||100)};
document.getElementById('art-coverage-reset').onclick=()=>setArtworkCoverage(100);
brandingToggle.onchange=()=>{
 systemState[activeSystem].branding=brandingToggle.checked;updateArtwork();
 s.textContent=brandingToggle.checked?'PlayStation 2 branding shown.':'PlayStation 2 branding hidden. Your artwork fills the label.';
};
