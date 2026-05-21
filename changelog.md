# 变更日志

## 2026-05-20

| 时间 | 操作类型 | 说明 |
|------|---------|------|
| 08:05 | 审查 | 审查项目要求.txt |
| 08:10 | 修订 | 更新项目要求.txt |
| 08:12 | 新建 | 项目计划书.md + changelog.md |
| 08:14 | 测试 | 阶段 0 链路验证通过 |
| 08:31-53 | 调试 | 声源选型：Yunxi + HyunsuMultilingual |
| 08:53 | 后端 | app.py + rvc_engine.py + config.yaml |
| 09:04 | 扩展 | manifest.json + content_script + popup + options |
| 09:09 | 扩展 | 选中朗读 + Logo 图标 + 状态变化 |
| 09:10 | 脚本 | 一键启动/关闭（中文 + 进度 + CRLF + GBK） |
| 09:22 | 工具 | TOOLS.md 新增 bat 编码铁律 |
| 09:28 | 后端 | GET /models + 模型切换 + synthesize 支持 model 参数 |
| 09:28 | 扩展 | popup 新增模型下拉选择，请求带 model 参数 |
| 17:30 | 后端 | 生产路径从 pyttsx3 子进程切换到 edge-tts 直接异步调用 |
| 17:30 | 后端 | rvc_engine.py 默认声音从 zh-Huihui 改为 config.default_voice |
| 17:32 | 后端 | app.py 添加 CORS 中间件（修复扩展无声问题） |
| 17:32 | 后端 | /synthesize 增加模型就绪检查 |
| 17:45 | 脚本 | 一键启动/关闭/服务管理：修复 CRLF 行尾 + GBK 编码 + 窗口标题自杀 bug |
| 18:00 | 文档 | 更新项目进度文档.md 为结项状态 |
| 18:00 | 文档 | 撰写 README.md（含完整技术架构 + 文件详解 + API 参考） |
