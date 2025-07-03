# Simple Named Agent Messages

**Goal:** Add agent names to existing chat messages with minimal changes

**Implementation:**
1. **Extend JSON format:** `{"role": "assistant", "content": "text", "name": "claude"}`
2. **Update display:** Change "assistant" to show `message.get("name", "assistant")` 
3. **Add CLI command:** `agent send "message" --name agentname` appends to current conversation

**Files to modify:**
- Display logic in chat interface (1-2 lines)
- Command handler for CLI injection (~10 lines)  
- Help text for new command (1 line)

**Backwards compatible:** Existing messages without "name" still show as "assistant"