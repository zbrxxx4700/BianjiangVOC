"""
阶段 0 — 链路验证测试
边江 TTS 全流程: 文本 -> edge-tts -> RVC 音色转换 -> 输出 WAV
"""

import os
import sys

RVC_ROOT = r"D:\Software\RVC20240604-AMD"
os.chdir(RVC_ROOT)
sys.path.insert(0, RVC_ROOT)

import zluda  # noqa: F401

from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(RVC_ROOT, '.env'), encoding='utf-8', override=True)

import asyncio
import tempfile
import traceback

import faiss
import numpy as np
import soundfile as sf
import edge_tts
import torch

from configs.config import Config
from infer.modules.vc.modules import VC

# ============================================================
# 配置
# ============================================================
MODEL_NAME = "BianjiangRVC_V2_e23_s1288.pth"
INDEX_PATH = (
    r"D:\Software\RVC20240604-AMD\logs\BianjiangRVC_V2"
    r"\added_IVF634_Flat_nprobe_1_BianjiangRVC_V2_v2.index"
)
OUTPUT_DIR = r"D:\Study\agent\BianjiangVOC\backend\test_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

F0_UP_KEY = 0
F0_METHOD = "pm"
INDEX_RATE = 0.75
FILTER_RADIUS = 3
RMS_MIX_RATE = 0.25
PROTECT = 0.33
RESAMPLE_SR = 0

TEST_TEXTS = [
    "你好，我是边江，很高兴认识你。",
]


async def generate_tts(text: str) -> str:
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    path = tmp.name
    tmp.close()
    await edge_tts.Communicate(text, "zh-CN-XiaoxiaoNeural").save(path)
    print(f"  [edge-tts] 生成: {path}")
    return path


def check_index():
    """检查 index 文件能否正常加载"""
    print(f"\n>>> Index 诊断 <<<")
    print(f"  路径: {INDEX_PATH}")
    print(f"  存在: {os.path.exists(INDEX_PATH)}")
    print(f"  大小: {os.path.getsize(INDEX_PATH)/1024/1024:.1f} MB")
    try:
        idx = faiss.read_index(INDEX_PATH)
        print(f"  类型: {type(idx).__name__}")
        print(f"  ntotal: {idx.ntotal}")
        print(f"  dim: {idx.d}")
        print(f"  is_trained: {idx.is_trained}")
        print(f"  >>> 加载成功! <<<")
        return True
    except Exception as e:
        print(f"  >>> 加载失败: {e} <<<")
        traceback.print_exc()
        return False


async def main():
    print("=" * 60)
    print("边江 TTS 链路测试 — index 诊断版")
    print("=" * 60)

    # 0. 直接验证 index
    index_ok = check_index()
    if not index_ok:
        print("\n!!! Index 有问题，继续但可能没检索效果 !!!")

    # 1. 环境检查
    print(f"\n[环境] CUDA: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"[环境] GPU: {torch.cuda.get_device_name(0)}")
    print(f"[环境] weight_root: {os.getenv('weight_root')}")

    # 2. 初始化 RVC
    print("\n[1/4] 初始化 RVC...")
    config = Config()
    print(f"  设备: {config.device}, 半精度: {config.is_half}")

    vc = VC(config)

    print(f"\n[2/4] 加载模型: {MODEL_NAME}")
    vc.get_vc(MODEL_NAME)
    print(f"  版本: {vc.version}, f0: {vc.if_f0}, sr: {vc.tgt_sr}")

    # 3. 推理
    print(f"\n[3/4] 推理...")
    for i, text in enumerate(TEST_TEXTS):
        print(f"\n--- #{i+1}: [{text}] ---")
        tts_path = await generate_tts(text)
        info, result = vc.vc_single(
            sid=0,
            input_audio_path=tts_path,
            f0_up_key=F0_UP_KEY,
            f0_file=None,
            f0_method=F0_METHOD,
            file_index=INDEX_PATH,
            file_index2="",
            index_rate=INDEX_RATE,
            filter_radius=FILTER_RADIUS,
            resample_sr=RESAMPLE_SR,
            rms_mix_rate=RMS_MIX_RATE,
            protect=PROTECT,
        )
        print(f"  [RVC] 结果:\n{info}")
        tgt_sr, audio_opt = result
        out = os.path.join(OUTPUT_DIR, f"test_diagnostic.wav")
        sf.write(out, audio_opt, tgt_sr)
        dur = len(audio_opt) / tgt_sr
        print(f"  [输出] {out} ({dur:.1f}s, {tgt_sr}Hz)")
        os.unlink(tts_path)

    print(f"\n[4/4] 完成!")


if __name__ == "__main__":
    asyncio.run(main())
