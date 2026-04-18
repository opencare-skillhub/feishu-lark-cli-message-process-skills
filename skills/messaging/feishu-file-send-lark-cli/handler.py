#!/usr/bin/env python3
"""
feishu-file-send-lark-cli 技能处理器
"""

import sys
import os
import json
import argparse
from pathlib import Path

# 添加共享模块路径
SKILLS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SKILLS_DIR))

from _utils.chat_selector import resolve_chat_id, copy_file_to_lark_cli_dir, send_file_via_lark


def main():
    parser = argparse.ArgumentParser(description='发送本地文件到飞书会话')
    parser.add_argument('--file', '-f', required=True, help='本地文件路径')
    parser.add_argument('--chat-id', '-c', help='会话 ID (oc_xxx)')
    parser.add_argument('--interactive', '-i', action='store_true', help='交互式选择会话')
    parser.add_argument('--to', '-t', help='根据会话名称关键词匹配')
    parser.add_argument('--refresh', '-r', action='store_true', help='强制重新选择会话')
    
    args = parser.parse_args()
    
    # 1. 解析 chat_id
    chat_id, error = resolve_chat_id(
        chat_id=args.chat_id,
        keyword=args.to,
        interactive=args.interactive,
        refresh=args.refresh,
        max_results=5
    )
    
    if error:
        print(f"❌ {error}")
        return 1
    
    if not chat_id:
        print("❌ 无法确定目标会话")
        return 1
    
    # 2. 发送文件
    print(f"📤 正在发送文件到会话: {chat_id}")
    success, message = send_file_via_lark(chat_id, args.file)
    
    if success:
        print(f"✅ {message}")
        return 0
    else:
        print(f"❌ {message}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
