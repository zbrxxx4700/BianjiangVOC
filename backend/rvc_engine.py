import os,sys,tempfile,logging,threading,yaml,librosa,soundfile as sf,asyncio,edge_tts
logger=logging.getLogger("rvc")
class R:
 def __init__(self,cfg):
  with open(cfg,encoding="utf-8")as f:self._c=yaml.safe_load(f)
  self._r=self._c["rvc_root"];os.chdir(self._r)
  if self._r not in sys.path:sys.path.insert(0,self._r)
  import zluda;from dotenv import load_dotenv
  load_dotenv(dotenv_path=os.path.join(self._r,".env"),override=True)
  self._v=None;self._g=None;self._s=None;self._m=None;self._l=threading.Lock();self._ld=False
  self._lm(self._c.get("model_name",""))
 def _lm(self,n):
  from configs.config import Config;from infer.modules.vc.modules import VC
  self._g=Config();self._v=VC(self._g);self._v.get_vc(n);self._s=self._v.tgt_sr;self._m=n;self._ld=True
 def list(self):
  w=self._c["weights_dir"];m=[]
  if os.path.exists(w):
   for f in sorted(os.listdir(w)):
    if f.endswith(".pth"):p=os.path.join(w,f);m.append({"name":f,"size_mb":round(os.path.getsize(p)/1024/1024,1),"current":f==self._m})
  return m
 @property
 def ready(self):return self._ld
 @property
 def info(self):return{"model":self._m,"sr":self._s,"device":str(self._g.device)}
 @property
 def voices(self):return self._c.get("source_voices",["zh-CN-YunxiNeural"])
 async def synth(self,t,v=None,k=None,mo=None):
  if v is None:v=self._c.get("default_voice","zh-CN-YunxiNeural")
  if k is None:k=self._c.get("f0_up_key",0)
  if mo is None:mo=self._m
  if mo!=self._m:
   with self._l:self._lm(mo)
  raw=await self._tts_edge(t,v)
  try:
   w=self._wav(raw)
   with self._l:i,r=self._v.vc_single(0,w,k,None,self._c.get("f0_method","pm"),self._c["index_path"],"",self._c.get("index_rate",.75),self._c.get("filter_radius",3),0,self._c.get("rms_mix_rate",.25),self._c.get("protect",.33))
  finally:
   for p in[raw,w]:os.unlink(p)
  return r
 async def _tts_edge(self,t,v):
  tp=tempfile.NamedTemporaryFile(suffix=".wav",delete=False);p=tp.name;tp.close()
  await edge_tts.Communicate(t,v).save(p)
  sz=os.path.getsize(p)
  if sz<100:raise Exception(f"TTS empty:{sz}")
  return p
 def _wav(self,m):
  a,s=librosa.load(m,sr=None)
  t=tempfile.NamedTemporaryFile(suffix=".wav",delete=False);o=t.name;t.close()
  sf.write(o,a,s,format="WAV",subtype="PCM_16");return o
