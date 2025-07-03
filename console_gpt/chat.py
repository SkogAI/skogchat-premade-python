import asyncio
from unichat import MODELS_LIST, UnifiedChatApi
from unichat.api_helper import openai

from console_gpt.catch_errors import handle_with_exceptions
from console_gpt.config_manager import fetch_variable
from console_gpt.custom_stdout import custom_print
from console_gpt.menus.command_handler import command_handler
from console_gpt.menus.tools_menu import response_tools
from console_gpt.ollama_helper import start_ollama
from console_gpt.prompts.save_chat_prompt import save_chat
from console_gpt.prompts.user_prompt import chat_user_prompt
from console_gpt.unichat_handler import (handle_non_streaming_completion,
                                         handle_non_streaming_response,
                                         handle_streaming_completion,
                                         handle_streaming_response)
from mcp_servers.mcp_tcp_client import MCPClient
from mcp_servers.server_manager import ServerManager


def chat(console, data, managed_user_prompt) -> None:
    # Handle out-of-date config.toml
    model_data = data.model
    api_key = model_data.get("api_key")
    base_url = model_data.get("base_url")
    # Unused anyway, no need to load them and waste time.
    # model_input_pricing_per_1k = model_data.get('model_input_pricing_per_1k')
    # model_max_tokens = model_data.get('model_max_tokens')
    # model_output_pricing_per_1k = model_data.get('model_output_pricing_per_1k')
    model_name = model_data.get("model_name")
    reasoning_effort = model_data.get("reasoning_effort")
    model_title = model_data.get("model_title")

    required_values = {
        "api_key": api_key,
        "base_url": base_url,
        "model_name": model_name,
        "model_title": model_title,
        "reasoning_effort": reasoning_effort,
    }
    missing_keys = [key for key, value in required_values.items() if value is None]
    if missing_keys:
        custom_print(
            "exit",
            f"Required parameters for model are missing from config.toml (missing: {', '.join(missing_keys)}). Consult config.toml.sample for examples.",
            1,
        )

    client_params = {"api_key": api_key}
    if base_url:
        client_params["base_url"] = base_url

    use_responses = model_name in MODELS_LIST["openai_models"]
    if use_responses:
        client = openai.OpenAI(api_key=api_key)
    else:
        client = openai.OpenAI(**client_params) if model_title == "ollama" else UnifiedChatApi(**client_params)
    conversation = data.conversation
    temperature = data.temperature

    cached = model_title.startswith("anthropic")
    tools = []
    if fetch_variable("features", "mcp_client"):
        try:
            with MCPClient() as mcp:
                if mcp is None:
                    custom_print(
                        "error", "Could not establish connection to MCP server. Chat functionality may be limited."
                    )
                else:
                    tools = mcp.get_available_tools()
                    custom_print("info", f"Total tools initialized: {len(tools)}", start="\n")
        except KeyboardInterrupt:
            ready = False
            while not ready:
                _, message = ServerManager().stop_server()
                if message in ["Server stopped successfully", "Server force stopped"]:
                    ready = True
            custom_print("exit", "Goodbye, see you soon!", 130)

    # Inner Loop
    while True:
        response = ""  # Adding this to satisfy the IDE
        error_appeared = False  # Used when the API returns an exception
        # Check if we're not in the middle of a tool call
        if (
            not conversation
            or isinstance(conversation[-1], str)
            or (conversation[-1].get("role") != "tool" and conversation[-1].get("type") != "function_call_output")
        ):
            if managed_user_prompt:
                user_input = managed_user_prompt
                managed_user_prompt = False
            else:
                user_input = chat_user_prompt()
            if not user_input:  # Used to catch SIGINT
                save_chat(conversation, ask=True)
            # Command Handler
            handled_user_input = command_handler(
                model_title, model_name, user_input["content"], conversation, cached, tools
            )
            match handled_user_input:
                case ("continue", new_tools):
                    tools = new_tools
                    custom_print("info", f"Total tools initialized: {len(tools)}", start="\n")
                    continue
                case "continue" | None:
                    continue
                case "break":
                    break
                case "multi_agent_broadcast":
                    asyncio.run(handle_multi_agent_broadcast(user_input["content"], conversation, temperature))
                    continue
                case "multi_agent_chain":
                    asyncio.run(handle_multi_agent_chain(user_input["content"], conversation, temperature))
                    continue
                case _:
                    if model_title.startswith("anthropic") and cached is True:
                        user_input["content"], cached = handled_user_input
                    else:
                        user_input["content"] = handled_user_input

            # Add user's input to the overall conversation
            conversation.append(user_input)

        # Get chat completion
        streaming = fetch_variable("features", "streaming")
        # Start the loading bar until API response is returned
        with console.status("[bold green]Generating a response...", spinner="aesthetic"):
            if use_responses:
                params = {
                    "model": model_name,
                    "input": conversation[1:] if conversation[0]["role"] == "system" else conversation,
                    "stream": streaming,
                }
                if conversation[0]["role"] == "system":
                    params["instructions"] = "Formatting re-enabled\n" + conversation[0]["content"]
                if tools is not False:
                    res_tools = response_tools(tools)
                    # res_tools.append({"type": "web_search_preview"})
                    params["tools"] = res_tools
                    params["parallel_tool_calls"] = False
                if reasoning_effort:
                    params.setdefault("reasoning", {})["effort"] = reasoning_effort
                    params["reasoning"]["summary"] = "detailed"
                else:
                    params["temperature"] = temperature
                if model_name == "o3-pro":
                    params["background"] = True

                response = handle_with_exceptions(lambda: client.responses.create(**params))
            else:
                params = {
                    "model": model_name,
                    "messages": conversation,
                    "temperature": temperature,
                    "tools": tools,
                    "stream": streaming,
                }
                if cached is not False:
                    params["cached"] = cached
                if reasoning_effort:
                    params["reasoning_effort"] = reasoning_effort

                response = handle_with_exceptions(lambda: client.chat.completions.create(**params))

        if response not in ["interrupted", "error_appeared"]:
            if streaming:
                attempted_conversation = (
                    handle_with_exceptions(lambda: handle_streaming_response(model_name, response, conversation))
                    if use_responses
                    else handle_with_exceptions(lambda: handle_streaming_completion(model_name, response, conversation))
                )
                if attempted_conversation not in ["interrupted", "error_appeared"]:
                    conversation = attempted_conversation
                else:
                    response = attempted_conversation  # Replacing it with "response" so it can be automatically handled

            else:
                conversation = (
                    handle_non_streaming_response(model_name, response, conversation)
                    if use_responses
                    else handle_non_streaming_completion(model_name, response, conversation)
                )

        if response == "interrupted":
            last_user_index = next((i for i, msg in enumerate(reversed(conversation)) if msg["role"] == "user"), None)

            if last_user_index is not None:
                conversation = conversation[: len(conversation) - 1 - last_user_index]
            continue

        if response == "error_appeared":
            if model_title == "ollama":
                custom_print("warn", "Restarting Ollama Server...")
                start_ollama()
                custom_print("info", "Note that your last message was lost.")
            else:
                custom_print(
                    "warn",
                    "Exception was raised. Decided whether to continue. Your last message is lost as well",
                )
            # Removes the last user input in order to avoid issues if the conversation continues
            if conversation:
                conversation.pop(-1)
            continue


