var B="http://localhost:8765"
function $(id){return document.getElementById(id)}
var sDot=$("sDot"),sTxt=$("sTxt")
var en=$("enabledToggle"),ar=$("autoReadToggle")
var ms=$("modelSelect"),vs=$("voiceSelect")
var ps=$("pitchSlider"),pv=$("pitchVal")
var dl=$("downloadBtn")

try{chrome.storage.sync.get(["enabled","model","voice","f0UpKey"],function(i){
if(i.enabled!==undefined)en.checked=i.enabled
if(i.model)ms.value=i.model
if(i.voice)vs.value=i.voice
if(i.f0UpKey!==undefined){ps.value=i.f0UpKey;pv.textContent=i.f0UpKey}
})}catch(e){}

function save(){try{chrome.storage.sync.set({enabled:en.checked,model:ms.value,voice:vs.value,f0UpKey:parseInt(ps.value)})}catch(e){}}
en.onchange=save;ms.onchange=save;vs.onchange=save
ps.oninput=function(){pv.textContent=ps.value;save()}

async function check(){
 try{
  var r=await fetch(B+"/models")
  if(!r.ok)throw Error("http "+r.status)
  var d=await r.json()
  var cur=ms.value
  ms.innerHTML=""
  d.models.forEach(function(m){
   var o=document.createElement("option");o.value=m.name
   var lbl=m.name
   if(m.current)lbl+=" [C]"
   o.textContent=lbl;ms.appendChild(o)
  })
  if(cur)ms.value=cur
  sDot.className="dot on";sTxt.textContent="Ready";sTxt.style.color="#4ade80"
 }catch(e){
  sDot.className="dot off";sTxt.textContent="Offline";sTxt.style.color="#f87171"
  ms.innerHTML="<option>Offline</option>"
 }
}

check();setInterval(check,5000)

dl.onclick=async function(){
 try{
  var t=prompt("Text to download:")
  if(!t)return
  this.textContent="DL..."
  var r=await fetch(B+"/synthesize",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({text:t,voice:vs.value,model:ms.value,f0_up_key:parseInt(ps.value)})})
  if(!r.ok)throw Error()
  var b=await r.blob();var u=URL.createObjectURL(b)
  chrome.downloads.download({url:u,filename:"bianjiang.wav",saveAs:true})
 }catch(e){alert("Fail:"+e.message)}
 this.textContent="Download"
}
