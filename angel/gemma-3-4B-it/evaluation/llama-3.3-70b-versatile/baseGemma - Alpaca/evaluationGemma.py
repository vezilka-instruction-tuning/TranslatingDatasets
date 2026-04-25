import pandas as pd
import time
import json
import re
import matplotlib.pyplot as plt
import numpy as np
from groq import Groq

# ─────────────────────────────────────────────
# 1. CONFIG
# ─────────────────────────────────────────────
CSV_PATH = "/content/base_gemma_results.csv"
client = Groq(api_key="...")
MODEL_NAME = "llama-3.3-70b-versatile"


# ─────────────────────────────────────────────
# 2. PROMPT & EVALUATION FUNCTION
# ─────────────────────────────────────────────
def get_full_metrics(instr, ref, gen):
    prompt = f"""
    Evaluate the GENERATED response based on REFERENCE and INSTRUCTION (Scale 0.0 to 1.0).

    Metrics:
    - Accuracy: Factual correctness vs reference.
    - Fluency: CRITICAL - First check: is the response written in MACEDONIAN language?
               If the response is in Bulgarian, Serbian, English or ANY other language → fluency = 0.0
               If Macedonian but with grammar issues → 0.3 to 0.7
               If natural, correct Macedonian → 0.8 to 1.0
               Key distinctions - Macedonian uses: "и" not "и" (same but context differs),
               "што" not "което", "јас" not "аз", "не" correctly, Macedonian verb forms.
    - Coherence: Logic and completeness (penalize if cut off or incomplete).
    - Relevance: Alignment with instruction.
    - Hallucination: 1.0 if NO false info added, 0.0 if false info added.

    LANGUAGE CHECK EXAMPLES:
    - "Јас сум добро" → Macedonian ✓
    - "Аз съм добре" → Bulgarian ✗ → fluency = 0.0
    - "Ja sam dobro" → Serbian ✗ → fluency = 0.0

    Output ONLY JSON, no explanation:
    {{
      "accuracy": float, "fluency": float, "coherence": float,
      "relevance": float, "hallucination": float
    }}
    INSTRUCTION: {instr} | REFERENCE: {ref} | GENERATED: {gen}
    """
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system",
                 "content": "You are a strict JSON evaluator specializing in Macedonian language detection. You must distinguish Macedonian from Bulgarian and Serbian."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        match = re.search(r'\{.*?\}', response.choices[0].message.content, re.DOTALL)
        return json.loads(match.group(0)) if match else None
    except:
        return None


# ─────────────────────────────────────────────
# 3. PROCESSING
# ─────────────────────────────────────────────
df = pd.read_csv(CSV_PATH)
all_results = []

print(f"Starting full evaluation of {len(df)} prompts...")
for i, row in df.iterrows():
    print(f"[{i + 1}] Evaluating...", end=" ")
    m = get_full_metrics(row.get("instruction"), row.get("reference"), row.get("generated"))
    if m:
        all_results.append(m)
        print("OK")
    else:
        all_results.append({"accuracy": 0, "fluency": 0, "coherence": 0, "relevance": 0, "hallucination": 0})
        print("FAIL")
    time.sleep(0.5)

# Креирање нов DataFrame со резултатите
results_df = pd.DataFrame(all_results)
avg_metrics = results_df.mean()

print("\nПРОСЕЧНИ ВРЕДНОСТИ:")
print(avg_metrics)