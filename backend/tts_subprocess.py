"""子进程 TTS：从文件读取文本"""
import sys, json, pyttsx3
with open(sys.argv[1], 'r', encoding='utf-8') as f:
    data = json.load(f)
e = pyttsx3.init()
for v in e.getProperty('voices'):
    if 'hui' in v.id.lower():
        e.setProperty('voice', v.id)
        break
e.setProperty('rate', 150)
e.save_to_file(data['text'], data['out'])
e.runAndWait()
