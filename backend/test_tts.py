import asyncio, os, edge_tts
from gtts import gTTS

async def main():
    # edge-tts
    try:
        c = edge_tts.Communicate('你好测试', 'zh-CN-YunxiNeural')
        p = r'D:\Study\agent\BianjiangVOC\backend\test_output\tts_test2.wav'
        await c.save(p)
        print(f'edge-tts OK: {os.path.getsize(p)} bytes')
    except Exception as e:
        print(f'edge-tts FAIL: {type(e).__name__}: {e}')
    
    # gTTS
    try:
        p = r'D:\Study\agent\BianjiangVOC\backend\test_output\gtts_test.mp3'
        gTTS('你好测试', lang='zh-cn').save(p)
        print(f'gTTS OK: {os.path.getsize(p)} bytes')
    except Exception as e:
        print(f'gTTS FAIL: {type(e).__name__}: {e}')

asyncio.run(main())
