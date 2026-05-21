# BianjiangRVC — 边江 TTS 浏览器扩展

用 RVC 音色转换，让 Edge 浏览器朗读网页时变成边江的声音。

> **项目代号**: BianjiangVOC | **版本**: v1.0 | **状态**: 已结项

---

## 快速开始

### 环境要求

- Windows 10/11
- AMD 显卡（已测试 RX 9070 GRE）或 CPU（慢但可用）
- Microsoft Edge 或 Chrome 浏览器
- Python 3.9（RVC 运行时自带）

### 前置资源

| 资源 | 说明 |
|------|------|
| RVC 推理仓库 | `D:\Software\RVC20240604-AMD`（含 Python 运行时） |
| 边江声线模型 | `BianjiangRVC_V2_e23_s1288.pth`（需训练好的 .pth 文件） |
| 特征检索库 | `added_IVF634_Flat_nprobe_1_BianjiangRVC_V2_v2.index` |

### 启动步骤

**1. 启动后端**

双击 `一键启动.bat`，等待控制台显示「启动成功」：

```
[1/5] 检查端口 8765 状态...
[2/5] 设置运行环境...
[3/5] 启动 Python 后端...
[4/5] 等待 ZLUDA 内核编译...  ← 首次约 2-3 分钟
[5/5] 完成！
```

> 首次启动需要编译 ZLUDA GPU 内核（约 2-3 分钟），之后秒级启动。

**2. 加载浏览器扩展**

1. 打开 Edge 浏览器，地址栏输入 `edge://extensions`
2. 打开「开发人员模式」
3. 点击「加载解压缩的扩展」
4. 选择项目下的 `extension/` 文件夹

加载成功后，工具栏会出现绿色图标。

**3. 使用**

- 任意网页**选中文字** → 出现浮动 Logo → **点击播放**
- `Space` 暂停/继续，`Esc` 停止
- 点扩展图标可切换开关、调音调/语速、选模型/声源

---

## 技术架构

### 系统总览

```
┌─────────────────────────────────────────────────────┐
│                  浏览器 (Edge/Chrome)                 │
│                                                       │
│  选中文字                                             │
│     ↓                                                 │
│  浮动播放按钮 (content_script.js)                     │
│     ↓ POST /synthesize {:8765}                       │
│     ↓                                                 │
│  AudioContext ← audio/wav ← ← ← ← ← ← ←             │
└─────────────────┬───────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────┐
│              Python 后端 (FastAPI :8765)              │
│                                                       │
│  POST /synthesize                                     │
│    ├─ edge-tts → 微软 TTS 合成源音频                 │
│    ├─ librosa → 标准化 WAV 格式                      │
│    ├─ RVC vc_single → 音色转换（GPU/ZLUDA）          │
│    └─ 返回 WAV 字节流 (40000Hz, PCM_16)              │
│                                                       │
│  GET /health  → 模型状态                             │
│  GET /models → 可用模型列表                          │
│                                                       │
│  设备: AMD GPU (ZLUDA 模拟 CUDA)                     │
│  运行时: runtime\python.exe (3.9.13)                 │
└─────────────────────────────────────────────────────┘
```

### 数据处理流

```
"你好，我是边江"
    ↓ edge_tts.Communicate("你好，我是边江", "zh-CN-YunxiNeural")
temp.wav (源声音: 云希)
    ↓ librosa.load + sf.write (标准化为 PCM_16 WAV)
norm.wav
    ↓ VC.vc_single(0, norm.wav, f0_up_key=0, f0_method="pm", ...)
      ├─ pyworld → f0 基频提取
      ├─ faiss → 特征检索 (index 库)
      └─ 生成模型 → 音色转换
    ↓
numpy array (40000Hz, float32)
    ↓ sf.write (PCM_16)
audio/wav bytes → Response → 浏览器 Audio 播放
```

### 浏览器扩展工作流

