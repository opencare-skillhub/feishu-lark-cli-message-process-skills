#!/usr/bin/env python3
"""
飞书会话选择器 - 共享工具模块
提供会话列表获取、交互选择、缓存管理功能
"""

import json
import subprocess
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Tuple

# 缓存文件路径
CACHE_DIR = Path.home() / '.hermes' / 'cache'
CACHE_FILE = CACHE_DIR / 'feishu_chat_cache.json'
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def run_lark_cli(args: List[str], timeout: int = 30) -> Optional[dict]:
    """执行 lark-cli 命令并返回 JSON 结果"""
    try:
        cmd = ['lark-cli'] + args
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=Path.home()
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            print(f"[ERROR] lark-cli 执行失败: {result.stderr[:200]}")
            return None
    except Exception as e:
        print(f"[ERROR] 执行 lark-cli 时出错: {e}")
        return None


def get_recent_chats(limit: int = 10) -> List[Dict]:
    """获取最近活跃的会话列表"""
    result = run_lark_cli(['im', '+messages-search', '--query', '', '--format', 'json', '--page-size', str(limit*2)])
    if not result:
        return []
    
    chats = []
    seen_chat_ids = set()
    
    for msg in result.get('messages', []):
        chat_id = msg.get('chat_id')
        if not chat_id or chat_id in seen_chat_ids:
            continue
        
        seen_chat_ids.add(chat_id)
        
        chat_info = msg.get('chat_info', {})
        chats.append({
            'chat_id': chat_id,
            'name': chat_info.get('name', '未知会话'),
            'chat_type': 'group' if chat_info.get('chat_type') == 'group' else 'private',
            'member_count': chat_info.get('member_count', 0),
            'last_message_time': msg.get('create_time', ''),
            'last_message_text': msg.get('body', {}).get('text', '')[:30],
        })
        
        if len(chats) >= limit:
            break
    
    return chats


def format_relative_time(iso_time: str) -> str:
    """将 ISO 时间转换为相对时间"""
    try:
        if ' ' in iso_time:
            dt_str = iso_time.split('+')[0].strip()
            dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
        else:
            dt = datetime.fromisoformat(iso_time.replace('Z', '+00:00'))
        
        now = datetime.now()
        diff = now - dt
        seconds = diff.total_seconds()
        
        if seconds < 60:
            return "刚刚"
        elif seconds < 3600:
            return f"{int(seconds//60)}分钟前"
        elif seconds < 86400:
            return f"{int(seconds//3600)}小时前"
        elif seconds < 604800:
            return f"{int(seconds//86400)}天前"
        else:
            return dt.strftime('%m-%d')
    except Exception:
        return "未知时间"


def load_cache() -> Optional[Dict]:
    """加载缓存的 chat_id"""
    try:
        if CACHE_FILE.exists():
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return None


def save_cache(chat_id: str, chat_name: str = '') -> None:
    """保存 chat_id 到缓存"""
    cache = {
        'last_chat_id': chat_id,
        'last_chat_name': chat_name,
        'updated_at': datetime.now().isoformat()
    }
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[WARN] 保存缓存失败: {e}")


def find_chat_by_keyword(chats: List[Dict], keyword: str) -> List[Dict]:
    """根据关键词查找会话（子串匹配，不区分大小写）"""
    if not keyword:
        return chats[:5]
    
    keyword_lower = keyword.lower()
    matched = []
    for chat in chats:
        name = chat.get('name', '').lower()
        if keyword_lower in name:
            matched.append(chat)
    
    matched.sort(key=lambda x: x.get('last_message_time', ''), reverse=True)
    return matched[:5]


def interactive_select_chat(chats: List[Dict], prompt: str = "请选择会话") -> Optional[str]:
    """交互式选择会话（显示最近5个）"""
    if not chats:
        print("[ERROR] 没有可用的会话")
        return None
    
    print(f"\n{'='*50}")
    print(f"📱 {prompt}")
    print(f"{'='*50}")
    
    for i, chat in enumerate(chats, 1):
        chat_id = chat['chat_id']
        name = chat['name']
        last_time = format_relative_time(chat.get('last_message_time', ''))
        chat_type = '群聊' if chat.get('chat_type') == 'group' else '私信'
        member_count = chat.get('member_count', 0)
        
        if chat_type == '群聊':
            print(f"  [{i}] {name} {chat_id} ({chat_type},{member_count}人) {last_time}")
        else:
            print(f"  [{i}] {name} {chat_id} ({chat_type}) {last_time}")
    
    print(f"  [0] 取消操作")
    print(f"{'='*50}")
    
    while True:
        try:
            choice = input("请输入会话编号: ").strip()
            if choice == '0':
                return None
            
            idx = int(choice) - 1
            if 0 <= idx < len(chats):
                selected = chats[idx]
                chat_id = selected['chat_id']
                chat_name = selected['name']
                print(f"✅ 已选择: {chat_name} ({chat_id})")
                return chat_id
            else:
                print(f"❌ 无效编号，请输入 0-{len(chats)}")
        except ValueError:
            print("❌ 请输入数字编号")
        except KeyboardInterrupt:
            print("\n❌ 操作取消")
            return None


