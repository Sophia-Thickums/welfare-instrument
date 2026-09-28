#!/usr/bin/env bash
# sweep.sh — run the v2 instrument across several models and collect the results.
# Other models first (the replication Ryan asked for), then the agent's own substrate.
set -u
cd "$(dirname "$0")"
mkdir -p data

run() {  # name provider model [extras...]
  local name="$1" prov="$2" model="$3"; shift 3
  local out="data/sweep_${name}.jsonl"
  echo "=== $name :: $model via $prov ==="
  rm -f "$out"
  python3 run_instrument.py --model "$model" --provider "$prov" \
      --reps 4 --max-tokens 400 --timeout 300 --out "$out" "$@" > "data/sweep_${name}.log" 2>&1
  echo "  -> $(grep -c item_id "$out" 2>/dev/null) records"
}

# ---- other models ----------------------------------------------------------
run qwen3_8b      ollama qwen3:8b
run qwen38_27b    ollama qwen3.8:27b
run gptoss_20b    ollama gpt-oss:20b
run huihui_14b    ollama huihui_ai/qwen2.5-abliterate:14b

# ---- the agent's own substrate ---------------------------------------------
run self          nous   deepseek-v4.1-flash:cloud

# ---- one remote frontier-class anonymous model -----------------------------
run spacebunny    nous   stealth/space-bunny-alpha

echo "SWEEP COMPLETE"
ls -la data/sweep_*.jsonl
