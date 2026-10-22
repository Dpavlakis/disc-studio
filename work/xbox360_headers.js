const xboxHeaders=XBOX_HEADERS;
const xboxDefaultArt=XBOX_DEFAULT_ART;
const xboxHeader=document.getElementById('xbox-header');
systemState.xbox360.header='none';
const originalArtTextures=new WeakMap();let artworkRevision=0;
function readArtworkImage(url){return new Promise((resolve,reject)=>{const img=new Image();img.onload=()=>resolve(img);img.onerror=()=>reject(new Error('Could not read the selected header or artwork.'));img.src=url})}
function drawXboxHeader(ctx,img,config,size){
 const scale=(size*.0587/.12)/(img.width*690/1440)*1.015;
 const offset=size/2-img.width*.5*scale;
 ctx.save();ctx.beginPath();ctx.arc(size/2,size/2,size*.0587/.12,0,Math.PI*2);ctx.clip();
 ctx.drawImage(img,0,0,img.width,config.cut*img.height/1440,offset,offset,img.width*scale,config.cut*img.height/1440*scale);ctx.restore();
}
async function composeXboxArtwork(art,header){
 const base=await readArtworkImage(art||xboxDefaultArt);
 const canvas=document.createElement('canvas');canvas.width=canvas.height=2048;
 const ctx=canvas.getContext('2d');ctx.drawImage(base,0,0,2048,2048);
 if(header!=='none'){
  const config=xboxHeaders[header];if(!config)throw new Error('Unknown Xbox header.');
  const img=await readArtworkImage(config.url);
  // Register the template's disc to the model's printed artwork circle.
  // Transparent PSD headers contain only printed branding, with no painted rim.
  // Small print bleed covers the PSD's inset edge; the model-aligned circle
  // below clips the excess, so the white field and color line meet the edge.
  drawXboxHeader(ctx,img,config,2048);
 }
 return canvas.toDataURL('image/png');
}
xboxHeader.onchange=async()=>{
 systemState.xbox360.header=xboxHeader.value;
 try{await requestArtworkUpdate();s.textContent=xboxHeader.value==='none'?'Xbox header removed.':'Xbox header applied. Download edited GLB to keep it.'}
 catch(err){s.textContent='Could not apply Xbox header: '+err.message}
};
