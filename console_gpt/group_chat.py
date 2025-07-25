"""
Group Chat Module for Multi-User Shared Conversations
Handles shared group chats where multiple users can participate with merged JSON histories.
"""
import json
import os
import time
import threading
from datetime import datetime
from typing import Dict, List, Optional, Any, TypedDict
from dataclasses import dataclass, asdict
from pathlib import Path
from contextlib import contextmanager

from console_gpt.config_manager import fetch_variable, _join_and_check
from console_gpt.custom_stdout import custom_print


class GroupChatMessage(TypedDict, total=False):
    """Type definition for group chat messages"""
    role: str  # Required: 'user', 'assistant', or 'system'
    content: str  # Required: message content
    username: str  # Optional: sender username
    timestamp: float  # Optional: message timestamp
    message_id: str  # Optional: unique message identifier
    tool_calls: Optional[List[Any]]  # Optional: tool calls made by the message
    reasoning_content: Optional[str]  # Optional: reasoning process for AI responses


@dataclass
class GroupChatMetadata:
    """Metadata for a group chat room"""
    room_id: str
    room_name: str
    participants: List[str]
    created_at: float
    last_activity: float
    description: Optional[str] = None
    max_history: Optional[int] = None  # Maximum number of messages to keep
    cleanup_age: Optional[int] = None  # Age in days after which to clean up messages


class GroupChatError(Exception):
    """Base exception for group chat errors"""
    pass


class RoomNotFoundError(GroupChatError):
    """Raised when attempting to access a non-existent room"""
    pass


class InvalidMessageError(GroupChatError):
    """Raised when message format is invalid"""
    pass


