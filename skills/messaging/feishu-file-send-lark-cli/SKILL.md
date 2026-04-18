---
name: feishu-file-send-lark-cli
description: 使用 lark-cli 命令行发送本地文件到飞书聊天会话（群聊/DM），支持智能会话选择
version: 1.1.0
---

# Skill: 飞书文件发送（增强版）

## 用途
通过 lark-cli 命令行工具发送本地文件到飞书聊天会话，支持：
- 自动获取最近会话列表并交互选择
- 根据会话名称关键词智能匹配
- 缓存最近使用的会话，避免重复查找
- 群聊和私信场景全覆盖

## 前置条件
1. 已安装 lark-cli 并完成设备码登录授权
2. 文件在本地存在且可读
3. Hermes 已加载本技能

---

## 🆕 新增参数说明

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `--file` / `-f` | string | ✅ | 本地文件路径（绝对或相对路径） |
| `--chat-id` / `-c` | string | ❌ | 会话 ID（oc_xxx），不指定时自动选择 |
| `--interactive` / `-i` | boolean | ❌ | 交互式选择会话（显示最近5个） |
| `--to` / `-t` | string | ❌ | 根据会话名称关键词匹配 |
| `--refresh` / `-r` | boolean | ❌ | 强制重新选择会话（忽略缓存） |

**默认行为**（不指定任何会话参数时）：
1. 尝试读取缓存的 chat_id
2. 缓存不存在 → 交互选择最近5个会话

---

## 🎯 使用示例

### 基础用法

```bash
# 1. 交互选择会话（推荐新手）
/feishu-file-send-lark-cli --file /path/to/report.md --interactive

# 2. 根据关键词匹配会话
/feishu-file-send-lark-cli --file report.md --to "病情"

# 3. 使用缓存（无参数，上次选择的会话）
/feishu-file-send-lark-cli --file report.md

# 4. 强制重新选择（忽略缓存）
/feishu-file-send-lark-cli --file report.md --refresh

# 5. 直接指定 chat_id（最快速）
/feishu-file-send-lark-cli --file report.md --chat-id oc_e92ded0f5dbeecd5601c811bd2247ddf
```

### 组合使用

```bash
# 关键词匹配 + 多个结果时交互选择
/feishu-file-send-lark-cli --file report.md --to "项目"
# 如果匹配到多个"项目"相关会话，会显示列表供选择

# 强制刷新缓存并交互选择
/feishu-file-send-lark-cli --file report.md --refresh
```

---

## 📋 交互选择界面示例

```
==================================================
📱 请选择会话
==================================================
  [1] 病情讨论组 oc_e92ded0f5dbeecd5601c811bd2247ddf (群聊,12人) 2分钟前
  [2] sam哥 oc_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx (私信) 1小时前
  [3] 项目组 oc_yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy (群聊,8人) 3小时前
  [4] 技术交流 oc_zzzzzzzzzzzzzzzzzzzzzzzzzzzzz (群聊,25人) 5小时前
  [5] 日报群 oc_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa (群聊,6人) 1天前
  [0] 取消操作
==================================================
请输入会话编号: _
```

---

## 🔧 底层实现逻辑

### chat_id 解析优先级

```
用户指定 --chat-id
    ↓ 使用指定值
关键词匹配 --to "xxx"
    ↓ 唯一匹配 → 自动使用
    ↓ 多个匹配 → 交互选择
交互模式 --interactive
    ↓ 显示最近5个会话 → 用户选择
读取缓存（默认）
    ↓ 使用上次选择的 chat_id
交互选择（ fallback）
    ↓ 显示最近5个会话 → 用户选择
```

### 缓存机制

- **位置**: `~/.hermes/cache/feishu_chat_cache.json`
- **内容**:
  ```json
  {
    "last_chat_id": "oc_xxx",
    "last_chat_name": "病情讨论组",
    "updated_at": "2026-04-18T10:30:00+08:00"
  }
  ```
- **更新时机**: 每次交互选择后自动更新
- **失效条件**: 手动 `--refresh` 或缓存文件被删除

---

## 🐛 故障排查

| 现象 | 原因 | 解决 |
|------|------|------|
| `无法获取会话列表` | lark-cli 未登录或网络问题 | 运行 `lark-cli auth login` 重新授权 |
| `未找到包含关键词的会话` | 关键词不匹配任何会话 | 去掉 `--to` 参数使用交互选择 |
| `文件复制失败` | 文件路径错误或无权限 | 检查文件是否存在，使用绝对路径 |
| `发送失败: open_id cross app` | 跨租户 DM 用了 `--user-id` | 改用 `--chat-id`（本技能已自动处理） |
| `缓存文件读写失败` | 目录权限问题 | 检查 `~/.hermes/cache/` 是否可写 |

---

## 📊 会话信息字段说明

交互选择时显示的信息来源：

| 字段 | 来源 | 说明 |
|------|------|------|
| 会话名称 | `chat_info.name` | 群聊名称或用户昵称 |
| chat_id | `chat_id` | 会话唯一标识（oc_xxx） |
| 会话类型 | `chat_info.chat_type` | `group`（群聊）或 `private`（私信） |
| 成员数 | `chat_info.member_count` | 仅群聊显示 |
| 最后活跃 | `create_time` → 相对时间 | 基于最近一条消息时间 |

---

## 🔄 更新日志

### v1.1.0 (2026-04-18)
- ✅ 新增交互式会话选择（默认显示5个最近会话）
- ✅ 新增关键词匹配（`--to` 参数）
- ✅ 新增缓存机制（记忆上次选择的会话）
- ✅ 新增 `--refresh` 强制刷新参数
- ✅ 优化错误提示和用户体验

### v1.0.0 (2026-04-16)
- 初始版本
- 基础文件发送功能

---

**创建时间**: 2026-04-18  
**适用场景**: 飞书文件发送（MD/PDF/图片等），支持智能会话管理


---

## 🚀 Python Handler 实现

本技能包含可直接执行的 Python handler，位于 `handler.py`。

### 直接运行

```bash
# 交互选择会话发送文件
python ~/.hermes/skills/messaging/feishu-file-send-lark-cli/handler.py \
  --file /path/to/report.md \
  --interactive

# 关键词匹配
python ~/.hermes/skills/messaging/feishu-file-send-lark-cli/handler.py \
  --file report.md \
  --to "病情"

# 使用缓存（默认）
python ~/.hermes/skills/messaging/feishu-file-send-lark-cli/handler.py \
  --file report.md
```

### 在 Hermes 中调用

Hermes 会自动调用 handler.py，你只需在 CLI 中使用 skill 命令：

```
/feishu-file-send-lark-cli --file report.md --interactive
```

### Handler 参数说明

与技能参数完全一致，详见上文「新增参数说明」。

---

## 📁 文件结构

```
feishu-file-send-lark-cli/
├── SKILL.md          # 技能文档（本文件）
├── handler.py        # Python 实现（可直接运行）
└── _utils/           # 共享工具模块（自动导入）
    └── chat_selector.py
```

