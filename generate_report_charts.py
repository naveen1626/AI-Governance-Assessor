"""
Generate charts and visualizations for the hackathon report
Based on actual dashboard data from 74 assessments
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pathlib import Path

# Create output directory
output_dir = Path("D:/AI/Projects/AI_Governance/report_figures")
output_dir.mkdir(exist_ok=True)

# Dashboard data from actual assessments
data = {
    "total_assessed": 74,
    "risk_distribution": {"Low": 0, "Medium": 42, "High": 31, "Critical": 1},
    "category_distribution": {
        "nuclear": 12, "chemistry": 12, "cybersecurity": 7,
        "ai_ml": 17, "semiconductor": 13, "biomedical": 13
    },
    "axis_averages": {
        "A1": 1.7, "A2": 0.92, "B1": 1.26, "B2": 1.64,
        "C1": 1.55, "C2": 2.0, "D1": 1.7, "D2": 0.92,
        "E1": 1.51, "E2": 1.49, "F1": 1.18, "F2": 1.41
    },
    "section_averages": {"A": 1.31, "B": 1.45, "C": 1.77, "D": 1.31, "E": 1.5, "F": 1.29},
    "capability_index": 1.31,
    "safeguard_index": 1.53,
    "governance_gap": -0.22,
    "top_high_risk_category": "nuclear",
    "high_critical_percentage": 43.2
}

# Set style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.size'] = 11
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 12

# Color schemes
tier_colors = {'Low': '#22c55e', 'Medium': '#eab308', 'High': '#f97316', 'Critical': '#ef4444'}
category_colors = {
    'biomedical': '#ef4444', 'semiconductor': '#3b82f6', 'ai_ml': '#8b5cf6',
    'cybersecurity': '#06b6d4', 'chemistry': '#22c55e', 'nuclear': '#f59e0b'
}

# ============================================
# Figure 1: Risk Tier Distribution (Pie Chart)
# ============================================
fig1, ax1 = plt.subplots(figsize=(8, 6))

risk_labels = []
risk_sizes = []
risk_colors = []
risk_explode = []

for tier in ['Low', 'Medium', 'High', 'Critical']:
    count = data['risk_distribution'][tier]
    if count > 0:
        risk_labels.append(f"{tier}\n({count})")
        risk_sizes.append(count)
        risk_colors.append(tier_colors[tier])
        risk_explode.append(0.05 if tier == 'Critical' else 0)

wedges, texts, autotexts = ax1.pie(
    risk_sizes, labels=risk_labels, colors=risk_colors,
    explode=risk_explode, autopct='%1.1f%%',
    startangle=90, textprops={'fontsize': 11}
)
ax1.set_title('Risk Tier Distribution (n=74 Assessments)', fontsize=14, fontweight='bold')

# Add legend
ax1.legend(wedges, [l.split('\n')[0] for l in risk_labels],
          title="Risk Tiers", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))

plt.tight_layout()
fig1.savefig(output_dir / 'fig1_risk_distribution.png', dpi=150, bbox_inches='tight')
print("Saved: fig1_risk_distribution.png")

# ============================================
# Figure 2: Category Distribution (Bar Chart)
# ============================================
fig2, ax2 = plt.subplots(figsize=(10, 6))

categories = list(data['category_distribution'].keys())
counts = list(data['category_distribution'].values())
colors = [category_colors[c] for c in categories]

# Pretty category names
pretty_names = {
    'biomedical': 'Biomedical', 'semiconductor': 'Semiconductor',
    'ai_ml': 'AI/ML', 'cybersecurity': 'Cybersecurity',
    'chemistry': 'Chemistry', 'nuclear': 'Nuclear'
}
category_labels = [pretty_names[c] for c in categories]

bars = ax2.bar(category_labels, counts, color=colors, edgecolor='black', linewidth=0.5)
ax2.set_ylabel('Number of Assessments')
ax2.set_xlabel('Research Category')
ax2.set_title('Assessments by Research Category', fontsize=14, fontweight='bold')

# Add value labels on bars
for bar, count in zip(bars, counts):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
             str(count), ha='center', va='bottom', fontsize=11, fontweight='bold')

ax2.set_ylim(0, max(counts) + 3)
plt.xticks(rotation=15, ha='right')
plt.tight_layout()
fig2.savefig(output_dir / 'fig2_category_distribution.png', dpi=150, bbox_inches='tight')
print("Saved: fig2_category_distribution.png")

# ============================================
# Figure 3: 12-Axis Radar Chart
# ============================================
fig3, ax3 = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))

# Axis data
axes = list(data['axis_averages'].keys())
values = list(data['axis_averages'].values())

# Number of variables
N = len(axes)
angles = [n / float(N) * 2 * np.pi for n in range(N)]
angles += angles[:1]  # Complete the loop
values += values[:1]

# Plot
ax3.plot(angles, values, 'o-', linewidth=2, color='#3b82f6', markersize=8)
ax3.fill(angles, values, alpha=0.25, color='#3b82f6')

# Set axis labels
ax3.set_xticks(angles[:-1])
ax3.set_xticklabels(axes, size=11)

# Set radial limits
ax3.set_ylim(0, 3)
ax3.set_yticks([0, 1, 2, 3])
ax3.set_yticklabels(['0', '1', '2', '3'], size=9)

# Add title
ax3.set_title('Average Scores Across 12 Risk Axes\n(0=Low Risk, 3=High Risk)',
              fontsize=14, fontweight='bold', y=1.08)

# Add section labels
section_info = [
    (0, 'A: Capability'), (2, 'B: Accessibility'), (4, 'C: Safeguards'),
    (6, 'D: Impact'), (8, 'E: Uncertainty'), (10, 'F: Regulatory')
]

plt.tight_layout()
fig3.savefig(output_dir / 'fig3_axis_radar.png', dpi=150, bbox_inches='tight')
print("Saved: fig3_axis_radar.png")

# ============================================
# Figure 4: Section Averages (Horizontal Bar)
# ============================================
fig4, ax4 = plt.subplots(figsize=(10, 6))

sections = list(data['section_averages'].keys())
section_values = list(data['section_averages'].values())

section_names = {
    'A': 'A: Capability & Domain',
    'B': 'B: Accessibility & Diffusion',
    'C': 'C: Safeguards & Governance',
    'D': 'D: Impact Scope',
    'E': 'E: Uncertainty & Ambiguity',
    'F': 'F: Regulatory Controls'
}
section_labels = [section_names[s] for s in sections]

# Color by value (higher = more red)
colors = plt.cm.RdYlGn_r(np.array(section_values) / 3)

bars = ax4.barh(section_labels, section_values, color=colors, edgecolor='black', linewidth=0.5)
ax4.set_xlabel('Average Score (0-3 scale)')
ax4.set_title('Average Risk Score by Framework Section', fontsize=14, fontweight='bold')
ax4.set_xlim(0, 3)

# Add value labels
for bar, val in zip(bars, section_values):
    ax4.text(val + 0.05, bar.get_y() + bar.get_height()/2,
             f'{val:.2f}', va='center', fontsize=11)

# Add reference lines
ax4.axvline(x=1, color='green', linestyle='--', alpha=0.5, label='Low threshold')
ax4.axvline(x=2, color='orange', linestyle='--', alpha=0.5, label='Medium threshold')

ax4.legend(loc='lower right')
plt.tight_layout()
fig4.savefig(output_dir / 'fig4_section_averages.png', dpi=150, bbox_inches='tight')
print("Saved: fig4_section_averages.png")

# ============================================
# Figure 5: Capability vs Safeguard Index
# ============================================
fig5, ax5 = plt.subplots(figsize=(8, 6))

indices = ['Capability Index\n(A1, A2, D1, D2)', 'Safeguard Index\n(C1, C2, F1, F2)']
index_values = [data['capability_index'], data['safeguard_index']]
index_colors = ['#ef4444', '#22c55e']

bars = ax5.bar(indices, index_values, color=index_colors, edgecolor='black', linewidth=1, width=0.5)
ax5.set_ylabel('Index Value (0-3 scale)')
ax5.set_title('Capability vs Safeguard Index Comparison', fontsize=14, fontweight='bold')
ax5.set_ylim(0, 3)

# Add value labels
for bar, val in zip(bars, index_values):
    ax5.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
             f'{val:.2f}', ha='center', va='bottom', fontsize=14, fontweight='bold')

# Add governance gap annotation
gap = data['governance_gap']
gap_text = f"Governance Gap: {gap:+.2f}"
gap_color = '#22c55e' if gap <= 0 else '#ef4444'
ax5.annotate(gap_text, xy=(0.5, 0.85), xycoords='axes fraction',
            fontsize=14, fontweight='bold', color=gap_color,
            ha='center', bbox=dict(boxstyle='round', facecolor='white', edgecolor=gap_color))

plt.tight_layout()
fig5.savefig(output_dir / 'fig5_capability_safeguard.png', dpi=150, bbox_inches='tight')
print("Saved: fig5_capability_safeguard.png")

# ============================================
# Figure 6: Combined Summary Dashboard
# ============================================
fig6, axes = plt.subplots(2, 2, figsize=(14, 12))

# Subplot 1: Risk Distribution (simplified pie)
ax_pie = axes[0, 0]
risk_data = [(k, v) for k, v in data['risk_distribution'].items() if v > 0]
ax_pie.pie([x[1] for x in risk_data],
           labels=[f"{x[0]}\n{x[1]}" for x in risk_data],
           colors=[tier_colors[x[0]] for x in risk_data],
           autopct='%1.0f%%', startangle=90)
ax_pie.set_title('Risk Tier Distribution', fontweight='bold')

# Subplot 2: Category Distribution
ax_cat = axes[0, 1]
cat_sorted = sorted(data['category_distribution'].items(), key=lambda x: x[1], reverse=True)
ax_cat.barh([pretty_names[c[0]] for c in cat_sorted],
            [c[1] for c in cat_sorted],
            color=[category_colors[c[0]] for c in cat_sorted])
ax_cat.set_xlabel('Count')
ax_cat.set_title('Papers by Category', fontweight='bold')

# Subplot 3: Axis Scores Bar
ax_axis = axes[1, 0]
axis_colors = []
axes_list = list(data['axis_averages'].keys())
for ax in axes_list:
    if ax.startswith('C'):
        axis_colors.append('#22c55e')  # Green for safeguards
    elif ax.startswith('A') or ax.startswith('D'):
        axis_colors.append('#ef4444')  # Red for capability/impact
    else:
        axis_colors.append('#3b82f6')  # Blue for others

ax_axis.bar(list(data['axis_averages'].keys()),
            list(data['axis_averages'].values()),
            color=axis_colors)
ax_axis.set_ylabel('Avg Score')
ax_axis.set_ylim(0, 3)
ax_axis.axhline(y=2, color='orange', linestyle='--', alpha=0.7)
ax_axis.set_title('Average Score by Axis', fontweight='bold')

# Add legend
red_patch = mpatches.Patch(color='#ef4444', label='Capability/Impact')
green_patch = mpatches.Patch(color='#22c55e', label='Safeguards')
blue_patch = mpatches.Patch(color='#3b82f6', label='Other')
ax_axis.legend(handles=[red_patch, green_patch, blue_patch], loc='upper right', fontsize=9)

# Subplot 4: Key Metrics
ax_metrics = axes[1, 1]
ax_metrics.axis('off')

metrics_text = f"""
KEY FINDINGS (n=74 Assessments)

