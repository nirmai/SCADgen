# SCAD Generator with NLP Component

## Overview

The updated SCAD Generator now includes a natural language processing (NLP) component that allows users to describe their CAD objects in plain English, and the system automatically extracts the required parameters and fills in the templates.

## Architecture

### Two-Model Approach

1. **NLP Extraction Model**: Receives user description → Extracts parameter values
   - Used strictly to understand user intent and extract information
   - Lightweight and focused on parameter extraction
   - Configurable to use different APIs

2. **SCAD Template Model**: Receives extracted parameters → Generates OpenSCAD code
   - Your existing model that fills in templates with concrete values
   - Remains unchanged; just receives better-structured input

### Data Flow

```
User Input (Natural Language)
    ↓
[NLP Extractor API Call]
    ↓
Extracted Parameters (key=value pairs)
    ↓
[SCAD Template Generator]
    ↓
Generated .scad File
```

## UI Modes

The application now has a tabbed interface with two modes:

### Mode 1: NLP Mode (Describe in Words)
- Write a natural description of what you want
- Click "Extract Parameters (NLP)" 
- System calls the NLP API to extract values
- Fields auto-populate with extracted values
- Click "Generate SCAD" to create the file

**Example**: 
- Input: "I want a gear with 20 teeth, 50mm pitch diameter, and 10mm width"
- Output: `teeth=20`, `pitch_diameter=50`, `width=10`

### Mode 2: Manual Mode (Original)
- Select template
- Manually enter parameter values in text fields
- Works the same as before
- Good for advanced users or when NLP extraction isn't needed

## Setup & Configuration

### Installation

```bash
# Install required package (if not already installed)
pip install requests
```

### Configuring NLP Provider

The system supports multiple NLP API providers. Set up one via environment variables:

#### Option 1: OpenAI API (Recommended)
```bash
export OPENAI_API_KEY="sk-..."
export NLP_PROVIDER="openai"
```

#### Option 2: Local Ollama (Free, Runs Locally)
```bash
# First, install and run Ollama: https://ollama.ai
ollama run mistral  # or: llama2, neural-chat, etc.

# Then set environment variable
export NLP_PROVIDER="ollama_local"
```

#### Option 3: HuggingFace Inference API
```bash
export HUGGINGFACE_API_KEY="hf_..."
export NLP_PROVIDER="huggingface"
```

#### Option 4: Together.ai API
```bash
export TOGETHER_API_KEY="..."
export NLP_PROVIDER="together"
```

#### Option 5: Custom Endpoint
```bash
export NLP_API_URL="http://your-server:port/endpoint"
export NLP_MODEL="your-model-name"
export NLP_PROVIDER="custom"
```

### Auto-Detection

If no provider is explicitly set, the system will:
1. Check for OpenAI API key → use OpenAI
2. Check for HuggingFace API key → use HuggingFace
3. Check if Ollama is running locally → use Ollama
4. Default to OpenAI (will fail if no API key set)

## Usage

### GUI Mode (Default)

```bash
cd SCADgen/SCAD_gen/CMTrain/
python ScadCodeGen.py
```

Then:
1. Click the "NLP Mode" tab
2. Select a template from dropdown
3. Describe what you want in the text area
4. Click "Extract Parameters (NLP)"
5. Review/adjust extracted values
6. Click "Generate SCAD"

### CLI Mode

#### List templates
```bash
python ScadCodeGen.py --list
```

#### Generate with NLP input
```bash
python ScadCodeGen.py --template gear_param.scad \
    --nlp-input "20 teeth gear with 50mm pitch diameter" \
    --output my_gear
```

#### Generate with manual parameters
```bash
python ScadCodeGen.py --template gear_param.scad \
    --set teeth=20 pitch_diameter=50 \
    --output my_gear
```

#### Headless mode (no GUI)
```bash
python ScadCodeGen.py --no-gui --template gear_param.scad \
    --nlp-input "your description here"
```

## How NLP Extraction Works

### The Extraction Prompt

The system sends a carefully crafted prompt to the NLP model:

```
You are a parameter extraction assistant. Extract numerical and categorical values 
from user descriptions.

User wants to create a CAD object with these parameters: teeth, pitch_diameter, width
Template: gear_param.scad

User input: "20 teeth gear with 50mm pitch diameter and 10mm width"

Extract the values for each parameter. Return ONLY a JSON object...
Response:
```

