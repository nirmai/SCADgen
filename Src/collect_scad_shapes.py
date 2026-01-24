"""
Download and collect diverse SCAD files from Thingiverse for comprehensive training.
Creates a diverse shape library for geometry model training.
"""

import os
import json
import urllib.request
import urllib.error
from typing import List, Dict
import time


class SCADCollector:
    """Collect diverse SCAD files for training."""
    
    def __init__(self, output_dir: str = None):
        # Import path resolver
        from path_resolver import get_scad_shapes_dir
        
        # Use default path if not provided
        if output_dir is None:
            output_dir = get_scad_shapes_dir()
        
        self.output_dir = output_dir
        self.metadata_file = os.path.join(output_dir, "metadata.json")
        os.makedirs(output_dir, exist_ok=True)
        self.metadata = {}
    
    # Common geometric shape categories on Thingiverse
    SEARCH_CATEGORIES = [
        # Basic shapes and primitives
        "cube parametric",
        "sphere parametric", 
        "cylinder parametric",
        "cone parametric",
        "torus parametric",
        
        # Mechanical parts
        "gear parametric",
        "bearing parametric",
        "pulley parametric",
        "shaft parametric",
        "bushing parametric",
        "bolt parametric",
        "nut parametric",
        "spring parametric",
        
        # Structural elements
        "bracket parametric",
        "frame parametric",
        "plate parametric",
        "tube parametric",
        "pipe parametric",
        "channel parametric",
        
        # Fasteners and connectors
        "screw parametric",
        "standoff parametric",
        "hinge parametric",
        "clamp parametric",
        
        # Common assemblies
        "motor mount parametric",
        "wheel parametric",
        "gear train parametric",
        "linkage parametric",
        
        # Utility shapes
        "box parametric",
        "enclosure parametric",
        "case parametric",
        "panel parametric",
        "duct parametric",
        "nozzle parametric",
    ]
    
    def get_thingiverse_download_urls(self, search_term: str, max_results: int = 5) -> List[str]:
        """
        Get download URLs for SCAD files from Thingiverse.
        NOTE: This would require API key or web scraping.
        For now, providing a template approach.
        """
        # In practice, you would:
        # 1. Use Thingiverse API (requires API key)
        # 2. Search for SCAD files
        # 3. Get direct download links
        
        print(f"[INFO] Would search Thingiverse for: {search_term}")
        return []
    
    def get_github_scad_files(self, max_per_search: int = 3) -> List[Dict]:
        """
        Find SCAD files on GitHub.
        Uses GitHub REST API (no auth needed for search).
        """
        files_found = []
        
        searches = [
            "path:*.scad parametric cube",
            "path:*.scad parametric cylinder",
            "path:*.scad parametric gear",
            "path:*.scad parametric bearing",
            "path:*.scad parametric bracket",
            "path:*.scad module:* size dimensions",
        ]
        
        for search in searches[:2]:  # Limit API calls
            try:
                # GitHub API search
                url = f"https://api.github.com/search/code?q={search}&per_page={max_per_search}"
                print(f"[INFO] Searching GitHub: {search}")
                
                req = urllib.request.Request(url)
                req.add_header('User-Agent', 'Mozilla/5.0')
                
                response = urllib.request.urlopen(req, timeout=5)
                data = json.loads(response.read().decode())
                
                for item in data.get('items', [])[:max_per_search]:
                    files_found.append({
                        'name': item['name'],
                        'url': item['download_url'],
                        'repo': item['repository']['full_name'],
                    })
                
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                print(f"[WARN] GitHub search failed: {e}")
        
        return files_found
    
    def download_scad_file(self, url: str, filename: str) -> bool:
        """Download a SCAD file."""
        try:
            filepath = os.path.join(self.output_dir, filename)
            
            # Check if already exists
            if os.path.exists(filepath):
                return True
            
            print(f"[INFO] Downloading {filename}...")
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0')
            
            response = urllib.request.urlopen(req, timeout=10)
            content = response.read().decode('utf-8', errors='ignore')
            
            # Verify it's SCAD content
            if 'module' not in content and 'cube' not in content:
                print(f"[WARN] File doesn't look like SCAD: {filename}")
                return False
            
            with open(filepath, 'w') as f:
                f.write(content)
            
            print(f"[SUCCESS] Downloaded {filename} ({len(content)} bytes)")
            return True
            
        except Exception as e:
            print(f"[WARN] Download failed: {e}")
            return False
    
    def create_sample_shapes(self):
        """Create sample parametric shape files if downloading fails."""
        print("\n[INFO] Creating sample parametric shapes...")
        
        samples = {
            'basic_cube.scad': '''// param: size=10
module param_cube(size=10) {
    cube([size, size, size], center=true);
}
param_cube(size=10);
''',
            'basic_cylinder.scad': '''// param: radius=5, height=20
module param_cylinder(radius=5, height=20) {
    cylinder(r=radius, h=height, center=true);
}
param_cylinder(radius=5, height=20);
''',
            'basic_sphere.scad': '''// param: radius=10
module param_sphere(radius=10) {
    sphere(r=radius);
}
param_sphere(radius=10);
''',
            'basic_cone.scad': '''// param: radius=10, height=20
module param_cone(radius=10, height=20) {
    cylinder(r1=radius, r2=0, h=height, center=true);
}
param_cone(radius=10, height=20);
''',
            'basic_torus.scad': '''// param: major_radius=20, minor_radius=5
module param_torus(major_radius=20, minor_radius=5) {
    rotate_extrude() translate([major_radius, 0, 0]) circle(r=minor_radius);
}
param_torus(major_radius=20, minor_radius=5);
''',
            'hexagonal_prism.scad': '''// param: size=10, height=20
module hexagonal_prism(size=10, height=20) {
    linear_extrude(height=height) circle(r=size, $fn=6);
}
hexagonal_prism(size=10, height=20);
''',
            'rectangular_box.scad': '''// param: width=20, depth=15, height=10
module rectangular_box(width=20, depth=15, height=10) {
    cube([width, depth, height], center=true);
}
rectangular_box(width=20, depth=15, height=10);
''',
            'hollow_cylinder.scac': '''// param: outer_radius=10, inner_radius=5, height=20
module hollow_cylinder(outer_radius=10, inner_radius=5, height=20) {
    difference() {
        cylinder(r=outer_radius, h=height, center=true);
        cylinder(r=inner_radius, h=height+1, center=true);
    }
}
hollow_cylinder(outer_radius=10, inner_radius=5, height=20);
''',
            'rounded_cube.scad': '''// param: size=10, radius=2
module rounded_cube(size=10, radius=2) {
    minkowski() {
        cube([size-2*radius, size-2*radius, size-2*radius], center=true);
        sphere(r=radius);
    }
}
rounded_cube(size=10, radius=2);
''',
            'pyramid.scad': '''// param: base_size=20, height=15
module pyramid(base_size=20, height=15) {
    linear_extrude(height=height, scale=0.01) square(base_size, center=true);
}
pyramid(base_size=20, height=15);
''',
        }
        
        created = 0
        for filename, content in samples.items():
            filepath = os.path.join(self.output_dir, filename)
            if not os.path.exists(filepath):
                with open(filepath, 'w') as f:
                    f.write(content)
                print(f"[INFO] Created {filename}")
                created += 1
        
        return created
    
    def catalog_shapes(self) -> Dict[str, Dict]:
        """Catalog all SCAD files in the library."""
        catalog = {}
        
        if not os.path.exists(self.output_dir):
            return catalog
        
        for filename in os.listdir(self.output_dir):
            if not filename.endswith('.scad'):
                continue
            
            filepath = os.path.join(self.output_dir, filename)
            try:
                with open(filepath, 'r') as f:
                    content = f.read()
                
                # Extract parameters
                import re
                param_match = re.search(r'//\s*param:\s*([^#\n]+)', content)
                params = param_match.group(1) if param_match else ""
                
                # Extract module name
                module_match = re.search(r'module\s+(\w+)', content)
                module_name = module_match.group(1) if module_match else "unknown"
                
                catalog[filename] = {
                    'module': module_name,
                    'params': params,
                    'path': filepath,
                }
            except Exception as e:
                print(f"[WARN] Error reading {filename}: {e}")
        
        return catalog
    
    def generate_index(self) -> None:
        """Generate an index of all shapes."""
        catalog = self.catalog_shapes()
        
        with open(self.metadata_file, 'w') as f:
            json.dump({
                'total_shapes': len(catalog),
                'shapes': catalog,
            }, f, indent=2)
        
        print(f"\n[SUCCESS] Cataloged {len(catalog)} SCAD files")
        print(f"[INFO] Index saved to {self.metadata_file}")


def main():
    """Collect and organize SCAD files."""
    print("=" * 60)
    print("SCAD Shape Library Builder")
    print("=" * 60)
    
    collector = SCADCollector()
    
    # Try to download from GitHub
    print("\n[STEP 1] Searching for SCAD files on GitHub...")
    github_files = collector.get_github_scad_files(max_per_search=2)
    
    if github_files:
        print(f"[INFO] Found {len(github_files)} files on GitHub")
        for file_info in github_files:
            collector.download_scad_file(file_info['url'], file_info['name'])
    
    # Create sample shapes
    print("\n[STEP 2] Creating sample parametric shapes...")
    created = collector.create_sample_shapes()
    print(f"[INFO] Created {created} sample shapes")
    
    # Catalog everything
    print("\n[STEP 3] Cataloging shapes...")
    collector.generate_index()
    
    print("\n[SUCCESS] Shape library ready!")
    print(f"[NEXT] Run: python generate_training_data.py")


if __name__ == "__main__":
    main()
