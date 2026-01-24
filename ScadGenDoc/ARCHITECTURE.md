# System Architecture

## High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER INTERFACE                              │
│                  (GUI with Tabbed Interface)                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────┐      ┌──────────────────────┐        │
│  │   NLP MODE (NEW)     │      │   MANUAL MODE        │        │
│  ├──────────────────────┤      ├──────────────────────┤        │
│  │ • Natural language   │      │ • Form fields        │        │
│  │   input text area    │      │ • Manual entry       │        │
│  │ • Extract button     │      │ • Direct generation  │        │
│  │ • Auto-filled fields │      │ • No API calls       │        │
│  │ • Status indicators  │      │ • For advanced users │        │
│  └──────────────────────┘      └──────────────────────┘        │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 │ (Selected mode)
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                    PROCESSING PIPELINE                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  IF NLP MODE: Extract Parameters from User Description  │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │                                                          │   │
│  │  Input: "20 tooth gear with 50mm pitch diameter"        │   │
│  │    │                                                    │   │
│  │    ▼                                                    │   │
│  │  ┌────────────────────────────────────────────────────┐ │   │
│  │  │        NLP EXTRACTOR MODULE                        │ │   │
│  │  │  (nlp_extractor.py)                               │ │   │
│  │  │                                                    │ │   │
│  │  │  1. Build extraction prompt                       │ │   │
│  │  │  2. Call NLP API (in background thread)           │ │   │
│  │  │  3. Parse response to extract parameters          │ │   │
│  │  │  4. Validate and sanitize values                  │ │   │
│  │  │                                                    │ │   │
│  │  └────────────────────────────────────────────────────┘ │   │
│  │         │                                              │   │
│  │         ▼                                              │   │
│  │  Output: {teeth: "20", pitch_diameter: "50"}          │   │
│  │                                                       │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                                 │
│                              │                                  │
│                              ▼                                  │
│                 ┌──────────────────────┐                       │
│                 │  Parameter Dictionary │                       │
│                 │  (teeth: "20", ...)   │                       │
│                 └──────────────────────┘                       │
│                              │                                  │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│              SCAD TEMPLATE GENERATION (EXISTING)               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Input: Template + Parameters                                  │
│    gear_param.scad + {teeth: "20", pitch_diameter: "50"}      │
│         │                                                      │
│         ▼                                                      │
│  ┌────────────────────────────────────────────────────────┐   │
│  │        SCAD CODE GENERATOR                            │   │
│  │  (ScadCodeGen.py - generate_scad_from_template)       │   │
│  │                                                        │   │
│  │  1. Load template file                                │   │
│  │  2. Find callable line (module call)                  │   │
│  │  3. Replace parameters with extracted values          │   │
│  │  4. Write to output file                              │   │
│  │                                                        │   │
│  └────────────────────────────────────────────────────────┘   │
│         │                                                      │
│         ▼                                                      │
│  Output: Generated SCAD file                                  │
│  Example: generated_scad/my_gear.scad                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                      OUTPUT FILES                              │
│  • .scad files in generated_scad/ directory                   │
│  • Ready for OpenSCAD preview/rendering                       │
└─────────────────────────────────────────────────────────────────┘
```

## NLP API Layer (Configurable)

```
┌──────────────────────────────────────────────────────────────┐
│                   NLP EXTRACTOR MODULE                       │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  NLPExtractor Class                                   │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │ • __init__(config, provider)                          │ │
│  │ • extract_parameters(input, params, template)         │ │
│  │ • _build_extraction_prompt(...)                       │ │
│  │ • _call_nlp_api(prompt)                               │ │
│  │ • _parse_nlp_response(response, params)               │ │
│  │ • validate_and_sanitize(extracted, types)             │ │
│  └────────────────────────────────────────────────────────┘ │
│                          │                                  │
│                          ▼                                  │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  NLP Configuration (nlp_config.py)                    │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │  Available Providers:                                 │ │
│  │  1. OpenAI          (api.openai.com)                 │ │
│  │  2. Ollama Local    (localhost:11434)                │ │
│  │  3. HuggingFace     (api-inference.huggingface.co)  │ │
│  │  4. Together.ai     (api.together.xyz)              │ │
│  │  5. Custom          (your own endpoint)             │ │
│  │                                                      │ │
│  │  Config includes:                                    │ │
│  │  • api_url                                           │ │
│  │  • model                                             │ │
│  │  • temperature                                       │ │
│  │  • max_tokens                                        │ │
│  │  • timeout                                           │ │
│  └────────────────────────────────────────────────────────┘ │
│                          │                                  │
│                          ▼                                  │
│  Environment Variables:                                    │
│  • NLP_PROVIDER (auto, openai, ollama_local, etc.)       │ │
│  • NLP_API_URL (optional override)                       │ │
│  • NLP_MODEL (optional override)                         │ │
│  • OPENAI_API_KEY, HUGGINGFACE_API_KEY, etc.            │ │
│                                                              │
└──────────────────────────────────────────────────────────────┘
                          │
                          ▼
    ┌─────────────────────────────────────────────┐
    │ HTTP/HTTPS API Call to Selected Provider   │
    │ (OpenAI, HuggingFace, Ollama, etc.)        │
    └─────────────────────────────────────────────┘
