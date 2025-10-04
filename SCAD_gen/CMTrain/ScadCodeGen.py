import os
import re
import sys
import argparse
import tkinter as tk
from tkinter import ttk, messagebox

# workingcode
# =========================
# Path resolution
# =========================
def resolve_paths():
    """
    Resolve dataset/output paths robustly:
    - Prefer ./scad_dataset if present
    - Else prefer ./CMTrain/scad_dataset
    - Else use ./CMTrain/scad_dataset (create output dir anyway)
    """
    cwd = os.getcwd()
    candidates = [
        os.path.join(cwd, "scad_dataset"),
        os.path.join(cwd, "CMTrain", "scad_dataset"),
    ]
    scad_dataset_dir = None
    for c in candidates:
        if os.path.isdir(c):
            scad_dataset_dir = c
            break

    if scad_dataset_dir is None:
        # fallback to ./CMTrain/scad_dataset even if not present
        scad_dataset_dir = os.path.join(cwd, "CMTrain", "scad_dataset")

    # OUTPUT_DIR next to dataset if possible; else ./generated_scad
    base_for_output = os.path.dirname(scad_dataset_dir) if os.path.isdir(scad_dataset_dir) else cwd
    output_dir = os.path.join(base_for_output, "generated_scad")
    os.makedirs(output_dir, exist_ok=True)

    print(f"[DEBUG] CWD                : {cwd}")
    print(f"[DEBUG] SCAD_DATASET_DIR   : {scad_dataset_dir} (exists={os.path.isdir(scad_dataset_dir)})")
    print(f"[DEBUG] OUTPUT_DIR         : {output_dir}")

    return scad_dataset_dir, output_dir

SCAD_DATASET_DIR, OUTPUT_DIR = resolve_paths()

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

