import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.patches import FancyBboxPatch

mpl.rcParams.update({'font.family': 'serif', 'figure.dpi': 150})

fig, ax = plt.subplots(figsize=(6.5, 8))
ax.set_xlim(0, 10)
ax.set_ylim(0, 15)
ax.axis('off')

#label, sublabel,and  y-center
boxes = [
    ("Cell Physics Engine", r"First-order Th$\acute{e}$venin ECM", 13),
    ("EKF State Estimator", r"SOC, $V_{RC}$", 10.5),
    ("Balancing Controller", r"$\delta$-SOC threshold", 8),
    ("Fault Detection Layer", "ISO 26262 thresholds", 5.5),
    ("Real-Time Dashboard", "Output interface", 3),
]

# arrow labels between boxes
arrow_labels = [r"$V_t(k)$, $I(k)$", r"$\widehat{SOC}(k)$", "Balance commands", "Fault flags"]

box_w, box_h = 5.5, 1.4
cx = 5.0

for i, (label, sub, yc) in enumerate(boxes):
    box = FancyBboxPatch((cx - box_w/2, yc - box_h/2), box_w, box_h,
                         boxstyle="round,pad=0.1", fill=True,
                         facecolor='#e8e8e8', edgecolor='black', linewidth=1.3)
    ax.add_patch(box)
    ax.text(cx, yc + 0.22, label, ha='center', va='center',
            fontsize=12, fontweight='bold')
    ax.text(cx, yc - 0.28, sub, ha='center', va='center',
            fontsize=9, style='italic', color='#444444')

    # arrow to next box
    if i < len(boxes) - 1:
        y_top = yc - box_h/2
        y_bot = boxes[i+1][2] + box_h/2
        ax.annotate('', xy=(cx, y_bot), xytext=(cx, y_top),
                    arrowprops=dict(arrowstyle='->', lw=1.4, color='black'))
        ax.text(cx + 0.3, (y_top + y_bot)/2, arrow_labels[i],
                ha='left', va='center', fontsize=8, color='#333333')

ax.set_title("Digital twin module hierarchy and data flow",
             fontsize=13, pad=10)

plt.tight_layout()
plt.savefig('fig4_architecture.png', dpi=300, bbox_inches='tight')
plt.show()
print("Saved fig4_architecture.png")
