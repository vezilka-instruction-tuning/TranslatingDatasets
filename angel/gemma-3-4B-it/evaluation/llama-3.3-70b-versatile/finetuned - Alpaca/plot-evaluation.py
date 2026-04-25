import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# Подесување на стилот
plt.style.use('seaborn-v0_8-muted') 
sns.set_context("talk")

# 1. ПОДГОТОВКА НА ПОДАТОЦИТЕ (од твоите резултати)
# Замени ги овие вредности со твоите реални просеци од results_df.mean()
labels = ['Accuracy', 'Fluency', 'Coherence', 'Relevance', 'Hallucination Free']
stats = avg_metrics.values.tolist() # Ова ги зема просеците од твојата евалуација

# ──────────────────────────────────────────────────────────
# ГРАФИК 1: СТИЛИЗИРАН RADAR CHART (THE "SPIDER")
# ──────────────────────────────────────────────────────────
num_vars = len(labels)
angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
stats += stats[:1]
angles += angles[:1]

fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))

# Пополнување на површината
ax.fill(angles, stats, color='#1f77b4', alpha=0.3)
ax.plot(angles, stats, color='#1f77b4', linewidth=3, marker='o', markersize=8)

# Стилизирање на мрежата
ax.set_theta_offset(np.pi / 2)
ax.set_theta_direction(-1)
ax.set_xticks(angles[:-1])
ax.set_xticklabels(labels, fontweight='bold', fontsize=12)

# Подесување на скалата (од 0 до 1)
ax.set_rlabel_position(0)
plt.yticks([0.2, 0.4, 0.6, 0.8, 1.0], ["0.2", "0.4", "0.6", "0.8", "1.0"], color="grey", size=10)
plt.ylim(0, 1)

plt.title('Профил на перформанси на LLM (Macedonian Alpaca)', size=20, y=1.08, fontweight='bold')

# ──────────────────────────────────────────────────────────
# ГРАФИК 2: МОДЕРЕН BAR CHART СО ОЦЕНКИ
# ──────────────────────────────────────────────────────────
plt.figure(figsize=(12, 6))
colors = sns.color_palette("viridis", len(labels))
barplot = sns.barplot(x=labels, y=stats[:-1], palette=colors, edgecolor='black', linewidth=1.5)

# Додавање на вредностите над секоја колона
for i, p in enumerate(barplot.patches):
    barplot.annotate(format(p.get_height(), '.2f'), 
                   (p.get_x() + p.get_width() / 2., p.get_height()), 
                   ha = 'center', va = 'center', 
                   xytext = (0, 9), 
                   textcoords = 'offset points',
                   fontweight='bold')

plt.title('Просечни вредности по метирка', fontsize=18, fontweight='bold', pad=20)
plt.ylim(0, 1.1)
plt.ylabel('Оценка (0-1)')
plt.grid(axis='y', linestyle='--', alpha=0.7)

plt.tight_layout()
plt.show()
