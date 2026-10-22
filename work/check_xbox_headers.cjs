const fs=require('fs'),vm=require('vm'),assert=require('assert');
const headerSource=fs.readFileSync('work/xbox360_headers.js','utf8').replace('XBOX_HEADERS',JSON.stringify(Object.fromEntries(['classic','live-classic','live-wordmark','no-live','live-wide','live-split','kinect','green-waves'].map(key=>[key,{url:key,cut:374}])))).replace('XBOX_DEFAULT_ART',JSON.stringify('default-art'));
const draws=[];const selected={value:'none'};const textures=new WeakMap();
const original={id:'original'};const mat={name:'TOP_ART_REPLACE_THIS_TEXTURE',pbrMetallicRoughness:{baseColorTexture:{texture:original}}};
const context=vm.createContext({console,Math,WeakMap,Promise,Image:class{},systemState:{xbox360:{}},document:{getElementById:()=>selected,createElement:()=>({getContext:()=>({drawImage:(...args)=>draws.push(args),save(){},beginPath(){},arc(){},clip(){},restore(){}}),toDataURL:()=> 'composite-png'})},artTextures:textures,activeSystem:'xbox360',artURL:null,v:{model:{materials:[mat]},createTexture:async url=>({url})},s:{},updateArtwork(){}});
vm.runInContext(headerSource,context);
vm.runInContext("readArtworkImage=async url=>({url,width:1440,height:1440})",context);
const pack=fs.readFileSync('work/package.py','utf8');const apply=pack.match(/async function applyArt\(\)\{[\s\S]*?\n\}/)[0];vm.runInContext(apply,context);
context.requestArtworkUpdate=()=>vm.runInContext('applyArt()',context);
(async()=>{
 for(const key of ['classic','live-classic','live-wordmark','no-live','live-wide','live-split','kinect','green-waves']){
  draws.length=0;selected.value=key;await selected.onchange();
  assert.equal(draws.length,2);assert.equal(draws[1][0].url,key);assert(draws[1][4]<=375);assert.equal(textures.get(mat).url,'composite-png');
 }
 context.artURL='uploaded-art';draws.length=0;await vm.runInContext('applyArt()',context);assert.equal(draws[0][0].url,'uploaded-art');
 selected.value='none';await selected.onchange();assert.equal(textures.get(mat).url,'uploaded-art');
 context.artURL=null;await vm.runInContext('applyArt()',context);assert.strictEqual(textures.get(mat),original);
 assert.equal(vm.runInContext('systemState.xbox360.header',context),'none');
 console.log('Verified all 8 PSD headers, upload composition, header removal and original texture restoration.');
})().catch(error=>{console.error(error);process.exitCode=1});
