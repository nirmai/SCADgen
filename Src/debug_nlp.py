#!/usr/bin/env python3
"""Debug script to check why NLP is disabled."""

import sys
import os

print("=" * 70)
print("DEBUG: Testing NLP Import  and Initialization")
print("=" * 70)
print()

# Check Python version
print(f"Python: {sys.version}")
print(f"Path: {sys.executable}")
print()

# Test direct import
print("[TEST 1] Direct import of nlp_extractor...")
try:
    from nlp_extractor import NLPExtractor
    print("✓ Direct import successful")
    HAS_NLP_DIRECT = True
except Exception as e:
    print(f"✗ Direct import failed: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    HAS_NLP_DIRECT = False

print()

# Test same way ScadCodeGen does it
print("[TEST 2] Import same way as ScadCodeGen.py...")
try:
    from nlp_extractor import NLPExtractor
    HAS_NLP = True
    print("[INFO] NLP extractor loaded successfully")
except Exception as e:
    HAS_NLP = False
    print(f"[ERROR] Failed to import NLP extractor: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()

print()

# Test initialization
if HAS_NLP:
    print("[TEST 3] Initialize NLPExtractor...")
    try:
        nlp = NLPExtractor()
        print("✓ NLPExtractor initialized successfully")
        print(f"  Provider: {nlp.provider}")
        print(f"  Geometry model available: {nlp.geometry_model is not None}")
    except Exception as e:
        print(f"✗ Initialization failed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
else:
    print("[TEST 3] SKIPPED - NLP not imported")

print()
print("=" * 70)
print(f"RESULT: HAS_NLP = {HAS_NLP}")
print("=" * 70)
