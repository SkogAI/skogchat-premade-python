#!/usr/bin/env bash

# Transform Claude CLI JSONL to Message model format
# Usage: ./claude-to-message.sh input.jsonl output.jsonl

INPUT_FILE="${1:-input-claude.jsonl}"
OUTPUT_FILE="${2:-messages-claude.jsonl}"


jq -s '
  to_entries | 
  map(
    .value | 
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
      id: (.key + 1),
      created_at: .timestamp,
      from_: .type,
      to: (if .type == "user" then "assistant" else "user" end),
      parent_id: (.parentUuid // null),
      eid: (.uuid + ".1")
    }
  )[]
' "$INPUT_FILE" > "$OUTPUT_FILE"

