// Keep the portable studio self-contained without parsing every raw GLB at startup.
const modelSourceCache=new Map();
let modelLoadVersion=0,modelPreparationPending=false;
async function unpackModelSource(finish){
 const value=models[finish];
 if(!value)throw new Error('The selected disc is unavailable.');
 if(!value.startsWith('gzip:')&&!value.startsWith('gzip-url:'))return 'data:model/gltf-binary;base64,'+value;
 if(!modelSourceCache.has(finish)){
  const pending=(async()=>{
   let compressed;
   if(value.startsWith('gzip-url:')){
    const response=await fetch(value.slice(9),{cache:'force-cache'});
    if(!response.ok)throw new Error('Disc download failed ('+response.status+').');
    compressed=response.body;
   }else{
    const decoded=atob(value.slice(5));const bytes=new Uint8Array(decoded.length);
    for(let i=0;i<decoded.length;i++)bytes[i]=decoded.charCodeAt(i);
    compressed=new Blob([bytes]).stream();
   }
   const stream=compressed.pipeThrough(new DecompressionStream('gzip'));
   const buffer=await new Response(stream).arrayBuffer();
   return URL.createObjectURL(new Blob([buffer],{type:'model/gltf-binary'}));
  })();
  modelSourceCache.set(finish,pending);
  pending.catch(()=>{if(modelSourceCache.get(finish)===pending)modelSourceCache.delete(finish)});
 }
 return modelSourceCache.get(finish);
}
function setDiscModel(finish){
 const version=++modelLoadVersion,value=models[finish];
 // Raw GLB payloads remain supported for older saved studios.
 if(value?.startsWith('url:')){modelPreparationPending=false;v.src=globalThis.location?new URL(value.slice(4),globalThis.location.href).href:value.slice(4);return Promise.resolve()}
 if(!value?.startsWith('gzip:')&&!value?.startsWith('gzip-url:')){modelPreparationPending=false;v.src='data:model/gltf-binary;base64,'+value;return Promise.resolve()}
 modelPreparationPending=true;v.style.visibility='hidden';
 document.getElementById('download-png').disabled=true;
 return unpackModelSource(finish).then(url=>{
  if(version!==modelLoadVersion)return;
  modelPreparationPending=false;
  if(v.src===url&&v.loaded){
   v.style.visibility='visible';document.getElementById('download-png').disabled=false;return;
  }
  v.src=url;
 }).catch(error=>{
  if(version!==modelLoadVersion)return;
  modelPreparationPending=false;s.textContent='Could not load this disc: '+error.message;
 });
}
