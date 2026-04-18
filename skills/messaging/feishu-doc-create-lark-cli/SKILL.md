---
name: feishu-doc-create-lark-cli
description: 使用 lark-cli 创建或更新飞书云文档（支持 Markdown 导入）
version: 1.0.0
---

# Skill: 飞书文档创建/更新（lark-cli 直接调用）

## 用途
通过 lark-cli 命令行创建新文档或更新现有文档内容，支持 Markdown 格式直接导入。

## 前置条件
1. 已安装 lark-cli 并完成设备码登录授权
2. lark-cli 路径：`~/.npm/_npx/.../@larksuite/cli/scripts/run.js`
3. 如需要父文件夹，需提前创建（`docs folder-create`）

## 步骤

### 1. 创建新文档（Markdown）
```bash
# 基础创建（需要先有父文件夹）
node <lark-cli-path>/scripts/run.js docs +create \
  --title "文档标题" \
  --folder <folder_token> \
  --markdown @local_file.md \
  --format json

# 或从标准输入读取
cat report.md | node run.js docs +create --title "报告" --folder <folder_token> --markdown @- --format json
```

返回 `{"doc": {"doc_token": "TAJ8d...", "title": "...", ...}}`，`doc_token` 即 `doc_id`。

### 2. 更新现有文档内容
```bash
# 方式 A：替换整个文档（推荐用于完整重写）
node <lark-cli-path>/scripts/run.js docs +blocks-replace \
  --doc <doc_id> \
  --markdown @local_file.md \
  --format json

# 方式 B：在指定位置插入内容（块操作）
node <lark-cli-path>/scripts/run.js docs +blocks-create \
  --doc <doc_id> \
  --index 1 \
  --markdown @local_file.md
```

### 3. 获取文档信息
```bash
# 查看文档元数据
node <lark-cli-path>/scripts/run.js docs get --doc <doc_id> --format json

# 列出文档块（用于定位插入位置）
node <lark-cli-path>/scripts/run.js docs blocks list --doc <doc_id> --format json
```

## 关键参数说明
- `--title` — 文档标题（创建时必需）
- `--folder` — 父文件夹的 `folder_token`（如 `/` 表示根目录）
- `--markdown @file` — 从本地文件读取 Markdown 内容（`@-` 从 stdin）
- `--doc` / `--doc-id` — 目标文档的 `doc_token`
- `--index` — 块插入位置索引（从 1 开始）
- `+blocks-replace` — 替换整个文档内容（保留文档属性）
- `+blocks-create` — 在指定位置插入新块

## 获取 folder_token 的方法
```bash
# 列出根目录下所有文件夹
node run.js docs folder list --format json

# 递归列出所有可访问文件夹（需权限）
node run.js docs folder tree --format json
```

返回的 `folder_token` 字段即为文件夹标识（如 `fldxxx` 或 `/` 表示根目录）。

## Python 调用示例
```python
import subprocess, shutil, os, json

base = '/Users/sammini/.npm/_npx/.../@larksuite/cli'
run_js = os.path.join(base, 'scripts/run.js')

def create_doc(title: str, md_path: str, folder_token: str = '/') -> str:
    """创建新文档，返回 doc_id"""
    # 复制 Markdown 文件到 lark-cli 工作目录
    dst = os.path.join(base, os.path.basename(md_path))
    shutil.copy2(md_path, dst)

    cmd = [
        'node', run_js, 'docs', '+create',
        '--title', title,
        '--folder', folder_token,
        '--markdown', f'@{os.path.basename(md_path)}',
        '--format', 'json'
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, cwd=base)
    data = json.loads(result.stdout)
    return data['doc']['doc_token']

def update_doc(doc_id: str, md_path: str) -> bool:
    """完整替换文档内容"""
    dst = os.path.join(base, os.path.basename(md_path))
    shutil.copy2(md_path, dst)

    cmd = [
        'node', run_js, 'docs', '+blocks-replace',
        '--doc', doc_id,
        '--markdown', f'@{os.path.basename(md_path)}',
        '--format', 'json'
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, cwd=base)
    return result.returncode == 0
```

## 注意事项
- `--markdown @file` 要求文件在当前工作目录，必须先复制
- 文档标题不能为空，长度建议 ≤ 255 字符
- 更新文档使用 `+blocks-replace` 会清空原有内容（保留标题/权限等元数据）
- 大文件（>5 MB）建议分段插入，避免超时
- 权限要求：`docx:document:write_only` 或 `docx:document:full`（设备码授权时需勾选）
- 飞书文档有配额限制（个人 5000 篇，企业更高），注意清理无用文档

## 故障排查
| 现象 | 原因 | 解决 |
|------|------|------|
| `permission denied` | 缺少文档写权限 | 重新设备码授权，勾选 "文档" 权限范围 |
| `folder not found` | `folder_token` 错误 | 用 `docs folder list` 确认正确值 |
| `file not found` | 文件未复制到工作目录 | 提前 `shutil.copy2` |
| `unknown command "blocks-replace"` | CLI 版本过旧 | 更新 `@larksuite/cli` |
| `request timeout` | 文档过大或网络慢 | 增加 `--timeout` 或分段更新 |

## 与 Hermes 网关的对应关系
- Hermes 网关 `send_document` → 底层仍使用飞书 API（非 lark-cli）
- 本技能直接调用 lark-cli，适合本地脚本/自动化场景
- 两者可并行使用，按需选择

---

**创建时间**: 2026-04-16
**适用场景**: 飞书文档创建、Markdown 导入、批量文档管理
