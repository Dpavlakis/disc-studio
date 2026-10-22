const fs=require('fs'),vm=require('vm'),assert=require('assert');
const elements=new Map();
const document={getElementById(id){if(!elements.has(id))elements.set(id,{});return elements.get(id)}};
const slot=texture=>({texture,setTexture(value){this.texture=value}});
function material(name){return {name,normalTexture:slot({name:'ink-normal'}),anisotropyStrength:.18,
 setAnisotropyStrength(value){this.anisotropyStrength=value},pbrMetallicRoughness:{
 baseColorTexture:slot({name:'unchanged-art'}),metallicRoughnessTexture:slot({name:'ink-roughness'}),
 setRoughnessFactor(value){this.roughnessFactor=value}}}}
const top=material('TOP_ART_REPLACE_THIS_TEXTURE'),badge=material('TOP_PERMANENT_PS2_BRANDING');
const optical=material('PS2_DATA_REFLECTIVE');
const viewer={model:{materials:[top,badge,optical]}};
const context=vm.createContext({document,v:viewer,activeSystem:'ps2',systemState:{ps2:{},ps4:{}},s:{}});
vm.runInContext(fs.readFileSync('work/artwork_controls.js','utf8'),context);
const run=code=>vm.runInContext(code,context);
run('requestLiveArtworkUpdate=async()=>{}');
const toggle=document.getElementById('print-texture');
const normals=[top.normalTexture.texture,badge.normalTexture.texture];
const rough=[top.pbrMetallicRoughness.metallicRoughnessTexture.texture,badge.pbrMetallicRoughness.metallicRoughnessTexture.texture];
const art=top.pbrMetallicRoughness.baseColorTexture.texture;
run('syncArtworkControls();applyPrintTexture()');assert(toggle.checked);
for(let repeat=0;repeat<3;repeat++){
 toggle.checked=false;toggle.onchange();
 for(const [i,m] of [top,badge].entries()){
  assert.equal(m.normalTexture.texture,null);assert.equal(m.pbrMetallicRoughness.metallicRoughnessTexture.texture,null);
  assert.equal(m.anisotropyStrength,0);assert.equal(m.pbrMetallicRoughness.roughnessFactor,i===0?.36:.38);
 }
 // Another artwork update must keep the user's off setting.
 run('applyPrintTexture()');assert.equal(top.normalTexture.texture,null);
 toggle.checked=true;toggle.onchange();
 for(const [i,m] of [top,badge].entries()){
  assert.strictEqual(m.normalTexture.texture,normals[i]);assert.strictEqual(m.pbrMetallicRoughness.metallicRoughnessTexture.texture,rough[i]);
  assert.equal(m.anisotropyStrength,.18);assert.equal(m.pbrMetallicRoughness.roughnessFactor,.52);
 }
}
assert.strictEqual(top.pbrMetallicRoughness.baseColorTexture.texture,art);
assert.equal(optical.normalTexture.texture.name,'ink-normal');assert.equal(optical.anisotropyStrength,.18);
toggle.checked=false;toggle.onchange();
run("activeSystem='ps4';syncArtworkControls();applyPrintTexture()");assert(toggle.checked);
const replacement=material('TOP_ART_REPLACE_THIS_TEXTURE');viewer.model={materials:[replacement]};
run("activeSystem='ps2';syncArtworkControls();applyPrintTexture()");assert(!toggle.checked);assert.equal(replacement.normalTexture.texture,null);
toggle.checked=true;toggle.onchange();assert.equal(replacement.normalTexture.texture.name,'ink-normal');
// Intensity remembers a separate value per console and zero removes relief.
const intensity=document.getElementById('print-intensity');
intensity.value='0';intensity.oninput();assert.equal(replacement.normalTexture.texture,null);
assert.equal(document.getElementById('print-intensity-value').textContent,'0%');
intensity.value='200';intensity.oninput();assert.equal(replacement.normalTexture.texture.name,'ink-normal');
run("activeSystem='ps4';syncArtworkControls()");assert.equal(intensity.value,'75');
run("activeSystem='ps2';syncArtworkControls()");assert.equal(intensity.value,'200');
// The visible ink layer uses dots, changes contrast on both light/dark ink,
// and clips to the source alpha rather than filling transparent cutouts.
const tileOps=[];
document.createElement=()=>({getContext:()=>({set fillStyle(v){tileOps.push(v)},beginPath(){},arc(){},fill(){}})});
const paintOps=[];const drawing={save(){},restore(){},scale(){},createPattern(){return 'dots'},fillRect(){paintOps.push(this.globalCompositeOperation)}};
context.drawing=drawing;
run('drawPrintedDots(drawing,4096)');assert.deepEqual(paintOps,['source-atop']);
assert(tileOps.includes('rgba(0,0,0,0.24)'));assert(tileOps.includes('rgba(255,255,255,0.18)'));
intensity.value='0';intensity.oninput();run('drawPrintedDots(drawing,4096)');assert.equal(paintOps.length,1);
console.log('Verified print texture toggle, intensity 0/200%, per-console memory, source-atop dot layer, source art retention, model reloads and untouched optical surfaces.');
