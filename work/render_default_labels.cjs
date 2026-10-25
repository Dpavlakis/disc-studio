const fs=require('fs'),path=require('path');
let sharp;try{sharp=require('sharp')}catch{sharp=require('C:/Users/dimit/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp')}
const root=path.resolve(__dirname,'..'),source=path.join(root,'outputs/branding-source/default-labels/templates'),output=path.join(root,'outputs/default-labels');
(async()=>{
 for(const file of fs.readdirSync(source).filter(x=>x.endsWith('.svg'))){
  // Rasterise at 8192px, then downsample to preserve partial edge coverage.
  await sharp(path.join(source,file),{density:144}).resize(4096,4096,{kernel:'lanczos3'}).png().toFile(path.join(output,file.replace('.svg','.png')));
 }
 console.log('Rendered eight 4096px antialiased cover layers from editable vectors.');
})().catch(error=>{console.error(error);process.exit(1)});
