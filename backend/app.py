import os,sys,io,logging,yaml,uvicorn,soundfile as sf
from fastapi import FastAPI,HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
BD=os.path.dirname(os.path.abspath(__file__))
if BD not in sys.path:sys.path.insert(0,BD)
from rvc_engine import R
CP=os.path.join(BD,"config.yaml")
with open(CP,encoding="utf-8")as f:CFG=yaml.safe_load(f)
logging.basicConfig(level=logging.INFO)
logger=logging.getLogger("app")
eng=R(CP)
app=FastAPI(title="BianjiangRVC")
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_methods=["*"],allow_headers=["*"])

class Req(BaseModel):text:str;voice:str=None;f0_up_key:int=None;model:str=None

@app.get("/health")
async def health():
 if not eng.ready:raise HTTPException(503,"compiling")
 return{"status":"ok","model_loaded":True,"model":eng.info,"available_models":[m["name"] for m in eng.list()],"available_voices":eng.voices}

@app.get("/models")
async def models():return{"models":eng.list()}

@app.post("/synthesize")
async def synth(req:Req):
 if not eng.ready:raise HTTPException(503,"model still loading, please wait")
 if not req.text:raise HTTPException(400,"text required")
 try:sr,audio=await eng.synth(req.text,req.voice,req.f0_up_key,req.model)
 except Exception as e:logger.error(f"fail:{e}",exc_info=True);raise HTTPException(500,str(e))
 import numpy as np
 if audio.ndim==1:audio=np.expand_dims(audio,-1)
 buf=io.BytesIO();sf.write(buf,audio,sr,format="WAV",subtype="PCM_16");buf.seek(0)
 return Response(content=buf.read(),media_type="audio/wav")

@app.post("/shutdown")
async def shutdown():
 logger.info("shutdown requested")
 os._exit(0)

if __name__=="__main__":uvicorn.run(app,host=CFG.get("host","0.0.0.0"),port=CFG.get("port",8765))
