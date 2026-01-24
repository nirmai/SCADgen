"""
Example: Using the NLP Extractor Programmatically

This example shows how to integrate the NLP component into your own scripts.
"""

import os
import sys
from pathlib import Path

# Add CMTrain to path if running from elsewhere
sys.path.insert(0, str(Path(__file__).parent))

from nlp_extractor import NLPExtractor
from nlp_config import get_config, list_providers


def example_1_basic_extraction():
    """Example 1: Basic parameter extraction from description."""
    print("=" * 60)
    print("Example 1: Basic Parameter Extraction")
    print("=" * 60)
    
    # Create extractor
    extractor = NLPExtractor()
    
    # User description
    user_input = "I need a cylindrical part that is 100mm tall with a 50mm diameter hole through the center"
    
    # Parameters the template expects
    expected_params = ["height", "diameter", "hole_diameter"]
    
    # Extract parameters
    try:
        extracted = extractor.extract_parameters(
            user_input, 
            expected_params,
            template_name="cylinder_param.scad"
        )
        
        print(f"\nUser input: {user_input}")
        print(f"Expected parameters: {expected_params}")
        print(f"\nExtracted parameters:")
        for param, value in extracted.items():
            print(f"  {param}: {value}")
        
    except Exception as e:
        print(f"Error: {e}")


