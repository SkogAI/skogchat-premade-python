"""
Group Chat Interface - Interactive commands for user + AI agents group chats
"""
import json
from typing import Dict, List, Optional, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt, Confirm
from datetime import datetime

from console_gpt.group_chat import GroupChatManager, GroupChatMessage
from console_gpt.multi_agent import MultiAgentHandler
from console_gpt.custom_stdout import custom_print, markdown_print
from console_gpt.menus.skeleton_menus import base_multiselect_menu, base_checkbox_menu
from console_gpt.config_manager import fetch_variable


class GroupChatInterface:
    """Interactive interface for group chat functionality"""
    
    def __init__(self):
        self.console = Console()
        self.group_manager = GroupChatManager()
        self.multi_agent_handler = MultiAgentHandler()
        self.current_room_id = None
        
    def show_main_menu(self):
        """Show the main group chat menu"""
        while True:
            self.console.print("\n[bold cyan]🤖 Group Chat - User + AI Agents[/bold cyan]")
            self.console.print("1. Create new group chat room")
            self.console.print("2. Join existing room")
            self.console.print("3. List all rooms")
            self.console.print("4. Start chatting in current room")
            self.console.print("5. Show room history")
            self.console.print("6. Exit")
            
            choice = Prompt.ask("Select option", choices=["1", "2", "3", "4", "5", "6"])
            
            if choice == "1":
                self.create_room()
            elif choice == "2":
                self.join_room()
            elif choice == "3":
                self.list_rooms()
            elif choice == "4":
                if self.current_room_id:
                    self.start_group_chat()
                else:
                    custom_print("error", "No room selected. Create or join a room first.")
            elif choice == "5":
                self.show_room_history()
            elif choice == "6":
                break
    
    def create_room(self):
        """Create a new group chat room"""
        room_name = Prompt.ask("Enter room name")
        description = Prompt.ask("Enter room description (optional)", default="")
        
        # Select AI agents to include
        self.console.print("\n[bold]Select AI agents for this room:[/bold]")
        available_groups = self.multi_agent_handler.get_agent_groups()
        
        if not available_groups:
            custom_print("error", "No agent groups configured. Please check your config.toml")
            return
            
        # Show group selection menu
        group_options = [(name, f"{name}: {', '.join(agents[:3])}{'...' if len(agents) > 3 else ''}") 
                        for name, agents in available_groups.items()]
        
        selected_group = base_multiselect_menu(
            "Choose AI agents for the room",
            [name for name, desc in group_options],
            "Select an agent group:"
        )
        
        if not selected_group:
            custom_print("error", "No agents selected. Room creation cancelled.")
            return
            
        # Get agents from selected group
        selected_agents = available_groups[selected_group]
        
        # Create room with user + selected AI agents
        participants = [self.group_manager.current_username] + selected_agents
        
        room_id = self.group_manager.create_group_chat(
            room_name=room_name,
            participants=participants,
            description=description if description else None
        )
        
        self.current_room_id = room_id
        custom_print("ok", f"Room created and joined: {room_name}")
        
        # Add initial system message
        system_msg = {
            "role": "system",
            "content": f"Group chat room '{room_name}' created with participants: {', '.join(participants)}"
        }
        self.group_manager.add_message(room_id, system_msg)
    
    def join_room(self):
        """Join an existing room"""
        rooms = self.group_manager.list_group_chats()
        
        if not rooms:
            custom_print("error", "No group chat rooms found.")
            return
            
        # Show room selection
        room_options = [(room['room_id'], f"{room['room_name']} - {len(room['participants'])} participants") 
                       for room in rooms]
        
        selected_room_id = base_multiselect_menu(
            "Choose a group chat room",
            [room_id for room_id, desc in room_options],
            "Select a room to join:"
        )
        
        if selected_room_id:
            self.current_room_id = selected_room_id
            self.group_manager.join_room(selected_room_id)
            
            # Show room info
            room_info = next((r for r in rooms if r['room_id'] == selected_room_id), None)
            if room_info:
                self.console.print(f"\n[bold green]Joined room: {room_info['room_name']}[/bold green]")
                self.console.print(f"Participants: {', '.join(room_info['participants'])}")
    
    def list_rooms(self):
        """List all available rooms"""
        rooms = self.group_manager.list_group_chats()
        
        if not rooms:
            custom_print("info", "No group chat rooms found.")
            return
            
        table = Table(title="Group Chat Rooms")
        table.add_column("Room Name", style="cyan")
        table.add_column("Participants", style="yellow")
        table.add_column("Last Activity", style="green")
        table.add_column("Description", style="white")
        
        for room in rooms:
            last_activity = datetime.fromtimestamp(room['last_activity']).strftime('%Y-%m-%d %H:%M')
            participants = ', '.join(room['participants'])
            description = room.get('description', '') or 'No description'
            
            table.add_row(room['room_name'], participants, last_activity, description)
            
        self.console.print(table)
    
    def start_group_chat(self):
        """Start chatting in the current room"""
        if not self.current_room_id:
            custom_print("error", "No room selected.")
            return
            
        room_info = next((r for r in self.group_manager.list_group_chats() 
                         if r['room_id'] == self.current_room_id), None)
        
        if not room_info:
            custom_print("error", "Room not found.")
            return
            
        self.console.print(f"\n[bold green]🤖 Group Chat: {room_info['room_name']}[/bold green]")
        self.console.print(f"Participants: {', '.join(room_info['participants'])}")
        self.console.print("[dim]Type 'exit' to leave the chat, 'history' to see recent messages[/dim]\n")
        
        # Show recent messages
        self.show_recent_messages(limit=5)
        
        while True:
            try:
                user_input = input(f"\n[{self.group_manager.current_username}] > ").strip()
                
                if user_input.lower() == 'exit':
                    break
                elif user_input.lower() == 'history':
                    self.show_room_history()
                    continue
                elif not user_input:
                    continue
                    
                # Add user message to room
                user_msg = {"role": "user", "content": user_input}
                self.group_manager.add_message(self.current_room_id, user_msg)
                
                # Get AI agents from room participants (exclude current user)
                ai_participants = [p for p in room_info['participants'] if p != self.group_manager.current_username]
                
                # Send message to AI agents using existing multi-agent functionality
                import asyncio
                asyncio.run(self.process_ai_responses(user_input, ai_participants))
                
            except KeyboardInterrupt:
                break
                
        custom_print("info", "Left group chat.")
    
    async def process_ai_responses(self, user_message: str, ai_agents: List[str]):
        """Process AI responses and add them to the group chat"""
        # Get conversation history in AI format
        history = self.group_manager.export_for_ai_models(self.current_room_id)
        
        # Extract system prompt from history
        system_prompt = None
        if history and history[0].get("role") == "system":
            system_prompt = history[0]["content"]
        
        # Use existing multi-agent handler to get responses
        try:
            result = await self.multi_agent_handler.broadcast_message(
                message=user_message,
                agents=ai_agents,
                temperature=1.0,
                system_prompt=system_prompt
            )
            
            # Add AI responses to group chat
            for response in result.responses:
                if not response.error:
                    ai_msg = {
                        "role": "assistant",
                        "content": response.content
                    }
                    if response.reasoning_content:
                        ai_msg["reasoning_content"] = response.reasoning_content
                    if response.tool_calls:
                        ai_msg["tool_calls"] = response.tool_calls
                    
                    self.group_manager.add_message(self.current_room_id, ai_msg)
                    
                    # Display response
                    self.console.print(f"\n[bold blue][{response.model_name}][/bold blue]")
                    markdown_print(response.content)
                else:
                    custom_print("error", f"Error from {response.model_name}: {response.error}")
                    
        except Exception as e:
            custom_print("error", f"Failed to get AI responses: {e}")
    
    def show_room_history(self):
        """Show chat history for current room"""
        if not self.current_room_id:
            custom_print("error", "No room selected.")
            return
            
        limit = Prompt.ask("Number of messages to show", default="20")
        try:
            limit = int(limit)
        except ValueError:
            limit = 20
            
        self.show_recent_messages(limit)
    
    def show_recent_messages(self, limit: int = 10):
        """Show recent messages from the current room"""
        if not self.current_room_id:
            return
            
        history = self.group_manager.get_chat_history(self.current_room_id, limit)
        
        if not history:
            custom_print("info", "No messages in this room yet.")
            return
            
        self.console.print(f"\n[bold]Recent Messages (last {len(history)}):[/bold]")
        
        for msg in history:
            timestamp = datetime.fromtimestamp(msg['timestamp']).strftime('%H:%M:%S')
            username = msg['username']
            role = msg['role']
            content = msg['content']
            
            if role == "system":
                self.console.print(f"[dim][{timestamp}] {content}[/dim]")
            elif role == "user":
                self.console.print(f"[green][{timestamp}] {username}: {content}[/green]")
            elif role == "assistant":
                model_name = msg.get('model_name', 'AI')
                self.console.print(f"[blue][{timestamp}] {model_name}: {content}[/blue]")
    
    def import_existing_chat(self, room_id: str, chat_file_path: str):
        """Import an existing chat file into a group room"""
        try:
            with open(chat_file_path, 'r', encoding='utf-8') as f:
                external_history = json.load(f)
                
            success = self.group_manager.merge_chat_histories(room_id, external_history)
            
            if success:
                custom_print("ok", f"Successfully imported chat from {chat_file_path}")
            else:
                custom_print("error", "Failed to import chat history")
                
        except Exception as e:
            custom_print("error", f"Failed to import chat: {e}")


