"""
CPU 推理 — 用男声 edge-tts 源
"""
import os, sys

RVC_ROOT = r"D:\Software\RVC20240604-AMD"
os.chdir(RVC_ROOT)
sys.path.insert(0, RVC_ROOT)

from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(RVC_ROOT, '.env'), encoding='utf-8', override=True)

import asyncio, tempfile
import numpy as np, soundfile as sf, edge_tts, torch

from configs.config import Config
from infer.modules.vc.modules import VC

MODEL_NAME = "BianjiangRVC_V2_e23_s1288.pth"
INDEX_PATH = r"D:\Software\RVC20240604-AMD\logs\BianjiangRVC_V2\added_IVF634_Flat_nprobe_1_BianjiangRVC_V2_v2.index"
OUT = r"D:\Study\agent\BianjiangVOC\backend\test_output"
TEXT = "你好，我是边江，很高兴认识你。"

# 试试几个男声
MALE_VOICES = [
    "zh-CN-YunjianNeural",
    "zh-CN-YunxiNeural",
    "zh-CN-YunyangNeural",
]

async def main():
    print("=" * 60)
    print("边江 TTS — CPU + 男声源测试")
    print("=" * 60)

    config = Config()
    print(f"设备: {config.device}")
    vc = VC(config)
    vc.get_vc(MODEL_NAME)
    print(f"模型: v{vc.version}, {vc.tgt_sr}Hz")

    for voice in MALE_VOICES:
        print(f"\n--- 源: {voice} ---")
        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        p = tmp.name; tmp.close()
        await edge_tts.Communicate(TEXT, voice).save(p)
        print(f"  TTS OK")

        info, r = vc.vc_single(0, p, 0, None, "pm", INDEX_PATH, "", 0.75, 3, 0, 0.25, 0.33)
        print(f"  RVC: {info.split(chr(10))[0]}")
        sr, audio = r
        out = os.path.join(OUT, f"test_{voice.split('-')[2].lower()}.wav")
        sf.write(out, audio, sr)
        print(f"  输出: {out} ({len(audio)/sr:.1f}s)")
        os.unlink(p)

    print("\n完成!")

asyncio.run(main())
