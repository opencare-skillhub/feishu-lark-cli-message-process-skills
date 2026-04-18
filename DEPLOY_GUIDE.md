# 飞书 CLI 消息处理技能包 - 部署与使用指南

## 📦 包内容（v1.1.0）

```
feishu-cli-messageprocess-skills-package/
├── LICENSE                          # MIT License
├── README.md                        # 项目说明
├── CHANGELOG.md                     # 版本更新日志
├── MANIFEST.json                    # 平台识别清单
├── package.json                     # Node.js 包配置
├── scripts/
│   ├── install.sh                   # macOS/Linux/WSL 自动安装
│   ├── install.ps1                  # Windows PowerShell 安装
│   └── install.bat                  # Windows CMD 安装
└── skills/
    └── messaging/
        ├── _utils/
        │   └── chat_selector.py     # 🔥 新增：共享会话选择器
        ├── feishu-file-send-lark-cli/
        │   ├── SKILL.md             # 技能文档
        │   └── handler.py           # 🔥 新增：Python 实现
        ├── feishu-message-send-lark-cli/
        │   ├── SKILL.md             # 技能文档
        │   └── handler.py           # 🔥 新增：Python 实现
        └── feishu-doc-create-lark-cli/
            └── SKILL.md             # 技能文档（未改动）
```

---

## 🚀 快速安装

### 方式一：自动检测平台（推荐）

```bash
cd feishu-cli-messageprocess-skills-package
./scripts/install.sh
# 自动检测 hermes/openclaw/codex/claude/amp/opencode 并安装
```

### 方式二：指定平台

```bash
# Hermes Agent
./scripts/install.sh hermes

# OpenClaw
./scripts/install.sh openclaw

# OpenAI Codex
./scripts/install.sh codex

# Claude Code
./scripts/install.sh claude

# AMP
./scripts/install.sh amp

# OpenCode
./scripts/install.sh opencode
```

### Windows 系统

```powershell
# PowerShell（推荐）
powershell -ExecutionPolicy Bypass -File scripts\install.ps1 hermes

# 或 CMD
scripts\install.bat hermes
```

---

## 🎯 快速使用

### 文件发送（增强版）

```bash
# 交互选择会话（显示最近5个）
/feishu-file-send-lark-cli --file report.md --interactive

# 关键词匹配（如"病情"）
/feishu-file-send-lark-cli --file report.md --to "病情"

# 使用缓存（默认行为，无需参数）
/feishu-file-send-lark-cli --file report.md

# 强制重新选择
/feishu-file-send-lark-cli --file report.md --refresh

# 直接指定 chat_id
/feishu-file-send-lark-cli --file report.md --chat-id oc_xxx
```

### 消息发送（增强版）

```bash
# 纯文本 + 交互选择
/feishu-message-send-lark-cli --text "你好" --interactive

# Markdown 富文本 + 关键词匹配
/feishu-message-send-lark-cli --markdown "**加粗** *斜体*" --to "项目组"

# 使用缓存（默认）
/feishu-message-send-lark-cli --text "测试消息"

# 发送到特定用户（同租户私信）
/feishu-message-send-lark-cli --text "私信内容" --user-id ou_xxx
```

---

## 🔧 参数详解

### 通用会话选择参数

| 参数 | 类型 | 默认 | 说明 |
|------|------|------|------|
| `--chat-id` / `-c` | string | None | 直接指定会话 ID（最高优先级） |
| `--interactive` / `-i` | bool | False | 交互式选择（显示最近5个会话） |
| `--to` / `-t` | string | None | 关键词匹配会话名称 |
| `--refresh` / `-r` | bool | False | 强制重新选择，忽略缓存 |

**优先级**：`--chat-id` > `--refresh` > `--to` > `--interactive` > 缓存

### 文件发送特有参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `--file` / `-f` | string | ✅ | 本地文件路径（绝对/相对） |

### 消息发送特有参数

| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `--text` / `-m` | string | ❌ | 纯文本内容（与 `--markdown` 二选一） |
| `--markdown` / `-md` | string | ❌ | Markdown 富文本内容 |
| `--user-id` / `-u` | string | ❌ | 私信接收人 user_id（仅同租户） |

---

## 💾 缓存机制

### 缓存位置
```
~/.hermes/cache/feishu_chat_cache.json
```

### 缓存内容
```json
{
  "last_chat_id": "oc_e92ded0f5dbeecd5601c811bd2247ddf",
  "last_chat_name": "病情讨论组",
  "updated_at": "2026-04-18T10:30:00+08:00"
}
```

### 缓存行为
- 每次交互选择后自动更新
- 无参数调用时自动使用缓存
- `--refresh` 参数强制忽略缓存并重新选择
- 缓存文件损坏或不存在时自动降级为交互选择

---

## 📊 交互选择界面示例

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
请输入会话编号: 1
✅ 已选择: 病情讨论组 (oc_e92ded0f5dbeecd5601c811bd2247ddf)
```

**显示字段说明**：
- `[编号]` - 选择序号（1-5）
- `会话名称` - 群聊名称或用户昵称
- `chat_id` - 会话唯一标识
- `(群聊/私信)` - 会话类型
- `成员数` - 仅群聊显示
- `最后活跃` - 相对时间（刚刚/分钟前/小时前/天前）

---

## 🔍 关键词匹配

### 匹配规则
- **子串匹配**：`--to "病情"` 会匹配"病情讨论组"、"病情分析"等
- **不区分大小写**：`--to "Project"` 和 `--to "project"` 效果相同
- **多结果处理**：匹配到多个会话时，仍进入交互选择（显示匹配的5个）

### 示例

```bash
# 匹配包含"病情"的会话
/feishu-file-send-lark-cli --file report.md --to "病情"

# 匹配包含"项目"的会话
/feishu-message-send-lark-cli --text "进度更新" --to "项目"
```

---

## 🐛 故障排除

### 问题：无法获取会话列表
```
🔍 正在获取会话列表...
[ERROR] lark-cli 执行失败: ...
```
**解决**：
1. 检查 lark-cli 是否已登录：`lark-cli auth list`
2. 重新登录：`lark-cli auth logout && lark-cli auth login`
3. 检查网络连接

### 问题：缓存文件读写失败
```
[WARN] 保存缓存失败: ...
```
**原因**：`~/.hermes/cache/` 目录权限问题  
**解决**：
```bash
mkdir -p ~/.hermes/cache
chmod 755 ~/.hermes/cache
```

### 问题：文件复制失败
```
❌ 无法复制文件到 lark-cli 目录
```
**解决**：
1. 确认 lark-cli 已安装：`which lark-cli`
2. 手动复制：`cp /path/to/file.md $(dirname $(which lark-cli))/`

### 问题：发送失败 `open_id cross app`
**原因**：跨租户 DM 使用了 `--user-id`  
**解决**：改用 `--chat-id`（本技能已自动处理，如遇到请反馈）

---

## 📚 相关文档

- [lark-cli 官方文档](https://github.com/larksuite/lark-cli)
- [Hermes Agent 文档](https://github.com/ai-playground-zzw/hermes-agent)
- [飞书 OpenAPI 文档](https://open.feishu.cn/document/)

---

## 🔄 从 v1.0.0 升级

如果你已安装 v1.0.0 版本：

```bash
# 1. 重新安装技能包（覆盖更新）
cd feishu-cli-messageprocess-skills-package
./scripts/install.sh hermes

# 2. 重启 Hermes（确保加载新代码）
hermes restart

# 3. 验证升级
hermes skills list | grep feishu
# 应显示版本 1.1.0
```

**Breaking Changes**: 无完全向后兼容

**新功能**：所有新参数均为可选，旧用法（指定 `--chat-id`）仍然有效。

---

**版本**: 1.1.0  
**更新**: 2026-04-18  
**作者**: Hermes Community
