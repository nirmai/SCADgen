# Getting Started - Setup & Troubleshooting

## ✅ Pre-Flight Checklist

### System Requirements
- [ ] Python 3.7+ installed
- [ ] pip package manager available
- [ ] One of: OpenAI account, Ollama, HuggingFace account, Together.ai account (or custom endpoint)
- [ ] Internet connection (for cloud APIs, not needed for Ollama)

### Files Verified
- [ ] `ScadCodeGen.py` - updated with NLP support
- [ ] `nlp_extractor.py` - NLP module created
- [ ] `nlp_config.py` - configuration management created
- [ ] `setup_nlp.py` - setup wizard created
- [ ] `examples_nlp_usage.py` - examples created
- [ ] `scad_dataset/` - template directory exists with .scad files
- [ ] `generated_scad/` - output directory exists (auto-created if missing)

### Documentation
- [ ] Read `NLP_INTEGRATION_GUIDE.md` - comprehensive guide
- [ ] Read `QUICK_REFERENCE.md` - command cheat sheet
- [ ] Read `ARCHITECTURE.md` - system design
- [ ] Read `IMPLEMENTATION_SUMMARY.md` - technical details

---

## ✅ Step 1: Install Dependencies

```bash
cd SCADgen/SCAD_gen/CMTrain/

# Install required Python package
pip install -r requirements.txt
# or manually:
# pip install requests
```

**Verification:**
```bash
python -c "import requests; print('✓ requests installed')"
```

---

## ✅ Step 2: Choose NLP Provider

### Option A: OpenAI (Recommended for accuracy)

**Steps:**
1. Go to https://platform.openai.com/api-keys
2. Create new API key (copy it)
3. Set environment variable:

**On Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY="sk-your-key-here"
```

**On Windows (Command Prompt):**
```cmd
set OPENAI_API_KEY=sk-your-key-here
```

**On Mac/Linux:**
```bash
export OPENAI_API_KEY="sk-your-key-here"
```

**Verification:**
```bash
python -c "import os; print('✓ API Key set' if os.getenv('OPENAI_API_KEY') else '✗ API Key not found')"
```

---

### Option B: Ollama (Free, Local)

**Steps:**
1. Download from https://ollama.ai
2. Install and start Ollama:
   ```bash
   ollama serve
   ```
3. In new terminal, download a model:
   ```bash
   ollama run mistral
   # or: ollama run llama2
   # or: ollama run neural-chat
   ```
4. Set environment variable:

**Windows (PowerShell):**
```powershell
$env:NLP_PROVIDER="ollama_local"
```

**Mac/Linux:**
```bash
export NLP_PROVIDER="ollama_local"
```

**Verification:**
```bash
python -c "from nlp_config import is_ollama_running; print('✓ Ollama running' if is_ollama_running() else '✗ Ollama not running')"
```

---

### Option C: HuggingFace (Free tier available)

**Steps:**
1. Create account at https://huggingface.co
2. Get API token from https://huggingface.co/settings/tokens
3. Set environment variables:

**Windows (PowerShell):**
```powershell
$env:HUGGINGFACE_API_KEY="hf_your_token_here"
$env:NLP_PROVIDER="huggingface"
```

**Mac/Linux:**
```bash
export HUGGINGFACE_API_KEY="hf_your_token_here"
export NLP_PROVIDER="huggingface"
```

---

### Option D: Together.ai (Free tier available)

**Steps:**
1. Sign up at https://www.together.ai/
2. Get API key from https://api.together.xyz/
3. Set environment variables:

**Windows (PowerShell):**
```powershell
$env:TOGETHER_API_KEY="your_token_here"
$env:NLP_PROVIDER="together"
```

**Mac/Linux:**
```bash
export TOGETHER_API_KEY="your_token_here"
export NLP_PROVIDER="together"
```

---

### Option E: Custom Endpoint

If you have your own NLP service:

```bash
export NLP_API_URL="http://your-server:port/endpoint"
export NLP_MODEL="your-model-name"
```

---

## ✅ Step 3: Run Setup Wizard (Recommended)

**Automated Setup:**
```bash
python setup_nlp.py
```

This will:
- Check Python packages
- Check NLP configuration
- Offer interactive setup if needed
- Test NLP connection
- Guide you through provider setup

---

## ✅ Step 4: Verify Installation

**Test 1: Check imports**
```bash
python -c "from nlp_extractor import NLPExtractor; print('✓ NLP module loaded')"
```

**Test 2: List available templates**
```bash
python ScadCodeGen.py --list
```

**Test 3: Test NLP extraction**
```bash
python examples_nlp_usage.py
```

**Test 4: Quick functionality test**
```bash
python -c "
from nlp_extractor import NLPExtractor
extractor = NLPExtractor()
print('✓ NLP Extractor initialized')
print(f'  API URL: {extractor.api_url}')
print(f'  Model: {extractor.model}')
"
```

---

## ✅ Step 5: First Run

### GUI Mode (Recommended)
```bash
python ScadCodeGen.py
```

Then:
1. Click "NLP Mode" tab
2. Select a template from dropdown
3. Type description: "I want a cube with 50mm sides"
4. Click "Extract Parameters (NLP)"
5. Review extracted values
6. Click "Generate SCAD"
7. Check `generated_scad/` folder for output

### CLI Mode
```bash
python ScadCodeGen.py --no-gui --list
# Output: List of available templates

python ScadCodeGen.py --template cube_param.scad \
    --nlp-input "cube with 50mm sides" \
    --output my_cube
