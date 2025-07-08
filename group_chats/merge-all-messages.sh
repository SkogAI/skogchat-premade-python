#!/usr/bin/env bash

OUTPUT_FILE="${1:-messages-unified.jsonl}"

# Combine all message files and sort by timestamp
cat messages-claude.jsonl messages-goose.jsonl messages-gptme.jsonl | jq -s 'sort_by(.created_at)[]' > "$OUTPUT_FILE"