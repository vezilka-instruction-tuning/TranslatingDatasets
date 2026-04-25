import torch
import pandas as pd
from datasets import Dataset, load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, BitsAndBytesConfig  # ← moved here
from trl import SFTTrainer, DPOTrainer
from peft import prepare_model_for_kbit_training, LoraConfig
from huggingface_hub import login
from dotenv import load_dotenv
import gc
import os

class TrainPipeline:
    def __init__(self):
        pass

    def hf_login(self, token):          
        login(token)

    def get_dataset(self, path):        
        ds = Dataset.from_json(path)
        return ds   
    
    def preprocess_function_sft(self, example, prompt_col="prompt", response_col="response"):
        return {
            "messages": [
                {"role": "user", "content": example[prompt_col]},
                {"role": "assistant", "content": example[response_col]},
            ],
        }

    def prepare_model(self, model_name, token):     
        tokenizer = AutoTokenizer.from_pretrained(
            model_name, 
            token=token,
            cache_dir="./model_cache"
        )
        tokenizer.pad_token = tokenizer.eos_token
        tokenizer.padding_side = "right"

        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_use_double_quant=True,
        )

        model = AutoModelForCausalLM.from_pretrained(
            model_name, 
            token=token, 
            cache_dir="./model_cache",
            quantization_config=bnb_config, 
            device_map="auto",
            low_cpu_mem_usage=True, 
            attn_implementation="eager"
        )

        model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=True)
        model.config.use_cache = False 


        lora = LoraConfig(
            r=16,
            lora_alpha=32,
            # r=8,          # reduce from 16
            # lora_alpha=16, # reduce from 32
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
            lora_dropout=0.05,
            task_type="CAUSAL_LM"
        )

        training_args = TrainingArguments(
            output_dir="./outputFixed",
            per_device_train_batch_size=1,
            gradient_accumulation_steps=16,
            bf16=True,
            fp16=False,
            optim="paged_adamw_8bit",
            num_train_epochs=1,
            learning_rate=5e-5,
            warmup_ratio=0.1,
            lr_scheduler_type="cosine",
            logging_steps=10,
            save_steps=10,
            save_total_limit=5,
            gradient_checkpointing=True,
            gradient_checkpointing_kwargs={"use_reentrant": False},
            max_grad_norm=0.3,
            report_to="none",
            # dispatch_batches=False, # Sometimes helps with pickle issues in TRL
            save_safetensors=True,  # Ensure future saves use the newer, safer format
        )
        training_args.require_safe_serialization = False

        return model, tokenizer, lora, training_args

    def delete_model(self, *args):      
        for obj in args:
            del obj
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.ipc_collect()
            print(f"VRAM free: {torch.cuda.mem_get_info()[0] / 1024**2:.1f} MB")
        print("Model deleted from RAM.")