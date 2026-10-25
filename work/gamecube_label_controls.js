const gcBrandingAssets=GC_BRANDING_ASSETS;
const gcLabelTextures=new WeakMap();
const gcLabelRenderedStates=new WeakMap();
const gcLabelImages=new Map();
function gcLabelImage(key){
 if(!gcLabelImages.has(key))gcLabelImages.set(key,readArtworkImage(gcAssetURL(key)).catch(error=>{gcLabelImages.delete(key);throw error}));
 return gcLabelImages.get(key);
}
let gcLabelRevision=0;
const gcFields={enabled:'gc-label-enabled',panel:'gc-panel-enabled',color:'gc-panel-color',seal:'gc-seal',rating:'gc-rating',code:'gc-game-code',angle:'gc-label-angle'};
function gcLabelState(){return systemState.gamecube.label||(systemState.gamecube.label={enabled:true,panel:true,color:'#080808',seal:'seal',rating:'e',code:'GZWE',angle:0})}
function syncGCLabelControls(){
 if(activeSystem!=='gamecube')return;
 const state=gcLabelState();for(const [key,id] of Object.entries(gcFields)){const el=document.getElementById(id);if(key==='enabled'||key==='panel')el.checked=state[key];else if(document.activeElement!==el)el.value=String(state[key])}
 document.getElementById('gc-panel-color-value').textContent=state.color.toUpperCase();
 document.getElementById('gc-label-angle-range').value=String(state.angle);
}
// SVG images need intrinsic dimensions: an unspecified size defaults to 300x150,
// which letterboxes the wide GameCube mark before the canvas scales it again.
function gcAssetBox(key){const values=gcBrandingAssets[key].match(/viewBox="([^"]+)"/)[1].trim().split(/[\s,]+/).map(Number);return {width:values[2],height:values[3]}}
function gcAssetURL(key){const box=gcAssetBox(key);const svg=gcBrandingAssets[key].replace('<svg ','<svg width="'+box.width+'" height="'+box.height+'" ');return 'data:image/svg+xml;charset=utf-8,'+encodeURIComponent(svg)}
function gcDrawAsset(c,key,image,x,y,width,height){const box=gcAssetBox(key);const scale=Math.min(width/box.width,height/box.height);const w=box.width*scale,h=box.height*scale;c.drawImage(image,x+(width-w)/2,y+(height-h)/2,w,h)}
function gcCanvasTexture(material,highResolution=false){
 let sizes=gcLabelTextures.get(material);if(!sizes){sizes=new Map();gcLabelTextures.set(material,sizes)}
 const size=material.name==='GAMECUBE_LABEL_FOIL'&&highResolution?8192:2048;
 if(!sizes.has(size)){const texture=v.createCanvasTexture();texture.source.element.width=texture.source.element.height=size;sizes.set(size,texture)}
 return sizes.get(size);
}
function gcFrame(canvas,angle,clear=true){
 const c=canvas.getContext('2d');c.setTransform(1,0,0,-1,0,canvas.height);if(clear)c.clearRect(0,0,canvas.width,canvas.height);
 c.save();c.scale(canvas.width/1280,canvas.height/1280);c.translate(640,640);c.rotate(angle*Math.PI/180);c.translate(-640,-640);
 c.beginPath();c.arc(640,640,626.4,0,Math.PI*2);c.arc(640,640,184,0,Math.PI*2,true);c.clip('evenodd');return c;
}
function gcText(c,text,x,y,size,maxWidth){
 c.font=size+'px Arial';c.textAlign='center';c.textBaseline='alphabetic';c.fillText(text,x,y,maxWidth);
}
function gcCurvedModelText(c){
 const radius=590; // Lower baseline follows the Batman reference, closer to the rim.
 const text='MODEL No. DOL-006(USA)';c.font='30px Arial';c.textAlign='center';c.textBaseline='alphabetic';let total=c.measureText(text).width;let offset=-total/2;
 for(const ch of text){const width=c.measureText(ch).width;const a=Math.PI/2-(offset+width/2)/radius;c.save();c.translate(640+radius*Math.cos(a),640+radius*Math.sin(a));c.rotate(a-Math.PI/2);c.fillText(ch,0,0);c.restore();offset+=width}
}
async function applyGCLabel(highResolution=false){
 if(activeSystem!=='gamecube'||!v.model)return;
 const model=v.model;const panel=model.materials.find(m=>m.name==='GAMECUBE_LABEL_PANEL');const foil=model.materials.find(m=>m.name==='GAMECUBE_LABEL_FOIL');if(!panel||!foil)return;
 const revision=++gcLabelRevision;const state={...gcLabelState()};syncGCLabelControls();
 const enabled=state.enabled;
 for(const [m,visible] of [[panel,enabled&&state.panel],[foil,enabled]]){m.setAlphaMode(visible&&m===panel?'MASK':'BLEND');m.pbrMetallicRoughness.setBaseColorFactor(visible?(m===foil?[.68,.68,.68,.90]:[1,1,1,1]):[1,1,1,0])}
 if(!enabled)return;
 const panelTexture=gcCanvasTexture(panel,highResolution);const texture=gcCanvasTexture(foil,highResolution);
 const renderKey=JSON.stringify({...state,highResolution});
 if(gcLabelRenderedStates.get(texture)===renderKey&&gcLabelRenderedStates.get(panelTexture)===renderKey){
  if(panel.pbrMetallicRoughness.baseColorTexture.texture!==panelTexture)panel.pbrMetallicRoughness.baseColorTexture.setTexture(panelTexture);
  if(foil.pbrMetallicRoughness.baseColorTexture.texture!==texture)foil.pbrMetallicRoughness.baseColorTexture.setTexture(texture);
  return;
 }
 const names=['logo',state.seal,...(state.rating==='none'?[]:['rating-'+state.rating])];
 const images=await Promise.all(names.map(gcLabelImage));
 if(revision!==gcLabelRevision||activeSystem!=='gamecube'||model!==v.model)return;
 let c=gcFrame(texture.source.element,state.angle);c.fillStyle='#fff';c.strokeStyle='#fff';
 gcDrawAsset(c,'logo',images[0],390,850,520,130);gcDrawAsset(c,state.seal,images[1],128,825,230,177);if(images[2])gcDrawAsset(c,'rating-'+state.rating,images[2],937,793,161,224);
 c.lineWidth=3;c.strokeRect(298,1058,688,48);gcText(c,'FOR USE ONLY IN USA, CANADA, MEXICO AND LATIN AMERICA',642,1090,20,660);
 gcText(c,'DL • DOL • '+state.code+' • USA',640,1150,31,650);gcCurvedModelText(c);c.restore();
 // The colour ink does not sit underneath the metallic lettering. Open its
 // exact mask in the panel so the foil's small transparency reaches the real
 // mastering ring and bars, rather than revealing another opaque paint layer.
 c=gcFrame(panelTexture.source.element,state.angle);c.fillStyle=state.color;c.fillRect(0,770,1280,510);c.restore();
 c.setTransform(1,0,0,1,0,0);c.globalCompositeOperation='destination-out';c.drawImage(texture.source.element,0,0,panelTexture.source.element.width,panelTexture.source.element.height);c.globalCompositeOperation='source-over';
 panelTexture.source.update();panel.pbrMetallicRoughness.baseColorTexture.setTexture(panelTexture);
 // Preserve the full-strength panel knockout, then reduce only the logo's
 // foil coverage. This compensates for the now-subtle physical security ring
 // without strengthening that ring across the rest of the printed face.
 c=gcFrame(texture.source.element,state.angle,false);c.globalCompositeOperation='destination-out';c.globalAlpha=.50;
 gcDrawAsset(c,'logo',images[0],390,850,520,130);c.restore();c.globalCompositeOperation='source-over';c.globalAlpha=1;
 texture.source.update();foil.pbrMetallicRoughness.baseColorTexture.setTexture(texture);
 gcLabelRenderedStates.set(texture,renderKey);gcLabelRenderedStates.set(panelTexture,renderKey);


}
for(const [key,id] of Object.entries(gcFields)){
 const el=document.getElementById(id);
 el.oninput=()=>{
  if(activeSystem!=='gamecube')return;
  const state=gcLabelState();
  if(key==='code'){
   el.value=el.value.toUpperCase().replace(/[^A-Z0-9]/g,'').slice(0,4);
   const valid=el.value.length===4;el.setCustomValidity?.(valid?'':'Enter four letters or numbers.');document.getElementById('gc-code-hint').textContent=valid?'DL • DOL • '+el.value+' • USA':'Enter all four letters or numbers to update the label.';
   if(!valid)return;state.code=el.value;
  }else if(key==='enabled'||key==='panel')state[key]=el.checked;
  else if(key==='angle'){if(!Number.isFinite(Number(el.value)))return;state.angle=Math.max(-180,Math.min(180,Number(el.value)))}
  else state[key]=el.value;
  artworkUpdate=applyGCLabel();artworkUpdate.catch(error=>{s.textContent='Could not update the GameCube label: '+error.message});
 };
 el.onchange=el.oninput;
}
document.getElementById('gc-label-reset').onclick=()=>{systemState.gamecube.label={enabled:true,panel:true,color:'#080808',seal:'seal',rating:'e',code:'GZWE',angle:0};syncGCLabelControls();artworkUpdate=applyGCLabel()};

const gcAngleRange=document.getElementById('gc-label-angle-range');
gcAngleRange.oninput=()=>{const number=document.getElementById('gc-label-angle');number.value=gcAngleRange.value;number.oninput()};
