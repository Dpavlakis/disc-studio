const fs=require('fs'),vm=require('vm'),assert=require('assert');
const html=fs.readFileSync('outputs/studio.html','utf8');
let script=html.match(/<script>([\s\S]*?)<\/script>/)[1];
script='const models='+JSON.stringify({'gamecube-disc':'GAMECUBE','ps2-blue-disc':'BLUE','ps2-silver-disc':'SILVER','ps2-gold-disc':'GOLD','ps1-black-disc':'BLACK','xbox360-test':'360','xbox-original-disc':'XBOX'})+script.slice(script.indexOf('; const v='));
const elements=new Map(),canvases=[],exportSnapshots=[];let blobCount=0;
function element(){return {style:{},disabled:false,loaded:true,value:'',checked:true,dataset:{},handlers:{},append(){},click(){},remove(){},setAttribute(k,v){this[k]=v},addEventListener(type,fn){(this.handlers[type]??=[]).push(fn)}}}
const originalTexture={id:'original'};
const textureSlot={texture:originalTexture,setTexture(t){this.texture=t}};
let badgeAlpha=1;
function pbr(){return {baseColorTexture:textureSlot,setBaseColorFactor(){},setMetallicFactor(){},setRoughnessFactor(){}}}
const top={name:'TOP_ART_REPLACE_THIS_TEXTURE',pbrMetallicRoughness:pbr(),setAlphaMode(){}};
const badge={name:'TOP_PERMANENT_PS2_BRANDING',pbrMetallicRoughness:{setBaseColorFactor(v){badgeAlpha=v[3]}},setAlphaMode(){}};
const viewer=Object.assign(element(),{model:{materials:[top,badge,{name:'PS2_DATA_REFLECTIVE',pbrMetallicRoughness:pbr()}]},updateComplete:Promise.resolve(),createTexture:async url=>({url}),exportScene:async()=>{exportSnapshots.push(textureSlot.texture);return new Blob(['glb'])},jumpCameraToGoal(){},toBlob:async()=>new Blob(['png'])});
elements.set('disc',viewer);
function canvas(){
 const c={calls:[],getContext(){return this.ctx},toDataURL(){return 'data:mock-canvas-'+canvases.indexOf(this)}};
 c.ctx={drawImage(...a){c.calls.push(['draw',...a])},translate(...a){c.calls.push(['translate',...a])},rotate(...a){c.calls.push(['rotate',...a])},save(){},restore(){},beginPath(){},arc(){},clip(){}};
 canvases.push(c);return c;
}
const doc={getElementById(id){if(!elements.has(id))elements.set(id,element());return elements.get(id)},querySelector(){return element()},querySelectorAll(){return []},createElement(tag){return tag==='canvas'?canvas():element()},head:{append(){}},body:{append(){}}};
const context=vm.createContext({document:doc,customElements:{whenDefined:()=>new Promise(()=>{})},console,URL:{createObjectURL:()=> 'blob:upload-'+(++blobCount),revokeObjectURL(){}},Image:class{constructor(){this.width=this.height=1254}set src(url){this.url=url;Promise.resolve().then(()=>this.onload())}},Blob,Uint8Array,Math,setTimeout(){},requestAnimationFrame:fn=>fn()});
vm.runInContext(script,context);vm.runInContext("chooseSystem('ps2')",context);
const run=code=>vm.runInContext(code,context);
(async()=>{
 assert(elements.get('art-angle').disabled);
 await elements.get('art').onchange({target:{files:[{}]}});
 assert(!elements.get('art-angle').disabled);assert.equal(textureSlot.texture.url,'blob:upload-1');
 await run('setArtworkAngle(-6.5)');
 assert.equal(elements.get('art-angle-number').value,'-6.5');
 const rotated=canvases.at(-1);assert.deepEqual(rotated.calls[0],['translate',1024,1024]);
 assert(Math.abs(rotated.calls[1][1]-(-6.5*Math.PI/180))<1e-10);
 assert.deepEqual(rotated.calls[2].slice(2),[-1024,-1024,2048,2048]);
 elements.get('show-branding').checked=false;elements.get('show-branding').onchange();assert.equal(badgeAlpha,0);
 run("chooseSystem('xbox')");assert.equal(elements.get('art-angle-number').value,'0');assert(elements.get('art-angle').disabled);
 await elements.get('art').onchange({target:{files:[{}]}});await elements.get('art-turn-right').onclick();assert.equal(run('systemState.xbox.artRotation'),90);
 run("chooseSystem('ps2')");assert.equal(elements.get('art-angle-number').value,'-6.5');assert.equal(elements.get('show-branding').checked,false);
 await run('requestArtworkUpdate()');assert.equal(badgeAlpha,0);
 const turn=run('setArtworkAngle(12.3)');await elements.get('export').onclick();await turn;
 assert.equal(exportSnapshots.at(-1),textureSlot.texture);assert(textureSlot.texture.url.startsWith('data:mock-canvas-'));
 await elements.get('art-angle-reset').onclick();assert.equal(textureSlot.texture.url,'blob:upload-1');
 elements.get('show-branding').checked=true;elements.get('show-branding').onchange();assert.equal(badgeAlpha,1);
 elements.get('show-art').checked=false;elements.get('show-art').onchange();assert.equal(badgeAlpha,0);
 elements.get('show-art').checked=true;elements.get('show-art').onchange();assert.equal(badgeAlpha,1);
 run("chooseSystem('xbox360')");await elements.get('art').onchange({target:{files:[{}]}});
 run("systemState.xbox360.header='classic'");canvases.length=0;await run('setArtworkAngle(17)');
 assert.equal(canvases.length,2);assert(canvases[0].calls.some(c=>c[0]==='rotate'));
 assert(!canvases[1].calls.some(c=>c[0]==='rotate'));assert.equal(canvases[1].calls.filter(c=>c[0]==='draw').length,2);
 // Force older asynchronous rotation to finish last; it must not replace the latest image.
 run("chooseSystem('ps2')");const waiting=[];
 viewer.createTexture=url=>new Promise(resolve=>waiting.push(()=>resolve({url})));
 const old=run('setArtworkAngle(21)');await new Promise(resolve=>setImmediate(resolve));
 const latest=run('setArtworkAngle(22)');await new Promise(resolve=>setImmediate(resolve));
 assert.equal(waiting.length,2);waiting[1]();await latest;const expected=textureSlot.texture;
 waiting[0]();await old;assert.strictEqual(textureSlot.texture,expected);
 assert(elements.get('status').textContent.includes('22°'));
 console.log('Verified centered rotation, 0.1° controls, reset, per-console memory, fixed headers, branding visibility, export waiting and stale-update protection.');
})().catch(error=>{console.error(error);process.exitCode=1});
