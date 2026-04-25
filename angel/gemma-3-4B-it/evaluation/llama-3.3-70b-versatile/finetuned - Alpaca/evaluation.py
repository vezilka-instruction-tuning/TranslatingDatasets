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
CSV_PATH = "/content/test_results.csv"
client = Groq(api_key="...")
MODEL_NAME = "llama-3.3-70b-versatile"

# ─────────────────────────────────────────────
# 2. PROMPT & EVALUATION FUNCTION
# ─────────────────────────────────────────────
def get_full_metrics(instr, ref, gen):
    prompt = f"""
    Evaluate the GENERATED response based on REFERENCE and INSTRUCTION (Scale 0.0 to 1.0).
    Metrics:
    - Accuracy: Factual correctness.
    - Fluency: Grammar and natural flow in Macedonian.
    - Coherence: Logic and completeness (penalize if cut off).
    - Relevance: Alignment with instruction.
    - Hallucination: 1.0 if NO false info added, 0.0 if false info added.

    Output ONLY JSON:
    {{
      "accuracy": float, "fluency": float, "coherence": float, 
      "relevance": float, "hallucination": float
    }}
    INSTRUCTION: {instr} | REFERENCE: {ref} | GENERATED: {gen}
    """
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "system", "content": "You are a strict JSON evaluator."},
                      {"role": "user", "content": prompt}],
            temperature=0
        )
        match = re.search(r'\{.*\}', response.choices[0].message.content, re.DOTALL)
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
    print(f"[{i+1}] Evaluating...", end=" ")
    m = get_full_metrics(row.get("instruction"), row.get("reference"), row.get("generated"))
    if m:
        all_results.append(m)
        print("OK")
    else:
        all_results.append({"accuracy":0,"fluency":0,"coherence":0,"relevance":0,"hallucination":0})
        print("FAIL")
    time.sleep(0.5)

# Креирање нов DataFrame со резултатите
results_df = pd.DataFrame(all_results)
avg_metrics = results_df.mean()

print("\nПРОСЕЧНИ ВРЕДНОСТИ:")
print(avg_metrics) 

# ПРОСЕЧНИ ВРЕДНОСТИ:
# accuracy         0.731579
# fluency          0.900000
# coherence        0.842105
# relevance        0.852632
# hallucination    0.657895
# dtype: float64