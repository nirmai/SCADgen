#!/usr/bin/env python3
"""
Test the trained geometry model with real parameter extraction.
"""

import json
import os
from nlp_extractor import NLPExtractor

# Load available templates from scad_dataset
def load_available_templates():
    """Load list of available SCAD templates."""
    from path_resolver import get_scad_dataset_dir
    
    templates = []
    scad_dir = get_scad_dataset_dir()
    
    if not os.path.exists(scad_dir):
        print(f"[WARN] {scad_dir} not found, using defaults")
        return ["cube_param", "cylinder_param", "gear_param", "bushing_param"]
    
    for filename in os.listdir(scad_dir):
        if filename.endswith(".scad"):
            template_name = filename.replace(".scad", "")
            templates.append(template_name)
    
    return templates if templates else ["cube_param", "cylinder_param", "gear_param", "bushing_param"]

# Test cases
test_cases = [
    "Create a cube with 50mm sides",
    "I want a bushing with hole 20 and thickness 5",
    "Make a gear with 30 teeth",
    "Cylinder with radius 10 and height 25",
    "A cube that's 25 units on each side",
]

print("=" * 70)
print("🎓 GEOMETRY MODEL TEST - Parameter Extraction")
print("=" * 70)
print()

# Initialize NLP extractor
print("[SETUP] Initializing NLP Extractor...")
nlp = NLPExtractor(use_geometry_model=True)
print("✓ NLP Extractor initialized")
print()

# Load templates
available_templates = load_available_templates()
print(f"[INFO] Available templates ({len(available_templates)}):")
for t in available_templates:
    print(f"  - {t}")
print()

# Run tests
print("=" * 70)
print("Testing Parameter Extraction")
print("=" * 70)
print()

for i, test_input in enumerate(test_cases, 1):
    print(f"[Test {i}] {test_input}")
    print("-" * 70)
    
    try:
        template, params = nlp.detect_template_and_extract(test_input, available_templates)
        print(f"  Template: {template}")
        print(f"  Parameters: {json.dumps(params, indent=4)}")
    except Exception as e:
        print(f"  ❌ Error: {str(e)[:150]}")
    
    print()

print("=" * 70)
print("✅ Model Test Complete!")
print("=" * 70)
