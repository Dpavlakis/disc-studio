const fs=require('fs'),path=require('path'),sharp=require('sharp');
const src=fs.readFileSync(path.resolve(__dirname,'../outputs/branding-source/xbox-flat.svg'),'utf8').replace('#187e3f','#252525');
sharp(Buffer.from(src)).resize(500,500).png().toFile(path.resolve(__dirname,'xbox-logo.png')).catch(e=>{console.error(e);process.exit(1)});
