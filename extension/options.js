// 杈规睙 TTS 鈥?璁剧疆椤?const backendUrl = document.getElementById('backendUrl');
const defaultVoice = document.getElementById('defaultVoice');
const defaultF0 = document.getElementById('defaultF0');
const saveBtn = document.getElementById('saveBtn');
const saveMsg = document.getElementById('saveMsg');

// 璇诲彇宸叉湁閰嶇疆
chrome.storage.sync.get(['backendUrl', 'voice', 'f0UpKey'], (items) => {
  if (items.backendUrl) backendUrl.value = items.backendUrl;
  if (items.voice) defaultVoice.value = items.voice;
  if (items.f0UpKey !== undefined) defaultF0.value = items.f0UpKey;
});

// 淇濆瓨
saveBtn.addEventListener('click', () => {
  chrome.storage.sync.set({
    backendUrl: backendUrl.value.trim(),
    voice: defaultVoice.value,
    f0UpKey: parseInt(defaultF0.value) || 0,
  }, () => {
    saveMsg.textContent = '淇濆瓨鎴愬姛 鉁?;
    setTimeout(() => { saveMsg.textContent = ''; }, 2000);
  });
});
