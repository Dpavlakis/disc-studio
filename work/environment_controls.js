const lightmaps=LIGHTMAPS;
const backgrounds=BACKGROUNDS;
const environmentPresets=ENVIRONMENT_PRESETS;
const lightChoice=document.getElementById('lights');
const showSurroundings=document.getElementById('show-surroundings');
const environmentHint=document.getElementById('environment-hint');
const environmentUpload=document.getElementById('environment-upload');
const environmentURLs=new Map();
const allocatedEnvironmentURLs=new Set();
let customEnvironment=null;
let transparentCapture=false;
let environmentUploadRevision=0;

function currentEnvironment(){
  const key=lightChoice.value;
  if(key==='custom')return customEnvironment;
  return environmentPresets[key]||null;
}
function environmentURL(key){
  if(key==='neutral')return 'neutral';
  if(key==='custom')return customEnvironment.url;
  if(!lightmaps[key].startsWith('data:'))return lightmaps[key];
  if(!environmentURLs.has(key)){
    const binary=atob(lightmaps[key].split(',')[1]);
    const bytes=Uint8Array.from(binary,c=>c.charCodeAt(0));
    const url=URL.createObjectURL(new Blob([bytes],{type:'application/octet-stream'}));
    allocatedEnvironmentURLs.add(url);
    environmentURLs.set(key,url+'#.hdr');
  }
  return environmentURLs.get(key);
}
function backgroundURL(key){
  if(key==='custom')return customEnvironment.url;
  if(!backgrounds[key].startsWith('data:'))return backgrounds[key];
  const cacheKey=key+'-background';
  if(!environmentURLs.has(cacheKey)){
    const binary=atob(backgrounds[key].split(',')[1]);
    const bytes=Uint8Array.from(binary,c=>c.charCodeAt(0));
    const url=URL.createObjectURL(new Blob([bytes],{type:'image/jpeg'}));
    allocatedEnvironmentURLs.add(url);
    environmentURLs.set(cacheKey,url+'#.jpg');
  }
  return environmentURLs.get(cacheKey);
}
function syncEnvironmentBackground(){
  const photo=currentEnvironment();
  showSurroundings.disabled=!photo;
  v.skyboxImage=photo&&showSurroundings.checked&&!transparentCapture?backgroundURL(lightChoice.value):null;
  environmentHint.textContent=photo
    ?(showSurroundings.checked?'360° surroundings and reflections.':'Reflections only. Turn on the surroundings to see the scene.')
    :'Studio lighting with a plain background.';
}
async function applyEnvironment(){
  const key=lightChoice.value;
  try{
    const label=currentEnvironment()?.label||(key==='neutral'?'Studio · Soft ambient':key+' softbox'+(key==='1'?'':'es'));
    s.textContent='Loading '+label+'…';
    v.environmentImage=environmentURL(key);
    syncEnvironmentBackground();
    await v.updateComplete;
  }catch(error){
    lightChoice.value='neutral';v.environmentImage='neutral';syncEnvironmentBackground();
    s.textContent='Could not load that environment. Studio lighting restored.';
  }
}
lightChoice.onchange=()=>{environmentUploadRevision++;return applyEnvironment()};
showSurroundings.onchange=()=>{
  syncEnvironmentBackground();
  s.textContent=showSurroundings.checked?'Surroundings shown. Drag the disc to explore the reflections.':'Surroundings hidden. Environment reflections stay active.';
};
v.addEventListener('environment-change',()=>{
  const key=lightChoice.value;
  const label=currentEnvironment()?.label||(key==='neutral'?'Studio lighting':key+' softbox'+(key==='1'?'':'es'));
  s.textContent=label+' selected. Reflections change as you rotate the disc.';
});
environmentUpload.onchange=async event=>{
  const file=event.target.files[0];if(!file)return;
  const revision=++environmentUploadRevision;
  let url;
  try{
    const hdr=/\.hdr$/i.test(file.name);
    if(!hdr&&!/\.(jpe?g|png)$/i.test(file.name))throw new Error('Choose an HDR, JPG or PNG panorama.');
    if(hdr){
      const signature=new TextDecoder().decode(await file.slice(0,16).arrayBuffer());
      if(revision!==environmentUploadRevision)return;
      if(!signature.startsWith('#?RADIANCE')&&!signature.startsWith('#?RGBE'))throw new Error('This file is not a Radiance HDR image.');
    }
    url=URL.createObjectURL(file);
    if(!hdr){
      const dimensions=await new Promise((resolve,reject)=>{
        const img=new Image();img.onload=()=>resolve([img.naturalWidth||img.width,img.naturalHeight||img.height]);
        img.onerror=()=>reject(new Error('This image could not be opened.'));img.src=url;
      });
      if(revision!==environmentUploadRevision){URL.revokeObjectURL(url);return;}
      if(Math.abs(dimensions[0]/dimensions[1]-2)>.12)throw new Error('Use a full 360° panorama, about twice as wide as it is tall.');
    }
    allocatedEnvironmentURLs.add(url);
    customEnvironment={label:file.name,url:url+(hdr?'#.hdr':/\.png$/i.test(file.name)?'#.png':'#.jpg')};
    const option=document.getElementById('custom-environment');option.hidden=false;option.disabled=false;option.textContent='Your panorama · '+file.name;
    lightChoice.value='custom';await applyEnvironment();
  }catch(error){
    if(url&&!allocatedEnvironmentURLs.has(url))URL.revokeObjectURL(url);
    s.textContent=error.message;
  }finally{environmentUpload.value='';}
};
// Keep embedded maps available when revisiting presets; release them with the page.
globalThis.addEventListener?.('pagehide',()=>{for(const url of allocatedEnvironmentURLs)URL.revokeObjectURL(url)});
