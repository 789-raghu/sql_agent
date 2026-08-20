#!/usr/bin/env bash
set -e

MODEL_DIR="models"
MODEL_FILE="${MODEL_DIR}/qwen2.5-coder-7b-instruct-q4_k_m.gguf"
MODEL_HF="Qwen/Qwen2.5-Coder-7B-Instruct-GGUF:Q4_K_M"

mkdir -p "${MODEL_DIR}"

echo "Starting llama-server for Qwen2.5-Coder-7B-Instruct..."

SERVER_BIN="llama-server"
if ! command -v llama-server &> /dev/null; then
    if [ -f "/usr/local/bin/llama-server" ]; then
        SERVER_BIN="/usr/local/bin/llama-server"
    else
        echo "Error: llama-server binary not found in PATH or /usr/local/bin/llama-server"
        exit 1
    fi
fi

if [ -f "${MODEL_FILE}" ]; then
    echo "Found local GGUF model file: ${MODEL_FILE}"
    ${SERVER_BIN} \
        -m "${MODEL_FILE}" \
        --host 127.0.0.1 \
        --port 8080 \
        -c 8192 \
        -t $(nproc)
else
    echo "Downloading and launching Hugging Face model GGUF: ${MODEL_HF}"
    ${SERVER_BIN} \
        -hf "${MODEL_HF}" \
        --host 127.0.0.1 \
        --port 8080 \
        -c 8192 \
        -t $(nproc)
fi
