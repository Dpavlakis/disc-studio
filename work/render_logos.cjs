const fs=require('fs');
const path=require('path');
const sharp=require('sharp');
async function main(){
 const dir=path.resolve(__dirname,'../outputs/branding-source');fs.mkdirSync(dir,{recursive:true});
 for(const [file,name,width,color] of [['PlayStation_logo.svg','ps-logo',1600,'#a1a6b7'],['PlayStation_2_wordmark.svg','ps2-wordmark',1800,'#a1a6b7'],['PlayStation_2_wordmark.svg','ps2-top-wordmark',3000,'#ffffff']]){
  const original=fs.readFileSync(path.join(dir,file),'utf8');
  // Keep supplied path geometry; use a single etching color and the viewBox aspect ratio.
  const svg=original.replace(/\swidth="[^"]*"/g,'').replace(/\sheight="[^"]*"/g,'').replace(/currentColor/g,color).replace('</svg>','<style>path{fill:'+color+' !important}</style></svg>');
  await sharp(Buffer.from(svg),{density:300}).resize({width}).png().toFile(path.resolve(__dirname,name+'.png'));
 }
}
main().catch(e=>{console.error(e);process.exit(1)});
