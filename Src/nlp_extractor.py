"""
NLP Extractor Module
Two-model approach for CAD parameter extraction:
1. Template Detection: LLM (Ollama/OpenAI) identifies which geometry type
2. Parameter Extraction: Geometry-trained model extracts parameters intelligently
"""

import os
import json
import re
from typing import Dict, List, Optional
import requests

# Try to use official OpenAI client
try:
    from openai import OpenAI
    HAS_OPENAI_CLIENT = True
except ImportError:
    HAS_OPENAI_CLIENT = False
    print("[WARN] openai package not installed. Install with: pip install openai")

# Try to import transformers for geometry model
HAS_TRANSFORMERS = False
try:
    from transformers import AutoTokenizer, AutoModelForCausalLM
    HAS_TRANSFORMERS = True
except ImportError:
    print("[WARN] transformers package not installed. Install with: pip install transformers torch")


class NLPExtractor:
    """
    Two-stage NLP extraction for CAD parameters:
    Stage 1: LLM detects which template/geometry the user wants
    Stage 2: Geometry-trained model extracts parameters from description
    """
    
    def __init__(self, provider: str = "auto", use_geometry_model: bool = True):
        """
        Initialize the NLP extractor with two models.
        
        Args:
            provider: "auto", "openai", or "ollama" (for template detection)
            use_geometry_model: Whether to use fine-tuned geometry model for parameter extraction
        """
        self.provider = self._detect_provider(provider)
        self.model = "mistral"  # Ollama default
        self.temperature = 0.3
        self.max_tokens = 500
        self.use_geometry_model = use_geometry_model and HAS_TRANSFORMERS
        
        # Load geometry model if available
        self.geometry_tokenizer = None
        self.geometry_model = None
        if self.use_geometry_model:
            self._load_geometry_model()
        
        if self.provider == "openai":
            if not HAS_OPENAI_CLIENT:
                raise ImportError("openai package required. Install with: pip install openai")
            
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set")
            
            self.client = OpenAI(api_key=api_key)
            self.model = "gpt-3.5-turbo"
            print("[INFO] Using OpenAI GPT-3.5-turbo for template detection")
            
        elif self.provider == "ollama":
            print("[INFO] Using local Ollama (mistral model) for template detection")
        else:
            raise ValueError(f"Unknown provider: {self.provider}")
    
    def _load_geometry_model(self):
        """Load the fine-tuned geometry model for parameter extraction."""
        try:
            # Import path resolver
            from path_resolver import get_geometry_model_dir
            # Try to load the specialized model first
            model_paths = [
                get_geometry_model_dir(),
                os.path.join(os.path.dirname(__file__), "..", "GeometryModel"),
            ]
            
            for model_path in model_paths:
                if os.path.exists(model_path) and os.path.exists(os.path.join(model_path, "config.json")):
                    print(f"[INFO] Loading geometry model from {model_path}")
                    self.geometry_tokenizer = AutoTokenizer.from_pretrained(model_path)
                    self.geometry_model = AutoModelForCausalLM.from_pretrained(model_path)
                    print("[INFO] Geometry model loaded successfully")
                    return
            
            print("[WARN] Geometry model not found in expected locations")
            print("[INFO] To create one:")
            print("  1. python generate_training_data.py")
            print("  2. python fine_tune_geometry_model.py")
            self.use_geometry_model = False
            
        except Exception as e:
            print(f"[WARN] Failed to load geometry model: {e}")
            self.use_geometry_model = False
    
    def _detect_provider(self, provider: str) -> str:
        """Auto-detect available provider for template detection."""
        if provider != "auto":
            return provider
        
        # Try Ollama first (local, fastest) - with short timeout
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=1)
            if response.status_code == 200:
                print("[INFO] Detected local Ollama")
                return "ollama"
        except:
            pass
        # Fallback detection via Ollama CLI if HTTP check fails
        try:
            import subprocess
            completed = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=5)
            if completed.returncode == 0 and "NAME" in completed.stdout:
                print("[INFO] Detected local Ollama via CLI")
                return "ollama"
        except:
            pass
        
        # Fall back to OpenAI if available
        if os.getenv("OPENAI_API_KEY"):
            print("[INFO] Detected OpenAI API key")
            return "openai"
        
        # Default to ollama
        print("[INFO] Defaulting to Ollama (make sure it's running)")
        return "ollama"
    
    def extract_parameters(
        self, 
        user_input: str, 
        param_names: List[str],
        template_name: str = ""
    ) -> Dict[str, str]:
        """
        Extract parameter values from natural language input.
        
        Args:
            user_input: Natural language description from user
            param_names: List of parameter names the template expects
            template_name: Optional template name for context
            
        Returns:
            Dictionary mapping param_name -> extracted_value (as strings)
        """
        if not user_input.strip():
            raise ValueError("User input cannot be empty")
        
        if not param_names:
            return {}
        
        # Build extraction prompt
        prompt = self._build_extraction_prompt(user_input, param_names, template_name)
        
        try:
            if self.provider == "openai":
                response_text = self._call_openai(prompt)
            else:  # ollama
                response_text = self._call_ollama(prompt)
            
            extracted = self._parse_nlp_response(response_text, param_names)
            return extracted
            
        except Exception as e:
            raise ValueError(f"NLP extraction failed: {str(e)}")
    
    def detect_template_and_extract(
        self,
        user_input: str,
        available_templates: List[str]
    ) -> tuple[str, Dict[str, str]]:
        """
        Detect which template the user wants AND extract its parameters.
        Uses LLM for template detection and geometry model for parameter extraction.
        
        Args:
            user_input: Full user description (e.g., "I want a 20 tooth gear")
            available_templates: List of available template names
            
        Returns:
            Tuple of (detected_template_name, parameters_dict)
        """
        if not user_input.strip():
            raise ValueError("User input cannot be empty")
        
        # Stage 1: Detect template using LLM
        prompt = f"""Identify which geometry type the user wants.

Available templates: {', '.join(available_templates)}

User request: "{user_input}"

Return ONLY the template name from the available list (exact match, no explanation):"""
        
        try:
            if self.provider == "openai":
                template_response = self._call_openai(prompt)
            else:
                template_response = self._call_ollama(prompt)
            
            template = template_response.strip().lower()
            
            # Find matching template
            matched_template = None
            for tpl in available_templates:
                if tpl.lower() in template or template in tpl.lower():
                    matched_template = tpl
                    break
            
            if not matched_template:
                for tpl in available_templates:
                    if tpl.split('_')[0].lower() in user_input.lower():
                        matched_template = tpl
                        break
            
            if not matched_template:
                raise ValueError(f"Could not match template. Got: {template}")
            
            # Stage 2: Extract parameters - LLM FIRST (more reliable for natural language)
            param_names = self._get_param_names_for_template(matched_template)
            
            # PRIMARY: Use LLM for parameter extraction (best for complex natural language)
            params = self._extract_with_llm(user_input, param_names, matched_template)
            
            # FALLBACK: If LLM got nothing, try geometry model
            if not params and self.use_geometry_model and self.geometry_model:
                print(f"[INFO] LLM extraction returned no results, trying geometry model...")
                params = self._extract_with_geometry_model(user_input, param_names, matched_template)
            
            return matched_template, params
            
        except Exception as e:
            raise ValueError(f"Template detection/extraction failed: {str(e)}")
    
    def _extract_with_geometry_model(self, user_input: str, param_names: List[str], template_name: str) -> Dict[str, str]:
        """Extract parameters using the fine-tuned geometry model."""
        result = {}
        
        # Build a prompt for the geometry model
        param_list = ", ".join(param_names)
        prompt = f"Extract parameters for {template_name.replace('_', ' ')}: {user_input}\nParameters: {param_list}\nExtracted: "
        
        try:
            # Tokenize and generate
            inputs = self.geometry_tokenizer(prompt, return_tensors="pt")
            outputs = self.geometry_model.generate(
                inputs["input_ids"],
                max_length=100,
                temperature=0.5,
                top_p=0.9,
                do_sample=True,
                pad_token_id=self.geometry_tokenizer.eos_token_id
            )
            
            generated_text = self.geometry_tokenizer.decode(outputs[0], skip_special_tokens=True)
            # Extract the part after "Extracted: "
            if "Extracted:" in generated_text:
                extracted_part = generated_text.split("Extracted:")[-1].strip()
            else:
                extracted_part = generated_text
            
            # Parse the generated text to extract parameter values
            result = self._parse_geometry_model_output(extracted_part, param_names)
            
            return result
            
        except Exception as e:
            print(f"[WARN] Geometry model extraction failed: {e}. Falling back to LLM.")
            return self._extract_with_llm(user_input, param_names, template_name)
    
    def _extract_with_llm(self, user_input: str, param_names: List[str], template_name: str) -> Dict[str, str]:
        """Fallback: Extract parameters using LLM with intelligent prompting."""
        
        extraction_prompt = f"""Extract parameters from this description for a {template_name.replace('_', ' ')}.

Parameters needed: {', '.join(param_names)}

User description: "{user_input}"

Return ONLY a JSON object with parameter names as keys:
{{"param_name": "value"}}

Example: {{"size": "40", "teeth": "20"}}

Rules:
1. Use ONLY the parameter names listed above (exact spelling)
2. Understand common geometric terminology and abbreviations
3. Return parameter values as strings
4. Return empty string "" if value not found
5. Return ONLY the JSON object, no other text
"""
        
        try:
            if self.provider == "openai":
                param_response = self._call_openai(extraction_prompt)
            else:
                param_response = self._call_ollama(extraction_prompt)
            
            params = self._parse_nlp_response(param_response, param_names)
            return params
            
        except Exception as e:
            raise ValueError(f"LLM parameter extraction failed: {str(e)}")
    
    def _get_param_names_for_template(self, template_name: str) -> List[str]:
        """Get parameter names for a template by looking at the .scad file."""
        import os
        # Handle template names with or without .scad extension
        if not template_name.lower().endswith('.scad'):
            template_path = os.path.join(os.path.dirname(__file__), "scad_dataset", f"{template_name}.scad")
        else:
            template_path = os.path.join(os.path.dirname(__file__), "scad_dataset", template_name)
        
        if not os.path.exists(template_path):
            return []
        
        try:
            with open(template_path, 'r') as f:
                content = f.read()
                # Look for // param: line
                param_match = re.search(r'//\s*param:\s*([^#\n]+)', content)
                if param_match:
                    param_str = param_match.group(1)
                    # Extract parameter names
                    params = []
                    for part in param_str.split(','):
                        if '=' in part:
                            param_name = part.split('=')[0].strip()
                            params.append(param_name)
                    return params
        except:
            pass
        
        return []
    
    def _parse_geometry_model_output(self, output: str, param_names: List[str]) -> Dict[str, str]:
        """Parse output from the geometry-trained model to extract parameters."""
        result = {}
        
        # The geometry model should understand parameter relationships
        # Try to extract JSON or key=value pairs
        
        # First try JSON format
        try:
            # Look for JSON in the output
            json_match = re.search(r'\{[^{}]*\}', output, re.DOTALL)
            if json_match:
                extracted_dict = json.loads(json_match.group())
                for param in param_names:
                    if param in extracted_dict:
                        result[param] = str(extracted_dict[param]).strip()
                    else:
                        # Try case-insensitive match
                        for key, value in extracted_dict.items():
                            if key.lower() == param.lower():
                                result[param] = str(value).strip()
                                break
                if result:
                    return result
        except:
            pass
        
        # Fallback: extract key=value or "key": "value" pairs
        for param in param_names:
            # Try various patterns
            patterns = [
                rf'{param}\s*[:=]\s*["\']?([^"\'\s,;]+)["\']?',
                rf'{param}["\']?\s*[:=]\s*["\']?(\d+)["\']?',
                rf'{param}\s*"\s*:\s*"([^"]+)"',
            ]
            
            for pattern in patterns:
                match = re.search(pattern, output, re.IGNORECASE)
                if match:
                    result[param] = match.group(1).strip()
                    break
        
        return result
    
    def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a CAD parameter extraction assistant. Extract values and return ONLY a valid JSON object with no extra text or markdown."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            timeout=30
        )
        return response.choices[0].message.content
    
    def _call_ollama(self, prompt: str) -> str:
        """Call local Ollama API."""
        # Ollama uses /api/chat endpoint
        api_url = "http://localhost:11434/api/chat"
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a CAD parameter extraction assistant. Extract values and return ONLY a valid JSON object."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "stream": False
        }
        
        try:
            response = requests.post(api_url, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            result = data["message"]["content"]
            return result
        except Exception as e:
            # Fallback to Ollama CLI if HTTP API is unavailable
            try:
                import subprocess
                # Use `ollama run` with the prompt; capture stdout
                # Note: `-p` expects the prompt string; ensure proper quoting on Windows
                completed = subprocess.run(
                    ["ollama", "run", self.model, "-p", prompt],
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                if completed.returncode == 0 and completed.stdout:
                    return completed.stdout.strip()
                else:
                    raise ValueError(completed.stderr.strip() or "Ollama CLI returned no output")
            except Exception as cli_err:
                raise ValueError(f"Ollama API error: {str(e)}; CLI fallback failed: {cli_err}")
    
    def _build_extraction_prompt(
        self, 
        user_input: str, 
        param_names: List[str],
        template_name: str = ""
    ) -> str:
        """
        Build the prompt to send to the LLM.
        Simplified for better Ollama compatibility.
        """
        params_str = ", ".join(param_names)
        
        prompt = f"""Extract CAD parameters from this description.

Parameters: {params_str}

Description: {user_input}

Return ONLY a JSON object like this (replace with actual values):
{{"param1": "value1", "param2": "value2"}}

If you don't know a value, use empty string "".
Return ONLY the JSON, nothing else."""
        return prompt
    
    def _parse_nlp_response(self, response: str, param_names: List[str]) -> Dict[str, str]:
        """
        Parse the API response to extract JSON parameters.
        More lenient parsing for Ollama. Maps synonyms to actual param names.
        """
        result = {}
        
        # Clean up response - remove markdown code blocks and extra whitespace
        response = response.replace("```json", "").replace("```", "").strip()
        
        # Ollama sometimes wraps JSON in extra text, try to extract just the JSON
        # Look for {...} pattern more carefully
        json_patterns = [
            r'\{[^{}]*(?:"[^"]*"[^{}]*)*\}',  # More flexible JSON pattern
            r'\{.*?\}',  # Greedy match
        ]
        
        for pattern in json_patterns:
            json_matches = re.finditer(pattern, response, re.DOTALL)
            for json_match in json_matches:
                try:
                    extracted_dict = json.loads(json_match.group())
                    
                    # Extract requested parameters
                    for param in param_names:
                        if param in extracted_dict:
                            value = extracted_dict[param]
                            if value and str(value).strip():
                                result[param] = str(value).strip()
                        else:
                            # Try case-insensitive match
                            for key, value in extracted_dict.items():
                                if key.lower() == param.lower():
                                    if value and str(value).strip():
                                        result[param] = str(value).strip()
                                    break
                    
                    if result:
                        return result
                except json.JSONDecodeError:
                    continue
        
        # Fallback: extract key=value pairs from text
        for param in param_names:
            pattern = rf'["\']?{param}["\']?\s*[:=]\s*["\']?(\d+)["\']?'
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                result[param] = match.group(1).strip()
        
        return result
    
    def validate_and_sanitize(
        self, 
        extracted: Dict[str, str],
        param_types: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        """
        Validate and sanitize extracted parameters.
        
        Args:
            extracted: Dictionary of extracted parameters
            param_types: Optional dict mapping param_name -> "numeric"|"string"|"enum"
            
        Returns:
            Sanitized parameter dictionary
        """
        sanitized = {}
        
        for param, value in extracted.items():
            if not value:
                continue
            
            param_type = (param_types or {}).get(param, "string")
            
            if param_type == "numeric":
                # Try to extract numeric value
                numeric_match = re.search(r'[-+]?\d+\.?\d*', str(value))
                if numeric_match:
                    sanitized[param] = numeric_match.group()
                else:
                    sanitized[param] = "0"  # Default numeric
            else:
                # String: clean up but keep as-is
                sanitized[param] = str(value).strip().strip('"\'')
        
        return sanitized


def test_nlp_extractor():
    """Test the NLP extractor with OpenAI API."""
    try:
        extractor = NLPExtractor()
        
        test_input = "I need a gear with 20 teeth and a pitch diameter of 50mm"
        params = ["teeth", "pitch_diameter", "width"]
        
        print("Testing NLP extraction...")
        print(f"Input: {test_input}")
        print(f"Parameters: {params}")
        print()
        
        result = extractor.extract_parameters(test_input, params, "gear_param.scad")
        print(f"Extraction successful!")
        print(f"Result: {result}")
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_nlp_extractor()
