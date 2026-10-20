const fs=require('fs'),vm=require('vm'),assert=require('assert');
const html=fs.readFileSync('outputs/disc-preview.html','utf8');let script=html.match(/<script>([\s\S]*?)<\/script>/)[1];
const end=script.indexOf('; const v=');script='const models='+JSON.stringify({'ps2-blue-disc':'BLUE','ps2-silver-disc':'SILVER','ps2-gold-disc':'GOLD','ps1-black-disc':'BLACK','xbox360-silver-disc':'XBOX'})+script.slice(end);
const elements=new Map();function element(){return {style:{},disabled:false,loaded:true,value:'',checked:true,append(){},setAttribute(k,v){this[k]=v},addEventListener(){}}}
const sections=['ps1','ps2','xbox360'].map(system=>Object.assign(element(),{dataset:{system}}));
const finishes=[['ps2','ps2-blue-disc'],['ps2','ps2-silver-disc'],['ps2','ps2-gold-disc'],['ps1','ps1-black-disc'],['xbox360','xbox360-silver-disc']].map(([platform,finish])=>Object.assign(element(),{dataset:{platform,finish}}));
const doc={getElementById(id){if(!elements.has(id))elements.set(id,element());return elements.get(id)},querySelector(){return element()},querySelectorAll(s){return s==='[data-system]'?sections:finishes},createElement:element,head:{append(){}},body:{append(){}}};
const context=vm.createContext({document:doc,customElements:{whenDefined:()=>new Promise(()=>{})},console,URL:{},setTimeout,Blob,Uint8Array,Math});vm.runInContext(script,context);
for(const [system,expected] of [['xbox360','XBOX'],['ps1','BLACK'],['ps2','BLUE']]){
 vm.runInContext(`chooseSystem('${system}')`,context);assert(elements.get('disc').src.endsWith(expected));assert(!elements.get('export').disabled);assert(!elements.get('art').disabled);
 for(const button of finishes)assert.strictEqual(button.hidden,button.dataset.platform!==system);
}
vm.runInContext("systemState.xbox360.art='blob:test-xbox';chooseSystem('xbox360')",context);assert.strictEqual(vm.runInContext('artURL',context),'blob:test-xbox');
console.log('Console controls checked: Xbox/PS1/PS2 model selection, finish filtering, artwork memory and export availability');
