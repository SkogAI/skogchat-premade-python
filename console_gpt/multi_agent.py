import asyncio
import json
from typing import Dict, List, Optional, Tuple, Any
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

from rich.console import Console
from rich.panel import Panel
from rich.columns import Columns
from rich.markdown import Markdown
from unichat import UnifiedChatApi
from unichat.api_helper import openai

from console_gpt.config_manager import fetch_variable
from console_gpt.constants import api_key_placeholders
from console_gpt.custom_stdout import custom_print, markdown_print
from console_gpt.menus.key_menu import set_api_key
from console_gpt.catch_errors import handle_with_exceptions


@dataclass
class AgentResponse:
    """Container for individual agent responses"""
    agent_name: str
    model_name: str
    content: str
    error: Optional[str] = None
    reasoning_content: Optional[str] = None
    tool_calls: Optional[List] = None


@dataclass
class MultiAgentResult:
    """Container for multi-agent operation results"""
    responses: List[AgentResponse]
    successful_count: int
    failed_count: int
    execution_time: float


class MultiAgentHandler:
    """Handles multi-agent conversations and operations"""
    
    def __init__(self):
        self.console = Console()
        
    def get_agent_groups(self) -> Dict[str, List[str]]:
        """Get configured agent groups from config"""
        groups = fetch_variable("groups")
        if not groups:
            # Return default groups if none configured
            return {
                "coding_team": ["gpt-4o", "anthropic-sonnet-3", "deepseek-chat"],
                "research_team": ["gpt-41", "anthropic-sonnet-4", "gemini-pro"],
                "creative_team": ["gpt-4o", "anthropic-opus-4", "mistral-large"],
                "analysis_team": ["o3", "anthropic-sonnet-4", "qwen-max"]
            }
        return groups
    
    def get_available_models(self) -> List[str]:
        """Get list of all available models from config"""
        models = fetch_variable("models")
        return list(models.keys()) if models else []
    
    def create_client(self, model_data: Dict) -> Any:
        """Create appropriate client for model"""
        api_key = model_data.get("api_key")
        base_url = model_data.get("base_url")
        model_name = model_data.get("model_name")
        
        # Handle placeholder API keys
        if api_key in api_key_placeholders:
            model_data = set_api_key(model_data)
            api_key = model_data.get("api_key")
        
        client_params = {"api_key": api_key}
        if base_url:
            client_params["base_url"] = base_url
            
        # Use OpenAI client for OpenAI models, UnifiedChatApi for others
        from unichat import MODELS_LIST
        if model_name in MODELS_LIST["openai_models"]:
            return openai.OpenAI(api_key=api_key)
        else:
            return UnifiedChatApi(**client_params)
    
    async def call_single_agent(self, model_key: str, messages: List[Dict], temperature: float = 1.0) -> AgentResponse:
        """Make async call to single agent"""
        try:
            model_data = fetch_variable("models", model_key)
            if not model_data:
                return AgentResponse(
                    agent_name=model_key,
                    model_name="unknown",
                    content="",
                    error=f"Model {model_key} not found in configuration"
                )
            
            model_data = dict(model_data)  # Make a copy
            model_data.update(model_title=model_key)
            
            # Handle placeholder API keys
            if model_data.get("api_key") in api_key_placeholders:
                model_data = set_api_key(model_data)
            
            client = self.create_client(model_data)
            model_name = model_data.get("model_name")
            reasoning_effort = model_data.get("reasoning_effort", False)
            
            # Prepare parameters
            params = {
                "model": model_name,
                "messages": messages,
                "temperature": temperature,
                "stream": False,
            }
            
            if reasoning_effort:
                params["reasoning_effort"] = reasoning_effort
            
            # Make the API call in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                response = await loop.run_in_executor(
                    executor, 
                    lambda: handle_with_exceptions(lambda: client.chat.completions.create(**params))
                )
            
            if response in ["interrupted", "error_appeared"]:
                return AgentResponse(
                    agent_name=model_key,
                    model_name=model_name,
                    content="",
                    error=f"API call failed: {response}"
                )
            
            # Extract response content
            message = response.choices[0].message
            content = getattr(message, "content", "") or ""
            reasoning_content = getattr(message, "reasoning_content", None)
            tool_calls = getattr(message, "tool_calls", None)
            
            return AgentResponse(
                agent_name=model_key,
                model_name=model_name,
                content=content,
                reasoning_content=reasoning_content,
                tool_calls=tool_calls
            )
            
        except Exception as e:
            return AgentResponse(
                agent_name=model_key,
                model_name=model_key,
                content="",
                error=str(e)
            )
    
    async def broadcast_message(self, message: str, agents: List[str], temperature: float = 1.0, 
                              system_prompt: Optional[str] = None) -> MultiAgentResult:
        """Send message to multiple agents simultaneously"""
        import time
        start_time = time.time()
        
        # Prepare messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": message})
        
        # Create tasks for all agents
        tasks = []
        for agent in agents:
            task = self.call_single_agent(agent, messages, temperature)
            tasks.append(task)
        
        # Execute all tasks concurrently
        with self.console.status(f"[bold green]Querying {len(agents)} agents...", spinner="aesthetic"):
            responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        successful_responses = []
        failed_responses = []
        
        for response in responses:
            if isinstance(response, Exception):
                failed_responses.append(AgentResponse(
                    agent_name="unknown",
                    model_name="unknown", 
                    content="",
                    error=str(response)
                ))
            elif response.error:
                failed_responses.append(response)
            else:
                successful_responses.append(response)
        
        execution_time = time.time() - start_time
        
        return MultiAgentResult(
            responses=successful_responses + failed_responses,
            successful_count=len(successful_responses),
            failed_count=len(failed_responses),
            execution_time=execution_time
        )
    
    def display_multi_agent_results(self, result: MultiAgentResult, show_reasoning: bool = False):
        """Display results from multiple agents in a formatted way"""
        custom_print("info", f"Multi-Agent Results ({result.successful_count} successful, {result.failed_count} failed, {result.execution_time:.2f}s)")
        
        # Group responses
        successful = [r for r in result.responses if not r.error]
        failed = [r for r in result.responses if r.error]
        
        # Display successful responses
        if successful:
            panels = []
            for response in successful:
                title = f"[bold blue]{response.agent_name}[/bold blue] ({response.model_name})"
                
                content_parts = []
                
                # Add reasoning if available and requested
                if show_reasoning and response.reasoning_content:
                    content_parts.append(f"**Reasoning:**\n{response.reasoning_content}\n")
                
                # Add main content
                if response.content:
                    content_parts.append(response.content)
                else:
                    content_parts.append("*No response content*")
                
                # Add tool calls if any
                if response.tool_calls:
                    content_parts.append(f"\n**Tool Calls:** {len(response.tool_calls)} calls made")
                
                panel_content = "\n".join(content_parts)
                panels.append(Panel(Markdown(panel_content), title=title, expand=True))
            
            # Display panels in columns if there are multiple responses
            if len(panels) > 1:
                self.console.print(Columns(panels, equal=True, expand=True))
            else:
                self.console.print(panels[0])
        
        # Display failed responses
        if failed:
            custom_print("error", "Failed Responses:")
            for response in failed:
                custom_print("error", f"  {response.agent_name}: {response.error}")
    
    async def sequential_chain(self, message: str, agents: List[str], temperature: float = 1.0,
                             system_prompt: Optional[str] = None) -> MultiAgentResult:
        """Send message through agents sequentially, each building on previous responses"""
        import time
        start_time = time.time()
        
        responses = []
        current_messages = []
        
        # Add system prompt if provided
        if system_prompt:
            current_messages.append({"role": "system", "content": system_prompt})
        
        # Add initial user message
        current_messages.append({"role": "user", "content": message})
        
        for i, agent in enumerate(agents):
            with self.console.status(f"[bold green]Agent {i+1}/{len(agents)}: {agent}...", spinner="aesthetic"):
                response = await self.call_single_agent(agent, current_messages, temperature)
                responses.append(response)
                
                # Add this agent's response to the conversation for the next agent
                if not response.error and response.content:
                    current_messages.append({
                        "role": "assistant", 
                        "content": f"[{response.agent_name}]: {response.content}"
                    })
        
        execution_time = time.time() - start_time
        successful_count = len([r for r in responses if not r.error])
        failed_count = len([r for r in responses if r.error])
        
        return MultiAgentResult(
            responses=responses,
            successful_count=successful_count,
            failed_count=failed_count,
            execution_time=execution_time
        )
    
    def get_group_models(self, group_name: str) -> List[str]:
        """Get models for a specific group"""
        groups = self.get_agent_groups()
        return groups.get(group_name, [])
    
    def list_available_groups(self) -> List[str]:
        """List all available agent groups"""
        groups = self.get_agent_groups()
        return list(groups.keys())


# Convenience functions for integration with existing code
async def broadcast_to_group(group_name: str, message: str, temperature: float = 1.0, 
                           system_prompt: Optional[str] = None) -> MultiAgentResult:
    """Convenience function to broadcast to a named group"""
    handler = MultiAgentHandler()
    models = handler.get_group_models(group_name)
    if not models:
        raise ValueError(f"Group '{group_name}' not found or has no models")
    return await handler.broadcast_message(message, models, temperature, system_prompt)


async def broadcast_to_models(models: List[str], message: str, temperature: float = 1.0,
                            system_prompt: Optional[str] = None) -> MultiAgentResult:
    """Convenience function to broadcast to specific models"""
    handler = MultiAgentHandler()
    return await handler.broadcast_message(message, models, temperature, system_prompt)


async def chain_through_models(models: List[str], message: str, temperature: float = 1.0,
                             system_prompt: Optional[str] = None) -> MultiAgentResult:
    """Convenience function to chain through specific models"""
    handler = MultiAgentHandler()
    return await handler.sequential_chain(message, models, temperature, system_prompt)