def example_2_multiple_inputs():
    """Example 2: Extract parameters from multiple user inputs."""
    print("\n" + "=" * 60)
    print("Example 2: Multiple Inputs")
    print("=" * 60)
    
    extractor = NLPExtractor()
    
    test_cases = [
        {
            "input": "A gear with 24 teeth, 40mm pitch diameter",
            "template": "gear_param.scad",
            "params": ["teeth", "pitch_diameter", "width"]
        },
        {
            "input": "Hexagonal bolt - 10mm diameter, 50mm long, coarse pitch",
            "template": "hexboltParam.scad",
            "params": ["diameter", "length", "pitch"]
        },
        {
            "input": "A spherical shape 75mm in diameter",
            "template": "sphereParam.scad",
            "params": ["diameter", "resolution"]
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n--- Test Case {i}: {test['template']} ---")
        print(f"Input: {test['input']}")
        
        try:
            extracted = extractor.extract_parameters(
                test['input'],
                test['params'],
                test['template']
            )
            
            print("Extracted:")
            for k, v in extracted.items():
                print(f"  {k}: {v}")
                
        except Exception as e:
            print(f"Error: {e}")


def example_3_with_validation():
    """Example 3: Extract and validate parameters."""
    print("\n" + "=" * 60)
    print("Example 3: Extraction with Validation")
    print("=" * 60)
    
    extractor = NLPExtractor()
    
    # Define expected parameter types
    param_types = {
        "width": "numeric",
        "height": "numeric",
        "material": "string",
        "thickness": "numeric"
    }
    
    user_input = "Box made of aluminum, 200mm wide, 150mm tall, 5mm thick walls"
    params = list(param_types.keys())
    
    try:
        # Extract
        extracted = extractor.extract_parameters(user_input, params)
        print(f"Raw extraction: {extracted}")
        
        # Validate and sanitize
        validated = extractor.validate_and_sanitize(extracted, param_types)
        print(f"Validated: {validated}")
        
    except Exception as e:
        print(f"Error: {e}")


def example_4_using_different_provider():
    """Example 4: Use a specific NLP provider."""
    print("\n" + "=" * 60)
    print("Example 4: Different NLP Providers")
    print("=" * 60)
    
    print("\nAvailable providers:")
    print("  - openai: Uses OpenAI GPT API")
    print("  - ollama_local: Uses local Ollama instance")
    print("  - huggingface: Uses HuggingFace Inference API")
    print("  - together: Uses Together.ai API")
    
    # Get config for a specific provider
    try:
        config = get_config("ollama_local")
        print(f"\nOllama config: {config}")
        
        # Create extractor with this config
        extractor = NLPExtractor(config)
        print(f"Extractor created with model: {extractor.model}")
        
    except Exception as e:
        print(f"Could not load Ollama: {e}")
        print("(Make sure Ollama is installed and running)")


def example_5_integration_with_scad_generation():
    """Example 5: Full workflow - NLP extraction + SCAD generation."""
    print("\n" + "=" * 60)
    print("Example 5: Full Workflow (NLP + SCAD Generation)")
    print("=" * 60)
    
    # This shows how to integrate with the main ScadCodeGen
    print("""
    # Typical workflow:
    
    1. Get user description (from UI or CLI)
    user_description = "20 tooth gear with 50mm pitch diameter"
    
    2. Select template
    template = "gear_param.scad"
    param_names = get_param_names(template)
    
    3. Extract parameters via NLP
    extractor = NLPExtractor()
    extracted_params = extractor.extract_parameters(
        user_description, 
        param_names,
        template
    )
    
    4. Generate SCAD
    generate_scad_from_template(
        template,
        extracted_params,
        output_filename="my_gear"
    )
    
    5. Done! File generated at: generated_scad/my_gear.scad
    """)


def example_6_error_handling():
    """Example 6: Proper error handling."""
    print("\n" + "=" * 60)
    print("Example 6: Error Handling")
    print("=" * 60)
    
    extractor = NLPExtractor()
    
    # Test various error conditions
    test_cases = [
        {
            "description": "Empty input",
            "input": "",
            "params": ["width"]
        },
        {
            "description": "No parameters in response",
            "input": "Just random text with no numbers or measurements",
            "params": ["width", "height"]
        },
    ]
    
    for test in test_cases:
        print(f"\n--- {test['description']} ---")
        try:
            result = extractor.extract_parameters(
                test['input'],
                test['params']
            )
            print(f"Result: {result}")
        except ValueError as e:
            print(f"Caught expected error: {e}")


def example_7_custom_extraction_logic():
    """Example 7: Custom extraction for specific use cases."""
    print("\n" + "=" * 60)
    print("Example 7: Custom Extraction Logic")
    print("=" * 60)
    
    class CustomNLPExtractor(NLPExtractor):
        """Extended extractor with custom logic for specific templates."""
        
        def _build_extraction_prompt(self, user_input, param_names, template_name=""):
            """Override to provide custom prompts per template type."""
            
            if "gear" in template_name.lower():
                return f"""
                Extract gear specifications from: "{user_input}"
                
                Return JSON with parameters: {param_names}
                Include common gear terminology (teeth count, pitch diameter, module, etc).
                """
            
            elif "bushing" in template_name.lower():
                return f"""
                Extract bushing dimensions from: "{user_input}"
                
                Return JSON with parameters: {param_names}
                Include bore diameter, outer diameter, length/height.
                """
            
            else:
                # Use default
                return super()._build_extraction_prompt(user_input, param_names, template_name)
    
    # Usage
    extractor = CustomNLPExtractor()
    
    print("Custom extractor created with template-specific prompts.")
    print("This allows for more accurate extraction for specific part types.")


def main():
    """Run all examples."""
    examples = [
        ("Basic Extraction", example_1_basic_extraction),
        ("Multiple Inputs", example_2_multiple_inputs),
        ("With Validation", example_3_with_validation),
        ("Different Providers", example_4_using_different_provider),
        ("Full Workflow", example_5_integration_with_scad_generation),
        ("Error Handling", example_6_error_handling),
        ("Custom Logic", example_7_custom_extraction_logic),
    ]
    
    print("\n" + "="*60)
    print("  SCAD Generator - NLP Examples")
    print("="*60)
    
    print("\nAvailable examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")
    
    print(f"  0. Run all examples")
    
    choice = input("\nSelect example to run (0-7): ").strip()
    
    if choice == "0":
        # Run all
        for name, func in examples:
            func()
    elif choice.isdigit() and 0 < int(choice) <= len(examples):
        # Run selected
        examples[int(choice)-1][1]()
    else:
        print("Invalid choice")
    
    print("\n" + "="*60)
    print("Examples complete!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
