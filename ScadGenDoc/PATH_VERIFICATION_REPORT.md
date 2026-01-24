# Path Verification Report - Post-Reorganization

**Date:** January 23, 2026  
**Status:** ⚠️ REQUIRES UPDATES

---

## Executive Summary

The code has been reorganized into a new structure, but **several Python scripts contain hardcoded relative paths that need to be updated** to work correctly with the new folder layout.

### New Structure Overview
```
SCADgen/
├── Src/                          # All Python source code
├── ScadLib/
│   ├── generated/               # Generated SCAD output
│   ├── datasets/                # Training datasets
│   └── shapes/                  # Shape library
├── GeometryModel/               # Model files (config, tokenizer, etc.)
├── ScadGenDoc/                  # Documentation (all .md files)
└── (legacy folders to clean up)
    ├── SCAD_gen/
    └── generated_scad/
```

---

## Path Dependencies Analysis

### 🔴 Critical Issues (Must Fix)

#### 1. **ScadCodeGen.py** - Lines 56-75
**Current hardcoded paths:**
- `scad_dataset` (relative to script location)
- `generated_scad` (at project root)

**Issue:** After reorganization:
- SCAD dataset moved to: `../ScadLib/datasets/`
- Generated output moved to: `../ScadLib/generated/`

**Status:** ⚠️ Script will not find datasets

**Fix Required:**
```python
# Current (broken):
scad_dataset_dir = os.path.join(script_dir, "scad_dataset")
output_dir = os.path.join(project_root, "generated_scad")

# Should be:
scad_dataset_dir = os.path.join(project_root, "ScadLib", "datasets")
output_dir = os.path.join(project_root, "ScadLib", "generated")
```

---

#### 2. **nlp_extractor.py** - Lines 80-85
**Current hardcoded paths:**
- `scad-gpt2-geometry-specialized` (relative to script)
- `scad-gpt2-finetuned/checkpoint-51`

**Issue:** Model files moved to: `../GeometryModel/`

**Status:** ⚠️ Geometry model will not load

**Fix Required:**
```python
# Current (broken):
os.path.join(os.path.dirname(__file__), "scad-gpt2-geometry-specialized")

# Should be:
os.path.join(os.path.dirname(__file__), "..", "GeometryModel")
```

---

#### 3. **generate_training_data.py** - Lines 17-18
**Current hardcoded paths:**
- `scad_dataset` (relative path, no base)
- `scad_shapes_library` (relative path, no base)

**Issue:** Files moved to: `../ScadLib/datasets/` and `../ScadLib/shapes/`

**Status:** ⚠️ Training data generation will fail

**Fix Required:**
```python
# Current (broken):
def __init__(self, scad_dataset_dir: str = "scad_dataset", library_dir: str = "scad_shapes_library"):

# Should be:
def __init__(self, scad_dataset_dir: str = None, library_dir: str = None):
    if scad_dataset_dir is None:
        scad_dataset_dir = os.path.join(os.path.dirname(__file__), "..", "ScadLib", "datasets")
    if library_dir is None:
        library_dir = os.path.join(os.path.dirname(__file__), "..", "ScadLib", "shapes")
```

---

#### 4. **collect_scad_shapes.py** - Lines 17-18
**Current hardcoded path:**
- `scad_shapes_library` (relative path)

**Issue:** Should point to: `../ScadLib/shapes/`

**Status:** ⚠️ Collection will fail

**Fix Required:**
```python
# Current (broken):
def __init__(self, output_dir: str = "scad_shapes_library"):

# Should be:
def __init__(self, output_dir: str = None):
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), "..", "ScadLib", "shapes")
```

---

#### 5. **test_geometry_model.py** - Line 10
**Current hardcoded path:**
- `scad_dataset` (relative path)

**Issue:** Should point to: `../ScadLib/datasets/`

**Status:** ⚠️ Tests will fail

**Fix Required:**
```python
# Current (broken):
scad_dir = "scad_dataset"

# Should be:
scad_dir = os.path.join(os.path.dirname(__file__), "..", "ScadLib", "datasets")
```

---

### 🟡 Secondary Issues (Best Practice)

#### 6. **nlp_extractor.py** - Line 153 (inside template loading)
**Current hardcoded path:**
- References `scad_dataset` directory

**Issue:** No immediate impact but inconsistent with new structure

---

## Path Resolution Strategy

### Recommended Approach: Dynamic Path Resolution

Create a utility module `path_resolver.py` in `Src/`:

```python
"""Path resolution utility for reorganized structure."""
import os

def get_project_root():
    """Get the SCADgen project root directory."""
    src_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(src_dir)

def get_scad_dataset_dir():
    """Get path to SCAD dataset directory."""
    return os.path.join(get_project_root(), "ScadLib", "datasets")

def get_scad_shapes_dir():
    """Get path to SCAD shapes library directory."""
    return os.path.join(get_project_root(), "ScadLib", "shapes")

def get_generated_scad_dir():
    """Get path to generated SCAD output directory."""
    return os.path.join(get_project_root(), "ScadLib", "generated")

def get_geometry_model_dir():
    """Get path to geometry model directory."""
    return os.path.join(get_project_root(), "GeometryModel")
```

Then use in scripts:
```python
from path_resolver import get_scad_dataset_dir, get_geometry_model_dir
# Instead of: scad_dataset_dir = "scad_dataset"
scad_dataset_dir = get_scad_dataset_dir()
```

---

## Verification Checklist

- [ ] Create `path_resolver.py` utility
- [ ] Update `ScadCodeGen.py` path resolution (lines 56-75)
- [ ] Update `nlp_extractor.py` model path (lines 80-85)
- [ ] Update `generate_training_data.py` __init__ (lines 17-18)
- [ ] Update `collect_scad_shapes.py` __init__ (lines 17-18)
- [ ] Update `test_geometry_model.py` load_available_templates (line 10)
- [ ] Test ScadCodeGen.py script execution
- [ ] Test NLP extractor model loading
- [ ] Test training data generation
- [ ] Test geometry model tests
- [ ] Verify all imports work from Src/ directory
- [ ] Clean up legacy directories (SCAD_gen/, generated_scad/)

---

## Current File Locations Status

### ✅ Correctly Located
- **Src/** - All 12 Python files
- **ScadLib/generated/** - All 6 generated SCAD files
- **ScadLib/datasets/** - All 9 dataset SCAD files
- **ScadLib/shapes/** - All 9 shape library SCAD files
- **GeometryModel/** - All 7 model config files
- **ScadGenDoc/** - All 13 markdown files

### ⚠️ Legacy (Can be removed)
- `SCAD_gen/CMTrain/` - Now empty (source files moved)
- `generated_scad/` - Now replaced by `ScadLib/generated/`

---

## Next Steps

1. **Implement path fixes** using the recommendations above
2. **Create path_resolver.py** for centralized path management
3. **Run verification tests** to ensure all paths work
4. **Update documentation** to reflect new paths
5. **Remove legacy directories** once verified

---

## Testing Commands

Once paths are fixed, test with:

```bash
# From Src/ directory
cd Src

# Test Python imports
python -c "import nlp_extractor; print('✓ NLP imports work')"

# Test geometry model loading
python test_geometry_model.py

# Test training data generation
python generate_training_data.py

# Test SCAD code generation (GUI)
python ScadCodeGen.py
```

---