def generate_scad_from_template(template, param_values):
    """
    Open the template and replace the FIRST callable line (e.g. mymodule(...);)
    or a line marked with "// CALL" with provided params.
    Saves to OUTPUT_DIR/generated_<template>.
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

    out_path = os.path.join(OUTPUT_DIR, f"generated_{os.path.basename(template)}")
    with open(out_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    print(f"[DEBUG] Wrote: {out_path}")
    return out_path

# =========================
# GUI
# =========================
def run_ui():
    root = tk.Tk()
    root.title("SCAD Template Generator")
    root.geometry("900x560")

    # Frames
    top = tk.Frame(root)
    top.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

    bottom = tk.Frame(root)
    bottom.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=(0,10))

    top.grid_columnconfigure(1, weight=1)
    bottom.grid_columnconfigure(0, weight=1)
    bottom.grid_rowconfigure(0, weight=1)

    # Template selection
    tk.Label(top, text="Select a template:").grid(row=0, column=0, sticky="w")
    templates = list_templates()
    selected_template = tk.StringVar(value=(templates[0] if templates else ""))

    combo = ttk.Combobox(
        top, textvariable=selected_template, values=templates,
        state=("readonly" if templates else "disabled"), width=50
    )
    combo.grid(row=0, column=1, sticky="ew", padx=6)

    # Params group
    param_entries = {}
    param_frame = tk.LabelFrame(top, text="Parameters")
    param_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10,0))
    param_frame.grid_columnconfigure(1, weight=1)

    def show_param_fields():
        for w in list(param_frame.winfo_children()):
            w.destroy()
        param_entries.clear()

        t = selected_template.get()
        if not t:
            tk.Label(param_frame, text="No template selected.").grid(row=0, column=0, sticky="w", padx=6, pady=6)
            return

        params = get_param_names(t)
        if not params:
            tk.Label(param_frame, text="No parameters found.\nAdd a line like:  // param: width=20, height=10").grid(
                row=0, column=0, sticky="w", padx=6, pady=6
            )
            return

        for i, p in enumerate(params):
            tk.Label(param_frame, text=f"{p}:").grid(row=i, column=0, sticky="w", padx=6, pady=3)
            e = tk.Entry(param_frame, width=24)
            e.grid(row=i, column=1, sticky="ew", padx=6, pady=3)
            param_entries[p] = e

    if templates:
        show_param_fields()
    combo.bind("<<ComboboxSelected>>", lambda e: show_param_fields())

    # Preview
    preview = tk.LabelFrame(bottom, text="Generated SCAD Preview")
    preview.grid(row=0, column=0, sticky="nsew")
    preview.grid_columnconfigure(0, weight=1)
    preview.grid_rowconfigure(0, weight=1)

    scad_text = tk.Text(preview, wrap=tk.NONE)
    scad_text.grid(row=0, column=0, sticky="nsew")

    yscroll = ttk.Scrollbar(preview, orient="vertical", command=scad_text.yview)
    yscroll.grid(row=0, column=1, sticky="ns")
    xscroll = ttk.Scrollbar(preview, orient="horizontal", command=scad_text.xview)
    xscroll.grid(row=1, column=0, sticky="ew")
    scad_text.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)

    # Generate button
    def on_generate():
        t = selected_template.get()
        if not t:
            messagebox.showerror("Error", "Please select a template (.scad).")
            return
        if not os.path.isdir(SCAD_DATASET_DIR):
            messagebox.showerror("Error", f"Dataset folder not found:\n{SCAD_DATASET_DIR}")
            return

        params = get_param_names(t)
        param_values = {}
        for p in params:
            if p not in param_entries:
                messagebox.showerror("Error", f"Missing input field for parameter '{p}'.")
                return
            v = param_entries[p].get().strip()
            if v == "":
                messagebox.showerror("Error", f"Please enter a value for '{p}'.")
                return
            param_values[p] = v

        try:
            out_path = generate_scad_from_template(t, param_values)
        except Exception as e:
            messagebox.showerror("Generation Failed", f"{e}")
            return

        with open(out_path, "r", encoding="utf-8") as f:
            scad_text.delete(1.0, tk.END)
            scad_text.insert(tk.END, f.read())
        messagebox.showinfo("Success", f"SCAD file generated:\n{out_path}")

    gen_btn = tk.Button(top, text="Generate SCAD",
                        command=on_generate,
                        state=("normal" if templates else "disabled"))
    gen_btn.grid(row=2, column=0, columnspan=2, pady=12)

    # Proactive notices
    if not os.path.isdir(SCAD_DATASET_DIR):
        messagebox.showwarning("Dataset Folder Missing",
                               f"Couldn't find the dataset folder:\n{SCAD_DATASET_DIR}\n\nCreate it and add .scad templates.")
    elif not templates:
        messagebox.showinfo("No Templates Found",
                            f"No .scad files were found in:\n{SCAD_DATASET_DIR}\n\nAdd templates to enable the UI.")

    root.mainloop()

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

        # Build param dict from --set key=value pairs
        param_values = {}
        for kv in args.set or []:
            if "=" not in kv:
                print(f"[ERROR] Invalid --set value (use key=value): {kv}")
                return 2
            k, v = kv.split("=", 1)
            param_values[k.strip()] = v.strip()

        # If template declares params and user didn't pass them, warn
        expected = get_param_names(tmpl)
        missing = [p for p in expected if p not in param_values]
        if expected and missing:
            print(f"[WARN] Missing values for: {', '.join(missing)} (template declared via // param: ...)")
            print("      You can pass them with: --set", " ".join([f"{m}=VALUE" for m in missing]))

        out_path = generate_scad_from_template(tmpl, param_values)
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
    parser = argparse.ArgumentParser(description="SCAD Template Generator (GUI with CLI fallback)")
    parser.add_argument("--list", action="store_true", help="List available templates")
    parser.add_argument("--template", type=str, help="Template filename to generate from (e.g., mypart.scad)")
    parser.add_argument("--set", nargs="*", help="Parameter pairs like width=20 height=10 ...")
    parser.add_argument("--no-gui", action="store_true", help="Force CLI mode (helpful on headless systems)")
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
