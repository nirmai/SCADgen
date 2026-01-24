#!/usr/bin/env python3
"""Quick test to verify NLP is enabled in the app."""

import os
import sys

print("\n" + "="*70)
print("VERIFICATION: NLP Status in ScadCodeGen")
print("="*70 + "\n")

# Test 1: Import ScadCodeGen and check HAS_NLP
print("[TEST 1] Check ScadCodeGen's HAS_NLP variable...")
try:
    import ScadCodeGen
    if ScadCodeGen.HAS_NLP:
        print("  Status: HAS_NLP = True")
        print("  [OK] NLP is enabled in ScadCodeGen")
    else:
        print("  Status: HAS_NLP = False")
        print("  [ERROR] NLP is disabled in ScadCodeGen")
        print("\n  Debugging: Let's see why...")
        print("  Checking if nlp_extractor can be imported...")
        try:
            from nlp_extractor import NLPExtractor
            print("    - nlp_extractor imports successfully")
            nlp = NLPExtractor()
            print("    - NLPExtractor initializes successfully")
            print("\n  [CONCLUSION] The import/init works standalone.")
            print("  Something else might be wrong in ScadCodeGen's import block.")
        except Exception as e:
            print(f"    - Error: {e}")
except ImportError as e:
    print(f"  Cannot import ScadCodeGen: {e}")

print("\n" + "="*70)
print("To use NLP mode:")
print("  1. Ensure Ollama is running (for template detection)")
print("  2. Click on the 'Smart NLP Mode' tab")
print("  3. Enter a natural language description")
print("  4. The model will extract parameters automatically")
print("="*70 + "\n")