```
content_script.js (注入所有页面)
    │
    ├─ 鼠标选中文字 → getSelection()
    │   ↓
    │   浮动 Logo 出现在选区旁
    │   ↓ 点击
    │   fetch POST /synthesize {text, voice, f0_up_key}
    │   ↓
    │   new Audio(blob_url) → play()
    │   ↓
    │   onended → 清理 URL, 恢复 idle
    │
    ├─ Space → pause() / resume()
    ├─ Esc → stop() + abort()
    └─ 下载按钮 → save as .wav

popup.js (扩展面板)
    │
    ├─ 每 5s GET /models → 健康状态灯
    ├─ 开关 → chrome.storage.sync.set
    ├─ 模型/声源/音调/语速选择
    └─ 预设管理 (保存/应用/删除)

background.js (Service Worker)
    ├─ Ctrl+Shift+V → 切换启用状态
    └─ 每 30s GET /health → badge "ON"
```

---

## 项目结构

```
BianjiangVOC/
│
├── 一键启动.bat               # 双击启动后端，显示 ZLUDA 编译进度
├── 一键关闭.bat               # 双击关闭后端 + 释放 GPU + 清理临时文件
│
├── backend/                   # Python 后端服务
│   ├── app.py                 # FastAPI 入口 (:8765)
│   ├── rvc_engine.py          # RVC 推理引擎封装 (edge-tts + RVC + 线程锁)
│   ├── config.yaml            # 配置文件 (模型路径、推理参数)
│   ├── service.ps1            # PowerShell 服务管理脚本
│   ├── 启动后端.bat           # 启动后端 (菜单式)
│   ├── 服务管理.bat           # 服务管理菜单 (启动/停止/状态)
│   ├── tts_subprocess.py      # [备用/未使用] pyttsx3 子进程 TTS
│   │
│   ├── test_pipeline.py       # edge-tts → RVC 全链路验证
│   ├── test_all_male.py       # 所有中文男声对照测试
│   ├── test_multilingual.py   # 多语种男声对照测试
│   ├── test_params.py         # RVC 参数对比测试 (f0/index_rate)
│   ├── test_cpu.py            # CPU 推理测试
│   ├── test_tts.py            # TTS 引擎独立测试
│   ├── test_pipeline2.py      # 含 librosa 重采样的链路测试
│   ├── list_male_voices.py    # 列出 edge-tts 所有中文男声
│   ├── check_model.py         # 训练模型 vs 预训练底模差异分析
│   │
│   └── test_output/           # 测试音频输出目录
│
├── extension/                 # Edge 浏览器扩展 (Manifest V3)
│   ├── manifest.json          # 扩展清单: 权限、注入规则、快捷键
│   ├── content_script.js      # 注入脚本: 选中朗读浮窗 + API 拦截
│   ├── background.js          # Service Worker: 快捷键 + badge 状态
│   ├── popup.html             # 弹出面板 UI (深色主题)
│   ├── popup.js               # 弹出面板逻辑
│   ├── options.html           # 设置页 UI
│   ├── options.js             # 设置页逻辑
│   └── Logo.png               # 扩展图标
│
├── Refer_voice/               # 边江原声切片 (参考音色, 测试对比用)
│   └── 1.0s_边江_*.wav        # 16 个 1 秒原声片段
│
├── 项目要求.txt               # 原始需求文档
├── 项目计划书.md               # 开发计划书
├── 项目进度文档.md              # 项目进度 + 技术细节
├── changelog.md               # 变更日志
└── README.md                  # 本文件
```

---

## 核心文件详解

### 后端

#### `backend/app.py`
FastAPI 服务主入口。启动时加载 RVC 模型为全局单例，提供三个路由：
- `GET /health` — 模型状态、设备信息、可用模型/声音列表
- `GET /models` — weights 目录下所有 .pth 文件
- `POST /synthesize` — 接收文本 → edge-tts 合成 → RVC 音色转换 → 返回 WAV

CORS 中间件已配置，允许所有来源（本地服务安全）。

