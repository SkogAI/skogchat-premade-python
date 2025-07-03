#!/usr/bin/env python3
"""
Simple Group Chat Prototype
Reads messages from messages.jsonl and displays them with sender names.
Sends user messages via skogcli agent send command.
"""

import json
import os
import subprocess
import sys
import time
import threading
from pathlib import Path


class SimpleGroupChat:
    def __init__(self, messages_file="messages.jsonl"):
        self.messages_file = Path(messages_file)
        self.last_position = 0
        self.running = True
        
        # Create messages file if it doesn't exist
        if not self.messages_file.exists():
            self.messages_file.touch()
            print(f"Created {self.messages_file}")
            
    def read_new_messages(self):
        """Read new messages from the file since last position."""
        try:
            with open(self.messages_file, 'r') as f:
                f.seek(self.last_position)
                new_lines = f.readlines()
                self.last_position = f.tell()
                
            for line in new_lines:
                line = line.strip()
                if line:
                    try:
                        message = json.loads(line)
                        self.display_message(message)
                    except json.JSONDecodeError:
                        print(f"[ERROR] Invalid JSON: {line}")
                        
        except FileNotFoundError:
            pass  # File doesn't exist yet
            
    def display_message(self, message):
        """Display a message with sender name."""
        name = message.get("name", "unknown")
        content = message.get("content", "")
        
        print(f"[{name}]: {content}")
            
    def send_message(self, content, agent_name):
        """Send a message via skogcli agent send command."""
        try:
            cmd = ["skogcli", "agent", "send", "--agent", agent_name, content]
            print(f"[SENDING] to {agent_name}: {content}")
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print(f"[SENT] ✓")
            return True
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Failed to send message: {e}")
            return False
        except FileNotFoundError:
            print(f"[ERROR] skogcli command not found")
            return False
            
    def parse_user_input(self, user_input):
        """Parse user input and determine agent and message."""
        if user_input.startswith('@'):
            # Parse @agent message format
            parts = user_input[1:].split(' ', 1)
            if len(parts) >= 2:
                agent_name, message = parts[0], parts[1]
            else:
                agent_name, message = parts[0], ""
        else:
            # Default agent
            agent_name = "claude"
            message = user_input
            
        return message, agent_name
    
    def file_watcher(self):
        """Background thread to watch for new messages."""
        while self.running:
            self.read_new_messages()
            time.sleep(0.5)  # Check every 500ms
    
    def run(self):
        """Main group chat loop."""
        print("=== Simple Group Chat Prototype ===")
        print(f"Watching: {self.messages_file.resolve()}")
        print("Commands:")
        print("  '@agent message' - send to specific agent")
        print("  'message' - send to claude (default)")
        print("  'quit' - exit")
        print("Add messages: echo '{\"name\": \"claude\", \"content\": \"hello\"}' >> messages.jsonl")
        print()
        
        # Start file watcher in background thread
        watcher_thread = threading.Thread(target=self.file_watcher, daemon=True)
        watcher_thread.start()
        
        try:
            while True:
                try:
                    user_input = input("[you]: ").strip()
                    
                    if user_input.lower() in ['quit', 'exit', 'bye']:
                        break
                        
                    if not user_input:
                        continue
                        
                    message, agent_name = self.parse_user_input(user_input)
                    if message:
                        # Log our own message to the file
                        our_message = {"name": "you", "content": user_input}
                        with open(self.messages_file, 'a') as f:
                            f.write(json.dumps(our_message) + '\n')
                            
                        # Send the message
                        self.send_message(message, agent_name)
                        
                except EOFError:
                    break
                except KeyboardInterrupt:
                    break
                    
        finally:
            self.running = False
            print("\n[INFO] Chat ended.")


if __name__ == "__main__":
    chat = SimpleGroupChat()
    chat.run()