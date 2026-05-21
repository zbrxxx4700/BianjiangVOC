var B = "http://localhost:8765";
var LB = "http://localhost:18765";
function $(id) { return document.getElementById(id); }
var sDot = $("sDot"), sTxt = $("sTxt");
var en = $("enabledToggle"), ar = $("autoReadToggle");
var ms = $("modelSelect"), vs = $("voiceSelect");
var ps = $("pitchSlider"), pv = $("pitchVal");
var rs = $("rateSlider"), rv = $("rateVal");
var dl = $("downloadBtn");
var pn = $("presetName"), psl = $("presetSelect"), sp = $("savePreset"), ap = $("applyPreset"), dp = $("delPreset");
var st = $("startBtn"), so = $("stopBtn");

chrome.storage.sync.get(["enabled","model","voice","f0UpKey","rate","autoRead"], function(i) {
  if (i.enabled !== undefined) en.checked = i.enabled;
  if (i.model) ms.value = i.model;
  if (i.voice) vs.value = i.voice;
  if (i.f0UpKey !== undefined) { ps.value = i.f0UpKey; pv.textContent = i.f0UpKey; }
  if (i.rate !== undefined) { rs.value = i.rate; rv.textContent = i.rate; }
  if (i.autoRead !== undefined) ar.checked = i.autoRead;
});

function save() {
  chrome.storage.sync.set({
    enabled: en.checked, model: ms.value, voice: vs.value,
    f0UpKey: parseInt(ps.value), rate: parseFloat(rs.value), autoRead: ar.checked
  });
}
en.onchange = save; ms.onchange = save; vs.onchange = save; ar.onchange = save;
ps.oninput = function(){ pv.textContent = ps.value; save(); };
rs.oninput = function(){ rv.textContent = rs.value; save(); };

function setStatus(cls, txt) {
  sDot.className = "dot " + cls;
  sTxt.textContent = txt;
  sTxt.style.color = cls === "on" ? "#4ade80" : cls === "off" ? "#f87171" : "#fbbf24";
}
function setBtns(s, o) {
  st.disabled = s; so.disabled = o;
  st.style.opacity = s ? "0.5" : "1";
  so.style.opacity = o ? "0.5" : "1";
}

// 启动
st.onclick = async function() {
  setStatus("busy", "启动中...");
  setBtns(true, true);
  try {
    var r = await chrome.runtime.sendMessage({ action: "launcher_start" });
    if (r && r.status === "ok") {
      setStatus("busy", "等待就绪...");
      for (var i = 0; i < 60; i++) {
        await new Promise(r => setTimeout(r, 2000));
        try {
          var h = await fetch(B + "/health");
          if (h.ok) { setStatus("on", "Ready"); setBtns(true, false); return; }
        } catch(e) {}
      }
      setStatus("off", "启动超时");
    } else {
      setStatus("off", "Launcher 未运行");
      alert("启动器未运行。请先双击 launcher_service.py 启动后台服务。");
    }
  } catch(e) {
    setStatus("off", "启动失败");
    alert("启动失败。请确保 launcher_service.py 正在运行。");
  }
  setBtns(false, true);
};

// 关闭
so.onclick = async function() {
  setStatus("busy", "关闭中...");
  setBtns(true, true);
  try {
    await chrome.runtime.sendMessage({ action: "launcher_stop" });
    for (var i = 0; i < 15; i++) {
      await new Promise(r => setTimeout(r, 1000));
      try { await fetch(B + "/health"); } catch(e) {
        setStatus("off", "Offline"); setBtns(false, true); return;
      }
    }
    setStatus("off", "已关闭");
  } catch(e) {
    setStatus("off", "已关闭");
  }
  setBtns(false, true);
};

// ---- 预设 ----
function loadPresets() {
  chrome.storage.sync.get("presets", function(i) {
    var presets = i.presets || {};
    var cur = psl.value;
    psl.innerHTML = '<option value="">-- 选择预设 --</option>';
    Object.keys(presets).forEach(function(k) {
      var o = document.createElement("option");
      o.value = k; o.textContent = k; psl.appendChild(o);
    });
    if (cur) psl.value = cur;
  });
}
sp.onclick = function() {
  var name = pn.value.trim();
  if (!name) return alert("输入预设名称");
  var cfg = { model: ms.value, voice: vs.value, f0UpKey: parseInt(ps.value), rate: parseFloat(rs.value), autoRead: ar.checked };
  chrome.storage.sync.get("presets", function(i) {
    var p = i.presets || {};
    p[name] = cfg;
    chrome.storage.sync.set({ presets: p }, function() { pn.value = ""; loadPresets(); });
  });
};
ap.onclick = function() {
  var name = psl.value;
  if (!name) return;
  chrome.storage.sync.get("presets", function(i) {
    var p = (i.presets || {})[name];
    if (!p) return;
    if (p.model) ms.value = p.model;
    if (p.voice) vs.value = p.voice;
    if (p.f0UpKey !== undefined) { ps.value = p.f0UpKey; pv.textContent = p.f0UpKey; }
    if (p.rate !== undefined) { rs.value = p.rate; rv.textContent = p.rate; }
    if (p.autoRead !== undefined) ar.checked = p.autoRead;
    save();
  });
};
dp.onclick = function() {
  var name = psl.value;
  if (!name || !confirm("删除预设 '" + name + "'?")) return;
  chrome.storage.sync.get("presets", function(i) {
    var p = i.presets || {};
    delete p[name];
    chrome.storage.sync.set({ presets: p }, function() { psl.value = ""; loadPresets(); });
  });
};
loadPresets();

// ---- 状态检查 ----
async function check() {
  try {
    var r = await fetch(B + "/models");
    if (!r.ok) throw Error();
    var d = await r.json();
    ms.innerHTML = "";
    d.models.forEach(function(m) {
      var o = document.createElement("option");
      o.value = m.name; o.textContent = m.current ? m.name + " [C]" : m.name;
      ms.appendChild(o);
    });
    chrome.storage.sync.get("model", function(i) { if (i.model) ms.value = i.model; });
    setStatus("on", "Ready"); setBtns(true, false);
  } catch(e) {
    // 启动过程中不显示 Offline
    if (!st.disabled) {
      setStatus("off", "Offline"); ms.innerHTML = "<option>Offline</option>";
      setBtns(false, true);
    }
  }
}
check();
setInterval(check, 5000);

dl.onclick = async function() {
  try {
    var t = prompt("下载文本:");
    if (!t) return;
    this.textContent = "DL...";
    var r = await fetch(B + "/synthesize", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: t, voice: vs.value, model: ms.value, f0_up_key: parseInt(ps.value) })
    });
    if (!r.ok) throw Error();
    var b = await r.blob(); var u = URL.createObjectURL(b);
    chrome.downloads.download({ url: u, filename: "bianjiang.wav", saveAs: true });
  } catch(e) { alert("失败:" + e.message); }
  this.textContent = "Download";
};
