#!/usr/bin/env python3
"""
Simple CLI for adding messages to group chats
Usage: python group_chat_cli.py --add-message "hello world" --room "my_room"
"""
import sys
import json
import argparse
from pathlib import Path

# Add the project root to path
sys.path.insert(0, str(Path(__file__).parent))

from console_gpt.group_chat import GroupChatManager
from console_gpt.custom_stdout import custom_print


def add_message_cli():
    """CLI interface for adding messages to group chats"""
    parser = argparse.ArgumentParser(description="Add messages to group chat rooms")
    
    # Message content
    parser.add_argument("--add-message", "-m", 
                       help="Message content to add")
    parser.add_argument("--role", "-r", 
                       choices=["user", "assistant", "system"], 
                       default="user",
                       help="Message role (default: user)")
    
    # Room selection
    parser.add_argument("--room", "-R", 
                       help="Room ID or name to add message to")
    parser.add_argument("--list-rooms", "-l", 
                       action="store_true",
                       help="List available rooms")
    
    # JSON input
    parser.add_argument("--json", "-j", 
                       help="Add message from JSON string")
    parser.add_argument("--json-file", "-f", 
                       help="Add message(s) from JSON file")
    
    # Stdin support
    parser.add_argument("--stdin", "-s", 
                       action="store_true",
                       help="Read message from stdin")
    
    args = parser.parse_args()
    
    # Initialize group chat manager
    try:
        manager = GroupChatManager()
    except Exception as e:
        print(f"Error initializing group chat: {e}", file=sys.stderr)
        sys.exit(1)
    
    # List rooms
    if args.list_rooms:
        rooms = manager.list_group_chats()
        if not rooms:
            print("No group chat rooms found.")
        else:
            print("Available rooms:")
            for room in rooms:
                print(f"  {room['room_id']}: {room['room_name']}")
        return
    
    # Determine room
    room_id = None
    if args.room:
        # Check if it's a room ID or name
        rooms = manager.list_group_chats()
        for room in rooms:
            if room['room_id'] == args.room or room['room_name'] == args.room:
                room_id = room['room_id']
                break
        
        if not room_id:
            print(f"Room '{args.room}' not found. Use --list-rooms to see available rooms.", file=sys.stderr)
            sys.exit(1)
    else:
        # Auto-select first room if only one exists
        rooms = manager.list_group_chats()
        if len(rooms) == 1:
            room_id = rooms[0]['room_id']
            print(f"Auto-selected room: {rooms[0]['room_name']}")
        elif len(rooms) == 0:
            print("No rooms available. Create a room first with 'groupchat'.", file=sys.stderr)
            sys.exit(1)
        else:
            print("Multiple rooms available. Specify with --room or use --list-rooms.", file=sys.stderr)
            sys.exit(1)
    
    # Process different input types
    messages = []
    
    if args.json:
        # JSON string input
        try:
            msg_data = json.loads(args.json)
            if isinstance(msg_data, list):
                messages.extend(msg_data)
            else:
                messages.append(msg_data)
        except json.JSONDecodeError as e:
            print(f"Invalid JSON: {e}", file=sys.stderr)
            sys.exit(1)
            
    elif args.json_file:
        # JSON file input
        try:
            with open(args.json_file, 'r', encoding='utf-8') as f:
                msg_data = json.load(f)
                if isinstance(msg_data, list):
                    messages.extend(msg_data)
                else:
                    messages.append(msg_data)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error reading JSON file: {e}", file=sys.stderr)
            sys.exit(1)
            
    elif args.stdin:
        # Read from stdin
        try:
            content = sys.stdin.read().strip()
            if content.startswith('{') or content.startswith('['):
                # Try to parse as JSON
                try:
                    msg_data = json.loads(content)
                    if isinstance(msg_data, list):
                        messages.extend(msg_data)
                    else:
                        messages.append(msg_data)
                except json.JSONDecodeError:
                    # Treat as plain text
                    messages.append({"role": args.role, "content": content})
            else:
                # Plain text
                messages.append({"role": args.role, "content": content})
        except Exception as e:
            print(f"Error reading from stdin: {e}", file=sys.stderr)
            sys.exit(1)
            
    elif args.add_message:
        # Simple text message
        messages.append({"role": args.role, "content": args.add_message})
        
    else:
        print("No message provided. Use --add-message, --json, --json-file, or --stdin.", file=sys.stderr)
        sys.exit(1)
    
    # Validate and add messages
    valid_messages = []
    for msg in messages:
        if not isinstance(msg, dict):
            print(f"Invalid message format: {msg}", file=sys.stderr)
            continue
            
        if 'role' not in msg or 'content' not in msg:
            print(f"Message missing 'role' or 'content': {msg}", file=sys.stderr)
            continue
            
        if msg['role'] not in ['user', 'assistant', 'system']:
            print(f"Invalid role '{msg['role']}': {msg}", file=sys.stderr)
            continue
            
        valid_messages.append(msg)
    
    if not valid_messages:
        print("No valid messages to add.", file=sys.stderr)
        sys.exit(1)
    
    # Add messages to room
    try:
        if len(valid_messages) == 1:
            success = manager.add_message(room_id, valid_messages[0])
        else:
            success = manager.add_messages(room_id, valid_messages)
            
        if success:
            print(f"Successfully added {len(valid_messages)} message(s) to room.")
        else:
            print("Failed to add messages.", file=sys.stderr)
            sys.exit(1)
            
    except Exception as e:
        print(f"Error adding messages: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    add_message_cli()