"""
测试不同参数对 edge-tts → RVC 转换效果的影响
"""
import os, sys
RVC_ROOT = r"D:\Software\RVC20240604-AMD"
os.chdir(RVC_ROOT)
sys.path.insert(0, RVC_ROOT)
import zluda
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(RVC_ROOT, '.env'), encoding='utf-8', override=True)
import asyncio, tempfile, warnings
warnings.filterwarnings('ignore')
import soundfile as sf, edge_tts
from configs.config import Config
from infer.modules.vc.modules import VC

MODEL = "BianjiangRVC_V2_e23_s1288.pth"
IDX = r"D:\Software\RVC20240604-AMD\logs\BianjiangRVC_V2\added_IVF634_Flat_nprobe_1_BianjiangRVC_V2_v2.index"
OUT = r"D:\Study\agent\BianjiangVOC\backend\test_output"
TEXT = "你好，我是边江，很高兴认识你。"
VOICE = "zh-CN-XiaoxiaoNeural"

# 多组参数
PARAMS = [
    ("f0+0_075idx", 0, "pm", 0.75),
    ("f0+4_075idx", 4, "pm", 0.75),  # 升调
    ("f0-4_075idx", -4, "pm", 0.75), # 降调
    ("f0+0_100idx", 0, "pm", 1.0),   # 全用 index
    ("f0+0_rmvpe", 0, "rmvpe", 0.75), # rmvpe 音高
]

async def main():
    print("="*60)
    print("edge-tts → RVC 参数测试")
    print("="*60)

    config = Config()
    print(f"设备: {config.device}")
    vc = VC(config)
    vc.get_vc(MODEL)

    # 生成一次 TTS
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    tts = tmp.name; tmp.close()
    await edge_tts.Communicate(TEXT, VOICE).save(tts)

    for name, key, method, idxr in PARAMS:
        print(f"\n--- {name} (key={key}, method={method}, idx={idxr}) ---")
        info, r = vc.vc_single(0, tts, key, None, method, IDX, "", idxr, 3, 0, 0.25, 0.33)
        sr, audio = r
        out = os.path.join(OUT, f"test_edgetts_{name}.wav")
        sf.write(out, audio, sr)
        lines = info.split(chr(10))
        print(f"  {lines[0]} | {lines[3] if len(lines)>3 else ''}")
        print(f"  输出: {out} ({len(audio)/sr:.1f}s)")

    os.unlink(tts)
    print("\n完成! 去听听哪个参数效果最好~")

asyncio.run(main())
