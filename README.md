# Hermes 飞书技能包集合

位于 `~/.hermes/skills/messaging/` 的飞书集成技能包，基于 `lark-cli` 命令行工具实现。

## 技能包列表

| 技能包 | 版本 | 说明 |
|--------|------|------|
| `feishu-doc-create-lark-cli` | 1.2.0 | 创建/更新飞书云文档（Markdown 导入） |
| `feishu-file-send-lark-cli` | 1.2.0 | 发送本地文件到飞书会话 |
| `feishu-message-send-lark-cli` | 1.2.0 | 发送文本/富文本消息到飞书会话 |

## 前置条件

1. **安装 lark-cli**（推荐 1.0.14+）
   ```bash
   npm update -g @larksuite/cli
   # 或首次安装
   npm install -g @larksuite/cli
   ```

2. **设备码登录授权**
   ```bash
   lark-cli login
   # 浏览器打开显示的 URL，输入设备码完成授权
   ```

3. **确认 lark-cli 路径**
   ```bash
   which lark-cli
   # 典型路径: ~/.npm/_npx/.../@larksuite/cli/bin/lark-cli
   # 或: /usr/local/bin/lark-cli
   ```

## 快速开始

### 1. 创建飞书在线文档（Markdown 导入）

**🆕 本功能为 v1.2.0 新增核心能力**

#### 步骤 1: 获取 `folder_token`

`folder_token` 是飞书知识库空间（Space）中文件夹的标识。有两种获取方式：

**方法 A：通过 lark-cli API 直接查询（推荐）**
```bash
# 列出所有可访问的知识库空间
lark-cli api GET /open-apis/wiki/v2/spaces

# 返回示例:
# {
#   "spaces": [
#     {
#       "name": "<YOUR_SPACE_NAME>",
#       "space_id": "<YOUR_SPACE_ID>",
#       "root_folder_token": "<YOUR_FOLDER_TOKEN>"
#     }
#   ]
# }

# 获取空间根节点信息（可选，用于验证）
lark-cli api GET /open-apis/wiki/v2/spaces/{space_id}/nodes
```

**方法 B：通过飞书网页端查看**
1. 打开目标知识库页面
2. 浏览器开发者工具 → Network → 过滤 `wiki` API
3. 查找 `space_id` 和 `node_token`（即 `folder_token`）

#### 步骤 2: 创建文档

```bash
# 基本语法
lark-cli docs +create \
  --title "文档标题" \
  --folder-token "<YOUR_FOLDER_TOKEN>" \
  --markdown "@本地文件.md"
```

**重要参数说明：**
- `--title`：文档标题（必需，建议 ≤255 字符）
- `--folder-token`：目标文件夹 token（必需）。**可以是任意有写权限的节点 token**（包括文档节点），根节点 token 已验证有效。
- `--markdown @file`：Markdown 文件路径（必需）。**文件必须位于当前工作目录**，否则需先复制。
- `--format`：**已移除** — `docs +create` 和 `im +messages-send` 子命令不支持此参数，添加会导致 Usage 错误。

**成功返回示例：**
```json
{
  "doc": {
    "doc_token": "<YOUR_DOC_TOKEN>",
    "title": "<DOC_TITLE>",
    "url": "https://www.feishu.cn/docx/<YOUR_DOC_TOKEN>"
  }
}
```

`doc_token` 即文档 ID，`url` 是访问链接。

#### 步骤 3: Python 调用示例

