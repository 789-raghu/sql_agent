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

echo "Starting llama-server for Qwen2.5-Coder-7B-Instruct..."

if [ -f "$CACHED_MODEL" ]; then
    MODEL_TO_USE="$CACHED_MODEL"
elif [ -f "$MODEL_FILE" ]; then
    MODEL_TO_USE="$MODEL_FILE"
else
    MODEL_TO_USE=""
fi

if [ -n "$SERVER_BIN" ] && [ -n "$MODEL_TO_USE" ]; then
    echo "Using llama-server binary: $SERVER_BIN"
    echo "Model: $MODEL_TO_USE"
    ${SERVER_BIN} \
        -m "$MODEL_TO_USE" \
        --host 127.0.0.1 \
        --port 8080 \
        -c 8192 \
        -t $(nproc)
elif python3 -c "import llama_cpp" 2>/dev/null; then
    echo "llama-server binary not found. Falling back to llama-cpp-python server."
    if [ -z "$MODEL_TO_USE" ]; then
        MODEL_TO_USE="$CACHED_MODEL"
    fi
    echo "Model: $MODEL_TO_USE"
    python3 -m llama_cpp.server \
        --model "$MODEL_TO_USE" \
        --host 127.0.0.1 \
        --port 8080 \
        --n_ctx 8192 \
        --n_threads $(nproc)
elif [ -n "$SERVER_BIN" ]; then
    echo "Downloading model from HuggingFace: $MODEL_HF"
    mkdir -p "$MODEL_DIR"
    ${SERVER_BIN} \
        -hf "$MODEL_HF" \
        --host 127.0.0.1 \
        --port 8080 \
        -c 8192 \
        -t $(nproc)
else
    echo "Error: Neither llama-server binary nor llama-cpp-python found."
    echo "Install one of:"
    echo "  Option A: sudo apt-get install -y unzip && wget ... (llama.cpp binary)"
    echo "  Option B: pip install 'llama-cpp-python[server]'"
    exit 1
fi
