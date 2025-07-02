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

- Receive a message via cli input which gets added to the existing system for now
- Each message comes with an identifier/name (instead of just "assistant")
- Display these in your existing chat interface, just changing "assistant" to the actual sender name
- Being able to send a string to any cli endpoint like so: foo <message> --name <name>

Key Constraints:

- Keep existing JSON message format
- No changes to core chat functionality
- Just extend to handle named senders instead of generic "assistant"

Quick Clarification Questions

1. Message injection format: When you run skogcli agent send "Hello Claude" --agent claude, should this:
   - Add a message to the current active conversation?
   - Or create/append to a specific conversation file?
     This is already implemented. You will need to be able to _call_ the command above with the variables being name and content which will be what my/users messages will be send to.

2. Message display: In the chat interface, should messages from different agents be:
   - Visually distinguished (different colors/formatting)?
   - Or just show the name and keep everything else the same?
     If you actually get the actual basic functionality in you may add this later as much as you like - until then this is considered WAY out of scope

3. Message structure: Should the JSON message format become:
   {"role": "assistant", "content": "message", "name": "claude"}
   i think actually - if possible - this would be a good idea for actual thinking ahead as well as proving that this is possible
4. Or do you prefer a different structure?
   if adding a extra name-identifier it would be helpful but only if possible
5. Backwards compatibility: Should existing chats with generic "assistant" messages still work normally?
   no
   This sounds like a fairly straightforward extension - ...
   if this is what you thought then we have a lot of planning to do to make sure you know what you are doing :)
