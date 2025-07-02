# User explanations

1. one user/me needing to message/handle name+message-chats where name is a identifier
2. currently you will get them in json with name, content and timestamp if needed
3. nothing will change _at all_ to begin with except maybe change the name above the message from "assistant" to <name> but _nothing more will need to change_.
   new messages will come in via regular cli command and if needed be in the format you need
4. the primary scenario is to be able to share chat information / write and recieve from multiple sources in a simple and easy way. nothing will be changed if implemented skillfully -
   if you see a reason for any change which could not be in addition to then please tell me now/early so we can plan together
5. Since you say it is simple - yes absolutely! they should be stored in json exactly as they are currently.

---

- You have individual chat logs in JSON format with messages from "user" and "assistant"
- Messages have content, and potentially name/timestamp metadata

Goal:

- Receive messages from multiple external agents/sources
- Each message comes with an identifier/name (instead of just "assistant")
- Display these in your existing chat interface, just changing "assistant" to the actual sender name
- Add a CLI command like skogcli agent send "Hello Claude" --agent claude to inject messages

Key Constraints:

- Keep existing JSON message format
- No changes to core chat functionality
- Just extend to handle named senders instead of generic "assistant"

Quick Clarification Questions

1. Message injection format: When you run skogcli agent send "Hello Claude" --agent claude, should this:
   - Add a message to the current active conversation?
   - Or create/append to a specific conversation file?

2. Message display: In the chat interface, should messages from different agents be:
   - Visually distinguished (different colors/formatting)?
   - Or just show the name and keep everything else the same?

3. Message structure: Should the JSON message format become:
   {"role": "assistant", "content": "message", "name": "claude"}
4. Or do you prefer a different structure?
5. Backwards compatibility: Should existing chats with generic "assistant" messages still work normally?

This sounds like a fairly straightforward extension - mainly adding a CLI command parser and updating the display logic to show sender names. Does this match your vision?
