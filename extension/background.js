const DEFAULT_CONFIG = {
  enabled: true,
  voice: 'zh-CN-YunxiNeural',
  f0UpKey: 0,
  backendUrl: 'http://localhost:8765',
};
const LAUNCHER_URL = 'http://localhost:18765';

chrome.runtime.onInstalled.addListener(() => {
  chrome.storage.sync.get(Object.keys(DEFAULT_CONFIG), (items) => {
    const toSet = {};
    for (const [key, val] of Object.entries(DEFAULT_CONFIG)) {
      if (items[key] === undefined) toSet[key] = val;
    }
    if (Object.keys(toSet).length > 0) chrome.storage.sync.set(toSet);
  });
});

chrome.commands.onCommand.addListener((command) => {
  if (command === 'toggle-bianjiang') {
    chrome.storage.sync.get(['enabled'], (items) => {
      chrome.storage.sync.set({ enabled: !items.enabled });
    });
  }
});

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.action === 'launcher_start') {
    fetch(LAUNCHER_URL + '/start', { method: 'POST' })
      .then(r => r.json()).then(sendResponse).catch(() => sendResponse({ status: 'error' }));
    return true;
  }
  if (msg.action === 'launcher_stop') {
    fetch(LAUNCHER_URL + '/stop', { method: 'POST' })
      .then(r => r.json()).then(sendResponse).catch(() => sendResponse({ status: 'error' }));
    return true;
  }
  if (msg.action === 'launcher_status') {
    fetch(LAUNCHER_URL + '/status')
      .then(r => r.json()).then(sendResponse).catch(() => sendResponse({ status: 'error' }));
    return true;
  }
});

async function updateBadge() {
  try {
    const { backendUrl } = await chrome.storage.sync.get('backendUrl');
    const r = await fetch(`${backendUrl || DEFAULT_CONFIG.backendUrl}/health`);
    if (r.ok) {
      chrome.action.setBadgeText({ text: 'ON' });
      chrome.action.setBadgeBackgroundColor({ color: '#4ade80' });
      return;
    }
  } catch {}
  chrome.action.setBadgeText({ text: '' });
}
updateBadge();
setInterval(updateBadge, 30000);
