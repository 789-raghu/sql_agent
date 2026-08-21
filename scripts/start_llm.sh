#!/usr/bin/env bash
set -e

# Cached GGUF model path (downloaded via huggingface-hub)
CACHED_MODEL="/home/ubuntu/.cache/huggingface/hub/models--Qwen--Qwen2.5-Coder-7B-Instruct-GGUF/snapshots/13fb94bfda8c8cf22497dc57b78f391a9acb426a/qwen2.5-coder-7b-instruct-q4_k_m-00001-of-00002.gguf"
# Fallback download path
MODEL_DIR="models"
MODEL_FILE="${MODEL_DIR}/qwen2.5-coder-7b-instruct-q4_k_m.gguf"
MODEL_HF="Qwen/Qwen2.5-Coder-7B-Instruct-GGUF:Q4_K_M"

SERVER_BIN=""
for candidate in \
    "$(command -v llama-server 2>/dev/null)" \
    "/usr/local/bin/llama-server" \
    "$HOME/.local/bin/llama-server" \
    "/opt/llama.cpp/llama-server" \
    "/usr/bin/llama-server"; do
    if [ -n "$candidate" ] && [ -f "$candidate" ]; then
        SERVER_BIN="$candidate"
        break
    fi
done

if [ -z "$SERVER_BIN" ]; then
    echo "Error: llama-server not found. Install llama.cpp or add it to PATH."
    exit 1
fi

echo "Starting llama-server for Qwen2.5-Coder-7B-Instruct..."

if [ -f "$CACHED_MODEL" ]; then
    echo "Using cached model: $CACHED_MODEL"
    ${SERVER_BIN} \
        -m "$CACHED_MODEL" \
        --host 127.0.0.1 \
        --port 8080 \
        -c 8192 \
        -t $(nproc)
elif [ -f "$MODEL_FILE" ]; then
    echo "Using local model: $MODEL_FILE"
    ${SERVER_BIN} \
        -m "$MODEL_FILE" \
        --host 127.0.0.1 \
        --port 8080 \
        -c 8192 \
        -t $(nproc)
else
    echo "Downloading model from HuggingFace: $MODEL_HF"
    mkdir -p "$MODEL_DIR"
    ${SERVER_BIN} \
        -hf "$MODEL_HF" \
        --host 127.0.0.1 \
        --port 8080 \
        -c 8192 \
        -t $(nproc)
fi
