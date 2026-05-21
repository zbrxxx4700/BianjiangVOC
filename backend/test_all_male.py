"""
测试所有 edge-tts 中文男声 → RVC 转换效果
"""
import os, sys, asyncio, tempfile
RVC_ROOT = r"D:\Software\RVC20240604-AMD"
os.chdir(RVC_ROOT)
sys.path.insert(0, RVC_ROOT)
import zluda
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(RVC_ROOT, '.env'), encoding='utf-8', override=True)
import warnings; warnings.filterwarnings('ignore')
import edge_tts, soundfile as sf, librosa
from configs.config import Config
from infer.modules.vc.modules import VC

MODEL = "BianjiangRVC_V2_e23_s1288.pth"
IDX = r"D:\Software\RVC20240604-AMD\logs\BianjiangRVC_V2\added_IVF634_Flat_nprobe_1_BianjiangRVC_V2_v2.index"
OUT = r"D:\Study\agent\BianjiangVOC\backend\test_output"
TEXT = "你好，我是边江，很高兴认识你。"

MALE_VOICES = [
    ("Yunjian", "zh-CN-YunjianNeural"),
    ("Yunxi", "zh-CN-YunxiNeural"),
    ("Yunxia", "zh-CN-YunxiaNeural"),
    ("Yunyang", "zh-CN-YunyangNeural"),
    ("YunJhe_TW", "zh-TW-YunJheNeural"),
]

async def gen_tts(voice, label):
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    p = tmp.name; tmp.close()
    await edge_tts.Communicate(TEXT, voice).save(p)
    # 转真 WAV
    a, sr = librosa.load(p, sr=None)
    fixed = os.path.join(OUT, f"raw_{label}.wav")
    sf.write(fixed, a, sr, format="WAV", subtype="PCM_16")
    os.unlink(p)
    return fixed

async def main():
    print("="*60)
    print("edge-tts 所有中文男声 → RVC 测试")
    print("="*60)
    
    config = Config()
    print(f"设备: {config.device}")
    vc = VC(config)
    vc.get_vc(MODEL)
    
    for label, voice in MALE_VOICES:
        print(f"\n--- {label} ({voice}) ---")
        raw = await gen_tts(voice, label)
        print(f"  原始: {raw}")
        
        info, r = vc.vc_single(0, raw, 0, None, "pm", IDX, "", 0.75, 3, 0, 0.25, 0.33)
        sr, audio = r
        out = os.path.join(OUT, f"test_{label}_rvc.wav")
        sf.write(out, audio, sr)
        lines = info.split(chr(10))
        print(f"  {lines[0]}")
        print(f"  输出: {out} ({len(audio)/sr:.1f}s)")
    
    print(f"\n{'='*60}")
    print("全部完成! 输出文件:")
    for f in sorted(os.listdir(OUT)):
        if f.endswith(".wav") and ("raw_" in f or "test_" in f):
            sz = os.path.getsize(os.path.join(OUT, f)) / 1024
            print(f"  {f} ({sz:.0f} KB)")

asyncio.run(main())
