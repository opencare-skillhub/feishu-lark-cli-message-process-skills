---
name: feishu-message-send-lark-cli
description: 使用 lark-cli 发送文本/富文本消息到飞书会话，支持智能会话选择
version: 1.1.0
---

# Skill: 飞书消息发送（增强版）

## 用途
通过 lark-cli 命令行向飞书聊天会话发送消息，支持：
- 纯文本、富文本（At/链接/加粗等）
- 自动获取最近会话并交互选择
- 根据会话名称关键词智能匹配
- 缓存最近使用的会话
- 群聊和私信场景全覆盖

## 前置条件
1. 已安装 lark-cli 并完成设备码登录授权
2. 已获取目标会话的 chat_id 或接收人 user_id（本技能可自动获取）
3. Hermes 已加载本技能

---

## 🆕 新增参数说明

### 会话选择参数（三选一，不指定则用缓存）

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `--chat-id` / `-c` | string | ❌ | 会话 ID（oc_xxx），直接指定 |
| `--interactive` / `-i` | boolean | ❌ | 交互式选择（显示最近5个会话） |
| `--to` / `-t` | string | ❌ | 根据会话名称关键词匹配 |
| `--refresh` / `-r` | boolean | ❌ | 强制重新选择（忽略缓存） |

### 消息内容参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `--text` / `-m` | string | ✅ | 纯文本消息内容 |
| `--markdown` / `-m` | string | ❌ | Markdown 富文本（与 `--text` 二选一） |
| `--user-id` / `-u` | string | ❌ | 私信接收人 user_id（仅同租户） |

**注意**：`--text` 和 `--markdown` 至少提供一个，优先使用 `--text`。

---

## 🎯 使用示例

### 纯文本消息

```bash
# 1. 交互选择会话
/feishu-message-send-lark-cli --text "你好，这是报告" --interactive

# 2. 关键词匹配
/feishu-message-send-lark-cli --text "请查收日报" --to "病情"

# 3. 使用缓存（默认）
/feishu-message-send-lark-cli --text "测试消息"

# 4. 直接指定 chat_id
/feishu-message-send-lark-cli --text "快速发送" --chat-id oc_xxx

# 5. 发送到特定用户（同租户私信）
/feishu-message-send-lark-cli --text "私信内容" --user-id ou_xxx
```

### 富文本消息（Markdown）

```bash
# 发送 Markdown 格式消息
/feishu-message-send-lark-cli \
  --markdown "**加粗** *斜体* [链接](https://example.com)" \
  --to "项目组"

# 组合：At 某人（需已知 user_id）
/feishu-message-send-lark-cli \
  --markdown "<at id=\"ou_123\">张三</at> 请查看报告" \
  --chat-id oc_xxx
```

---

## 📋 交互选择界面

与文件发送技能相同，显示最近5个会话：

```
==================================================
📱 请选择会话
==================================================
  [1] 病情讨论组 oc_xxx (群聊,12人) 2分钟前
  [2] sam哥 oc_yyy (私信) 1小时前
  [3] 项目组 oc_zzz (群聊,8人) 3小时前
  [4] 技术交流 oc_aaa (群聊,25人) 5小时前
  [5] 日报群 oc_bbb (群聊,6人) 1天前
  [0] 取消操作
==================================================
请输入会话编号: _
```

---

## 🔧 底层实现

### 会话选择逻辑（与文件发送技能共享）

通过 `~/.hermes/skills/messaging/_utils/chat_selector.py` 共享同一套选择逻辑：

```python
from ._utils.chat_selector import resolve_chat_id

chat_id, error = resolve_chat_id(
    chat_id=args.get('--chat-id'),
    keyword=args.get('--to'),
    interactive=args.get('--interactive', False),
    refresh=args.get('--refresh', False),
    max_results=5
)
```

### chat_id vs user_id 选择指南

| 场景 | 推荐参数 | 说明 |
|------|----------|------|
| 已知群聊 | `--chat-id` | 从 `im chats list` 或交互选择获取 |
| 当前 DM 会话 | `--chat-id` | 交互选择或 `+messages-search` |
| 同租户私信（已知 user_id） | `--user-id` | 仅同租户，需对方 user_id |
| 跨租户 DM | `--chat-id` | 必须用 chat_id，`--user-id` 会报错 |

**最佳实践**：优先使用 `--chat-id`，兼容性最好。

---

## 🐛 故障排查

| 现象 | 原因 | 解决 |
|------|------|------|
| `invalid chat_id` | chat_id 格式错误或会话不存在 | 重新交互选择 |
| `open_id cross app` | 跨租户使用 `--user-id` | 改用 `--chat-id` |
| `permission denied` | 缺少发送权限 | 重新登录 lark-cli 并授权 |
| `unknown field "text"` | JSON 格式错误 | 确保 `--text` 内容为纯字符串 |
| `message too long` | 文本超限（≤5000字符） | 分段发送或使用文件发送 |

---

## 🔄 更新日志

### v1.1.0 (2026-04-18)
- ✅ 新增交互式会话选择（显示最近5个）
- ✅ 新增关键词匹配（`--to`）
- ✅ 新增缓存机制
- ✅ 新增 `--refresh` 参数
- ✅ 统一使用 chat_selector 共享模块

### v1.0.0 (2026-04-16)
- 初始版本
- 基础文本/富文本发送功能

---

**创建时间**: 2026-04-18  
**适用场景**: 飞书消息发送、群聊通知、DM 沟通、At 提醒


---

## 🚀 Python Handler 实现

本技能包含可直接执行的 Python handler，位于 `handler.py`。

### 直接运行

```bash
# 交互选择会话发送消息
python ~/.hermes/skills/messaging/feishu-message-send-lark-cli/handler.py \
  --text "你好，这是日报" \
  --interactive

# 关键词匹配 + Markdown
python ~/.hermes/skills/messaging/feishu-message-send-lark-cli/handler.py \
  --markdown "**加粗** *斜体*" \
  --to "项目组"

# 使用缓存（默认）
python ~/.hermes/skills/messaging/feishu-message-send-lark-cli/handler.py \
  --text "测试消息"
```

### Handler 参数说明

| 参数 | 必需 | 说明 |
|------|------|------|
| `--text` | 否（与 `--markdown` 二选一） | 纯文本内容 |
| `--markdown` | 否（与 `--text` 二选一） | Markdown 内容 |
| `--chat-id` | 否 | 直接指定会话 ID |
| `--user-id` | 否 | 指定私信接收人（同租户） |
| `--interactive` | 否 | 交互选择会话 |
| `--to` | 否 | 关键词匹配会话 |
| `--refresh` | 否 | 强制刷新缓存 |

---

## 📁 文件结构

```
feishu-message-send-lark-cli/
├── SKILL.md          # 技能文档（本文件）
├── handler.py        # Python 实现（可直接运行）
└── _utils/           # 共享工具模块（自动导入）
    └── chat_selector.py
```