```

## Data Flow Example

```
USER DESCRIBES:
"I need a gear with 20 teeth and 50mm pitch diameter"

    │
    ▼

NLP EXTRACTOR RECEIVES:
{
  "user_input": "I need a gear with 20 teeth and 50mm pitch diameter",
  "param_names": ["teeth", "pitch_diameter", "width"],
  "template_name": "gear_param.scad"
}

    │
    ▼

BUILDS PROMPT:
"Extract parameter values from: 'I need a gear with 20 teeth...'
 Parameters: teeth, pitch_diameter, width
 Return JSON: {"teeth": "20", "pitch_diameter": "50", ...}"

    │
    ▼

CALLS NLP API:
POST https://api.openai.com/v1/chat/completions
{
  "model": "gpt-3.5-turbo",
  "messages": [{"role": "user", "content": "[PROMPT]"}]
}

    │
    ▼

API RETURNS:
{
  "choices": [{
    "message": {
      "content": "{\"teeth\": \"20\", \"pitch_diameter\": \"50\", \"width\": \"\"}"
    }
  }]
}

    │
    ▼

PARSES RESPONSE:
{
  "teeth": "20",
  "pitch_diameter": "50",
  "width": ""
}

    │
    ▼

POPULATES UI:
[teeth field] = 20
[pitch_diameter field] = 50
[width field] = [user can edit]

    │
    ▼

USER CLICKS "Generate SCAD"

    │
    ▼

TEMPLATE GENERATOR RECEIVES:
{
  "template": "gear_param.scad",
  "params": {"teeth": "20", "pitch_diameter": "50", "width": "..."}
}

    │
    ▼

GENERATES & SAVES:
generated_scad/my_gear.scad
```

## File Organization

```
SCADgen/
│
├── README.md
├── NLP_INTEGRATION_GUIDE.md       ← Comprehensive setup guide
├── IMPLEMENTATION_SUMMARY.md      ← Technical details
├── QUICK_REFERENCE.md             ← Command cheat sheet
├── ARCHITECTURE.md                ← This file
│
├── generated_scad/
│   ├── cube01.scad
│   ├── Gear01.scad
│   └── ...
│
└── SCAD_gen/CMTrain/
    │
    ├── ScadCodeGen.py             ← Main application (MODIFIED)
    │                                 • GUI with tabbed interface
    │                                 • NLP mode integration
    │                                 • Manual mode (original)
    │                                 • CLI with --nlp-input
    │
    ├── nlp_extractor.py           ← NLP extraction logic (NEW)
    │                                 • Parameter extraction
    │                                 • API communication
    │                                 • Response parsing
    │                                 • Validation
    │
    ├── nlp_config.py              ← Provider configuration (NEW)
    │                                 • 5 pre-configured providers
    │                                 • Auto-detection logic
    │                                 • Configuration management
    │
    ├── setup_nlp.py               ← Setup wizard (NEW)
    │                                 • Interactive configuration
    │                                 • Dependency checking
    │                                 • Connection testing
    │
    ├── examples_nlp_usage.py       ← Code examples (NEW)
    │                                 • 7 detailed examples
    │                                 • Integration patterns
    │                                 • Custom extraction
    │
    ├── requirements.txt           ← Python dependencies (NEW)
    │                                 • requests library
    │                                 • Optional packages
    │
    ├── scad_dataset/
    │   ├── bushing_param.scad
    │   ├── cube_param.scad
    │   ├── cylinder_param.scad
    │   ├── gear_param.scad
    │   └── ...
    │
    └── scad-gpt2-finetuned/       ← Your existing model
        └── (unchanged)
