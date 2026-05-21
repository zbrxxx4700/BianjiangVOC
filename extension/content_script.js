var C={backendUrl:"http://localhost:8765",enabled:true,model:null,voice:"zh-CN-YunxiNeural",f0UpKey:0,rate:1,autoRead:false,lastBlob:null}
chrome.storage.sync.get(["enabled","model","voice","f0UpKey","rate","backendUrl","autoRead"],function(i){
if(i.enabled!==undefined)C.enabled=i.enabled;if(i.model)C.model=i.model;if(i.voice)C.voice=i.voice
if(i.f0UpKey!==undefined)C.f0UpKey=i.f0UpKey;if(i.rate!==undefined)C.rate=i.rate
if(i.backendUrl)C.backendUrl=i.backendUrl;if(i.autoRead!==undefined)C.autoRead=i.autoRead})
chrome.storage.onChanged.addListener(function(c){
if(c.enabled)C.enabled=c.enabled.newValue;if(c.model)C.model=c.model.newValue
if(c.voice)C.voice=c.voice.newValue;if(c.f0UpKey)C.f0UpKey=c.f0UpKey.newValue
if(c.rate)C.rate=c.rate.newValue;if(c.backendUrl)C.backendUrl=c.backendUrl.newValue;if(c.autoRead)C.autoRead=c.autoRead.newValue})

// 创建 AudioContext 并保持引用（用于解锁音频）
var audioCtx=null
function ensureAudioCtx(){
 if(!audioCtx||audioCtx.state==="closed")audioCtx=new(window.AudioContext||window.webkitAudioContext)()
 if(audioCtx.state==="suspended")audioCtx.resume()
 return audioCtx
}

class AP{
constructor(){this.a=null;this.ac=null;this.u=null;this.s="idle";this.cb=null;this._dl=null}
get state(){return this.s}
onStateChange(f){this.cb=f}
setState(s){this.s=s;if(this.cb)this.cb(s)}
async play(t){
this.stop();this.ac=new AbortController();this.setState("playing")
try{var _r=await chrome.storage.sync.get("rate");if(_r.rate!==undefined)C.rate=_r.rate}catch(e){}

// 分句：按句号、问号、感叹号、换行分割
var sentences=t.split(/[。！？
]+/).filter(function(s){return s.trim().length>0})
if(sentences.length===0){this.setState("idle");return}

// 单句直接播
if(sentences.length===1){
 this._playOne(t);return
}

// 多句：播第一句，后台排队后续
var _this=this
this._queue=[]
this._queueIdx=0

function playNext(){
 if(!_this._queue||_this._queueIdx>=_this._queue.length){_this.setState("idle");_this.cleanup();return}
 var item=_this._queue[_this._queueIdx++]
 ensureAudioCtx()
 _this.a=new Audio(item.url);_this.u=item.url
 _this.a.playbackRate=C.rate
 _this.a.onended=function(){if(_this.s==="playing")playNext()}
 _this.a.onerror=function(){playNext()}
 _this.a.play().catch(function(){playNext()})
}

// 先播第一句
var first=sentences.shift()
try{
 var b={text:first,voice:C.voice,f0_up_key:C.f0UpKey,rate:C.rate};if(C.model)b.model=C.model
 var r=await fetch(C.backendUrl+"/synthesize",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(b),signal:this.ac.signal})
 if(!r.ok)throw Error("HTTP "+r.status)
 var blob=await r.blob();C.lastBlob=blob
 var u=URL.createObjectURL(blob)
 ensureAudioCtx()
 _this.a=new Audio(u);_this.u=u
 _this.a.playbackRate=C.rate
 _this.a.onended=function(){if(_this.s==="playing")playNext()}
 _this.a.onerror=function(){playNext()}
 try{await _this.a.play()}catch(pe){
  var src=audioCtx.createMediaElementSource(_this.a)
  src.connect(audioCtx.destination)
  await _this.a.play()
 }
 // 后台预取后续句子
 sentences.forEach(function(s){
  if(!_this.ac||_this.ac.signal.aborted)return
  var bb={text:s,voice:C.voice,f0_up_key:C.f0UpKey,rate:C.rate};if(C.model)bb.model=C.model
  fetch(C.backendUrl+"/synthesize",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(bb),signal:_this.ac.signal})
  .then(function(rr){if(!rr.ok)throw Error();return rr.blob()})
  .then(function(blb){
   var uu=URL.createObjectURL(blb)
   _this._queue.push({url:uu})
  }).catch(function(){})
 })
}catch(e){if(e.name!=="AbortError"){console.warn(e);this.setState("idle");this.cleanup()}}}

