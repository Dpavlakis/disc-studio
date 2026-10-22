// Middle drag rotates the model independently of the camera and environment.
let middleDiscDrag=null;
function discRotationState(){
 return systemState[activeSystem].discRotation||(systemState[activeSystem].discRotation={roll:0,pitch:0,yaw:0});
}
function applyDiscRotation(){
 const pose=discRotationState();v.orientation=pose.roll+'deg '+pose.pitch+'deg '+pose.yaw+'deg';
}
function stopDiscDrag(event){
 if(!middleDiscDrag||event&&event.pointerId!==undefined&&event.pointerId!==middleDiscDrag.id)return;
 const drag=middleDiscDrag;middleDiscDrag=null;v.style.cursor=drag.cursor;
 if(v.hasPointerCapture?.(drag.id))v.releasePointerCapture(drag.id);
}
function resetDiscRotation(){
 stopDiscDrag();systemState[activeSystem].discRotation={roll:0,pitch:0,yaw:0};applyDiscRotation();
}
v.addEventListener('pointerdown',event=>{
 if(event.button!==1||!v.loaded)return;
 event.preventDefault();event.stopImmediatePropagation();
 middleDiscDrag={id:event.pointerId,x:event.clientX,y:event.clientY,pose:{...discRotationState()},system:activeSystem,cursor:v.style.cursor};
 v.style.cursor='grabbing';v.setPointerCapture?.(event.pointerId);
},true);
v.addEventListener('pointermove',event=>{
 const drag=middleDiscDrag;if(!drag||event.pointerId!==drag.id)return;
 event.preventDefault();event.stopImmediatePropagation();
 if(drag.system!==activeSystem){stopDiscDrag(event);return;}
 const wrap=value=>((value+180)%360+360)%360-180;
 const pose=discRotationState();pose.pitch=wrap(drag.pose.pitch+(event.clientY-drag.y)*.35);pose.yaw=wrap(drag.pose.yaw-(event.clientX-drag.x)*.35);applyDiscRotation();
},true);
for(const type of ['pointerup','pointercancel','lostpointercapture'])v.addEventListener(type,event=>{
 if(!middleDiscDrag||event.pointerId!==middleDiscDrag.id)return;
 event.preventDefault();event.stopImmediatePropagation();stopDiscDrag(event);
},true);
v.addEventListener('auxclick',event=>{if(event.button===1){event.preventDefault();event.stopImmediatePropagation()}},true);
v.addEventListener('load',()=>{stopDiscDrag();applyDiscRotation()});
