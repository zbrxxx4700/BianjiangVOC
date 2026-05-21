"""
直接用 WebUI 的 Gradio API 跑推理（绕过可能的问题）
需要先启动 WebUI：.\runtime\python.exe .\infer-web.py
"""
import os, sys, requests, json, tempfile, asyncio, edge_tts

GRADIO_URL = "http://localhost:7865"
TEXT = "你好，我是边江，很高兴认识你。"

async def main():
    # 生成 TTS 音频
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    tts_path = tmp.name
    tmp.close()
    await edge_tts.Communicate(TEXT, "zh-CN-XiaoxiaoNeural").save(tts_path)

    # 用 Gradio API 调用推理
    # 先获取当前 sid 和 spk
    sid = "BianjiangRVC_V2_e23_s1288.pth"
    
    # 1. 加载模型
    r = requests.post(f"{GRADIO_URL}/api/predict", json={
        "data": [sid, 0.5, 0.33],
        "event_data": None,
        "fn_index": 8,  # infer_change_voice api
    })
    print(f"加载模型: {r.status_code}")
    # print(r.text[:500])

    # 2. 推理
    with open(tts_path, "rb") as f:
        files = {"files": ("input.wav", f, "audio/wav")}
        # 先上传音频
        r = requests.post(f"{GRADIO_URL}/upload", files=files)
        upload_data = r.json()
        audio_path = upload_data[0] if isinstance(upload_data, list) else upload_data
        print(f"上传音频成功")

    # 3. 单次推理
    r = requests.post(f"{GRADIO_URL}/api/predict", json={
        "data": [
            0,          # spk_item (speaker id)
            audio_path, # input_audio
            0,          # f0_up_key
            None,       # f0_file
            "pm",       # f0_method
            f"D:\\Software\\RVC20240604-AMD\\logs\\BianjiangRVC_V2\\added_IVF634_Flat_nprobe_1_BianjiangRVC_V2_v2.index",  # file_index
            "",         # file_index2
            0.75,       # index_rate
            3,          # filter_radius
            0,          # resample_sr
            0.25,       # rms_mix_rate
            0.33,       # protect
        ],
        "event_data": None,
        "fn_index": 10,  # vc_single
    })
    print(f"推理结果: {r.status_code}")
    data = r.json()
    if isinstance(data, dict) and 'data' in data:
        print(f"输出: {data['data']}")
    else:
        print(f"原始响应前500字: {str(data)[:500]}")

    os.unlink(tts_path)

asyncio.run(main())