_playOne=async function(t){
try{
 var b={text:t,voice:C.voice,f0_up_key:C.f0UpKey,rate:C.rate};if(C.model)b.model=C.model
 var r=await fetch(C.backendUrl+"/synthesize",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(b),signal:this.ac.signal})
 if(!r.ok)throw Error("HTTP "+r.status)
 C.lastBlob=await r.blob()
 var u=URL.createObjectURL(C.lastBlob)
 ensureAudioCtx()
 this.a=new Audio(u);this.u=u
 var s=this
 this.a.onended=function(){s.setState("idle");s.cleanup()}
 this.a.onerror=function(){s.setState("idle");s.cleanup()}
 this.a.playbackRate=C.rate
 try{await this.a.play()}catch(pe){
  var src=audioCtx.createMediaElementSource(this.a)
  src.connect(audioCtx.destination)
  await this.a.play()
 }
}catch(e){if(e.name!=="AbortError"){console.warn(e);this.setState("idle");this.cleanup()}}}
pause(){if(this.a&&!this.a.paused){this.a.pause();this.setState("paused")}}
resume(){if(this.a&&this.a.paused&&this.a.currentTime>0){this.a.play().catch(function(){});this.setState("playing")}}
stop(){if(this.ac){this.ac.abort();this.ac=null}if(this._queue){this._queue=[];this._queueIdx=0}if(this.a){this.a.pause();this.a.onended=null;this.a.onerror=null;this.a=null}if(this.u){URL.revokeObjectURL(this.u);this.u=null}if(this.s!=="idle")this.setState("idle")}
cleanup(){if(this.u){URL.revokeObjectURL(this.u);this.u=null}this.a=null;this.ac=null}
toggle(t){if(this.s==="playing")this.pause();else if(this.s==="paused")this.resume();else this.play(t)}
download(){if(C.lastBlob){var u=URL.createObjectURL(C.lastBlob);var a=document.createElement("a");a.href=u;a.download="bianjiang.wav";a.click();setTimeout(function(){URL.revokeObjectURL(u)},1000)}}
addDl(el){var s=this;var b=document.createElement("div");b.id="bj-dl";b.innerHTML="d";
b.style.cssText="position:absolute;top:-8px;right:-8px;width:18px;height:18px;background:#4ade80;color:#1a1a2e;border-radius:50%;font-size:12px;display:none;align-items:center;justify-content:center;cursor:pointer;z-index:2147483647;box-shadow:0 1px 4px rgba(0,0,0,.3)"
b.onmousedown=function(e){e.preventDefault();e.stopPropagation();s.download()};el.appendChild(b);this._dl=b}
showDl(){if(this._dl)this._dl.style.display="flex"}
hideDl(){if(this._dl)this._dl.style.display="none"}
}

