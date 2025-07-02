# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is **skogai** (console-chat-gpt v6), a CLI tool for chatting with multiple AI models including OpenAI, Anthropic, Mistral, xAI, Google AI, DeepSeek, Alibaba, Inception, and Ollama-hosted models. It's built on Python and uses the `unichat` library for unified chat completion across providers.

## Development Commands

### Installation and Setup
```bash
# Install dependencies (use uv if available, otherwise pip3)
pip3 install -r requirements.txt

# Copy sample config (done automatically on first run)
cp config.toml.sample config.toml

# Run the application
python3 main.py
```

### Development Workflow
```bash
# Run the application directly
python3 main.py

# For development, create a symlink or alias to run from anywhere
# The 'run' file in the root appears to be a convenience script
```

### Configuration Management
```bash
# Edit main configuration
config.toml  # Contains all model configurations, API keys, and feature flags

# Edit MCP server configuration  
mcp_config.json  # Based on claude_desktop_config.json format
```

## Architecture Overview

### Core Components

**Main Entry Point** (`main.py`):
- Initializes console, sets locale, checks config version
- Handles the main application loop with AI managed mode support
- Routes between chat and assistant modes based on user selection

**Chat System** (`console_gpt/chat.py`):
- Main chat interface using the `unichat` library for unified API calls
- Supports streaming and non-streaming responses
- Integrates with MCP (Model Context Protocol) servers
- Handles model parameter validation and error management

**Assistant System** (`console_gpt/assistant.py`):
- OpenAI Assistants API integration
- Thread-based conversations with persistent context
- Separate command handling for assistant-specific features

**Configuration Management** (`console_gpt/config_manager.py`):
- TOML-based configuration with automatic sample file copying
- Handles API keys, model parameters, and feature flags
- Version checking and migration support

**Menu System** (`console_gpt/menus/`):
- Modular menu architecture with combined_menu as the main orchestrator
- Separate menus for models, roles, settings, assistants, and tools
- Command handler for in-chat commands and shortcuts

**Model Context Protocol (MCP)** (`mcp_servers/`):
- TCP server/client implementation for MCP protocol
- Server manager for starting/stopping MCP servers
- Integrates with existing MCP server configurations

### Key Dependencies

- **unichat (~4.1.16)**: Unified chat completion library (core functionality)
- **rich (~13.7.0)**: Terminal formatting and progress displays
- **questionary (~2.0.1)**: Interactive prompts and menus
- **mcp (~1.1.2)**: Model Context Protocol implementation
- **toml (~0.10.2)**: Configuration file parsing

### Configuration Structure

The `config.toml` file contains:
- `[chat.defaults]`: Default model, temperature, and system role
- `[chat.features]`: Feature flags for different functionality
- `[chat.managed]`: AI managed mode settings with model assignments
- `[chat.roles]`: Predefined system roles for different use cases
- `[chat.models.*]`: Individual model configurations with API keys and parameters

### Data Flow

1. **Initialization**: Load config, check version, display intro
2. **Mode Selection**: AI managed mode vs manual model selection
3. **Chat/Assistant Routing**: Based on user choice, route to appropriate handler
4. **Model Interaction**: Use unichat library for API calls with streaming support
5. **Command Processing**: Handle in-chat commands via command_handler
6. **MCP Integration**: Optional MCP server communication for enhanced capabilities

### Testing and Validation

Currently uses basic Python error handling and exception management. No formal test suite detected - testing appears to be manual through the CLI interface.

### Special Features

- **AI Managed Mode**: Automatically selects optimal model based on query complexity
- **MCP Integration**: Supports Model Context Protocol servers for extended capabilities
- **Multi-Provider Support**: Unified interface across 8+ AI providers
- **Assistant Mode**: Full OpenAI Assistants API integration with persistent threads
- **Image Processing**: Support for image inputs with compatible models
- **Conversation History**: Save/load chat sessions with metadata

## Important Notes

- API keys are stored in `config.toml` - ensure this file is properly secured
- The application supports both streaming and non-streaming responses
- MCP server configuration is optional but provides enhanced capabilities
- Temperature and model selection can be configured per-session or globally
- The application handles graceful shutdown with conversation saving