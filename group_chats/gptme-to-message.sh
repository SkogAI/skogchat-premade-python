#!/usr/bin/env bash

INPUT_FILE="${1:-input-gptme.jsonl}"
OUTPUT_FILE="${2:-messages-gptme.jsonl}"

jq -s '
  to_entries |
  map(
    select(.value | has("role") and (.value.role != "system")) |
    .value |
    {
      content: (
        if .content and (.content | type) == "string" then
          .content
        else
          "Empty message"
        end
      ),
      id: (.key + 1),
      created_at: .timestamp,
      from_: .role,
      to: (if .role == "user" then "assistant" else "user" end),
      parent_id: null,
      eid: ((.timestamp // (now | tostring)) + ".1")
    }
  )[]
' "$INPUT_FILE" > "$OUTPUT_FILE"