def start_group_chat_interface():
    """Entry point for group chat interface"""
    # Check if multi-agent is enabled
    if not fetch_variable("features", "multi_agent"):
        custom_print("error", "Multi-agent functionality is disabled. Enable it in config.toml")
        return
        
    interface = GroupChatInterface()
    interface.show_main_menu()


def merge_current_conversation(conversation: List[Dict[str, Any]]):
    """Merge current conversation into a selected group chat room"""
    from rich.prompt import Prompt
    from rich.console import Console
    
    console = Console()
    
    # Check if multi-agent is enabled
    if not fetch_variable("features", "multi_agent"):
        custom_print("error", "Multi-agent functionality is disabled. Enable it in config.toml")
        return
    
    if not conversation or len(conversation) == 0:
        custom_print("error", "No conversation to merge!")
        return
    
    # Initialize group chat manager
    group_manager = GroupChatManager()
    
    # Get available rooms
    rooms = group_manager.list_group_chats()
    
    if not rooms:
        console.print("[yellow]No group chat rooms found. Creating a new room...[/yellow]")
        
        # Quick room creation
        room_name = Prompt.ask("Enter room name for this conversation")
        
        # Get available AI models for the room
        from console_gpt.multi_agent import MultiAgentHandler
        handler = MultiAgentHandler()
        available_groups = handler.get_agent_groups()
        
        if available_groups:
            # Use first available group
            first_group = list(available_groups.keys())[0]
            selected_agents = available_groups[first_group]
            custom_print("info", f"Using agent group '{first_group}': {', '.join(selected_agents)}")
        else:
            selected_agents = ["anthropic-sonnet-3", "deepseek-chat"]  # Fallback
        
        participants = [group_manager.current_username] + selected_agents
        
        room_id = group_manager.create_group_chat(
            room_name=room_name,
            participants=participants,
            description=f"Merged conversation from main chat"
        )
        
        custom_print("ok", f"Created new room: {room_name}")
        
    else:
        # Show room selection
        console.print("\n[bold]Available Group Chat Rooms:[/bold]")
        for i, room in enumerate(rooms, 1):
            last_activity = datetime.fromtimestamp(room['last_activity']).strftime('%Y-%m-%d %H:%M')
            console.print(f"{i}. {room['room_name']} - {len(room['participants'])} participants (Last: {last_activity})")
        
        choice = Prompt.ask("Select room number (or 'new' to create new room)", 
                          choices=[str(i) for i in range(1, len(rooms) + 1)] + ["new"])
        
        if choice == "new":
            # Create new room
            room_name = Prompt.ask("Enter room name for this conversation")
            
            from console_gpt.multi_agent import MultiAgentHandler
            handler = MultiAgentHandler()
            available_groups = handler.get_agent_groups()
            
            if available_groups:
                first_group = list(available_groups.keys())[0]
                selected_agents = available_groups[first_group]
                custom_print("info", f"Using agent group '{first_group}': {', '.join(selected_agents)}")
            else:
                selected_agents = ["anthropic-sonnet-3", "deepseek-chat"]
            
            participants = [group_manager.current_username] + selected_agents
            
            room_id = group_manager.create_group_chat(
                room_name=room_name,
                participants=participants,
                description=f"Merged conversation from main chat"
            )
            
            custom_print("ok", f"Created new room: {room_name}")
        else:
            # Use existing room
            selected_room = rooms[int(choice) - 1]
            room_id = selected_room['room_id']
            custom_print("info", f"Selected room: {selected_room['room_name']}")
    
    # Convert conversation format for group chat
    merged_messages = []
    
    for msg in conversation:
        if isinstance(msg, dict) and 'role' in msg and 'content' in msg:
            # Determine username based on role
            if msg['role'] == 'user':
                username = group_manager.current_username
            elif msg['role'] == 'assistant':
                username = 'merged_ai'  # Generic name for merged AI responses
            else:
                username = 'system'
            
            # Create group chat message format
            group_msg = {
                'role': msg['role'],
                'content': msg['content'],
                'username': username,
                'timestamp': time.time(),  # Use current time for merged messages
                'message_id': f"merged_{int(time.time()*1000)}_{len(merged_messages)}",
                'tool_calls': msg.get('tool_calls'),
                'reasoning_content': msg.get('reasoning_content')
            }
            merged_messages.append(group_msg)
    
    # Merge into group chat
    success = group_manager.merge_chat_histories(room_id, merged_messages)
    
    if success:
        custom_print("ok", f"Successfully merged {len(merged_messages)} messages into group chat!")
        
        # Ask if user wants to continue in group chat mode
        continue_in_group = Prompt.ask("Continue this conversation in the group chat?", 
                                     choices=["y", "n"], default="y")
        
        if continue_in_group == "y":
            # Switch to group chat interface
            interface = GroupChatInterface()
            interface.current_room_id = room_id
            interface.start_group_chat()
    else:
        custom_print("error", "Failed to merge conversation into group chat")


if __name__ == "__main__":
    start_group_chat_interface()