#### `backend/rvc_engine.py`
RVC 推理引擎封装 `class R`。
- `__init__` — 加载配置，切换 RVC 仓库目录，初始化 ZLUDA，加载模型
- `synth(text, voice, f0_up_key, model)` — 异步推理主方法
  - 支持动态切换模型（如果指定不同模型名）
  - 使用 `threading.Lock` 保证串行推理（AMD GPU 单线程更稳定）
  - edge-tts 直接异步调用（不通过子进程）
- `_tts_edge(text, voice)` — 异步调用 edge-tts 生成源音频
- `_wav(path)` — librosa 加载 → 标准化 → sf.write 重写为 PCM_16 WAV
- `list()` — 扫描 weights 目录返回所有可用模型
- `voices` — 从配置读取可选源声音列表

#### `backend/config.yaml`
```yaml
model_name: "BianjiangRVC_V2_e23_s1288.pth"   # 默认加载的模型
weights_dir: "D:/Software/RVC20240604-AMD/assets/weights"
index_path: "..."                              # 特征检索库路径
rvc_root: "D:/Software/RVC20240604-AMD"        # RVC 仓库根目录
default_voice: "zh-CN-YunxiNeural"             # 默认源 TTS 声音
source_voices:                                  # 可选源声音列表
  - "zh-CN-YunxiNeural"
  - "ko-KR-HyunsuMultilingualNeural"
f0_up_key: 0                                   # 变调（半音）
f0_method: "pm"                                # 基频提取算法
index_rate: 0.75                               # 特征检索混合比例
filter_radius: 3
rms_mix_rate: 0.25
protect: 0.33
host: "0.0.0.0"
port: 8765
```

### 浏览器扩展

#### `extension/manifest.json`
Manifest V3 配置：
- `content_scripts` — 所有页面 (`<all_urls>`) 在 `document_start` 注入
- `host_permissions` — 允许访问 `http://localhost:8765/`
- `commands` — `Ctrl+Shift+V` 切换开关
- `permissions` — `storage`, `activeTab`, `downloads`
- `web_accessible_resources` — Logo.png 可供网页访问

#### `extension/content_script.js`
核心注入脚本，不依赖任何第三方库。功能：
1. **选中朗读** — 监听 `mouseup`，获取 `getSelection()` 文字，在选区旁显示浮动 Logo
2. **播放引擎** — `class AP`：fetch 后端 → createObjectURL → Audio 播放
   - 支持播放/暂停/继续/停止
   - `AbortController` 中止网络请求
   - `AudioContext` 处理自动播放策略
3. **状态同步** — 浮动图标反映播放状态（绿=就绪/金=播放中/黄=暂停）
4. **快捷键** — `Space` 暂停/继续，`Esc` 停止
5. **下载** — 上次播放的音频可保存为 .wav

#### `extension/background.js`
Service Worker：
- 初始化默认配置到 chrome.storage
- 监听 `toggle-bianjiang` 命令（Ctrl+Shift+V）
- 每 30 秒检查后端健康状态，更新扩展 badge

#### `extension/popup.html` + `popup.js`
弹出控制面板：
- 健康状态指示灯（绿/红/黄）
- 启用替换开关
- 自动朗读开关（选中即读）
- 推理模型下拉选择（从后端 /models 获取）
- 源声音选择（Yunxi / Hyunsu）
- 音调滑块（-12 ~ +12）
- 语速滑块（0.5x ~ 2.0x）
- 预设方案管理（保存/应用/删除）
- 下载朗读音频按钮
- 快捷键提示

### 测试脚本

| 文件 | 用途 |
|------|------|
| `test_pipeline.py` | 阶段 0 验证：edge-tts → RVC 全流程，含 index 诊断 |
| `test_all_male.py` | 对比 5 个 edge-tts 中文男声 + RVC 效果 |
| `test_multilingual.py` | 测试 8 个多语种男声 + RVC 效果 |
| `test_params.py` | 参数组合对比：f0_up_key {-4,0,+4} × index_rate {0.75,1.0} |
| `test_cpu.py` | CPU 推理测试（无 ZLUDA 时备用） |
| `check_model.py` | 分析训练模型与预训练底模的差异 |

