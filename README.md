# SCADgen

SCAD generation tool using AI — the original prototype.

**This project has been superseded by [SCADGenV2](https://github.com/nirmai/SCADGenV2), a full rebuild.** This repo is kept for reference.

## What this was

A desktop (Tkinter) tool that generated single OpenSCAD shapes from a natural-language description:

- **Templates were `.scad` files edited as text.** Generation worked by finding the first module-call-like line (or a line marked `// CALL`) in a template and regex-replacing its argument list with new parameter values — no structured schema, no validation, no engineering constraints.
- **One shape at a time.** There was no concept of an assembly — no multi-part positioning, no connectors, no way to combine parts into a mechanism.

### The NLP layer: a two-model split

Parameter extraction (`nlp_extractor.py`) settled on a two-model architecture:

1. **Template detection** — an LLM (Ollama or OpenAI) picks which geometry the user means from the available template names.
2. **Parameter extraction** — the LLM again, as the primary path, with a locally fine-tuned GPT-2 model (`fine_tune_geometry_model.py`, trained on synthetic data from `generate_training_data.py`) kept only as a fallback for when the LLM returned nothing.

**Strengths:** separating "what shape" from "what values" made each stage easier to reason about and debug independently, and a fallback path meant one failure mode didn't take down the whole extraction.

**Limitations:** two sequential model calls meant two latency hits and two independent failure points per request. Template detection resolved to a name via loose substring matching (`if tpl.lower() in template`), not a real confidence score, so a bad match in stage 1 silently poisoned stage 2 with no way to reconcile it. And because the fine-tuned geometry model was only ever invoked when the LLM extraction came back empty, it was rarely exercised in practice — most of the investment in training it didn't end up on the primary path. Values were also passed between stages as raw strings with no schema or constraints to catch a wrong extraction.

## What worked

- The core idea — describe a part in plain English, get a parametric `.scad` file back — was sound and worth pursuing further.
- Splitting "detect what shape" from "extract its values" was a reasonable decomposition of the problem, and the version with LLM-primary/model-fallback for extraction was more reliable than either alone.

## What didn't

- **Regex-based text substitution on raw `.scad` files was brittle.** Any deviation from the expected call-line format broke generation, and there was no way to validate that the result was even correct, let alone renderable.
- **Fine-tuning a small local model for the primary extraction path was the wrong tool for the job** — it ended up as an underused fallback (see above) rather than earning its training cost.
- **No path to multi-part assemblies.** Generating a single primitive doesn't get you to "build an engine" or "make a lamp" — real objects are made of parts that connect to each other.

## What replaced it

[SCADGenV2](https://github.com/nirmai/SCADGenV2) rebuilds this from the ground up: templates carry real parametric metadata (params, constraints, connectors) instead of being edited as text; a general-purpose LLM (Claude, GPT-4o, or a local Ollama model) drives decomposition and generation instead of a fine-tuned local model; and a five-stage agentic pipeline turns a description into a fully positioned, multi-part assembly — generating and OpenSCAD-verifying any geometry the template library doesn't already have.
