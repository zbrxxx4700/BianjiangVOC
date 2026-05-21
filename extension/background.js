/**
 * 杈规睙 TTS 鈥?Background Service Worker
 * 绠＄悊蹇嵎閿€佹爣绛鹃〉閫氫俊
 */

// 榛樿閰嶇疆
const DEFAULT_CONFIG = {
  enabled: true,
  voice: 'zh-CN-YunxiNeural',
  f0UpKey: 0,
  backendUrl: 'http://localhost:8765',
};

// 鍒濆鍖栭厤缃?chrome.runtime.onInstalled.addListener(() => {
  chrome.storage.sync.get(Object.keys(DEFAULT_CONFIG), (items) => {
    const toSet = {};
    for (const [key, val] of Object.entries(DEFAULT_CONFIG)) {
      if (items[key] === undefined) toSet[key] = val;
    }
    if (Object.keys(toSet).length > 0) {
      chrome.storage.sync.set(toSet);
    }
  });
});

// 蹇嵎閿垏鎹?chrome.commands.onCommand.addListener((command) => {
  if (command === 'toggle-bianjiang') {
    chrome.storage.sync.get(['enabled'], (items) => {
      chrome.storage.sync.set({ enabled: !items.enabled });
    });
  }
});

// 瀹氭湡妫€鏌ュ悗绔姸鎬侊紙鐢ㄤ簬 badge 鏄剧ず锛?async function updateBadge() {
  try {
    const { backendUrl } = await chrome.storage.sync.get('backendUrl');
    const resp = await fetch(`${backendUrl || DEFAULT_CONFIG.backendUrl}/health`);
    if (resp.ok) {
      const data = await resp.json();
      if (data.status === 'ok') {
        chrome.action.setBadgeText({ text: 'ON' });
        chrome.action.setBadgeBackgroundColor({ color: '#4ade80' });
        return;
      }
    }
  } catch {}
  chrome.action.setBadgeText({ text: '' });
}

// 姣?30 绉掓鏌ヤ竴娆?updateBadge();
setInterval(updateBadge, 30000);