```python
import subprocess, shutil, os, json
from pathlib import Path

# lark-cli 路径（根据实际安装位置调整）
LARK_CLI_BASE = Path.home() / '.npm' / '_npx' / '@larksuite' / 'cli'
RUN_JS = LARK_CLI_BASE / 'scripts' / 'run.js'

def create_feishu_doc(title: str, md_path: str, folder_token: str) -> dict:
    """创建飞书文档，返回 doc_token 和 url"""
    md_file = Path(md_path)
    if not md_file.exists():
        raise FileNotFoundError(f"Markdown 文件不存在: {md_path}")

    # 复制 Markdown 文件到 lark-cli 工作目录（--markdown @file 要求）
    dst = LARK_CLI_BASE / md_file.name
    shutil.copy2(md_file, dst)

    cmd = [
        'node', str(RUN_JS), 'docs', '+create',
        '--title', title,
        '--folder-token', folder_token,
        '--markdown', f'@{md_file.name}'
        # 注意：不添加 --format json
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=60,
        cwd=LARK_CLI_BASE
    )

    if result.returncode != 0:
        raise RuntimeError(f"创建失败: {result.stderr}")

    data = json.loads(result.stdout)
    doc = data['doc']
    return {
        'doc_id': doc['doc_token'],
        'title': doc['title'],
        'url': doc.get('url', '')
    }

# 使用示例
doc_info = create_feishu_doc(
    title="<DOC_TITLE>",
    md_path="/Users/sammini/report.md",
    folder_token="<YOUR_FOLDER_TOKEN>"
)
print(f"✅ 文档创建成功: {doc_info['url']}")
```

#### 更新现有文档

```bash
# 完全替换文档内容（保留标题/权限等元数据）
lark-cli docs +blocks-replace \
  --doc "<YOUR_DOC_TOKEN>" \
  --markdown "@更新后的文件.md"
```

### 2. 发送文件到飞书会话

详见 `feishu-file-send-lark-cli` 技能包文档。

### 3. 发送消息到飞书会话

详见 `feishu-message-send-lark-cli` 技能包文档。

## 已验证的配置

| 项目 | 值 |
|------|-----|
| lark-cli 版本 | 1.0.14 |
| 知识库空间 | <YOUR_SPACE_NAME> |
| space_id | <YOUR_SPACE_ID> |
| 根节点 folder_token | <YOUR_FOLDER_TOKEN> |

## ⚠️ 安全提醒

**切勿将真实 token、doc_id、space_id 提交到版本控制系统！**

- `folder_token`、`space_id`、`doc_token` 属于敏感凭证
- 示例代码中的占位符 `<YOUR_XXX>` 需替换为实际值
- 建议将敏感信息存储在环境变量或配置文件中，勿硬编码
- 推送前检查是否有敏感信息泄露（可使用 `git grep` 或 `trufflehog`）

## 故障排查

### 错误: `Unknown flag: --format`
**原因**：`docs +create` 或 `im +messages-send` 子命令不支持 `--format` 参数。  
**解决**：从命令中移除 `--format json`。

### 错误: `Markdown file not found`
**原因**：`--markdown @file` 要求文件位于 lark-cli 当前工作目录。  
**解决**：使用 `shutil.copy2()` 复制文件到 `Path.cwd()` 或 `lark-cli` 安装目录。

### 错误: `folder_token invalid`
**原因**：token 无效或当前账号无写权限。  
**解决**：
1. 通过 `lark-cli api GET /open-apis/wiki/v2/spaces` 重新获取
2. 确认 space_id 对应的知识库在账号「可编辑」列表中
3. 根节点 token (`/`) 或根节点 token 在任意有写权限的空间中均有效

### 权限不足
某些 API（如 `wiki.nodes.list`）需要管理员权限。如遇 403 错误，联系飞书管理员授予「知识库管理」权限。

## 更新日志

### v1.2.0（2026-04-18）
- ✨ 新增：飞书在线文档创建完整功能（Markdown 导入）
- ✨ 新增：`folder_token` 获取的官方 API 方法
- 🔧 修复：移除 `--format` 参数（不兼容子命令）
- 🔧 修复：文件复制到当前工作目录的路径处理
- 📝 文档：完整的使用说明和 Python 调用示例

### v1.1.0
- 文件发送技能包：会话智能选择和缓存机制
- 消息发送技能包：富文本（Markdown）消息支持

### v1.0.0
- 初始版本：基础飞书文档创建/更新功能

## 相关链接

- [lark-cli 官方文档](https://open.feishu.cn/document/ukTMukTMukTM/uAjLw4CMzUjLwIzhN)
- [飞书开放 API - 知识库](https://open.feishu.cn/document/ukTMukTMukTM/uUnz4UjL2QzL24iN3IjN)
- Hermes Agent 文档：`~/.hermes/docs/`