class GroupChatManager:
    """Manages shared group chat functionality"""
    
    def __init__(self):
        self.base_path = self._get_group_chat_path()
        self.current_username = self._get_current_username()
        self._locks = {}  # Room-specific locks
        self._global_lock = threading.Lock()
        
    @contextmanager
    def _room_lock(self, room_id: str):
        """Get or create a lock for a specific room"""
        with self._global_lock:
            if room_id not in self._locks:
                self._locks[room_id] = threading.Lock()
            lock = self._locks[room_id]
            
        with lock:
            yield
    
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
    
    def validate_message(self, message: Dict[str, Any]) -> bool:
        """Validate message format"""
        if not isinstance(message, dict):
            return False
            
        # Check required fields
        required_fields = ['role', 'content']
        if not all(field in message for field in required_fields):
            return False
            
        # Validate role
        valid_roles = ['user', 'assistant', 'system']
        if message['role'] not in valid_roles:
            return False
            
        # Validate content
        if not isinstance(message['content'], str) or not message['content'].strip():
            return False
            
        return True
    
    def prepare_message(self, message: Dict[str, Any]) -> GroupChatMessage:
        """Prepare message with required fields"""
        if not self.validate_message(message):
            raise InvalidMessageError("Invalid message format")
            
        prepared_msg = GroupChatMessage(
            role=message['role'],
            content=message['content'],
            username=message.get('username', self.current_username),
            timestamp=message.get('timestamp', time.time()),
            message_id=message.get('message_id', f"msg_{int(time.time()*1000)}"),
        )
        
        # Add optional fields if present
        if message.get('tool_calls'):
            prepared_msg['tool_calls'] = message['tool_calls']
        if message.get('reasoning_content'):
            prepared_msg['reasoning_content'] = message['reasoning_content']
            
        return prepared_msg
    
    def create_group_chat(self, room_name: str, participants: List[str], 
                         description: Optional[str] = None,
                         max_history: Optional[int] = None,
                         cleanup_age: Optional[int] = None) -> str:
        """Create a new group chat room"""
        room_id = f"group_{int(time.time())}_{room_name.replace(' ', '_').lower()}"
        
        # Create metadata
        metadata = GroupChatMetadata(
            room_id=room_id,
            room_name=room_name,
            participants=participants,
            created_at=time.time(),
            last_activity=time.time(),
            description=description,
            max_history=max_history,
            cleanup_age=cleanup_age
        )
        
        # Create room directory
        room_path = os.path.join(self.base_path, room_id)
        os.makedirs(room_path, exist_ok=True)
        
        with self._room_lock(room_id):
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
        """Add a message to a group chat room"""
        try:
            room_path = os.path.join(self.base_path, room_id)
            if not os.path.exists(room_path):
                raise RoomNotFoundError(f"Group chat room not found: {room_id}")
                
            # Prepare and validate message
            prepared_msg = self.prepare_message(message)
            
            with self._room_lock(room_id):
                history_path = os.path.join(room_path, "chat_history.json")
                
                # Load existing history
                try:
                    with open(history_path, 'r', encoding='utf-8') as f:
                        history = json.load(f)
                except (FileNotFoundError, json.JSONDecodeError):
                    history = []
                    
                # Add message
                history.append(prepared_msg)
                
                # Check if we need to clean up old messages
                metadata = self._get_room_metadata(room_id)
                if metadata.cleanup_age:
                    cutoff = time.time() - (metadata.cleanup_age * 24 * 60 * 60)
                    history = [msg for msg in history if msg.get('timestamp', 0) > cutoff]
                
                if metadata.max_history and len(history) > metadata.max_history:
                    history = history[-metadata.max_history:]
                
                # Save updated history
                with open(history_path, 'w', encoding='utf-8') as f:
                    json.dump(history, f, indent=2, ensure_ascii=False)
                    
                # Update last activity
                self._update_room_activity(room_id)
                return True
                
        except GroupChatError as e:
            custom_print("error", str(e))
            return False
        except Exception as e:
            custom_print("error", f"Failed to add message: {e}")
            return False
    
    def get_chat_history(self, room_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get chat history for a room"""
        try:
            room_path = os.path.join(self.base_path, room_id)
            if not os.path.exists(room_path):
                raise RoomNotFoundError(f"Room not found: {room_id}")
                
            history_path = os.path.join(room_path, "chat_history.json")
            if not os.path.exists(history_path):
                return []
                
            with self._room_lock(room_id):
                with open(history_path, 'r', encoding='utf-8') as f:
                    history = json.load(f)
                    
                if limit:
                    history = history[-limit:]
                    
                return history
                
        except GroupChatError as e:
            custom_print("error", str(e))
            return []
        except Exception as e:
            custom_print("error", f"Failed to load chat history: {e}")
            return []
    
    def add_messages(self, room_id: str, messages: List[Dict[str, Any]]) -> bool:
        """Add multiple messages to a group chat room"""
        try:
            room_path = os.path.join(self.base_path, room_id)
            if not os.path.exists(room_path):
                raise RoomNotFoundError(f"Group chat room not found: {room_id}")
                
            # Prepare and validate all messages
            prepared_messages = [self.prepare_message(msg) for msg in messages]
            
            with self._room_lock(room_id):
                history_path = os.path.join(room_path, "chat_history.json")
                
                # Load existing history
                try:
                    with open(history_path, 'r', encoding='utf-8') as f:
                        history = json.load(f)
                except (FileNotFoundError, json.JSONDecodeError):
                    history = []
                    
                # Add messages
                history.extend(prepared_messages)
                
                # Check if we need to clean up
                metadata = self._get_room_metadata(room_id)
                if metadata.cleanup_age:
                    cutoff = time.time() - (metadata.cleanup_age * 24 * 60 * 60)
                    history = [msg for msg in history if msg.get('timestamp', 0) > cutoff]
                
                if metadata.max_history and len(history) > metadata.max_history:
                    history = history[-metadata.max_history:]
                
                # Save updated history
                with open(history_path, 'w', encoding='utf-8') as f:
                    json.dump(history, f, indent=2, ensure_ascii=False)
                    
                self._update_room_activity(room_id)
                custom_print("ok", f"Added {len(messages)} messages to group chat")
                return True
                
        except GroupChatError as e:
            custom_print("error", str(e))
            return False
        except Exception as e:
            custom_print("error", f"Failed to add messages: {e}")
            return False
    
    def _get_room_metadata(self, room_id: str) -> GroupChatMetadata:
        """Get room metadata"""
        room_path = os.path.join(self.base_path, room_id)
        metadata_path = os.path.join(room_path, "metadata.json")
        
        if not os.path.exists(metadata_path):
            raise RoomNotFoundError(f"Room not found: {room_id}")
            
        with open(metadata_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return GroupChatMetadata(**data)
    
    def export_for_ai_models(self, room_id: str, include_metadata: bool = False) -> List[Dict[str, Any]]:
        """Export group chat history in standard OpenAI format for AI models"""
        try:
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
            
        except Exception as e:
            custom_print("error", f"Failed to export chat history: {e}")
            return []
    
    def _update_room_activity(self, room_id: str):
        """Update the last activity timestamp for a room"""
        room_path = os.path.join(self.base_path, room_id)
        metadata_path = os.path.join(room_path, "metadata.json")
        
        if not os.path.exists(metadata_path):
            raise RoomNotFoundError(f"Room not found: {room_id}")
            
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
        try:
            room_path = os.path.join(self.base_path, room_id)
            metadata_path = os.path.join(room_path, "metadata.json")
            
            if not os.path.exists(metadata_path):
                raise RoomNotFoundError(f"Room not found: {room_id}")
                
            with self._room_lock(room_id):
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                    
                if self.current_username not in metadata['participants']:
                    metadata['participants'].append(self.current_username)
                    
                    with open(metadata_path, 'w', encoding='utf-8') as f:
                        json.dump(metadata, f, indent=2)
                        
                    custom_print("ok", f"Joined room: {metadata['room_name']}")
                    
                return True
                
        except GroupChatError as e:
            custom_print("error", str(e))
            return False
        except Exception as e:
            custom_print("error", f"Failed to join room: {e}")
            return False
    
    def cleanup_room(self, room_id: str, max_age_days: Optional[int] = None) -> bool:
        """Clean up old messages from a room"""
        try:
            with self._room_lock(room_id):
                metadata = self._get_room_metadata(room_id)
                cleanup_age = max_age_days or metadata.cleanup_age
                
                if not cleanup_age:
                    return True  # Nothing to clean up
                    
                history = self.get_chat_history(room_id)
                cutoff = time.time() - (cleanup_age * 24 * 60 * 60)
                
                # Filter messages
                current_messages = [
                    msg for msg in history 
                    if msg.get('timestamp', 0) > cutoff
                ]
                
                # Save cleaned history
                history_path = os.path.join(self.base_path, room_id, "chat_history.json")
                with open(history_path, 'w', encoding='utf-8') as f:
                    json.dump(current_messages, f, indent=2)
                    
                removed_count = len(history) - len(current_messages)
                if removed_count > 0:
                    custom_print("info", f"Cleaned up {removed_count} old messages from room {room_id}")
                    
                return True
                
        except Exception as e:
            custom_print("error", f"Failed to clean up room: {e}")
            return False
