import os
import re
import sys
import argparse
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from typing import Dict, List, Optional
import traceback as tb

# Ensure current directory is in path for imports
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

# Setup logging to file for debugging
LOG_FILE = "scadcodegen_debug.log"
def log_message(msg):
    """Log to both console and file."""
    print(msg)
    try:
        with open(LOG_FILE, "a") as f:
            f.write(msg + "\n")
    except:
        pass

log_message(f"[STARTUP] Script directory: {script_dir}")
log_message(f"[STARTUP] Python path: {sys.path[0]}")

# Import the NLP extractor module
try:
    from nlp_extractor import NLPExtractor
    HAS_NLP = True
    log_message("[INFO] NLP extractor loaded successfully")
except Exception as e:
    HAS_NLP = False
    log_message(f"[ERROR] Failed to import NLP extractor: {type(e).__name__}: {e}")
    tb.print_exc()
    try:
        with open(LOG_FILE, "a") as f:
            tb.print_exc(file=f)
    except:
        pass

# Import path resolver for centralized path management
from path_resolver import get_scad_dataset_dir, get_generated_scad_dir

# =========================
# Path resolution
# =========================
SCAD_DATASET_DIR = get_scad_dataset_dir()
OUTPUT_DIR = get_generated_scad_dir()
os.makedirs(OUTPUT_DIR, exist_ok=True)

print(f"[DEBUG] SCRIPT_DIR         : {script_dir}")
print(f"[DEBUG] SCAD_DATASET_DIR   : {SCAD_DATASET_DIR} (exists={os.path.isdir(SCAD_DATASET_DIR)})")
print(f"[DEBUG] OUTPUT_DIR         : {OUTPUT_DIR}")

# =========================
# Helpers
# =========================
def list_templates():
    """Return .scad files in the dataset directory (sorted)."""
    if not os.path.isdir(SCAD_DATASET_DIR):
        return []
    return sorted([f for f in os.listdir(SCAD_DATASET_DIR) if f.lower().endswith(".scad")])

