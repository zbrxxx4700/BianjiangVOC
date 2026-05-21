import edge_tts, asyncio, json

async def main():
    voices = await edge_tts.list_voices()
    males = [v for v in voices if v['Gender'] == 'Male']
    with open(r'D:\Study\agent\BianjiangVOC\backend\test_output\male_voices.txt', 'w', encoding='utf-8') as f:
        for v in males:
            line = "{} | {} | {}".format(v['ShortName'], v['Locale'], v['FriendlyName'])
            f.write(line + "\n")
            print(line)
    print("\n总共 {} 个男声".format(len(males)))

asyncio.run(main())
