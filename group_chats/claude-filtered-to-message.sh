#!/usr/bin/env bash

jq 'if .type == .type then
  {
    content: (
      if .message.content and (.message.content | type) == "array" then
        [.message.content[] | select(.type == "text") | .text] | join("\n")
      elif .message.content and (.message.content | type) == "string" then
        .message.content
      else
        "Empty message"
      end
    ),
    id: 1,
    created_at: .timestamp,
    from_: .type,
    to: (if .type == "user" then "assistant" else "user" end),
    parent_id: (.parentUuid // null),
    eid: (.uuid + ".1")
  }
else
  empty
end'