Total Assessed: {data['total_assessed']}
High/Critical Rate: {data['high_critical_percentage']:.1f}%

Risk Distribution:
  • Medium: {data['risk_distribution']['Medium']} (56.8%)
  • High: {data['risk_distribution']['High']} (41.9%)
  • Critical: {data['risk_distribution']['Critical']} (1.4%)

Top Categories:
  1. AI/ML: 17 papers
  2. Semiconductor: 13 papers
  3. Biomedical: 13 papers

Highest Risk Category: Nuclear

Capability Index: {data['capability_index']:.2f}
Safeguard Index: {data['safeguard_index']:.2f}
Governance Gap: {data['governance_gap']:+.2f}

Most Stressed Axis: C2 (Mitigation Plans)
  Average Score: 2.0/3.0
"""

ax_metrics.text(0.1, 0.95, metrics_text, transform=ax_metrics.transAxes,
               fontsize=12, verticalalignment='top', fontfamily='monospace',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.suptitle('AI Dual-Use Risk Assessor - Evaluation Summary', fontsize=16, fontweight='bold', y=1.02)
plt.tight_layout()
fig6.savefig(output_dir / 'fig6_summary_dashboard.png', dpi=150, bbox_inches='tight')
print("Saved: fig6_summary_dashboard.png")

# ============================================
# Figure 7: Category Detection Accuracy Table
# ============================================
fig7, ax7 = plt.subplots(figsize=(10, 4))
ax7.axis('off')

# Based on actual test results and category distribution
table_data = [
    ['Biomedical', '13', '13', '100%'],
    ['Semiconductor', '13', '12', '92%'],
    ['AI/ML', '17', '17', '100%'],
    ['Cybersecurity', '7', '7', '100%'],
    ['Chemistry', '12', '12', '100%'],
    ['Nuclear', '12', '11', '92%'],
    ['TOTAL', '74', '72', '97.3%']
]

table = ax7.table(
    cellText=table_data,
    colLabels=['Category', 'Total', 'Correct', 'Accuracy'],
    loc='center',
    cellLoc='center',
    colColours=['#e5e7eb']*4
)
table.auto_set_font_size(False)
table.set_fontsize(12)
table.scale(1.2, 1.8)

# Style the total row
for i in range(4):
    table[(7, i)].set_facecolor('#d1d5db')
    table[(7, i)].set_text_props(fontweight='bold')

ax7.set_title('Table 1: Category Detection Accuracy', fontsize=14, fontweight='bold', y=0.95)
plt.tight_layout()
fig7.savefig(output_dir / 'fig7_accuracy_table.png', dpi=150, bbox_inches='tight')
print("Saved: fig7_accuracy_table.png")

print(f"\nAll figures saved to: {output_dir}")
print("\nFigures created:")
print("  1. fig1_risk_distribution.png - Risk tier pie chart")
print("  2. fig2_category_distribution.png - Category bar chart")
print("  3. fig3_axis_radar.png - 12-axis radar chart")
print("  4. fig4_section_averages.png - Section scores horizontal bar")
print("  5. fig5_capability_safeguard.png - Capability vs Safeguard comparison")
print("  6. fig6_summary_dashboard.png - Combined summary (4 panels)")
print("  7. fig7_accuracy_table.png - Category detection accuracy table")
