#!/usr/bin/env bash

INPUT_FILE="${1:-messages-unified.jsonl}"
OUTPUT_FILE="${2:-simple-format.json}"

jq -s '[.[] | {role: (if .from_ == "assistant" then "assistant" else .from_ end), content: .content}]' "$INPUT_FILE" > "$OUTPUT_FILE"