def get_param_names(scad_file):
    """
    Extract param names from a comment line like:
      // param: width=20, height=20, thickness=10
    Returns ['width','height','thickness'].
    """
    if not scad_file:
        return []
    path = os.path.join(SCAD_DATASET_DIR, scad_file)
    if not os.path.isfile(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                s = line.strip().lower()
                if s.startswith("// param:") or s.startswith("// params:"):
                    param_line = line.strip()
                    param_str = param_line.split(":", 1)[1].strip()
                    params = []
                    for p in param_str.split(","):
                        name = p.split("=")[0].strip()
                        if name:
                            params.append(name)
                    return params
    except Exception as e:
        print(f"[WARN] get_param_names failed: {e}")
        return []
    return []

def replace_args_in_call(line, param_values):
    """
    Replace the argument list between the first '(' and its matching ')'
    with rendered 'k=v' pairs. If ')' missing, append one.
    """
    param_str = ", ".join([f"{k}={v}" for k, v in param_values.items()])
    try:
        open_idx = line.index("(")
    except ValueError:
        # No '(' — append call-like arg list at end
        end = "" if line.rstrip().endswith(";") else ";"
        return line.rstrip() + f"({param_str}){end}\n"

    close_idx = line.find(")", open_idx + 1)
    if close_idx == -1:
        prefix = line[:open_idx + 1]
        end = ");\n" if not line.rstrip().endswith(");") else ")\n"
        return f"{prefix}{param_str}{end}"

    prefix = line[:open_idx + 1]
    suffix = line[close_idx:]
    return f"{prefix}{param_str}{suffix}"

def generate_scad_from_template(template, param_values, output_filename=None):
    """
    Open the template and replace the FIRST callable line (e.g. mymodule(...);)
    or a line marked with "// CALL" with provided params.
    Saves to OUTPUT_DIR/output_filename or OUTPUT_DIR/generated_<template> if no filename provided.
    """
    template_path = os.path.join(SCAD_DATASET_DIR, template)
    if not os.path.isfile(template_path):
        raise FileNotFoundError(f"Template not found: {template_path}")

    with open(template_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    replaced = False
    call_line_regex = re.compile(r"^[A-Za-z_]\w*\s*\(.*")

    for line in lines:
        if not replaced and ("// CALL" in line or call_line_regex.match(line.strip())):
            new_lines.append(replace_args_in_call(line, param_values))
            replaced = True
        else:
            new_lines.append(line)

    if not replaced:
        new_lines.append("\n// Auto-generated call\n")
        call_line = "param_module();\n"
        new_lines.append(replace_args_in_call(call_line, param_values))

    if output_filename:
        if not output_filename.lower().endswith('.scad'):
            output_filename += '.scad'
        out_path = os.path.join(OUTPUT_DIR, output_filename)
    else:
        out_path = os.path.join(OUTPUT_DIR, f"generated_{os.path.basename(template)}")
    
    with open(out_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    print(f"[DEBUG] Wrote: {out_path}")
    return out_path

# =========================
# GUI with NLP Support
# =========================
def run_ui():
    global HAS_NLP
    root = tk.Tk()
    root.title("SCAD Template Generator - with NLP")
    root.geometry("1000x700")

    # Track UI state
    nlp_extractor = None
    nlp_available = HAS_NLP
    if nlp_available:
        try:
            nlp_extractor = NLPExtractor()
            log_message("[UI] NLP Extractor initialized successfully in UI")
        except Exception as e:
            log_message(f"[UI] ERROR initializing NLP Extractor: {e}")
            tb.print_exc()
            nlp_available = False
            nlp_extractor = None
    
    param_entries = {}
    extraction_in_progress = False

    # ===== Create notebook (tabbed interface) =====
    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    # NLP Mode (Primary interface - no need for manual mode anymore)
    nlp_frame = tk.Frame(notebook)
    notebook.add(nlp_frame, text="Smart NLP Mode" if nlp_available else "Smart NLP Mode (Disabled)")
    setup_unified_nlp_tab(nlp_frame, root, nlp_extractor)

    # Disable NLP tab if not available
    if not nlp_available:
        notebook.tab(0, state="disabled")

    # Proactive notices
    templates = list_templates()
    if not os.path.isdir(SCAD_DATASET_DIR):
        messagebox.showwarning("Dataset Folder Missing",
                               f"Couldn't find the dataset folder:\n{SCAD_DATASET_DIR}\n\nCreate it and add .scad templates.")
    elif not templates:
        messagebox.showinfo("No Templates Found",
                            f"No .scad files were found in:\n{SCAD_DATASET_DIR}\n\nAdd templates to enable the UI.")

    root.mainloop()


def setup_unified_nlp_tab(parent, root, nlp_extractor):
    """Unified NLP tab - auto-detects template and extracts parameters in one go."""
    if not HAS_NLP:
        tk.Label(parent, text="NLP module not available.", 
                 fg="red", font=("Arial", 12)).pack(pady=20)
        return

    # Input section
    input_frame = tk.LabelFrame(parent, text="Describe what you want to create")
    input_frame.pack(fill=tk.X, padx=10, pady=10)
    input_frame.grid_columnconfigure(0, weight=1)

    user_text = tk.Text(input_frame, height=6, wrap=tk.WORD)
    user_text.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

    # Detection results section
    results_frame = tk.LabelFrame(parent, text="Detection & Extraction Results")
    results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    results_frame.grid_columnconfigure(0, weight=1)

    # Template display
    template_frame = tk.Frame(results_frame)
    template_frame.pack(fill=tk.X, padx=6, pady=6)
    tk.Label(template_frame, text="Detected Template:", font=("Arial", 10, "bold")).pack(side=tk.LEFT)
    detected_template_label = tk.Label(template_frame, text="(enter description)", fg="gray", font=("Arial", 10))
    detected_template_label.pack(side=tk.LEFT, padx=10)

    # Parameters display
    param_frame = tk.LabelFrame(results_frame, text="Extracted Parameters (you can edit these)")
    param_frame.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)
    param_frame.grid_columnconfigure(1, weight=1)

    param_entries = {}
    param_labels = {}
    detection_timer = [None]
    current_template = [None]

    def clear_results():
        """Clear all results."""
        for w in list(param_frame.winfo_children()):
            w.destroy()
        param_entries.clear()
        param_labels.clear()
        detected_template_label.config(text="(detecting...)", fg="orange")
        current_template[0] = None

    def trigger_detection():
        """Debounce and trigger detection."""
        if detection_timer[0]:
            root.after_cancel(detection_timer[0])
        detection_timer[0] = root.after(2000, perform_detection)

    def perform_detection():
        """Auto-detect template and extract parameters."""
        user_input = user_text.get(1.0, tk.END).strip()
        if not user_input:
            clear_results()
            detected_template_label.config(text="(enter description)", fg="gray")
            return

        clear_results()
        
        def do_detection():
            try:
                templates = list_templates()
                template, params = nlp_extractor.detect_template_and_extract(user_input, templates)
                
                current_template[0] = template
                detected_template_label.config(text=template, fg="green")

                # Display parameters
                param_names = get_param_names(template)
                for i, p in enumerate(param_names):
                    tk.Label(param_frame, text=f"{p}:").grid(row=i, column=0, sticky="w", padx=6, pady=3)
                    e = tk.Entry(param_frame, width=30, bg="#e8f4f8")
                    
                    # Fill with detected value if available
                    if p in params and params[p]:
                        e.insert(0, str(params[p]))
                    
                    e.grid(row=i, column=1, sticky="ew", padx=6, pady=3)
                    param_entries[p] = e
                    
                    # Status indicator
                    status = "(extracted)" if (p in params and params[p]) else "(please fill)"
                    color = "green" if (p in params and params[p]) else "orange"
                    label = tk.Label(param_frame, text=status, fg=color, font=("Arial", 8))
                    label.grid(row=i, column=2, sticky="w", padx=6, pady=3)
                    param_labels[p] = label

            except Exception as e:
                detected_template_label.config(text=f"Error: {str(e)[:40]}", fg="red")
                print(f"[Detection Error] {e}")

        detect_thread = threading.Thread(target=do_detection, daemon=True)
        detect_thread.start()

    # Bind text changes
    def on_text_change(event):
        trigger_detection()

    user_text.bind("<KeyRelease>", on_text_change)

    # Generation section
    gen_frame = tk.Frame(parent)
    gen_frame.pack(fill=tk.X, padx=10, pady=10)
    gen_frame.grid_columnconfigure(1, weight=1)

    tk.Label(gen_frame, text="Output filename:").grid(row=0, column=0, sticky="w", padx=5)
    filename_entry = tk.Entry(gen_frame, width=50)
    filename_entry.grid(row=0, column=1, sticky="ew", padx=5)
    tk.Label(gen_frame, text=".scad").grid(row=0, column=2, sticky="w", padx=(0, 5))

    def generate_nlp():
        """Generate SCAD from detected template and parameters."""
        if not current_template[0]:
            messagebox.showerror("Error", "No template detected. Describe what you want first.")
            return

        template = current_template[0]
        param_names = get_param_names(template)
        param_values = {}

        for p in param_names:
            if p not in param_entries:
                messagebox.showerror("Error", f"Missing field for '{p}'")
                return
            v = param_entries[p].get().strip()
            if not v:
                messagebox.showerror("Error", f"Please fill in value for '{p}'")
                return
            param_values[p] = v

        filename = filename_entry.get().strip()
        try:
            out_path = generate_scad_from_template(template, param_values, filename)
            with open(out_path, "r", encoding="utf-8") as f:
                content = f.read()
            show_preview(content, out_path)
            messagebox.showinfo("Success", f"Generated:\n{out_path}")
        except Exception as e:
            messagebox.showerror("Error", f"{e}")

    button_frame = tk.Frame(parent)
    button_frame.pack(fill=tk.X, padx=10, pady=10)
    tk.Button(button_frame, text="Generate SCAD", command=generate_nlp, bg="#4CAF50", fg="white", 
              font=("Arial", 11, "bold")).pack(side=tk.LEFT, padx=5)
    tk.Label(button_frame, text="Auto-detects shape type and extracts parameters as you type",
             fg="gray", font=("Arial", 9, "italic")).pack(side=tk.LEFT, padx=10)


def setup_manual_tab(parent, root):
    """[DEPRECATED] Manual input tab - no longer used.
    
    The app now uses NLP-only mode. This function is kept for backward compatibility.
    All template functionality is still available through the NLP interface.
    """
    
    # Simple deprecation notice
    notice_frame = tk.Frame(parent, bg="#f0f0f0")
    notice_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=40)
    
    tk.Label(notice_frame, 
             text="Manual Mode - Deprecated", 
             font=("Arial", 16, "bold"),
             bg="#f0f0f0").pack(pady=(0, 20))
    
    tk.Label(notice_frame, 
             text="The template-based manual mode has been replaced with NLP-powered mode.\n\n"
                  "Please use the 'Smart NLP Mode' tab to describe what you want in natural language.\n\n"
                  "Simply type things like:\n"
                  "• 'Create a cube with 50mm sides'\n"
                  "• 'I want a bushing with inner diameter 30 and outer 40'\n"
                  "• 'Make a gear with 30 teeth'\n\n"
                  "The system will automatically detect the shape and extract parameters!",
             font=("Arial", 11),
             bg="#f0f0f0",
             justify=tk.LEFT,
             wraplength=500).pack(pady=20)
    
    tk.Button(notice_frame, text="Go to Smart NLP Mode", 
              command=lambda: print("[INFO] Switch to NLP tab above"),
              font=("Arial", 10), 
              padx=20, pady=10).pack()
    gen_btn.pack(pady=12)


def show_preview(content: str, filepath: str):
    """Display content in a preview window."""
    preview_window = tk.Toplevel()
    preview_window.title(f"Preview: {os.path.basename(filepath)}")
    preview_window.geometry("700x500")

    text = tk.Text(preview_window)
    text.pack(fill=tk.BOTH, expand=True)
    text.insert(tk.END, content)
    text.config(state=tk.DISABLED)

# =========================
# CLI fallback (headless / Colab)
# =========================
def cli_main(args):
    if args.list:
        t = list_templates()
        print("Templates:")
        for name in t:
            print("  -", name)
        if not t:
            print("  (none found)")
        return 0

    if args.template:
        if not os.path.isdir(SCAD_DATASET_DIR):
            print(f"[ERROR] Dataset folder not found: {SCAD_DATASET_DIR}")
            return 2
        tmpl = args.template
        available = list_templates()
        if tmpl not in available:
            print(f"[ERROR] Template not found in dataset: {tmpl}")
            print("Available templates:", ", ".join(available) if available else "(none)")
            return 2

        param_values = {}

        # Handle NLP input if provided
        if args.nlp_input:
            if not HAS_NLP:
                print("[ERROR] NLP not available. Install nlp_extractor module.")
                return 2
            
            print(f"[INFO] Processing NLP input: {args.nlp_input}")
            expected = get_param_names(tmpl)
            
            try:
                extractor = NLPExtractor()
                param_values = extractor.extract_parameters(args.nlp_input, expected, tmpl)
                print(f"[INFO] Extracted parameters: {param_values}")
            except Exception as e:
                print(f"[ERROR] NLP extraction failed: {e}")
                return 2
        
        # Handle manual parameter input (--set overrides NLP extraction)
        if args.set:
            for kv in args.set:
                if "=" not in kv:
                    print(f"[ERROR] Invalid --set value (use key=value): {kv}")
                    return 2
                k, v = kv.split("=", 1)
                param_values[k.strip()] = v.strip()

        # If no params provided via NLP or --set, warn and exit
        if not param_values:
            expected = get_param_names(tmpl)
            if expected:
                print(f"[ERROR] No parameters provided. Use --nlp-input or --set")
                print(f"Expected: {', '.join(expected)}")
                return 2

        out_path = generate_scad_from_template(tmpl, param_values, args.output)
        with open(out_path, "r", encoding="utf-8") as f:
            print("\n===== Generated SCAD =====")
            print(f.read())
        print(f"\n[OK] Wrote: {out_path}")
        return 0

    # Default action in CLI mode: show help
    print("[INFO] No GUI and no CLI action specified. Use --help.")
    return 0

def main():
    print("[DEBUG] Script entry point reached.")
    parser = argparse.ArgumentParser(description="SCAD Template Generator with NLP Support")
    parser.add_argument("--list", action="store_true", help="List available templates")
    parser.add_argument("--template", type=str, help="Template filename to generate from")
    parser.add_argument("--nlp-input", type=str, help="Natural language description (requires NLP module)")
    parser.add_argument("--output", type=str, help="Output filename")
    parser.add_argument("--set", nargs="*", help="Manual parameters like width=20 height=10")
    parser.add_argument("--no-gui", action="store_true", help="Force CLI mode (headless)")
    args = parser.parse_args()

    # Force CLI if requested or if Tk fails to start (headless)
    if args.no_gui:
        sys.exit(cli_main(args))

    try:
        # Try GUI first
        run_ui()
    except tk.TclError as e:
        print(f"[WARN] GUI unavailable (headless?): {e}")
        print("[INFO] Falling back to CLI. Use --no-gui to skip GUI next time.")
        sys.exit(cli_main(args))

if __name__ == "__main__":
    main()
