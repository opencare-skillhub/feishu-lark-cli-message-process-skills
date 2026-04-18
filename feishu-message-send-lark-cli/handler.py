#!/usr/bin/env python3
"""
feishu-message-send-lark-cli 技能处理器
"""

import sys
import os
import json
import argparse
from pathlib import Path

# 添加共享模块路径
SKILLS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SKILLS_DIR))

from _utils.chat_selector import resolve_chat_id, send_message_via_lark


def main():
    parser = argparse.ArgumentParser(description='发送消息到飞书会话')
    parser.add_argument('--text', '-m', help='纯文本消息内容')
    parser.add_argument('--markdown', '-md', help='Markdown 富文本内容')
    parser.add_argument('--chat-id', '-c', help='会话 ID (oc_xxx)')
    parser.add_argument('--user-id', '-u', help='接收人 user_id (仅同租户)')
    parser.add_argument('--interactive', '-i', action='store_true', help='交互式选择会话')
    parser.add_argument('--to', '-t', help='根据会话名称关键词匹配')
    parser.add_argument('--refresh', '-r', action='store_true', help='强制重新选择会话')
    
    args = parser.parse_args()
    
    # 验证消息内容
    if not args.text and not args.markdown:
        print("❌ 必须提供 --text 或 --markdown 参数")
        return 1
    
    # 1. 解析 chat_id（如果使用了 --user-id 则不需要）
    chat_id = None
    if args.user_id:
        # 使用 user_id 模式（同租户私信）
        chat_id = args.user_id
        print(f"💬 使用 user_id 模式发送私信: {chat_id}")
    else:
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
    
    # 2. 确定消息类型和内容
    if args.markdown:
        msg_type = 'markdown'
        content = args.markdown
    else:
        msg_type = 'text'
        content = args.text
    
    # 3. 发送消息
    print(f"📤 正在发送{msg_type}消息到: {chat_id}")
    success, message = send_message_via_lark(chat_id, content, msg_type)
    
    if success:
        print(f"✅ {message}")
        return 0
    else:
        print(f"❌ {message}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
