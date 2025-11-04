#!/usr/bin/env python3
"""
Group Chat UI for skogai
Reads messages from group_messages.jsonl and displays them with sender names.
Sends user messages via skogcli agent send command.
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

from rich.console import Console

# Import existing display functions
from console_gpt.custom_stdout import custom_print
from console_gpt.prompts.assistant_prompt import assistance_reply
from console_gpt.prompts.user_prompt import user_prompt


class GroupChat:
    def __init__(self, messages_file="group_messages.skogchat"):
        self.messages_file = Path(messages_file)
        self.console = Console()
        self.last_position = 0

        # Create messages file if it doesn't exist
        if not self.messages_file.exists():
            self.messages_file.touch()
            
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
                    except json.JSONDecodeError as e:
                        custom_print("error", f"Invalid JSON in message: {line}")
                        
        except FileNotFoundError:
            pass  # File doesn't exist yet
            
    def display_message(self, message):
        """Display a message from .skogchat format or legacy format."""
        # Support both .skogchat format (from, to, eid, created-at, parent)
        # and legacy format (role, name)

        # Get sender - try 'from' first (skogchat), fall back to 'name' or 'role'
        sender = message.get("from") or message.get("name") or message.get("role", "assistant")
        content = message.get("content", "")

        # Ignore skogchat fields we don't need: eid, to, created-at, parent

        if sender == "user":
            custom_print("user", f"{sender}: {content}")
        else:
            # Display assistant/other messages using existing function
            assistance_reply(content, sender)
            
    def send_message(self, content, agent_name):
        """Send a message via skogcli agent send command."""
        try:
            cmd = ["skogcli", "agent", "send", "--agent", agent_name, content]
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            return True
        except subprocess.CalledProcessError as e:
            custom_print("error", f"Failed to send message: {e}")
            return False
        except FileNotFoundError:
            custom_print("error", "skogcli command not found")
            return False
            
    def get_user_input(self):
        """Get user input and determine which agent to send to."""
        try:
            # Use existing user prompt function
            user_input = user_prompt()
            
            if not user_input:  # Handle None/empty input (Ctrl+C, etc.)
                return None, None
                
            if user_input.lower() in ['quit', 'exit', 'bye']:
                return None, None
                
            # Simple format: "message" or "@agent message"
            if user_input.startswith('@'):
                # Parse @agent message format
                parts = user_input[1:].split(' ', 1)
                if len(parts) >= 2:
                    agent_name, message = parts[0], parts[1]
                else:
                    agent_name, message = parts[0], ""
            else:
                # Default agent (you could make this configurable)
                agent_name = "claude"
                message = user_input
                
            return message, agent_name
            
        except KeyboardInterrupt:
            return None, None
            
    def run(self):
        """Main group chat loop."""
        custom_print("info", "Group Chat started. Type 'quit' to exit.")
        custom_print("info", f"Watching: {self.messages_file.resolve()}")
        custom_print("info", "Format: '@agent message' or just 'message' (defaults to claude)")
        custom_print("info", "Supports .skogchat format: {\"from\": \"claude\", \"to\": \"user\", \"content\": \"hi\", ...}")
        
        try:
            while True:
                # Check for new messages
                self.read_new_messages()
                
                # Get user input (non-blocking would be better, but this works for PoC)
                message, agent_name = self.get_user_input()
                
                if message is None:  # quit/exit
                    break
                    
                if message.strip():  # Don't send empty messages
                    if self.send_message(message, agent_name):
                        # Optionally log our own message to the file
                        our_message = {
                            "role": "user", 
                            "content": message, 
                            "name": "you"
                        }
                        with open(self.messages_file, 'a') as f:
                            f.write(json.dumps(our_message) + '\n')
                            
                # Small delay to prevent busy waiting
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            custom_print("info", "\nGroup chat ended.")


if __name__ == "__main__":
    chat = GroupChat()
    chat.run()