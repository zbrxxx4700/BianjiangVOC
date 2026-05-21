"""测试所有 multilingual 男声 + 所有中文男声 → RVC"""
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

VOICES = [
    # Multilingual
    ("WilliamMulti_EN_AU", "en-AU-WilliamMultilingualNeural"),
    ("AndrewMulti_EN_US", "en-US-AndrewMultilingualNeural"),
    ("BrianMulti_EN_US", "en-US-BrianMultilingualNeural"),
    ("RemyMulti_FR", "fr-FR-RemyMultilingualNeural"),
    ("FlorianMulti_DE", "de-DE-FlorianMultilingualNeural"),
    ("GiuseppeMulti_IT", "it-IT-GiuseppeMultilingualNeural"),
    ("HyunsuMulti_KO", "ko-KR-HyunsuMultilingualNeural"),
    # Chinese (already tested Yunjian/Yunxi/Yunxia/Yunyang, adding the others)
    ("WanLung_HK", "zh-HK-WanLungNeural"),
    ("YunJhe_TW", "zh-TW-YunJheNeural"),
]

async def gen_tts(voice, label):
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    p = tmp.name; tmp.close()
    await edge_tts.Communicate(TEXT, voice).save(p)
    a, sr = librosa.load(p, sr=None)
    fixed = os.path.join(OUT, "raw_" + label + ".wav")
    sf.write(fixed, a, sr, format="WAV", subtype="PCM_16")
    os.unlink(p)
    return fixed

async def main():
    print("="*60)
    print("测试所有 Multilingual + 其他中文男声")
    print("="*60)
    
    config = Config()
    print("设备: {}".format(config.device))
    vc = VC(config)
    vc.get_vc(MODEL)
    
    for label, voice in VOICES:
        print("\n--- {} ---".format(label))
        raw = await gen_tts(voice, label)
        info, r = vc.vc_single(0, raw, 0, None, "pm", IDX, "", 0.75, 3, 0, 0.25, 0.33)
        sr, audio = r
        out = os.path.join(OUT, "test_" + label + "_rvc.wav")
        sf.write(out, audio, sr)
        print("  OK -> {}".format(out))
    
    print("\n完成! 加上之前的 Yunxi 对比~")

asyncio.run(main())
