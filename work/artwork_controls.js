const angleSlider=document.getElementById('art-angle');
const angleNumber=document.getElementById('art-angle-number');
const brandingToggle=document.getElementById('show-branding');
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

// Placeholder artwork uses the approved footer; personal artwork keeps the
// existing independent PS2 branding controls and its original band.
const defaultPS2Bands=new WeakMap();
async function applyDefaultPS2Branding(){
 if(activeSystem!=='ps2'||!v.model)return;
 const model=v.model;
 const badge=model.materials.find(m=>m.name==='TOP_PERMANENT_PS2_BRANDING');
 const slot=badge?.pbrMetallicRoughness.baseColorTexture;
 if(!slot?.setTexture)return;
 if(!defaultPS2Bands.has(badge))defaultPS2Bands.set(badge,{original:slot.texture});
 const saved=defaultPS2Bands.get(badge);
 if(systemState.ps2.art){slot.setTexture(saved.original);return}
 if(!saved.placeholder)saved.placeholder=v.createTexture(defaultLabels.ps2Branding);
 const texture=await saved.placeholder;
 if(v.model===model&&activeSystem==='ps2'&&!systemState.ps2.art)slot.setTexture(texture);
}