class Pop{
constructor(p){
var s=this;this.p=p;this.e=null;this.t="";this.v=false;this._t=null
var logo=chrome.runtime.getURL("Logo.png")
this.e=document.createElement("div");this.e.id="bj-pop"
var h="<div class=bx><img class=im src="+logo+"><div class=ov op></div><div class=ov pa>P</div><div class=ov ld>L</div></div>"
this.e.innerHTML=h
p.addDl(this.e)
var c=document.createElement("style")
c.textContent="#bj-pop{position:fixed;z-index:2147483647;cursor:pointer;display:none;opacity:0;transition:opacity .15s}#bj-pop.s{display:block;opacity:1}#bj-pop .bx{position:relative;width:40px;height:40px;border-radius:50%;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,.4);border:2px solid #fff;transition:all .2s}#bj-pop .bx:hover{transform:scale(1.1)}#bj-pop .im{width:100%;height:100%;object-fit:cover;display:block}#bj-pop .ov{display:none;position:absolute;inset:0;align-items:center;justify-content:center;background:rgba(0,0,0,.55);color:#fff;font-size:14px;font-weight:bold}#bj-pop:not(.pl):not(.ps) .op{display:flex}#bj-pop:not(.pl):not(.ps) .bx{border-color:#4ade80}#bj-pop.pl .ld{display:flex;animation:f1 1s infinite}#bj-pop.pl .bx{border-color:#ffd700;animation:p1 1.5s infinite}#bj-pop.pl .ld{animation:s1 .8s linear infinite}#bj-pop.ps .pa{display:flex}#bj-pop.ps .bx{border-color:#fbbf24}#bj-pop.dl #bj-dl{display:flex}@keyframes p1{0%,100%{box-shadow:0 0 0 0 rgba(255,215,0,.5)}50%{box-shadow:0 0 0 10px rgba(255,215,0,0)}}@keyframes s1{from{transform:rotate(0deg)}to{transform:rotate(360deg)}}@keyframes f1{0%,100%{opacity:.6}50%{opacity:1}}"
document.head.appendChild(c);document.body.appendChild(this.e)
this.e.onmousedown=function(e){e.preventDefault();e.stopPropagation();if(!C.enabled)return;if(!s.v)return;ensureAudioCtx();s.p.toggle(s.t)}
document.addEventListener("mouseup",function(e){if(s.e&&s.e.contains(e.target))return;clearTimeout(s._t);setTimeout(function(){s.chk()},50)})
document.addEventListener("mousedown",function(e){if(s.e&&!s.e.contains(e.target)&&s.p.state==="idle")s.hide()})
window.addEventListener("scroll",function(){if(s.v)s.pos()})
p.onStateChange(function(s2){s.upd(s2)})
}
chk(){var w=window.getSelection();var t=w?w.toString().trim():"";if(!t||t.length===0){if(this.p.state==="idle")this.hide();return}this.t=t;this.pos();this.show();if(C.autoRead){ensureAudioCtx();this.p.play(t)}}
pos(){var w=window.getSelection();if(!w||w.rangeCount===0){this.hide();return}var r=w.getRangeAt(0).getBoundingClientRect();var x=r.right+8,y=r.top-8;if(x+40>window.innerWidth)x=r.left-48;if(y<0)y=r.bottom+8;this.e.style.left=x+"px";this.e.style.top=y+"px"}
show(){this.v=true;this.e.classList.add("s");clearTimeout(this._t)}
hide(){this.v=false;this.e.classList.remove("s")}
upd(st){this.e.classList.remove("pl","ps","dl");if(st==="playing"){this.e.classList.add("pl");this.show()}else if(st==="paused"){this.e.classList.add("ps");this.show()}else{this.e.classList.add("dl");var s=this;this._t=setTimeout(function(){s.hide();s.p.hideDl()},3000);this.p.showDl()}}
}

document.addEventListener("keydown",function(e){if(!C.enabled)return;var p=window.__bjPlayer;if(!p||p.state==="idle")return;if(e.key==="Escape"){p.stop();e.preventDefault()}else if(e.code==="Space"){e.preventDefault();p.toggle(p._lastText||"")}})

function init(){var fn=function(){var p=new AP();window.__bjPlayer=p;new Pop(p)};if(document.readyState==="loading")document.addEventListener("DOMContentLoaded",fn);else fn()}
init()