async def handle_multi_agent_broadcast(user_message: str, conversation: list, temperature: float):
    """Handle broadcast command to multiple agents"""
    from console_gpt.multi_agent import MultiAgentHandler
    from console_gpt.menus.skeleton_menus import base_multiselect_menu, base_checkbox_menu
    
    handler = MultiAgentHandler()
    
    # Let user choose group or individual models
    choice = base_multiselect_menu(
        "Multi-Agent Broadcast",
        ["Use Group", "Select Individual Models"],
        "How would you like to broadcast your message?",
        "Use Group"
    )
    
    if choice == "Use Group":
        groups = handler.list_available_groups()
        if not groups:
            custom_print("error", "No agent groups configured. Please check your config.toml")
            return
        
        selected_group = base_multiselect_menu(
            "Agent Groups",
            groups,
            "Select an agent group:",
            groups[0] if groups else None
        )
        
        models = handler.get_group_models(selected_group)
        custom_print("info", f"Broadcasting to {selected_group}: {', '.join(models)}")
        
    else:
        available_models = handler.get_available_models()
        if not available_models:
            custom_print("error", "No models configured. Please check your config.toml")
            return
            
        models = base_checkbox_menu(
            available_models,
            " Select models to broadcast to:",
            default_checked=available_models[:3]  # Default to first 3 models
        )
        
        if not models:
            custom_print("info", "No models selected.")
            return
    
    # Extract system prompt from conversation
    system_prompt = None
    if conversation and conversation[0].get("role") == "system":
        system_prompt = conversation[0]["content"]
    
    # Broadcast the message
    result = await handler.broadcast_message(user_message, models, temperature, system_prompt)
    
    # Display results
    handler.display_multi_agent_results(result, show_reasoning=True)
    
    # Add to conversation for context
    summary = f"Broadcasted to {len(models)} agents: {result.successful_count} successful, {result.failed_count} failed"
    conversation.append({"role": "assistant", "content": f"[Multi-Agent Broadcast] {summary}"})


async def handle_multi_agent_chain(user_message: str, conversation: list, temperature: float):
    """Handle chain command through multiple agents"""
    from console_gpt.multi_agent import MultiAgentHandler
    from console_gpt.menus.skeleton_menus import base_multiselect_menu, base_checkbox_menu
    
    handler = MultiAgentHandler()
    
    # Let user choose group or individual models
    choice = base_multiselect_menu(
        "Multi-Agent Chain",
        ["Use Group", "Select Individual Models"],
        "How would you like to chain your message?",
        "Use Group"
    )
    
    if choice == "Use Group":
        groups = handler.list_available_groups()
        if not groups:
            custom_print("error", "No agent groups configured. Please check your config.toml")
            return
        
        selected_group = base_multiselect_menu(
            "Agent Groups",
            groups,
            "Select an agent group:",
            groups[0] if groups else None
        )
        
        models = handler.get_group_models(selected_group)
        custom_print("info", f"Chaining through {selected_group}: {', '.join(models)}")
        
    else:
        available_models = handler.get_available_models()
        if not available_models:
            custom_print("error", "No models configured. Please check your config.toml")
            return
            
        models = base_checkbox_menu(
            available_models,
            " Select models to chain through (in order):",
            default_checked=available_models[:3]  # Default to first 3 models
        )
        
        if not models:
            custom_print("info", "No models selected.")
            return
    
    # Extract system prompt from conversation
    system_prompt = None
    if conversation and conversation[0].get("role") == "system":
        system_prompt = conversation[0]["content"]
    
    # Chain through the models
    result = await handler.sequential_chain(user_message, models, temperature, system_prompt)
    
    # Display results
    handler.display_multi_agent_results(result, show_reasoning=True)
    
    # Add final result to conversation
    if result.responses and result.responses[-1].content:
        final_response = result.responses[-1].content
        conversation.append({"role": "assistant", "content": f"[Multi-Agent Chain Result] {final_response}"})
