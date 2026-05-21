"""
阶段 0 — 链路验证测试 v2
直接用 rtrvc.RVC 类，对比 ZLUDA vs CPU 推理结果
"""

import os
import sys
import asyncio
import tempfile

# 切到 RVC 仓库
RVC_ROOT = r"D:\Software\RVC20240604-AMD"
os.chdir(RVC_ROOT)
sys.path.insert(0, RVC_ROOT)

# ZLUDA 可选：通过环境变量控制
USE_ZLUDA = os.environ.get("USE_ZLUDA", "1") == "1"
if USE_ZLUDA:
    import zluda  # noqa: F401

from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(RVC_ROOT, '.env'), encoding='utf-8', override=True)

import warnings
warnings.filterwarnings("ignore")

import numpy as np
import soundfile as sf
import edge_tts
import torch
import traceback

# 配置
MODEL_NAME = "BianjiangRVC_V2_e23_s1288.pth"
MODEL_PATH = rf"{RVC_ROOT}\assets\weights\{MODEL_NAME}"
INDEX_PATH = (
    rf"{RVC_ROOT}\logs\BianjiangRVC_V2"
    r"\added_IVF634_Flat_nprobe_1_BianjiangRVC_V2_v2.index"
)
OUTPUT_DIR = r"D:\Study\agent\BianjiangVOC\backend\test_output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

TEXT = "你好，我是边江，很高兴认识你。"


async def generate_tts(text) -> str:
    """edge-tts 生成临时音频"""
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    path = tmp.name
    tmp.close()
    await edge_tts.Communicate(text, "zh-CN-XiaoxiaoNeural").save(path)
    return path


def test_on_device(device_name: str, device: torch.device):
    """在指定设备上跑一次 RVC 推理"""
    print(f"\n{'='*50}")
    print(f"  [{device_name}] 设备: {device}")
    print(f"{'='*50}")

    from configs.config import Config
    from infer.lib.audio import load_audio
    from infer.lib.rtrvc import RVC
    from multiprocessing import Manager

    mm = Manager()
    inp_q = mm.Queue()
    opt_q = mm.Queue()

    # 创建 Config 但手动覆盖设备
    config = Config()
    config.device = device
    config.is_half = False

    print(f"  加载模型: {MODEL_PATH}")
    print(f"  加载索引: {INDEX_PATH}")

    rvc = RVC(
        key=0,              # f0_up_key
        formant=0,          # formant_shift
        pth_path=MODEL_PATH,
        index_path=INDEX_PATH,
        index_rate=0.75,
        n_cpu=4,
        inp_q=inp_q,
        opt_q=opt_q,
        config=config,
    )

    # 生成 TTS 音频
    tts_path = asyncio.run(generate_tts(TEXT))
    print(f"  输入音频: {tts_path}")

    # 加载音频（16000 Hz）
    audio = load_audio(tts_path, 16000)
    audio_t = torch.from_numpy(audio).to(device)

    # 推理参数
    block_frame = 160 * 3  # 跟 pipeline 默认一致
    skip_head = 160 * 1
    return_length = audio.shape[0] // 160 * 160
    f0_method = "pm"

    print(f"  音频长度: {audio.shape[0]} samples ({audio.shape[0]/16000:.1f}s)")
    print(f"  推理中...")

    try:
        out_audio = rvc.infer(audio_t, block_frame, skip_head, return_length, f0_method)
        out_audio = out_audio.cpu().numpy()

        out_path = os.path.join(OUTPUT_DIR, f"test_{device_name}.wav")
        sf.write(out_path, out_audio, rvc.tgt_sr)
        print(f"  输出: {out_path} ({len(out_audio)/rvc.tgt_sr:.1f}s, {rvc.tgt_sr}Hz)")
    except Exception as e:
        print(f"  错误: {e}")
        traceback.print_exc()
    finally:
        os.unlink(tts_path)


if __name__ == "__main__":
    print("=" * 60)
    print("边江 TTS 链路测试 v2 — 设备对比")
    print("=" * 60)

    # 先试 ZLUDA (CUDA)
    if USE_ZLUDA and torch.cuda.is_available():
        test_on_device("zluda_cuda", torch.device("cuda:0"))
    else:
        print("\nZLUDA 不可用或已禁用")

    # 再试 CPU（作为参照）
    test_on_device("cpu", torch.device("cpu"))

    print(f"\n输出目录: {OUTPUT_DIR}")
    for f in sorted(os.listdir(OUTPUT_DIR)):
        if f.endswith(".wav"):
            sz = os.path.getsize(os.path.join(OUTPUT_DIR, f)) / 1024
            print(f"  {f} ({sz:.1f} KB)")
