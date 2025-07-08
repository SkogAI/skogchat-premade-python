#!/usr/bin/env bash

# Transform Goose JSONL to Message model format
# Usage: ./goose-to-message.sh input-goose.jsonl messages-goose.jsonl

INPUT_FILE="${1:-input-goose.jsonl}"
OUTPUT_FILE="${2:-messages-goose.jsonl}"


jq -s '
  to_entries |
  map(
    select(.value | has("role")) |
    .value |
    {
      content: (
        if .content and (.content | type) == "array" then
          [.content[] | select(.type == "text") | .text] | join("\n")
        elif .content and (.content | type) == "string" then
          .content
        else
          "Empty message"
        end
      ),
      id: (.key + 1),
      created_at: (.created | todate),
      from_: .role,
      to: (if .role == "user" then "assistant" else "user" end),
      parent_id: null,
      eid: ((.created | tostring) + ".1")
    }
  )[]
' "$INPUT_FILE" > "$OUTPUT_FILE"

