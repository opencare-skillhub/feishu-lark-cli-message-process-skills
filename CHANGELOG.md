# 更新日志

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.1.0] - 2026-04-18

### Added
- ✅ 新增交互式会话选择功能（默认显示最近5个会话）
- ✅ 新增关键词匹配会话（`--to` / `-t` 参数）
- ✅ 新增会话缓存机制（记忆上次选择的会话）
- ✅ 新增 `--refresh` / `-r` 参数强制刷新缓存
- ✅ 新增 Python Handler 直接运行支持
- ✅ 新增共享工具模块 `_utils/chat_selector.py`

### Changed
- 🔄 优化会话选择逻辑：优先使用缓存 → 关键词匹配 → 交互选择
- 🔄 统一文件格式显示：`[1] 病情讨论组 oc_xxx (群聊,12人) 2分钟前`

### Fixed
- 🐛 修复跨租户 DM 使用 `--user-id` 导致的 `open_id cross app` 错误（现在强制使用 `--chat-id`）
- 🐛 修复文件路径处理问题（自动复制到 lark-cli 工作目录）

---

## [1.0.0] - 2026-04-16

### Added
- 初始版本发布
- 基础文件发送功能（支持 MD/PDF/图片等）
- 基础消息发送功能（纯文本 + 富文本）
- 文档创建/更新功能
- 完整的错误处理和故障排查指南

---

**版本号**: 1.1.0  
**更新日期**: 2026-04-18  
**兼容平台**: Hermes / OpenClaw / Codex / Claude Code / AMP / OpenCode
