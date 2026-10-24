const fs=require('fs'),vm=require('vm'),assert=require('assert');
const html=fs.readFileSync('outputs/studio.html','utf8');let script=html.match(/<script>([\s\S]*?)<\/script>/)[1];
const end=script.indexOf('; const v=');script='const models='+JSON.stringify({'gamecube-disc':'GAMECUBE','ps3-silver-disc':'PS3','ps4-silver-disc':'PS4','ps2-blue-disc':'BLUE','ps2-silver-disc':'SILVER','ps2-gold-disc':'GOLD','ps1-black-disc':'BLACK','xbox360-silver-disc':'XBOX','xbox360-test':'XBOXTEST','xbox360-disc-matched':'360MATCHED','xbox-original-disc':'ORIGINAL','xbox-original-disc-matched':'MATCHED'})+script.slice(end);
const elements=new Map();function element(){return {style:{},disabled:false,loaded:true,value:'',checked:true,append(){},setAttribute(k,v){this[k]=v},addEventListener(){}}}
const sections=['ps1','ps2','ps3','ps4','xbox360','xbox','gamecube'].map(system=>Object.assign(element(),{dataset:{system}}));
const finishes=[['ps3','ps3-silver-disc'],['ps4','ps4-silver-disc'],['gamecube','gamecube-disc'],['ps2','ps2-blue-disc'],['ps2','ps2-silver-disc'],['ps2','ps2-gold-disc'],['ps1','ps1-black-disc'],['xbox360','xbox360-silver-disc'],['xbox360','xbox360-disc-matched'],['xbox','xbox-original-disc'],['xbox','xbox-original-disc-matched']].map(([platform,finish])=>Object.assign(element(),{dataset:{platform,finish}}));
const doc={getElementById(id){if(!elements.has(id))elements.set(id,element());return elements.get(id)},querySelector(){return element()},querySelectorAll(s){return s==='[data-system]'?sections:finishes},createElement:element,head:{append(){}},body:{append(){}}};
const persisted=new Map();const storage={getItem:key=>persisted.get(key)||null,setItem:(key,value)=>persisted.set(key,value)};
const context=vm.createContext({localStorage:storage,document:doc,customElements:{whenDefined:()=>new Promise(()=>{})},console,URL:{},setTimeout,Blob,Uint8Array,Math});vm.runInContext(script,context);
for(const [system,expected] of [['ps3','PS3'],['ps4','PS4'],['gamecube','GAMECUBE'],['xbox','MATCHED'],['xbox360','360MATCHED'],['ps1','BLACK'],['ps2','BLUE']]){
 vm.runInContext(`chooseSystem('${system}')`,context);assert(elements.get('disc').src.endsWith(expected));assert(!elements.get('export').disabled);assert(!elements.get('art').disabled);
 for(const button of finishes)assert.strictEqual(button.hidden,button.dataset.platform!==system);
}
vm.runInContext("systemState.xbox360.art='blob:test-xbox';chooseSystem('xbox360')",context);assert.strictEqual(vm.runInContext('artURL',context),'blob:test-xbox');
vm.runInContext("chooseSystem('xbox')",context);
const extra=finishes.find(b=>b.dataset.finish==='xbox-original-disc-matched');extra.onclick();assert(elements.get('disc').src.endsWith('MATCHED'));
vm.runInContext("chooseSystem('ps3');chooseSystem('xbox')",context);assert(elements.get('disc').src.endsWith('MATCHED'));
vm.runInContext("chooseSystem('xbox360')",context);
finishes.find(b=>b.dataset.finish==='xbox360-disc-matched').onclick();assert(elements.get('disc').src.endsWith('360MATCHED'));
vm.runInContext("chooseSystem('ps3');chooseSystem('xbox360')",context);assert(elements.get('disc').src.endsWith('360MATCHED'));
// Finish selection survives a page reload, and invalid cross-console values do not.
vm.runInContext("chooseSystem('xbox')",context);
finishes.find(b=>b.dataset.finish==='xbox-original-disc').onclick();
function reloaded(){const c=vm.createContext({localStorage:storage,document:doc,customElements:{whenDefined:()=>new Promise(()=>{})},console,URL:{},setTimeout,Blob,Uint8Array,Math});vm.runInContext(script,c);return c}
assert.equal(vm.runInContext('systemState.xbox.finish',reloaded()),'xbox-original-disc');
assert.equal(vm.runInContext('systemState.xbox360.finish',reloaded()),'xbox360-disc-matched');
storage.setItem('discStudio.finishes.v1',JSON.stringify({xbox:'ps2-gold-disc',xbox360:'missing-file'}));
assert.equal(vm.runInContext('systemState.xbox.finish',reloaded()),'xbox-original-disc-matched');
assert.equal(vm.runInContext('systemState.xbox360.finish',reloaded()),'xbox360-disc-matched');
storage.setItem('discStudio.finishes.v1','bad json');reloaded();
console.log('Console controls checked: Original Xbox/Xbox 360/PS1/PS2/PS3/PS4 model selection, finish filtering, artwork memory and export availability');
