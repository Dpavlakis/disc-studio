const fs=require('fs'),vm=require('vm'),assert=require('assert');
const handlers={};let captured=null;
const v={loaded:true,style:{cursor:'grab'},cameraTarget:'0m 0m 0m',cameraOrbit:'180deg 90deg .23m',environmentImage:'office.hdr',skyboxImage:'office.hdr',orientation:'0deg 0deg 0deg',addEventListener(k,f){(handlers[k]??=[]).push(f)},setPointerCapture(id){captured=id},hasPointerCapture:id=>captured===id,releasePointerCapture(){captured=null}};
const state={gamecube:{},ps2:{}};const context=vm.createContext({v,systemState:state,activeSystem:'gamecube'});vm.runInContext(fs.readFileSync('work/disc_object_rotation.js','utf8'),context);
function e(button=1,x=0,y=0,id=4){return {button,clientX:x,clientY:y,pointerId:id,preventDefault(){this.prevented=true},stopImmediatePropagation(){this.stopped=true}}}
function fire(type,event){for(const f of handlers[type])f(event);return event}
for(const b of [0,2])assert(!fire('pointerdown',e(b)).prevented);
assert(fire('pointerdown',e()).prevented);fire('pointermove',e(1,100,40));assert.equal(v.orientation,'0deg 14deg -35deg');assert.equal(v.cameraTarget,'0m 0m 0m');assert.equal(v.cameraOrbit,'180deg 90deg .23m');assert.equal(v.skyboxImage,'office.hdr');assert.equal(v.environmentImage,'office.hdr');
const pose=v.orientation;fire('pointermove',e(1,500,0,9));assert.equal(v.orientation,pose);fire('pointerup',e());assert.equal(captured,null);assert.equal(v.style.cursor,'grab');
vm.runInContext("activeSystem='ps2'",context);fire('load',{});assert.equal(v.orientation,'0deg 0deg 0deg');vm.runInContext("activeSystem='gamecube'",context);fire('load',{});assert.equal(v.orientation,pose);
fire('pointerdown',e());fire('pointermove',e(1,0,10));fire('pointercancel',e());assert.equal(captured,null);vm.runInContext('resetDiscRotation()',context);assert.equal(v.orientation,'0deg 0deg 0deg');
assert(fire('auxclick',e()).prevented);v.loaded=false;assert(!fire('pointerdown',e()).prevented);
console.log('Verified middle drag rotates only the disc; camera, target and office remain fixed. Checked left/right input, console pose memory, reset and pointer cleanup.');