```

## Threading Model

```
┌─ Main UI Thread ──────────────────────────────────────────┐
│                                                           │
│  User clicks "Extract Parameters"                        │
│         │                                                │
│         ▼                                                │
│  Spawn Background Thread                                │
│         │                                                │
│         ├───────────────────┐                            │
│         │                   │                            │
│  Main Thread          Background Thread                 │
│  ┌──────────┐        ┌──────────────────┐               │
│  │ UI stays │        │ NLP API call     │               │
│  │ responsive       │ (may take 1-5s)  │               │
│  │ (shows  │        │                  │               │
│  │ spinner)         │ Parse response   │               │
│  │                  │ Extract params   │               │
│  │                  │ Update UI via    │               │
│  │                  │ thread-safe call │               │
│  └──────────┘        └──────────────────┘               │
│         │                   │                            │
│         └───────────────────┘                            │
│                   │                                      │
│                   ▼                                      │
│         UI updated with results                         │
│                                                           │
└───────────────────────────────────────────────────────────┘
```

## Error Handling Flow

```
User Input
    │
    ▼
Validate (empty check)
    ├─ Error? → Show message, Stop
    │
    ▼
Call NLP API
    ├─ Connection error? → Show "API unavailable"
    ├─ Timeout? → Show "Request timeout"
    ├─ Invalid key? → Show "Authentication failed"
    │
    ▼
Parse Response
    ├─ Invalid JSON? → Try alternative parsing
    ├─ No parameters found? → Use defaults/empty
    │
    ▼
Validate Extracted Values
    ├─ Type mismatch? → Sanitize (numeric: extract numbers)
    ├─ Missing values? → User can fill manually
    │
    ▼
Success → Populate UI
```

## Graceful Degradation

```
System Start
    │
    ├─ Try to import NLP modules
    │  ├─ Success? → Enable NLP mode
    │  └─ Fail? → Disable NLP mode (tab grayed out)
    │
    ├─ Try to load NLP config
    │  ├─ Success? → Configure API provider
    │  └─ Fail? → Show warning but allow manual mode
    │
    ├─ User selects NLP mode
    │  ├─ API available? → Proceed
    │  └─ API fails? → Show error, suggest Manual mode
    │
    └─ User clicks Manual Mode
       └─ Always works (original functionality)
```

## Key Design Decisions

1. **Modular Architecture**
   - NLP extraction separated from SCAD generation
   - Each module has single responsibility
   - Easy to replace or upgrade components

2. **Graceful Degradation**
   - System works without NLP
   - NLP failures don't crash application
   - Fallback to manual mode always available

3. **Multiple Provider Support**
   - Not locked to single NLP API
   - Easy to switch providers
   - Can use local (Ollama) or cloud (OpenAI)

4. **Threading for UX**
   - NLP API calls don't freeze GUI
   - User sees status feedback
   - Responsive interface

5. **Configuration Over Code**
   - Providers defined in config file
   - Easy to add new providers
   - Environment variables for flexibility

6. **Backward Compatible**
   - Existing templates work unchanged
   - Original CLI arguments preserved
   - Manual mode identical to original

---
Last Updated: 2026-01-18
