"""
Generate synthetic training data from SCAD templates for geometry model fine-tuning.
Creates diverse parameter descriptions to train the model on parameter extraction.
"""

import os
import json
import re
import random
from typing import Dict, List, Tuple
from itertools import product


class SCADTrainingDataGenerator:
    """Generate training data from SCAD templates."""
    
    def __init__(self, scad_dataset_dir: str = None, library_dir: str = None):
        # Import path resolver
        from path_resolver import get_scad_dataset_dir, get_scad_shapes_dir
        
        # Use default paths if not provided
        if scad_dataset_dir is None:
            scad_dataset_dir = get_scad_dataset_dir()
        if library_dir is None:
            library_dir = get_scad_shapes_dir()
        
        # Try library first (comprehensive), then fall back to dataset
        self.scad_dir = scad_dataset_dir
        self.library_dir = library_dir
        self.templates = {}
        
        # Load from library first
        if os.path.isdir(library_dir):
            print(f"[INFO] Loading from shape library: {library_dir}")
            self.templates = self._load_templates(library_dir)
        
        # Supplement with dataset templates
        if os.path.isdir(scad_dataset_dir):
            print(f"[INFO] Loading from dataset: {scad_dataset_dir}")
            dataset_templates = self._load_templates(scad_dataset_dir)
            self.templates.update(dataset_templates)
        
        # Natural language variations for describing parameters
        self.param_descriptions = {
            'size': [
                'size of {value}',
                'cube with sides of {value}',
                '{value} unit cube',
                'dimensions {value}x{value}x{value}',
                '{value} cubic',
            ],
            'inner_d': [
                'hole diameter {value}',
                'bore of {value}',
                'inner diameter {value}',
                'bore diameter {value}',
                '{value} hole',
            ],
            'outer_d': [
                'outer diameter {value}',
                'outside diameter {value}',
                'OD {value}',
                '{value} outer diameter',
                'external diameter {value}',
            ],
            'thickness': [
                'thickness of {value}',
                '{value} thick',
                'wall thickness {value}',
                '{value} mm thick',
                'depth {value}',
            ],
            'height': [
                'height {value}',
                '{value} tall',
                '{value} height',
                'vertical dimension {value}',
            ],
            'teeth': [
                '{value} teeth',
                'gear with {value} teeth',
                '{value} tooth gear',
                '{value} tooth count',
            ],
            'pitch_diameter': [
                'pitch diameter {value}',
                'pitch {value}',
                '{value} pitch diameter',
            ],
            'width': [
                'width {value}',
                '{value} wide',
            ],
            'diameter': [
                'diameter {value}',
                '{value} diameter',
            ],
        }
        
        # Combining phrases for multi-parameter descriptions
        self.combiners = [
            'with {param2} {value2}',
            'and {param2} is {value2}',
            ', {param2} {value2}',
            'with {param2} of {value2}',
        ]
    
    
    def _load_templates(self, directory: str) -> Dict[str, Dict]:
        """Load all SCAD templates from a directory and extract parameters."""
        templates = {}
        
        if not os.path.isdir(directory):
            return templates
        
        for filename in os.listdir(directory):
            if not filename.endswith('.scad'):
                continue
            
            filepath = os.path.join(directory, filename)
            template_name = filename.replace('.scad', '')
            
            params = self._extract_params(filepath)
            if params:
                templates[template_name] = params
                print(f"[INFO] Loaded {template_name}: {list(params.keys())}")
        
        return templates
    
    def _extract_params(self, filepath: str) -> Dict[str, float]:
        """Extract parameters from SCAD file."""
        try:
            with open(filepath, 'r') as f:
                content = f.read()
                
            # Look for // param: line
            param_match = re.search(r'//\s*param:\s*([^#\n]+)', content)
            if not param_match:
                return {}
            
            param_str = param_match.group(1)
            params = {}
            
            for part in param_str.split(','):
                if '=' in part:
                    name, value = part.split('=', 1)
                    name = name.strip()
                    try:
                        value = float(value.strip())
                        params[name] = value
                    except:
                        pass
            
            return params
        except Exception as e:
            print(f"[WARN] Error reading {filepath}: {e}")
            return {}
    
    def _get_param_ranges(self, template: str, param_name: str) -> Tuple[float, float, float]:
        """Get reasonable min, max, and step for a parameter."""
        # Default ranges
        ranges = {
            'size': (5, 100, 5),
            'inner_d': (5, 50, 5),
            'outer_d': (20, 100, 10),
            'thickness': (1, 50, 2),
            'height': (5, 100, 5),
            'teeth': (10, 50, 2),
            'pitch_diameter': (20, 100, 10),
            'width': (5, 50, 5),
            'diameter': (10, 100, 10),
        }
        
        # Override with actual defaults if available
        if template in self.templates:
            actual_value = self.templates[template].get(param_name)
            if actual_value:
                min_val = max(actual_value * 0.5, 1)
                max_val = actual_value * 3
                step = actual_value * 0.2
                return (min_val, max_val, step)
        
        return ranges.get(param_name, (10, 100, 10))
    
    def generate_single_param_examples(self, template: str, num_per_param: int = 5) -> List[Dict]:
        """Generate examples with single parameter variation."""
        examples = []
        
        if template not in self.templates:
            return examples
        
        params = self.templates[template]
        
        for param_name, default_value in params.items():
            min_val, max_val, step = self._get_param_ranges(template, param_name)
            
            # Generate a few values
            values = []
            current = min_val
            while current <= max_val and len(values) < num_per_param:
                values.append(int(current))
                current += step
            
            # Create descriptions for each value
            for value in values:
                if param_name in self.param_descriptions:
                    descriptions = self.param_descriptions[param_name]
                    description = random.choice(descriptions).format(value=value)
                else:
                    description = f"{param_name} {value}"
                
                # Create training example
                param_dict = params.copy()
                param_dict[param_name] = value
                
                example = {
                    'template': template,
                    'description': f"Create a {template.replace('_', ' ')}: {description}",
                    'parameters': param_dict,
                }
                examples.append(example)
        
        return examples
    
    def generate_multi_param_examples(self, template: str, num_examples: int = 10) -> List[Dict]:
        """Generate examples with multiple parameter variations."""
        examples = []
        
        if template not in self.templates:
            return examples
        
        params = self.templates[template]
        
        # Generate combinations
        for _ in range(num_examples):
            param_dict = {}
            descriptions = []
            
            for param_name, default_value in params.items():
                min_val, max_val, step = self._get_param_ranges(template, param_name)
                
                # Random value in range
                value = int(random.uniform(min_val, max_val) // step) * step
                param_dict[param_name] = value
                
                # Get description
                if param_name in self.param_descriptions:
                    desc = random.choice(self.param_descriptions[param_name]).format(value=int(value))
                    descriptions.append(desc)
            
            # Combine descriptions
            description = descriptions[0] if descriptions else ""
            for desc in descriptions[1:]:
                combiner = random.choice(self.combiners)
                param_name = list(params.keys())[descriptions.index(desc)]
                value = param_dict[param_name]
                description += " with " + desc
            
            example = {
                'template': template,
                'description': f"Create a {template.replace('_', ' ')}: {description}",
                'parameters': param_dict,
            }
            examples.append(example)
        
        return examples
    
    def generate_all_training_data(self, output_file: str = "synthetic_training_data.jsonl", 
                                   examples_per_template: int = 20) -> int:
        """Generate all training data and save to file."""
        all_examples = []
        
        for template in self.templates.keys():
            print(f"[INFO] Generating examples for {template}...")
            
            # Single parameter variations
            single_examples = self.generate_single_param_examples(template, num_per_param=5)
            all_examples.extend(single_examples)
            
            # Multi-parameter variations
            multi_examples = self.generate_multi_param_examples(
                template, 
                num_examples=max(1, examples_per_template - len(single_examples))
            )
            all_examples.extend(multi_examples)
        
        # Shuffle
        random.shuffle(all_examples)
        
        # Save to JSONL
        with open(output_file, 'w') as f:
            for example in all_examples:
                # Format for GPT-2 fine-tuning
                # "description" -> extract params -> output format
                line = {
                    'text': f"Extract: {example['description']}\nParameters: {json.dumps(example['parameters'])}"
                }
                f.write(json.dumps(line) + '\n')
        
        print(f"[INFO] Generated {len(all_examples)} training examples")
        print(f"[INFO] Saved to {output_file}")
        
        return len(all_examples)


def main():
    """Generate training data."""
    print("=" * 60)
    print("Synthetic Training Data Generator")
    print("=" * 60)
    
    # First, ensure we have shape library
    if not os.path.exists("scad_shapes_library"):
        print("\n[INFO] Shape library not found. Creating...")
        import subprocess
        result = subprocess.run(["python", "collect_scad_shapes.py"], capture_output=True, text=True)
        print(result.stdout)
        if result.returncode != 0:
            print(f"[ERROR] Failed to create shape library: {result.stderr}")
            return
    
    generator = SCADTrainingDataGenerator()
    
    if not generator.templates:
        print("[ERROR] No SCAD templates found!")
        return
    
    print(f"\n[INFO] Found {len(generator.templates)} templates")
    
    # Generate training data
    count = generator.generate_all_training_data(
        output_file="synthetic_training_data.jsonl",
        examples_per_template=20
    )
    
    print(f"\n[SUCCESS] Generated {count} training examples!")
    print("[NEXT] Run: python fine_tune_geometry_model.py")


if __name__ == "__main__":
    main()
