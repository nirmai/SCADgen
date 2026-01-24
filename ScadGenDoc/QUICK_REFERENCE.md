# SCAD Generator with NLP - Quick Reference

## Installation

```bash
# 1. Install dependencies
pip install requests

# 2. Configure NLP provider (choose one):

# Option A: OpenAI
export OPENAI_API_KEY="sk-your-key"
python ScadCodeGen.py

# Option B: Ollama (local, free)
ollama serve &
ollama run mistral &
export NLP_PROVIDER="ollama_local"
python ScadCodeGen.py

# Option C: HuggingFace
export HUGGINGFACE_API_KEY="hf_your-key"
export NLP_PROVIDER="huggingface"
python ScadCodeGen.py

# Option D: Together.ai
export TOGETHER_API_KEY="your-key"
export NLP_PROVIDER="together"
python ScadCodeGen.py

# Option E: Custom endpoint
export NLP_API_URL="http://localhost:8000/endpoint"
python ScadCodeGen.py
```

## GUI Usage

```
1. Run: python ScadCodeGen.py
2. Click "NLP Mode" tab
3. Select template from dropdown
4. Describe what you want in the text area
5. Click "Extract Parameters (NLP)"
6. Review extracted values (edit if needed)
7. Click "Generate SCAD"
8. Find output in: generated_scad/
```

## CLI Usage

### List templates
```bash
python ScadCodeGen.py --list
```

### Generate with NLP
```bash
python ScadCodeGen.py --template gear_param.scad \
    --nlp-input "20 teeth gear with 50mm pitch diameter" \
    --output my_gear
```

### Generate with manual parameters
```bash
python ScadCodeGen.py --template gear_param.scad \
    --set teeth=20 pitch_diameter=50 \
    --output my_gear
```

### Headless mode (no GUI)
```bash
python ScadCodeGen.py --no-gui --template gear_param.scad \
    --nlp-input "your description" \
    --output output_name
```

## File Locations

```
SCAD_gen/CMTrain/
├── ScadCodeGen.py             # Main application
├── nlp_extractor.py           # NLP extraction module
├── nlp_config.py              # Configuration management
├── setup_nlp.py               # Setup wizard
├── examples_nlp_usage.py       # Usage examples
├── requirements.txt           # Python dependencies
└── scad_dataset/
    └── *.scad                 # Your templates
```

## Templates

Templates need parameter declarations:

```scad
// param: width=20, height=30, thickness=5

module my_part(width, height, thickness) {
    // Your OpenSCAD code here
}

my_part(width=20, height=30, thickness=5);
```

The `// param:` comment tells the system what parameters to extract.

## Troubleshooting

### "NLP module not available"
```bash
pip install requests
```

### "API request failed"
- Check internet connection
- Verify API key is set correctly
- For Ollama: make sure `ollama serve` is running

### "Extracted values are wrong"
- Try rephrasing more clearly
- Include units (mm, inches, etc.)
- Provide example numbers in description
- Use Manual Mode tab for critical values

### "AttributeError: 'NoneType'"
- NLP provider not configured
- Run: `python setup_nlp.py`
- Or set environment variables manually

## Customization

### Change extraction prompt
Edit `nlp_extractor.py`:
```python
def _build_extraction_prompt(self, user_input, param_names, template_name=""):
    return f"Your custom prompt..."
```

### Add new NLP provider
Edit `nlp_config.py`:
```python
CONFIGS["my_provider"] = {
    "api_url": "...",
    "model": "...",
    ...
}
```

### Create custom extractor
```python
from nlp_extractor import NLPExtractor

class MyExtractor(NLPExtractor):
    def _build_extraction_prompt(self, ...):
        # Custom logic here
        pass

extractor = MyExtractor()
```

## Environment Variables

```bash
# NLP Configuration
NLP_PROVIDER          # auto, openai, ollama_local, huggingface, together
NLP_API_URL           # Custom API endpoint
NLP_MODEL             # Custom model name

# API Keys
OPENAI_API_KEY        # For OpenAI provider
HUGGINGFACE_API_KEY   # For HuggingFace provider
TOGETHER_API_KEY      # For Together.ai provider
```

## Performance Tips

1. **Ollama for speed**: Local Ollama is faster than cloud APIs
2. **Cache descriptions**: Common descriptions can be cached
3. **Batch operations**: Process multiple parts in sequence
4. **Validation**: Always check extracted values before generation

## Links

- **NLP Integration Guide**: See `NLP_INTEGRATION_GUIDE.md`
- **Implementation Details**: See `IMPLEMENTATION_SUMMARY.md`
- **Code Examples**: Run `python examples_nlp_usage.py`
- **Setup Wizard**: Run `python setup_nlp.py`

## Common Descriptions

```
Gear: "20 tooth gear with 50mm pitch diameter and 10mm width"
Cylinder: "100mm tall cylinder with 50mm diameter"
Box: "200mm wide, 150mm tall, 10mm thick box"
Sphere: "75mm diameter sphere"
Bolt: "M10 bolt, 50mm long"
Hexnut: "M10 hex nut"
```

## Quick Test

```bash
# Test NLP connection
python -c "from nlp_extractor import NLPExtractor; e = NLPExtractor(); print('✓ NLP Ready')"

# Run examples
python examples_nlp_usage.py

# Run setup wizard
python setup_nlp.py
```

## Support

For issues:
1. Check `NLP_INTEGRATION_GUIDE.md` - Troubleshooting section
2. Review code comments in `nlp_extractor.py`
3. Run `examples_nlp_usage.py` to see working examples
4. Fall back to Manual Mode if NLP has issues
5. Check API provider status and logs

---
**Last Updated**: 2026-01-18
