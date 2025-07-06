"""
Group Chat Module for Multi-User Shared Conversations
Handles shared group chats where multiple users can participate with merged JSON histories.
"""
import json
import os
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path

from console_gpt.config_manager import fetch_variable, _join_and_check
from console_gpt.custom_stdout import custom_print


@dataclass
class GroupChatMetadata:
    """Metadata for a group chat room"""
    room_id: str
    room_name: str
    participants: List[str]
    created_at: float
    last_activity: float
    description: Optional[str] = None


class GroupChatManager:
    """Manages shared group chat functionality"""
    
    def __init__(self):
        self.base_path = self._get_group_chat_path()
        self.current_username = self._get_current_username()
        
    def _get_group_chat_path(self) -> str:
        """Get the path to group chat storage directory"""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(base_dir)
        return _join_and_check(project_root, "group_chats", create="folder")
    
    def _get_current_username(self) -> str:
        """Get the current user's username"""
        # Try to get from config first
        username = fetch_variable("defaults", "username")
        if username:
            return username
            
        # Fallback to environment or system username
        username = os.environ.get("USER") or os.environ.get("USERNAME") or "unknown_user"
        return username
    
    def create_group_chat(self, room_name: str, participants: List[str], description: Optional[str] = None) -> str:
        """Create a new group chat room"""
        room_id = f"group_{int(time.time())}_{room_name.replace(' ', '_').lower()}"
        
        # Create metadata
        metadata = GroupChatMetadata(
            room_id=room_id,
            room_name=room_name,
            participants=participants,
            created_at=time.time(),
            last_activity=time.time(),
            description=description
        )
        
        # Create room directory
        room_path = os.path.join(self.base_path, room_id)
        os.makedirs(room_path, exist_ok=True)
        
        # Save metadata
        metadata_path = os.path.join(room_path, "metadata.json")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(metadata), f, indent=2)
            
        # Initialize empty chat history
        history_path = os.path.join(room_path, "chat_history.json")
        with open(history_path, 'w', encoding='utf-8') as f:
            json.dump([], f, indent=2)
            
        custom_print("ok", f"Created group chat room: {room_name} (ID: {room_id})")
        return room_id
    
    def list_group_chats(self) -> List[Dict[str, Any]]:
        """List all available group chat rooms"""
        rooms = []
        
        if not os.path.exists(self.base_path):
            return rooms
            
        for room_dir in os.listdir(self.base_path):
            room_path = os.path.join(self.base_path, room_dir)
            if os.path.isdir(room_path):
                metadata_path = os.path.join(room_path, "metadata.json")
                if os.path.exists(metadata_path):
                    try:
                        with open(metadata_path, 'r', encoding='utf-8') as f:
                            metadata = json.load(f)
                            rooms.append(metadata)
                    except Exception as e:
                        custom_print("error", f"Failed to load metadata for room {room_dir}: {e}")
                        
        return sorted(rooms, key=lambda x: x.get('last_activity', 0), reverse=True)
    
    def add_message(self, room_id: str, message: Dict[str, Any]) -> bool:
        """Add a standard OpenAI format message to a group chat room"""
        room_path = os.path.join(self.base_path, room_id)
        
        if not os.path.exists(room_path):
            custom_print("error", f"Group chat room not found: {room_id}")
            return False
            
        history_path = os.path.join(room_path, "chat_history.json")
        
        # Load existing history
        try:
            with open(history_path, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            history = []
            
        # Add message directly (standard OpenAI format)
        history.append(message)
        
        # Save updated history
        try:
            with open(history_path, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
                
            # Update last activity in metadata
            self._update_room_activity(room_id)
            return True
            
        except Exception as e:
            custom_print("error", f"Failed to save message: {e}")
            return False
    
    def get_chat_history(self, room_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get chat history for a room"""
        room_path = os.path.join(self.base_path, room_id)
        history_path = os.path.join(room_path, "chat_history.json")
        
        if not os.path.exists(history_path):
            return []
            
        try:
            with open(history_path, 'r', encoding='utf-8') as f:
                history = json.load(f)
                
            if limit:
                history = history[-limit:]
                
            return history
            
        except Exception as e:
            custom_print("error", f"Failed to load chat history: {e}")
            return []
    
    def add_messages(self, room_id: str, messages: List[Dict[str, Any]]) -> bool:
        """Add multiple standard OpenAI format messages to a group chat room"""
        room_path = os.path.join(self.base_path, room_id)
        
        if not os.path.exists(room_path):
            custom_print("error", f"Group chat room not found: {room_id}")
            return False
            
        history_path = os.path.join(room_path, "chat_history.json")
        
        # Load existing history
        try:
            with open(history_path, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            history = []
            
        # Add all messages directly (standard OpenAI format)
        history.extend(messages)
        
        # Save updated history
        try:
            with open(history_path, 'w', encoding='utf-8') as f:
                json.dump(history, f, indent=2, ensure_ascii=False)
                
            self._update_room_activity(room_id)
            custom_print("ok", f"Added {len(messages)} messages to group chat")
            return True
            
        except Exception as e:
            custom_print("error", f"Failed to add messages: {e}")
            return False
    
    def export_for_ai_models(self, room_id: str, include_metadata: bool = False) -> List[Dict[str, Any]]:
        """Export group chat history in standard OpenAI format for AI models"""
        history = self.get_chat_history(room_id)
        
        ai_format = []
        for msg in history:
            # Convert to standard format
            ai_msg = {
                "role": msg["role"],
                "content": msg["content"]
            }
            
            # Add optional fields if present
            if msg.get("tool_calls"):
                ai_msg["tool_calls"] = msg["tool_calls"]
            if msg.get("reasoning_content"):
                ai_msg["reasoning_content"] = msg["reasoning_content"]
                
            # Add metadata as content suffix if requested
            if include_metadata and msg["role"] in ["user", "assistant"]:
                metadata_suffix = f"\n\n*[{msg['username']} - {datetime.fromtimestamp(msg['timestamp']).strftime('%Y-%m-%d %H:%M:%S')}]*"
                ai_msg["content"] += metadata_suffix
                
            ai_format.append(ai_msg)
            
        return ai_format
    
    def _update_room_activity(self, room_id: str):
        """Update the last activity timestamp for a room"""
        room_path = os.path.join(self.base_path, room_id)
        metadata_path = os.path.join(room_path, "metadata.json")
        
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    
                metadata['last_activity'] = time.time()
                
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2)
                    
            except Exception as e:
                custom_print("error", f"Failed to update room activity: {e}")
    
    def join_room(self, room_id: str) -> bool:
        """Join a group chat room (add current user to participants)"""
        room_path = os.path.join(self.base_path, room_id)
        metadata_path = os.path.join(room_path, "metadata.json")
        
        if not os.path.exists(metadata_path):
            custom_print("error", f"Room not found: {room_id}")
            return False
            
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                
            if self.current_username not in metadata['participants']:
                metadata['participants'].append(self.current_username)
                
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2)
                    
                custom_print("ok", f"Joined room: {metadata['room_name']}")
                
            return True
            
        except Exception as e:
            custom_print("error", f"Failed to join room: {e}")
            return False