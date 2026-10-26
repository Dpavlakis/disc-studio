const fs=require('fs'),vm=require('vm'),assert=require('assert');
const html=fs.readFileSync('outputs/studio.html','utf8');
let script=html.match(/<script>([\s\S]*?)<\/script>/)[1];
script='const models='+JSON.stringify({'gamecube-disc':'GAMECUBE','ps2-blue-disc':'BLUE','ps2-silver-disc':'SILVER','ps2-gold-disc':'GOLD','ps1-black-disc':'BLACK','xbox360-test':'360','xbox-original-disc':'XBOX'})+script.slice(script.indexOf('; const v='));
const elements=new Map(),canvases=[],frames=[],exportSnapshots=[];let blobCount=0,textureUploads=0,encodedTextures=0;
function element(){return {style:{},disabled:false,loaded:true,value:'',checked:true,dataset:{},handlers:{},append(){},click(){},remove(){},setAttribute(k,v){this[k]=v},addEventListener(type,fn){(this.handlers[type]??=[]).push(fn)}}}
const textureSlot={texture:{id:'original'},setTexture(t){this.texture=t}};let badgeAlpha=1;
function pbr(){return {baseColorTexture:textureSlot,setBaseColorFactor(){},setMetallicFactor(){},setRoughnessFactor(){}}}
const top={name:'TOP_ART_REPLACE_THIS_TEXTURE',pbrMetallicRoughness:pbr(),setAlphaMode(){}};
const badge={name:'TOP_PERMANENT_PS2_BRANDING',pbrMetallicRoughness:{setBaseColorFactor(v){badgeAlpha=v[3]}},setAlphaMode(){}};
function canvas(){
 const c={calls:[],getContext(){return this.ctx},toDataURL(){throw new Error('Live rotation must not encode PNG data.')}};
 let angle=0;const stack=[];
 c.ctx={setTransform(...args){angle=0;c.transform=args},clearRect(){c.calls=[]},drawImage(...args){c.calls.push({kind:'draw',args,angle})},translate(...args){c.calls.push({kind:'translate',args})},rotate(value){angle+=value;c.calls.push({kind:'rotate',value})},save(){stack.push(angle)},restore(){angle=stack.pop()},beginPath(){},arc(){},clip(){},scale(){},fillRect(){},strokeRect(){},fillText(...args){c.calls.push({kind:'text',args})},measureText(s){return {width:s.length*15}}};
 canvases.push(c);return c;
}
const viewer=Object.assign(element(),{model:{materials:[top,badge,{name:'PS2_DATA_REFLECTIVE',pbrMetallicRoughness:pbr()}]},updateComplete:Promise.resolve(),createCanvasTexture(){return {source:{element:canvas(),update(){textureUploads++}}}},createTexture:async url=>{encodedTextures++;throw new Error('Live rotation must not reload a texture.')},exportScene:async()=>{exportSnapshots.push({texture:textureSlot.texture,angle:canvases.at(-1).calls.find(c=>c.kind==='rotate').value});return new Blob(['glb'])},jumpCameraToGoal(){},toBlob:async()=>new Blob(['png'])});
elements.set('disc',viewer);
const doc={activeElement:null,getElementById(id){if(!elements.has(id))elements.set(id,element());return elements.get(id)},querySelector(){return element()},querySelectorAll(){return []},createElement(tag){return tag==='canvas'?canvas():element()},head:{append(){}},body:{append(){}}};
const context=vm.createContext({document:doc,customElements:{whenDefined:()=>new Promise(()=>{})},console,atob:value=>Buffer.from(value,'base64').toString('binary'),URL:{createObjectURL:()=> 'blob:upload-'+(++blobCount),revokeObjectURL(){}},Image:class{constructor(){this.width=this.height=1254}set src(url){this.url=url;Promise.resolve().then(()=>this.onload())}},Blob,Uint8Array,Math,setTimeout(){},requestAnimationFrame:fn=>frames.push(fn)});
vm.runInContext(script,context);
vm.runInContext("chooseSystem('ps2')",context);
const run=code=>vm.runInContext(code,context);
const flush=()=>{const work=frames.splice(0);for(const frame of work)frame()};
const turn=async angle=>{const pending=run(`setArtworkAngle(${angle})`);flush();await pending};
const watchdog=setTimeout(()=>{console.error('Live artwork checks did not finish.');process.exit(1)},15000);
(async()=>{
 assert(elements.get('art-angle').disabled);
 await elements.get('art').onchange({target:{files:[{}]}});assert(!elements.get('art-angle').disabled);
 assert.equal(canvases.length,1);const liveTexture=textureSlot.texture;
 await turn(-6.5);assert.strictEqual(textureSlot.texture,liveTexture);
 assert.equal(canvases.length,1);assert.equal(encodedTextures,0);
 assert(Math.abs(canvases[0].calls.find(c=>c.kind==='rotate').value-(-6.5*Math.PI/180))<1e-10);
 assert.deepEqual(canvases[0].calls.find(c=>c.kind==='translate').args,[1024,1024]);
 assert.deepEqual(canvases[0].transform,[1,0,0,-1,0,2048]);
 const coverage=run('setArtworkCoverage(102.5)');flush();await coverage;
 let covered=canvases[0].calls.find(c=>c.kind==='draw').args;
 assert.equal(covered[3],2048*1.025);assert.equal(covered[1],-covered[3]/2);
 assert.equal(run('systemState.ps2.artCoverage'),102.5);
 const coverageReset=elements.get('art-coverage-reset').onclick();flush();await coverageReset;
 assert.equal(canvases[0].calls.find(c=>c.kind==='draw').args[3],2048);
 // The draw-side flip and CanvasTexture upload flip cancel exactly.
 const originalPoint=[137,421];const drawPoint=[originalPoint[0],2048-originalPoint[1]];
 assert.deepEqual([drawPoint[0],2048-drawPoint[1]],originalPoint);
 // Many drag events within one frame should paint only the latest angle.
 const before=textureUploads;const first=run('setArtworkAngle(7.5)');const second=run('setArtworkAngle(7.6)');const latest=run('setArtworkAngle(7.8)');
 assert.equal(frames.length,1);assert.equal(textureUploads,before);flush();await Promise.all([first,second,latest]);assert.equal(textureUploads,before+1);
 assert.equal(elements.get('art-angle-number').value,'7.8');
 // Numeric editing updates on input, without requiring blur or Enter.
 const number=elements.get('art-angle-number');doc.activeElement=number;number.value='8.2';const typed=number.oninput();flush();await typed;
 assert.equal(run('systemState.ps2.artRotation'),8.2);doc.activeElement=null;
 elements.get('show-branding').checked=false;elements.get('show-branding').onchange();assert.equal(badgeAlpha,0);
 run("chooseSystem('xbox')");assert(elements.get('art-angle').disabled);await elements.get('art').onchange({target:{files:[{}]}});await turn(90);
 run("chooseSystem('ps2')");assert.equal(elements.get('art-angle-number').value,'8.2');assert.equal(elements.get('show-branding').checked,false);await run('requestArtworkUpdate()');
 // Pending artwork must finish before PNG capture.
 const pending=run('setArtworkAngle(12.3)');const exporting=elements.get('download-png').onclick();
 for(let i=0;i<20;i++){await Promise.resolve();flush()}await Promise.all([pending,exporting]);
 assert(Math.abs(canvases[0].calls.find(c=>c.kind==='rotate').value-12.3*Math.PI/180)<1e-10);
 const reset=elements.get('art-angle-reset').onclick();flush();await reset;assert.equal(canvases[0].calls.find(c=>c.kind==='rotate').value,0);
 run("chooseSystem('xbox360')");await elements.get('art').onchange({target:{files:[{}]}});run("systemState.xbox360.header='classic'");await turn(17);
 const draws=canvases[0].calls.filter(c=>c.kind==='draw');assert.equal(draws.length,2);assert(Math.abs(draws[0].angle-17*Math.PI/180)<1e-10);assert.equal(draws[1].angle,0);
 // A stale source finishing last must not repaint the shared live canvas.
 const deferred=[];run("const savedReadArtworkImage=readArtworkImage;artworkImageCache.clear();readArtworkImage=url=>new Promise(resolve=>deferred.push(()=>resolve({url,width:1254,height:1254})))");context.deferred=deferred;
 run("chooseSystem('ps2');artURL=systemState.ps2.art='slow-art'");const old=run('requestArtworkUpdate()');
 run("artURL=systemState.ps2.art='latest-art'");const current=run('requestArtworkUpdate()');assert.equal(deferred.length,2);
 deferred[1]();await current;const uploaded=textureUploads;deferred[0]();await old;assert.equal(textureUploads,uploaded);
 assert.equal(canvases[0].calls.find(c=>c.kind==='draw').args[0].url,'latest-art');
 assert.equal(encodedTextures,0);assert.equal(canvases.length,1);
 run('readArtworkImage=savedReadArtworkImage');
 // A visible HDR skybox must be excluded from transparent PNGs, then restored.
 elements.get('lights').value='forest';await elements.get('lights').onchange();elements.get('show-surroundings').checked=true;elements.get('show-surroundings').onchange();
 const skybox=viewer.skyboxImage;assert(skybox);let captures=0;
 viewer.toBlob=async()=>{assert.equal(viewer.skyboxImage,null);captures++;return new Blob(['png'])};
 const png=elements.get('download-png').onclick();for(let i=0;i<20;i++){await Promise.resolve();flush()}await png;
 assert.equal(captures,1);assert.equal(viewer.skyboxImage,skybox);
 viewer.toBlob=async()=>{throw new Error('Capture failed')};const badPNG=elements.get('download-png').onclick();for(let i=0;i<20;i++){await Promise.resolve();flush()}await badPNG;assert.equal(viewer.skyboxImage,skybox);
 // PSX label construction preserves the black body and shares the live art.
 function labelMaterial(name){const slot={texture:null,setTexture(t){this.texture=t}};const p={baseColorTexture:slot,setBaseColorFactor(c){this.color=c},setMetallicFactor(v){this.metal=v},setRoughnessFactor(v){this.rough=v}};return {name,pbrMetallicRoughness:p,setAlphaMode(v){this.alpha=v}}}
 const face=labelMaterial('PS1_FRONT_MASTERING_FOIL'),centre=labelMaterial('PS1_CENTRE_PRINT');
 viewer.model={materials:[top,face,centre,{name:'BLACK_DATA_REFLECTIVE',pbrMetallicRoughness:pbr()}]};
 run("chooseSystem('ps1')");await run('requestArtworkUpdate()');
 const style=elements.get('ps1-label-style');assert.equal(style.value,'silver');assert.equal(face.pbrMetallicRoughness.metal,1);assert.equal(centre.pbrMetallicRoughness.color[3],0);
 style.value='white';style.onchange();assert.equal(face.pbrMetallicRoughness.metal,0);assert.equal(face.pbrMetallicRoughness.color[0],.9);assert.equal(centre.pbrMetallicRoughness.color[3],0);
 style.value='centre-print';style.onchange();assert.equal(centre.alpha,'MASK');assert.equal(centre.pbrMetallicRoughness.color[3],1);assert.strictEqual(centre.pbrMetallicRoughness.baseColorTexture.texture,textureSlot.texture);
 await elements.get('art').onchange({target:{files:[{}]}});await turn(17.4);assert.strictEqual(centre.pbrMetallicRoughness.baseColorTexture.texture,textureSlot.texture);
 elements.get('show-art').checked=false;elements.get('show-art').onchange();assert.equal(centre.pbrMetallicRoughness.color[3],0);elements.get('show-art').checked=true;elements.get('show-art').onchange();assert.equal(centre.pbrMetallicRoughness.color[3],1);
 run("chooseSystem('ps2');chooseSystem('ps1')");assert.equal(style.value,'centre-print');
 // GameCube starts bare, uses translucent ink over its mastering details,
 // and retains independent artwork transforms across console switches.
 let gcAlpha,gcColor;top.setAlphaMode=v=>gcAlpha=v;top.pbrMetallicRoughness.setBaseColorFactor=v=>gcColor=v;
 const gcPanel=labelMaterial('GAMECUBE_LABEL_PANEL'),gcFoil=labelMaterial('GAMECUBE_LABEL_FOIL');viewer.model.materials.push(gcPanel,gcFoil);
 run("chooseSystem('gamecube')");await run('requestArtworkUpdate()');assert.equal(gcColor[3],.94);
 await elements.get('art').onchange({target:{files:[{}]}});assert.equal(gcAlpha,'BLEND');assert.equal(gcColor[3],.94);
 const gcCoverage=run('setArtworkCoverage(103)');flush();await gcCoverage;await turn(24);
 run("chooseSystem('ps2');chooseSystem('gamecube')");assert.equal(run('systemState.gamecube.artCoverage'),103);assert.equal(run('systemState.gamecube.artRotation'),24);
 await run('requestArtworkUpdate()');assert.equal(canvases[0].calls.find(c=>c.kind==='draw').args[3],2048*1.03);
 // Hiding GameCube artwork must leave its enabled branding visible.
 elements.get('show-art').checked=false;elements.get('show-art').onchange();
 assert.equal(gcColor[3],0);assert.equal(gcPanel.pbrMetallicRoughness.color[3],1);assert.equal(gcFoil.pbrMetallicRoughness.color[3],.90);
 elements.get('gc-label-enabled').checked=false;elements.get('gc-label-enabled').oninput();await run('artworkUpdate');
 elements.get('show-art').checked=true;elements.get('show-art').onchange();
 assert.equal(gcColor[3],.94);assert.equal(gcPanel.pbrMetallicRoughness.color[3],0);assert.equal(gcFoil.pbrMetallicRoughness.color[3],0);
 elements.get('gc-label-enabled').checked=true;elements.get('gc-label-enabled').oninput();await run('artworkUpdate');
 // PS2 branding likewise remains independent from artwork visibility.
 viewer.model.materials.push(badge);
 run("chooseSystem('ps2')");elements.get('show-branding').checked=true;elements.get('show-branding').onchange();
 elements.get('show-art').checked=false;elements.get('show-art').onchange();assert.equal(badgeAlpha,1);
 elements.get('show-branding').checked=false;elements.get('show-branding').onchange();assert.equal(badgeAlpha,0);
 elements.get('show-art').checked=true;elements.get('show-art').onchange();assert.equal(badgeAlpha,0);
 run("chooseSystem('gamecube')");await run('requestArtworkUpdate()');
 // Initial baked branding stays hidden until the editable canvas and model
 // update finish; the viewer then reveals one prepared presentation.
 viewer.style.visibility='hidden';let finishUpdate;viewer.updateComplete=new Promise(resolve=>{finishUpdate=resolve});
 const initialLoads=viewer.handlers.load.map(fn=>fn({}));await new Promise(resolve=>setImmediate(resolve));assert.equal(viewer.style.visibility,'hidden');
 finishUpdate();await Promise.all(initialLoads);assert.equal(viewer.style.visibility,'visible');
 console.log('Verified live artwork, coverage, rotation, headers, PNG capture, PSX styles, GameCube branding and deferred initial reveal.');
})().catch(error=>{console.error(error);process.exitCode=1}).finally(()=>clearTimeout(watchdog));