```

---

## ✅ Troubleshooting Checklist

### ❌ "NLP module not available"
- [ ] Check `nlp_extractor.py` exists in same directory
- [ ] Check `nlp_config.py` exists in same directory
- [ ] Check Python path includes current directory

### ❌ "API request failed"
- [ ] Check internet connection
- [ ] Check API key is correct (try creating new key)
- [ ] For Ollama: verify `ollama serve` is running
- [ ] For cloud APIs: check service status page
- [ ] Try different provider if available

### ❌ "AttributeError: 'NoneType'"
- [ ] Provider not configured
- [ ] Run: `python setup_nlp.py`
- [ ] Manually set environment variables
- [ ] Check environment variables set: `echo $NLP_PROVIDER` (or `echo %NLP_PROVIDER%` on Windows)

### ❌ "Module not found: requests"
- [ ] Run: `pip install requests`
- [ ] Verify: `pip list | grep requests`

### ❌ "Extracted values are wrong"
- [ ] Try more specific description with units (mm, inches)
- [ ] Include example numbers in description
- [ ] Fall back to Manual Mode for critical values
- [ ] Try different NLP provider (some are better than others)

### ❌ "NLP mode tab is disabled"
- [ ] NLP module failed to load (check errors above)
- [ ] Click Manual Mode tab instead
- [ ] Check console for error messages

---

## ✅ Next Steps

1. **Explore Examples**
   ```bash
   python examples_nlp_usage.py
   ```

2. **Read Full Documentation**
   - `NLP_INTEGRATION_GUIDE.md` - comprehensive reference
   - `QUICK_REFERENCE.md` - command cheat sheet
   - `ARCHITECTURE.md` - system design

3. **Customize for Your Use Case**
   - Create new templates in `scad_dataset/`
   - Edit extraction prompts in `nlp_extractor.py`
   - Add custom parameter types

4. **Optimize Performance**
   - Use Ollama for offline operation
   - Cache common descriptions
   - Batch process multiple parts

---

## ✅ Important Notes

### API Keys Security
- ⚠️ Never commit API keys to git
- ⚠️ Use environment variables
- ⚠️ Use `.gitignore` to exclude `.env` files
- ⚠️ Rotate keys periodically

### Cost Management
- OpenAI: ~$0.001-0.002 per extraction (very cheap)
- Ollama: Free (runs locally)
- HuggingFace: Free tier available
- Together.ai: Free tier available
- Consider using free tier APIs during development

### Performance Tips
- Ollama: No internet needed, local processing, slower
- OpenAI: Requires API key, very fast, minimal cost
- HuggingFace: Good middle ground
- Together.ai: Good alternative to OpenAI

### Backward Compatibility
- ✓ All existing templates still work
- ✓ Original CLI commands unchanged
- ✓ Manual Mode preserves original functionality
- ✓ No breaking changes

---

## ✅ Quick Test Commands

```bash
# 1. Check Python version
python --version
# Should be 3.7+

# 2. Check requests installed
pip show requests

# 3. Check NLP module loads
python -c "from nlp_extractor import NLPExtractor; print('OK')"

# 4. Check configuration
python setup_nlp.py

# 5. Run examples
python examples_nlp_usage.py

# 6. List templates
python ScadCodeGen.py --list

# 7. Test NLP extraction (CLI)
python ScadCodeGen.py --template cube_param.scad \
    --nlp-input "50mm cube" --output test

# 8. Open GUI
python ScadCodeGen.py
```

---

## ✅ File Checklist

After setup, verify these files exist:

**Core files:**
- [ ] `ScadCodeGen.py` - main application
- [ ] `nlp_extractor.py` - NLP module
- [ ] `nlp_config.py` - configuration
- [ ] `setup_nlp.py` - setup wizard
- [ ] `requirements.txt` - dependencies

**Documentation:**
- [ ] `NLP_INTEGRATION_GUIDE.md`
- [ ] `IMPLEMENTATION_SUMMARY.md`
- [ ] `QUICK_REFERENCE.md`
- [ ] `ARCHITECTURE.md`
- [ ] `GETTING_STARTED.md` (this file)

**Directories:**
- [ ] `scad_dataset/` - templates
- [ ] `generated_scad/` - output (auto-created)
- [ ] `scad-gpt2-finetuned/` - your model

---

## ✅ Support & Help

If stuck:
1. Check **Troubleshooting** section above
2. Read **QUICK_REFERENCE.md** for commands
3. Read **NLP_INTEGRATION_GUIDE.md** for detailed setup
4. Run **setup_nlp.py** for interactive help
5. Check **examples_nlp_usage.py** for code patterns
6. Review **ARCHITECTURE.md** to understand system

---

## ✅ Success Indicators

You know it's working when:

1. ✓ `python setup_nlp.py` completes without errors
2. ✓ `python ScadCodeGen.py --list` shows your templates
3. ✓ NLP Mode tab is **enabled** (not greyed out)
4. ✓ Can describe a part in natural language
5. ✓ Parameters auto-extract when you click "Extract Parameters"
6. ✓ Generated .scad files appear in `generated_scad/`
7. ✓ Files are valid OpenSCAD syntax

---

## Timeline

**5 minutes:** Install dependencies, set API key
**10 minutes:** Run setup wizard, verify installation
**15 minutes:** First test run with GUI
**30 minutes:** Explore examples and documentation
**1+ hour:** Customize for your specific templates

---

**Ready to go!** 🚀

Follow the steps above in order, and you should have a working NLP-enabled SCAD generator within 30 minutes.

If you have questions, check the documentation files or run the setup wizard!

---
*Last Updated: 2026-01-18*
