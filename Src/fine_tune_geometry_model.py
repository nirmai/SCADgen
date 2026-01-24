"""
Fine-tune GPT-2 model on geometry parameter extraction data.
Builds on the existing checkpoint to create a specialized geometry model.
"""

import os
import torch
from transformers import GPT2Tokenizer, GPT2LMHeadModel, TextDataset, DataCollatorForLanguageModeling
from transformers import Trainer, TrainingArguments


def fine_tune_geometry_model(
    training_file: str = "synthetic_training_data.jsonl",
    checkpoint_dir: str = "scad-gpt2-finetuned/checkpoint-51",
    output_dir: str = "scad-gpt2-geometry-specialized",
    num_epochs: int = 3,
    batch_size: int = 8,
):
    """
    Fine-tune GPT-2 model on geometry parameter extraction data.
    
    Args:
        training_file: JSONL file with training data
        checkpoint_dir: Starting checkpoint to build upon
        output_dir: Directory to save fine-tuned model
        num_epochs: Number of training epochs
        batch_size: Batch size for training
    """
    
    print("[INFO] Loading model and tokenizer...")
    
    # Check if checkpoint exists
    if os.path.exists(checkpoint_dir):
        print(f"[INFO] Loading from checkpoint: {checkpoint_dir}")
        try:
            tokenizer = GPT2Tokenizer.from_pretrained(checkpoint_dir)
            model = GPT2LMHeadModel.from_pretrained(checkpoint_dir)
        except Exception as e:
            print(f"[WARN] Could not load checkpoint: {e}")
            print("[INFO] Loading default GPT-2...")
            tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
            model = GPT2LMHeadModel.from_pretrained("gpt2")
    else:
        print("[INFO] Using default GPT-2...")
        tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
        model = GPT2LMHeadModel.from_pretrained("gpt2")
    
    # Add padding token if needed
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    print(f"[INFO] Model loaded: {model.config.model_type}")
    print(f"[INFO] Tokenizer vocab size: {len(tokenizer)}")
    
    # Check for training data
    if not os.path.exists(training_file):
        print(f"[ERROR] Training file not found: {training_file}")
        print("[INFO] Generate it first with: python generate_training_data.py")
        return
    
    print(f"[INFO] Loading training data from {training_file}")
    
    # Load and prepare dataset
    dataset = TextDataset(
        tokenizer=tokenizer,
        file_path=training_file,
        block_size=128,
    )
    
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False,  # We're doing causal LM, not MLM
    )
    
    print(f"[INFO] Dataset size: {len(dataset)} examples")
    
    # Setup training
    training_args = TrainingArguments(
        output_dir=output_dir,
        overwrite_output_dir=True,
        num_train_epochs=num_epochs,
        per_device_train_batch_size=batch_size,
        save_steps=100,
        save_total_limit=3,
        logging_steps=50,
        learning_rate=5e-5,
        weight_decay=0.01,
        warmup_steps=100,
        fp16=torch.cuda.is_available(),  # Use mixed precision if GPU available
    )
    
    trainer = Trainer(
        model=model,
        args=training_args,
        data_collator=data_collator,
        train_dataset=dataset,
    )
    
    print("\n[INFO] Starting fine-tuning...")
    print(f"[INFO] Epochs: {num_epochs}")
    print(f"[INFO] Batch size: {batch_size}")
    print(f"[INFO] GPU available: {torch.cuda.is_available()}")
    
    # Train
    trainer.train()
    
    # Save the fine-tuned model
    print(f"\n[INFO] Saving model to {output_dir}")
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)
    
    print("[SUCCESS] Fine-tuning complete!")
    print(f"[SUCCESS] Model saved to {output_dir}")
    print(f"\n[NEXT] Update nlp_extractor.py to use: {output_dir}")


def main():
    """Main entry point."""
    print("=" * 60)
    print("Geometry Model Fine-Tuning")
    print("=" * 60)
    
    # Check prerequisites
    try:
        from transformers import __version__ as tf_version
        print(f"[INFO] Transformers version: {tf_version}")
    except:
        print("[ERROR] Transformers not installed. Install with: pip install transformers")
        return
    
    print(f"[INFO] CUDA available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"[INFO] GPU: {torch.cuda.get_device_name(0)}")
    
    # Generate training data if needed
    training_file = "synthetic_training_data.jsonl"
    if not os.path.exists(training_file):
        print(f"\n[INFO] Training file not found. Generating...")
        os.system("python generate_training_data.py")
    
    # Fine-tune
    fine_tune_geometry_model(
        training_file=training_file,
        output_dir="scad-gpt2-geometry-specialized",
        num_epochs=3,
        batch_size=8,
    )


if __name__ == "__main__":
    main()
