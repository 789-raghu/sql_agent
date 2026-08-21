#!/usr/bin/env bash
set -e

MODEL_DIR="$(cd "$(dirname "$0")/.." && pwd)/models"
MODEL_FILE="${MODEL_DIR}/qwen2.5-coder-7b-instruct-q4_k_m.gguf"
MODEL_HF="Qwen/Qwen2.5-Coder-7B-Instruct-GGUF"
MODEL_PATTERN="qwen2.5-coder-7b-instruct-q4_k_m-00001-of-00002.gguf"

# Dynamically find cached HuggingFace model
HF_CACHE="${HOME}/.cache/huggingface/hub"
CACHED_MODEL=$(find "${HF_CACHE}" -name "${MODEL_PATTERN}" 2>/dev/null | head -1)

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
elif "$(dirname "$0")/../.venv/bin/python3" -c "import llama_cpp" 2>/dev/null || python3 -c "import llama_cpp" 2>/dev/null; then
    echo "llama-server binary not found. Falling back to llama-cpp-python server."
    # Prefer venv Python
    VENV_DIR="$(cd "$(dirname "$0")/.." && pwd)/.venv"
    if [ -f "$VENV_DIR/bin/python3" ]; then
        PYTHON="$VENV_DIR/bin/python3"
    else
        PYTHON="python3"
    fi

    if [ -z "$MODEL_TO_USE" ]; then
        echo "No model GGUF found locally. Auto-downloading Qwen2.5-Coder-7B-Instruct-GGUF from Hugging Face..."
        MODEL_TO_USE=$($PYTHON -c "
from huggingface_hub import hf_hub_download
import sys
try:
    path = hf_hub_download(repo_id='Qwen/Qwen2.5-Coder-7B-Instruct-GGUF', filename='qwen2.5-coder-7b-instruct-q4_k_m-00001-of-00002.gguf')
    # also download part 2
    hf_hub_download(repo_id='Qwen/Qwen2.5-Coder-7B-Instruct-GGUF', filename='qwen2.5-coder-7b-instruct-q4_k_m-00002-of-00002.gguf')
    print(path)
except Exception as e:
    sys.exit(1)
")
    fi

    echo "Python: $PYTHON"
    echo "Model: $MODEL_TO_USE"
    $PYTHON -m llama_cpp.server \
        --model "$MODEL_TO_USE" \
        --host 127.0.0.1 \
        --port 8080 \
        --n_ctx 2048 \
        --n_threads 4
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
