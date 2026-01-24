#!/usr/bin/env python3
"""
Quick Setup Script for SCAD Generator with NLP

This script helps you configure the NLP component for the SCAD generator.
It checks your environment and guides you through setup.
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header(text):
    """Print a formatted header."""
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def print_section(text):
    """Print a section header."""
    print(f"\n→ {text}")

def check_python_packages():
    """Check if required Python packages are installed."""
    print_section("Checking Python packages...")
    
    required = ["requests"]
    missing = []
    
    for package in required:
        try:
            __import__(package)
            print(f"  ✓ {package} is installed")
        except ImportError:
            print(f"  ✗ {package} is MISSING")
            missing.append(package)
    
    if missing:
        print(f"\nInstall missing packages with:")
        print(f"  pip install {' '.join(missing)}")
        return False
    
    return True

def check_nlp_config():
    """Check if NLP is configured."""
    print_section("Checking NLP configuration...")
    
    provider = os.getenv("NLP_PROVIDER", "not set")
    api_url = os.getenv("NLP_API_URL", "not set")
    api_key = os.getenv("OPENAI_API_KEY", "not set")
    
    print(f"  NLP_PROVIDER: {provider}")
    print(f"  NLP_API_URL: {api_url}")
    print(f"  OPENAI_API_KEY: {'set' if api_key != 'not set' else 'not set'}")
    
    if provider == "not set":
        print("\n  ⚠ No NLP provider configured!")
        return False
    
    return True

def list_providers():
    """Show available NLP providers."""
    print_header("Available NLP Providers")
    
    providers = {
        "openai": {
            "desc": "OpenAI GPT API (recommended)",
            "setup": [
                "1. Get API key from https://platform.openai.com/api-keys",
                "2. Set: export OPENAI_API_KEY='your-key'",
                "3. Set: export NLP_PROVIDER='openai'",
            ]
        },
        "ollama_local": {
            "desc": "Local Ollama (free, runs on your computer)",
            "setup": [
                "1. Install Ollama from https://ollama.ai",
                "2. Run: ollama serve",
                "3. In another terminal: ollama run mistral",
                "4. Set: export NLP_PROVIDER='ollama_local'",
            ]
        },
        "huggingface": {
            "desc": "HuggingFace Inference API",
            "setup": [
                "1. Get API key from https://huggingface.co/settings/tokens",
                "2. Set: export HUGGINGFACE_API_KEY='your-key'",
                "3. Set: export NLP_PROVIDER='huggingface'",
            ]
        },
        "together": {
            "desc": "Together.ai API",
            "setup": [
                "1. Get API key from https://www.together.ai/",
                "2. Set: export TOGETHER_API_KEY='your-key'",
                "3. Set: export NLP_PROVIDER='together'",
            ]
        }
    }
    
    for provider_name, info in providers.items():
        print(f"\n{provider_name.upper()}")
        print(f"  {info['desc']}")
        print("  Setup steps:")
        for step in info['setup']:
            print(f"    {step}")

def test_nlp_connection():
    """Test NLP API connection."""
    print_section("Testing NLP connection...")
    
    try:
        from nlp_config import get_config, is_ollama_running
        from nlp_extractor import NLPExtractor
        
        try:
            config = get_config("auto")
            print(f"  ✓ Config loaded: {config.get('model')}")
            
            # Try creating extractor (doesn't require API call yet)
            extractor = NLPExtractor()
            print(f"  ✓ NLP Extractor initialized")
            print(f"  ✓ API URL: {extractor.api_url}")
            
            # Note: Don't actually call the API in this check to avoid cost/throttling
            print(f"\n  Ready to use! Run ScadCodeGen.py to test.")
            return True
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
            return False
    
    except ImportError as e:
        print(f"  ✗ Could not import NLP modules: {e}")
        return False

def interactive_setup():
    """Interactive setup wizard."""
    print_header("SCAD Generator - NLP Setup Wizard")
    
    print("\nThis wizard will help you set up the NLP component.")
    print("You can set up any of these providers:")
    
    print("\n1. OpenAI (easiest, costs money)")
    print("2. Ollama (local, free, no internet required)")
    print("3. HuggingFace (free tier available)")
    print("4. Together.ai (free tier available)")
    print("5. Skip setup (manual configuration later)")
    
    choice = input("\nSelect option (1-5): ").strip()
    
    if choice == "1":
        api_key = input("Enter your OpenAI API key: ").strip()
        if api_key:
            print(f"\nAdd these lines to your shell profile (~/.bashrc, ~/.zshrc, etc.):")
            print(f"export OPENAI_API_KEY='{api_key}'")
            print(f"export NLP_PROVIDER='openai'")
            return True
    
    elif choice == "2":
        print("\nTo use Ollama:")
        print("1. Install from https://ollama.ai")
        print("2. Run 'ollama serve' in one terminal")
        print("3. Run 'ollama run mistral' in another terminal")
        print("4. Add to shell profile:")
        print("export NLP_PROVIDER='ollama_local'")
        return True
    
    elif choice == "3":
        api_key = input("Enter your HuggingFace API key: ").strip()
        if api_key:
            print(f"\nAdd these lines to your shell profile:")
            print(f"export HUGGINGFACE_API_KEY='{api_key}'")
            print(f"export NLP_PROVIDER='huggingface'")
            return True
    
    elif choice == "4":
        api_key = input("Enter your Together.ai API key: ").strip()
        if api_key:
            print(f"\nAdd these lines to your shell profile:")
            print(f"export TOGETHER_API_KEY='{api_key}'")
            print(f"export NLP_PROVIDER='together'")
            return True
    
    return False

def main():
    print_header("SCAD Generator - NLP Setup Checker")
    
    # Check packages
    packages_ok = check_python_packages()
    
    # Check config
    config_ok = check_nlp_config()
    
    if not config_ok:
        response = input("\nWould you like to set up NLP now? (y/n): ").strip().lower()
        if response == 'y':
            interactive_setup()
        else:
            print("\nYou can set up NLP later. See NLP_INTEGRATION_GUIDE.md for details.")
    
    print("\n" + "="*60)
    if packages_ok:
        print("  ✓ Python packages are ready")
    else:
        print("  ✗ Please install missing packages: pip install requests")
    
    if config_ok:
        print("  ✓ NLP configuration looks good")
        # Try to test connection
        if test_nlp_connection():
            print("\n✓ Setup complete! You're ready to use the NLP features.")
            print("  Run: python ScadCodeGen.py")
        else:
            print("\n⚠ Could not test NLP connection. Check your configuration.")
    else:
        print("  ⚠ NLP not configured. See NLP_INTEGRATION_GUIDE.md for setup.")
    
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