---

## 配置调优

### 源声音选择

推荐 `zh-CN-YunxiNeural`（云希，中文男声）。可切换 `ko-KR-HyunsuMultilingualNeural`（韩语多语言男声）或其他 edge-tts 声音。

### RVC 参数

| 参数 | 范围 | 推荐 | 说明 |
|------|------|------|------|
| f0_up_key | -12 ~ +12 | 0 | 调高声音更尖细，调低更低沉 |
| f0_method | pm/harvest/crepe/rmvpe/fcpe | pm | pm 最快，rmvpe 更准但慢 |
| index_rate | 0 ~ 1 | 0.75 | 越大越像目标音色，过大会有 artifacts |
| protect | 0 ~ 1 | 0.33 | 保护清辅音不被过度转换 |

---

## API 参考

### `GET /health`

```json
{
  "status": "ok",
  "model_loaded": true,
  "model": {
    "model": "BianjiangRVC_V2_e23_s1288.pth",
    "sr": 40000,
    "device": "cuda"
  },
  "available_models": [
    {"name": "BianjiangRVC_V2_e23_s1288.pth", "size_mb": 52.7, "current": true}
  ],
  "available_voices": ["zh-CN-YunxiNeural", "ko-KR-HyunsuMultilingualNeural"]
}
```

### `GET /models`

```json
{
  "models": [
    {"name": "BianjiangRVC_V2_e23_s1288.pth", "size_mb": 52.7, "current": true}
  ]
}
```

### `POST /synthesize`

请求:
```json
{
  "text": "你好，我是边江，很高兴认识你。",
  "voice": "zh-CN-YunxiNeural",
  "f0_up_key": 0,
  "model": "BianjiangRVC_V2_e23_s1288.pth"
}
```

响应: `Content-Type: audio/wav` (40000Hz, PCM_16, mono)

---

## 常见问题

### 扩展图标显示红色 "Offline"

后端未运行。双击 `一键启动.bat` 启动后端，等待编译完成。

### 点击浮动按钮没有声音

1. 检查扩展图标是否绿色「Ready」
2. 检查扩展设置里 `启用替换` 是否打开
3. 打开 F12 开发者工具 → Console，看有无 CORS 或网络错误
4. 确认 `config.yaml` 中的模型路径和 index 路径正确
5. 首次启动需等待 ZLUDA 内核编译完成

### 音色不像边江

- 调整 `f0_up_key`（popup 面板里的音调滑块）：男声可试 -2 ~ +2
- 调整 `index_rate`：增大到 0.85 ~ 0.95 更像目标音色
- 尝试不同的源声音：Yunxi → Yunjian → Hyunsu

### 首次启动很慢

ZLUDA 首次需要编译 GPU 内核，约 2-3 分钟。之后启动会快很多。也可以保持后端运行不关闭。

### 端口 8765 被占用

先运行 `一键关闭.bat` 释放端口，再重新启动。

---

## 本地开发

```bash
# 安装额外依赖（在 RVC 运行时中）
D:\Software\RVC20240604-AMD\runtime\python.exe -m pip install edge-tts fastapi uvicorn

# 启动后端
一键启动.bat

# 单独运行测试
set PYTHONPATH=D:\Study\agent\BianjiangVOC\backend;%PYTHONPATH%
D:\Software\RVC20240604-AMD\runtime\python.exe backend/test_pipeline.py
```

---

## 依赖清单

### 后端（RVC 运行时已有）

大部分依赖在 `D:\Software\RVC20240604-AMD\runtime\` 中已安装：
- torch + torch_directml
- faiss
- fairseq
- pyworld / parselmouth / torchcrepe
- librosa / soundfile

### 额外安装（已装）

```bash
pip install edge-tts fastapi uvicorn
```

### 浏览器扩展

无外部依赖，纯原生 Web API。
