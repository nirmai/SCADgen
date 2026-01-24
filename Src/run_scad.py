#!/usr/bin/env python3
"""Wrapper to check NLP status before running ScadCodeGen."""

import sys
import os

# Fix encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Log to file
logfile = open("nlp_status.log", "w", encoding='utf-8')

def log(msg):
    print(msg)
    logfile.write(msg + "\n")
    logfile.flush()

# Check NLP import
log("Checking NLP import...")
try:
    from nlp_extractor import NLPExtractor
    log("[OK] NLP imported successfully")
    
    # Try to initialize
    log("Initializing NLP extractor...")
    nlp = NLPExtractor()
    log("[OK] NLP initialized successfully")
    
    log("")
    log("NLP Status:")
    log(f"  Provider: {nlp.provider}")
    log(f"  Geometry Model: {nlp.geometry_model is not None}")
    log("")
    log("[READY] NLP is ready! Starting ScadCodeGen...")
    log("")
    
except Exception as e:
    log(f"[ERROR] NLP initialization failed: {e}")
    log("Will start ScadCodeGen without NLP...")

logfile.close()

# Now run ScadCodeGen
print("Loading ScadCodeGen...")
from ScadCodeGen import main

print("Starting UI...")
main()
