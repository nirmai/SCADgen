"""
NLP Configuration Module

Configure different NLP API providers and models here.
Supports:
- OpenAI API
- Local Ollama
- HuggingFace Inference API
- Custom endpoints
"""

import os
from typing import Dict, Optional
from pathlib import Path

# Load .env file if it exists (for development)
def load_env_file():
    """Load environment variables from .env file if it exists."""
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip()

load_env_file()

# ===== Configuration Presets =====

CONFIGS = {
    "openai": {
        "description": "OpenAI GPT API",
        "api_url": "https://api.openai.com/v1/chat/completions",
        "model": "gpt-3.5-turbo",
        "temperature": 0.3,
        "max_tokens": 500,
        "timeout": 30,
        "requires_api_key": True,
        "env_vars": ["OPENAI_API_KEY"]
    },
    
    "ollama_local": {
        "description": "Local Ollama instance (requires ollama running)",
        "api_url": "http://localhost:11434/v1/chat/completions",
        "model": "mistral",  # or "llama2", "neural-chat", etc.
        "temperature": 0.3,
        "max_tokens": 500,
        "timeout": 60,
        "requires_api_key": False,
    },
    
    "huggingface": {
        "description": "HuggingFace Inference API",
        "api_url": "https://api-inference.huggingface.co/v1/chat/completions",
        "model": "HuggingFaceH4/zephyr-7b-beta",
        "temperature": 0.3,
        "max_tokens": 500,
        "timeout": 30,
        "requires_api_key": True,
        "env_vars": ["HUGGINGFACE_API_KEY"]
    },
    
    "together": {
        "description": "Together.ai API",
        "api_url": "https://api.together.xyz/v1/chat/completions",
        "model": "mistralai/Mistral-7B-Instruct-v0.1",
        "temperature": 0.3,
        "max_tokens": 500,
        "timeout": 30,
        "requires_api_key": True,
        "env_vars": ["TOGETHER_API_KEY"]
    },
    
    "local_test": {
        "description": "Test/mock endpoint (for development)",
        "api_url": "http://localhost:8000/extract",
        "model": "local-test",
        "temperature": 0.0,
        "max_tokens": 500,
        "timeout": 30,
        "requires_api_key": False,
    }
}


def get_config(provider: str = "auto") -> Dict:
    """
    Get NLP configuration.
    
    Args:
        provider: One of "openai", "ollama_local", "huggingface", "together", "local_test", or "auto"
                  If "auto", tries to detect from environment or use default
    
    Returns:
        Configuration dictionary
    """
    
    if provider == "auto":
        # Auto-detect based on available environment variables
        if os.getenv("OPENAI_API_KEY"):
            provider = "openai"
        elif os.getenv("HUGGINGFACE_API_KEY"):
            provider = "huggingface"
        elif os.getenv("TOGETHER_API_KEY"):
            provider = "together"
        elif is_ollama_running():
            provider = "ollama_local"
        else:
            provider = "openai"  # Default fallback
            print("[WARN] NLP_PROVIDER not set. Defaulting to 'openai'.")
            print("       Set NLP_PROVIDER env var to: openai, ollama_local, huggingface, together, or local_test")
    
    if provider not in CONFIGS:
        raise ValueError(f"Unknown NLP provider: {provider}. Options: {list(CONFIGS.keys())}")
    
    config = CONFIGS[provider].copy()
    
    # Check for required API keys
    if config.get("requires_api_key"):
        env_vars = config.get("env_vars", [])
        found_key = False
        for var in env_vars:
            if os.getenv(var):
                found_key = True
                break
        
        if not found_key:
            raise ValueError(
                f"Provider '{provider}' requires API key. Set one of: {', '.join(env_vars)}"
            )
    
    # Allow overrides via environment
    if os.getenv("NLP_API_URL"):
        config["api_url"] = os.getenv("NLP_API_URL")
    if os.getenv("NLP_MODEL"):
        config["model"] = os.getenv("NLP_MODEL")
    
    return config


def is_ollama_running() -> bool:
    """Check if Ollama is running locally."""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        return response.status_code == 200
    except:
        return False


def list_providers():
    """Print available providers and their descriptions."""
    print("Available NLP Providers:")
    print("-" * 60)
    for name, config in CONFIGS.items():
        desc = config.get("description", "")
        model = config.get("model", "unknown")
        requires_key = config.get("requires_api_key", False)
        key_info = " [requires API key]" if requires_key else ""
        print(f"  {name:20} - {desc} (model: {model}){key_info}")
    print("-" * 60)
    print("Use: export NLP_PROVIDER=<provider_name>")
    print("Or:  from nlp_config import get_config; config = get_config('provider_name')")


if __name__ == "__main__":
    # Print available options
    list_providers()
    
    # Test current config
    print("\nCurrent auto-detected config:")
    try:
        config = get_config("auto")
        print(f"  Provider: {config.get('api_url', 'unknown')}")
        print(f"  Model: {config.get('model', 'unknown')}")
    except Exception as e:
        print(f"  Error: {e}")