def resolve_chat_id(
    chat_id: Optional[str] = None,
    keyword: Optional[str] = None,
    interactive: bool = False,
    refresh: bool = False,
    max_results: int = 5
) -> Tuple[Optional[str], str]:
    """
    解析并确定目标 chat_id
    
    优先级:
        1. 显式指定 chat_id → 直接返回
        2. refresh=True → 忽略缓存，重新选择
        3. keyword 匹配 → 列出匹配的会话供选择
        4. interactive=True → 列出最近会话供选择
        5. 缓存存在 → 使用缓存的 chat_id
        6. 以上都不行 → 交互选择最近5个会话
    
    返回: (chat_id, error_message)
    """
    # 1. 显式指定
    if chat_id:
        return chat_id, ""
    
    # 2. 尝试加载缓存
    cache = None if refresh else load_cache()
    if cache and not keyword and not interactive:
        cached_chat_id = cache.get('last_chat_id')
        if cached_chat_id:
            print(f"💾 使用缓存的会话: {cache.get('last_chat_name', '未知')} ({cached_chat_id})")
            return cached_chat_id, ""
    
    # 3. 获取最近会话列表
    print("🔍 正在获取会话列表...")
    chats = get_recent_chats(limit=max_results * 2)
    if not chats:
        return None, "无法获取会话列表，请检查 lark-cli 是否已登录"
    
    # 4. 关键词匹配
    if keyword:
        matched = find_chat_by_keyword(chats, keyword)
        if not matched:
            return None, f"未找到包含关键词 '{keyword}' 的会话"
        if len(matched) == 1:
            chat = matched[0]
            print(f"✅ 自动匹配: {chat['name']} ({chat['chat_id']})")
            return chat['chat_id'], ""
        else:
            chats = matched[:max_results]
            interactive = True
    
    # 5. 交互选择（默认只显示5个）
    if interactive or (not chat_id and not keyword):
        selected_chats = chats[:max_results]
        chat_id = interactive_select_chat(selected_chats)
        if chat_id:
            chat_name = next((c['name'] for c in chats if c['chat_id'] == chat_id), '')
            save_cache(chat_id, chat_name)
            return chat_id, ""
        else:
            return None, "用户取消选择"
    
    return None, "无法确定目标会话"


def copy_file_to_lark_cli_dir(file_path: str) -> Tuple[bool, str, str]:
    """将文件复制到 lark-cli 工作目录"""
    try:
        src = Path(file_path).resolve()
        if not src.exists():
            return False, str(src), ""
        
        result = subprocess.run(['which', 'lark-cli'], capture_output=True, text=True)
        if result.returncode == 0:
            lark_cli_path = Path(result.stdout.strip()).parent
            dst = lark_cli_path / src.name
            shutil.copy2(str(src), str(dst))
            return True, str(src), str(dst)
        else:
            return False, str(src), ""
    except Exception as e:
        print(f"[ERROR] 复制文件失败: {e}")
        return False, str(src), ""


def send_file_via_lark(chat_id: str, file_path: str) -> Tuple[bool, str]:
    """使用 lark-cli 发送文件"""
    success, src, dst = copy_file_to_lark_cli_dir(file_path)
    if not success:
        return False, f"无法复制文件到 lark-cli 目录: {file_path}"
    
    try:
        cmd = [
            'lark-cli', 'im', '+messages-send',
            '--as', 'user',
            '--chat-id', chat_id,
            '--file', Path(dst).name,
            '--format', 'json'
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            resp = json.loads(result.stdout)
            msg_id = resp.get('data', {}).get('message_id', 'N/A')
            return True, f"文件已发送 (消息ID: {msg_id})"
        else:
            return False, f"发送失败: {result.stderr[:200]}"
    except Exception as e:
        return False, f"执行 lark-cli 时出错: {e}"


def send_message_via_lark(chat_id: str, content: str, msg_type: str = 'text') -> Tuple[bool, str]:
    """使用 lark-cli 发送消息"""
    try:
        cmd = [
            'lark-cli', 'im', '+messages-send',
            '--as', 'user',
            '--chat-id', chat_id,
            '--format', 'json'
        ]
        
        if msg_type == 'text':
            cmd.extend(['--content', json.dumps({'text': content}, ensure_ascii=False)])
        elif msg_type == 'markdown':
            cmd.extend(['--markdown', content])
        else:
            return False, f"不支持的消息类型: {msg_type}"
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            resp = json.loads(result.stdout)
            msg_id = resp.get('data', {}).get('message_id', 'N/A')
            return True, f"消息已发送 (消息ID: {msg_id})"
        else:
            return False, f"发送失败: {result.stderr[:200]}"
    except Exception as e:
        return False, f"执行 lark-cli 时出错: {e}"