### Parsing the Response

The extractor handles multiple response formats:
1. **JSON format** (preferred): `{"teeth": "20", "pitch_diameter": "50", "width": "10"}`
2. **Key-value pairs**: `teeth=20, pitch_diameter=50, width=10`
3. **Partial matches**: If only some parameters are found, uses reasonable defaults

### Error Handling

If extraction fails:
- Missing parameters get empty strings (user can fill manually)
- Invalid API responses show an error dialog
- User can always fall back to Manual Mode

## File Structure

```
SCAD_gen/CMTrain/
├── ScadCodeGen.py           # Main script (updated with NLP support)
├── nlp_extractor.py         # NLP extraction module (NEW)
├── nlp_config.py            # Configuration for different NLP providers (NEW)
├── scad_dataset/
│   └── *.scad               # Your template files
└── scad-gpt2-finetuned/     # Existing template generation model
```

## Template Requirements

Your templates should include parameter declarations:

```scad
// param: width=20, height=30, thickness=5

module my_part(width, height, thickness) {
    // Your OpenSCAD code here
}

my_part(width=20, height=30, thickness=5);  // This line gets replaced
```

The NLP extractor looks for:
- `// param:` or `// params:` comment
- Lists parameter names with example values
- These tell the system what parameters to extract

## Customization

### Changing the Extraction Prompt

Edit the `_build_extraction_prompt()` method in `nlp_extractor.py`:

```python
def _build_extraction_prompt(self, user_input, param_names, template_name=""):
    # Customize the prompt here
    prompt = f"Your custom prompt... {user_input}... {param_names}"
    return prompt
```

### Adding Parameter Type Hints

In your templates, you can add type information:

```scad
// param: teeth=20:numeric, pitch_diameter=50:numeric, material=steel:string
```

The extractor can use this to validate/convert values.

### Custom Parameter Validation

```python
extractor = NLPExtractor()
extracted = extractor.extract_parameters(user_input, params)

# Add custom validation
validated = extractor.validate_and_sanitize(
    extracted, 
    param_types={"teeth": "numeric", "material": "string"}
)
```

## Troubleshooting

### "NLP module not available" error
- Install requests: `pip install requests`
- Ensure `nlp_extractor.py` and `nlp_config.py` are in same directory

### API connection failed
- Check internet connection (for cloud APIs)
- For Ollama: ensure `ollama serve` is running
- Check API key is set correctly
- Verify endpoint URL is accessible

### Extracted values are wrong
- Try rephrasing your description more clearly
- Include units (mm, inches, etc.)
- Provide example values in your description
- Fall back to Manual Mode for critical values

### "Please fill in value for X" error
- Parameter wasn't extracted by NLP
- Manually fill in the field before generating
- Or adjust your description to be more specific

## Performance Notes

### Speed
- NLP API call: 1-5 seconds (depends on provider)
- Local Ollama: 2-10 seconds (depends on model size)
- Cloud APIs (OpenAI, HuggingFace): Usually <2 seconds

### Cost
- **OpenAI**: ~$0.001-0.002 per extraction
- **Local Ollama**: Free (runs on your computer)
- **HuggingFace**: Free tier available
- **Together.ai**: Free tier available

## Advanced: Running Your Own NLP Service

If you want to use a custom model:

```python
# Create a simple Flask server
from flask import Flask, request
app = Flask(__name__)

@app.route('/extract', methods=['POST'])
def extract():
    data = request.json
    # Use your custom model to extract parameters
    return {"parameters": {...}}

if __name__ == '__main__':
    app.run(port=8000)
```

Then configure:
```bash
export NLP_API_URL="http://localhost:8000/extract"
export NLP_PROVIDER="custom"
```

## Future Enhancements

Potential improvements:
- [ ] Multi-turn conversations (user Q&A)
- [ ] Parameter validation against templates
- [ ] Learning from previous extractions
- [ ] Caching API responses for common descriptions
- [ ] Voice input support
- [ ] Parameter suggestions based on template
- [ ] Export/import extraction presets

## Support

For issues or feature requests:
1. Check the Troubleshooting section above
2. Test with Manual Mode to isolate NLP issues
3. Try different NLP providers
4. Check API logs/console output for details
