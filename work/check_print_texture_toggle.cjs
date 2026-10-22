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
console.log('Verified print texture off/on, exact map restoration, branding, per-console memory, model reloads, unchanged art and untouched optical surfaces.');
