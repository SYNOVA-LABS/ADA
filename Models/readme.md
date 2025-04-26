# ADA Models

This directory contains language and speech models used by the Advanced Digital Agent system.

## Overview

The Models directory houses the pre-trained models that power ADA's various AI capabilities:
- Speech recognition for understanding user commands
- Language models for intelligent responses
- Visual processing models for context understanding
- Face recognition encodings for user identification

## Current Models

- **vosk-model-small-en-us-0.15** - A lightweight English (US) speech recognition model for processing spoken commands and user input
- **tinyllama-1.1b-chat-v1.0.Q8_0.gguf** - A quantized LLM for generating contextual responses and questions

## Model Configuration

Models can be configured in their respective module settings:

### LLM Configuration Example
```python
llm = Llama(
    model_path=model_path,
    n_ctx=512,         # Context window size
    n_threads=4,       # CPU threads for inference
    n_batch=32,        # Batch size for token processing
    f16_kv=True,       # Half-precision key/value cache
    use_mlock=True,    # Keep model in RAM
    n_gpu_layers=-1    # Use GPU acceleration when available
)
```

## Setup


## Hardware Requirements

Different models have different hardware requirements:
- Speech models: Minimal requirements, runs on CPU
- LLM models: Benefits from GPU acceleration, requires more RAM
- Face recognition: Moderate CPU requirements
