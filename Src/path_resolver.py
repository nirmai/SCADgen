"""
Path Resolution Utility for Reorganized SCADgen Structure

Centralizes path handling to work with the new folder organization:
- Src/              - Python source code
- ScadLib/
  - generated/      - Generated SCAD output
  - datasets/       - Training datasets
  - shapes/         - Shape library
- GeometryModel/    - Model configuration and tokenizer files
- ScadGenDoc/       - Documentation
"""

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


def get_src_dir():
    """Get path to Src directory."""
    return os.path.dirname(os.path.abspath(__file__))


def get_documentation_dir():
    """Get path to documentation directory."""
    return os.path.join(get_project_root(), "ScadGenDoc")


# Convenience exports
PROJECT_ROOT = get_project_root()
SCAD_DATASET_DIR = get_scad_dataset_dir()
SCAD_SHAPES_DIR = get_scad_shapes_dir()
GENERATED_SCAD_DIR = get_generated_scad_dir()
GEOMETRY_MODEL_DIR = get_geometry_model_dir()
SRC_DIR = get_src_dir()
DOCUMENTATION_DIR = get_documentation_dir()


def ensure_directories_exist():
    """Ensure all key directories exist."""
    dirs = [
        SCAD_DATASET_DIR,
        SCAD_SHAPES_DIR,
        GENERATED_SCAD_DIR,
        GEOMETRY_MODEL_DIR,
        DOCUMENTATION_DIR,
    ]
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)


if __name__ == "__main__":
    # Test the path resolver
    print("Path Resolution Test")
    print("=" * 60)
    print(f"Project Root:      {PROJECT_ROOT}")
    print(f"Src Directory:     {SRC_DIR}")
    print(f"Dataset Directory: {SCAD_DATASET_DIR}")
    print(f"Shapes Directory:  {SCAD_SHAPES_DIR}")
    print(f"Generated Output:  {GENERATED_SCAD_DIR}")
    print(f"Model Directory:   {GEOMETRY_MODEL_DIR}")
    print(f"Documentation:     {DOCUMENTATION_DIR}")
    print("=" * 60)
    print(f"Dataset exists:    {os.path.isdir(SCAD_DATASET_DIR)}")
    print(f"Shapes exist:      {os.path.isdir(SCAD_SHAPES_DIR)}")
    print(f"Generated exists:  {os.path.isdir(GENERATED_SCAD_DIR)}")
    print(f"Model exists:      {os.path.isdir(GEOMETRY_MODEL_DIR)}")
