const fs=require('fs'),vm=require('vm'),assert=require('assert'),crypto=require('crypto');
const presets=JSON.parse(fs.readFileSync('outputs/lighting/environments.json','utf8'));
const maps={};
for(const [key,preset] of Object.entries(presets)){
  const data=fs.readFileSync('outputs/lighting/'+preset.file);
  assert.equal(crypto.createHash('sha256').update(data).digest('hex'),preset.sha256);
  assert(data.subarray(0,20).toString().startsWith('#?RADIANCE'));
  assert(data.subarray(0,300).toString().includes('-Y 1024 +X 2048'));
  maps[key]='data:application/octet-stream;base64,'+Buffer.from('HDR '+key).toString('base64');
}
for(let i=1;i<=4;i++)maps[i]='data:application/octet-stream;base64,'+Buffer.from('softbox '+i).toString('base64');
const controls=new Map(),revoked=[],images=[],events={};let sequence=0;
function el(id){if(!controls.has(id))controls.set(id,{value:'',checked:false,disabled:false});return controls.get(id)}
el('lights').value='neutral';
const viewer={environmentImage:'neutral',skyboxImage:null,updateComplete:Promise.resolve(),addEventListener:(key,fn)=>events[key]=fn};
const context=vm.createContext({document:{getElementById:el},v:viewer,s:{textContent:''},console,Blob,Uint8Array,TextDecoder,
  atob:value=>Buffer.from(value,'base64').toString('binary'),
  URL:{createObjectURL:()=> 'blob:environment-'+(++sequence),revokeObjectURL:url=>revoked.push(url)},
  Image:class{set src(value){this.url=value;this.width=2048;this.height=1024;images.push(this)}}});
const source=fs.readFileSync('work/environment_controls.js','utf8').replace('LIGHTMAPS',JSON.stringify(maps)).replace('ENVIRONMENT_PRESETS',JSON.stringify(presets));
vm.runInContext(source,context);const run=code=>vm.runInContext(code,context);
async function select(key){el('lights').value=key;await el('lights').onchange()}
const upload=file=>el('environment-upload').onchange({target:{files:[file]}});
(async()=>{
  await select('neutral');assert.equal(viewer.environmentImage,'neutral');assert(el('show-surroundings').disabled);
  for(let i=1;i<=4;i++){await select(String(i));assert(viewer.environmentImage.endsWith('#.hdr'));assert.equal(viewer.skyboxImage,null)}
  for(const key of Object.keys(presets)){
    await select(key);assert(!el('show-surroundings').disabled);assert.equal(viewer.skyboxImage,null);
    el('show-surroundings').checked=true;el('show-surroundings').onchange();assert.equal(viewer.skyboxImage,viewer.environmentImage);
    el('show-surroundings').checked=false;el('show-surroundings').onchange();assert.equal(viewer.skyboxImage,null);
  }
  const count=sequence;await select('living-room');const room=viewer.environmentImage;await select('office');await select('living-room');assert.equal(viewer.environmentImage,room);assert.equal(sequence,count);assert.equal(revoked.length,0);
  el('show-surroundings').checked=true;el('show-surroundings').onchange();run('transparentCapture=true;syncEnvironmentBackground()');assert.equal(viewer.skyboxImage,null);
  run('transparentCapture=false;syncEnvironmentBackground()');assert.equal(viewer.skyboxImage,room);
  await select('neutral');assert.equal(viewer.skyboxImage,null);assert(el('show-surroundings').disabled);
  const hdr={name:'test.hdr',slice:()=>({arrayBuffer:async()=>Buffer.from('#?RADIANCE\n')})};
  await upload(hdr);assert.equal(el('lights').value,'custom');assert(viewer.environmentImage.endsWith('#.hdr'));
  const previous=viewer.environmentImage;
  await upload({name:'bad.hdr',slice:()=>({arrayBuffer:async()=>Buffer.from('not an HDR')})});assert.equal(viewer.environmentImage,previous);
  await upload({name:'unsupported.exr'});assert.equal(viewer.environmentImage,previous);
  const ldr=upload({name:'panorama.jpg'});images.at(-1).onload();await ldr;assert(viewer.environmentImage.endsWith('#.jpg'));
  const portrait=upload({name:'portrait.png'});images.at(-1).width=1000;images.at(-1).height=1500;images.at(-1).onload();await portrait;assert(viewer.environmentImage.endsWith('#.jpg'));
  const stale=upload({name:'stale.jpg'});await select('forest');images.at(-1).onload();await stale;assert.equal(el('lights').value,'forest');assert(viewer.environmentImage.endsWith('#.hdr'));
  await select('missing');assert.equal(viewer.environmentImage,'neutral');assert.equal(viewer.skyboxImage,null);
  const html=fs.readFileSync('outputs/studio.html','utf8');
  for(const key of Object.keys(presets))assert(html.includes('value="'+key+'"'));
  console.log('Verified 5 HDR files and hashes, 4 retained softboxes, reflections/backdrop separation, URL reuse, transparent capture, custom HDR/JPG validation, stale uploads and fallback.');
})().catch(error=>{console.error(error);process.exitCode=1});
