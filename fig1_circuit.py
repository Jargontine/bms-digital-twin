#Generates Fig. 1 of the accompanying paper: First-order Thevenin equivalent-circuit cell model (OCV source, series R0, parallel R1-C1 branch).

import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.patches import Rectangle

mpl.rcParams.update({
    'font.size': 11,
    'font.family': 'serif',
    'figure.dpi': 150,
})

fig, ax = plt.subplots(figsize=(7, 3.5))
ax.set_xlim(0, 10)
ax.set_ylim(0, 5)
ax.axis('off')

lw = 1.6
col = 'black'

def wire(x1, y1, x2, y2):
    ax.plot([x1, x2], [y1, y2], color=col, lw=lw, zorder=1)

# OCV voltage source (battery symbol)
wire(1.0, 3.5, 1.0, 2.8) # top lead
ax.plot([0.7, 1.3], [2.8, 2.8], color=col, lw=lw)   # long plate (+)
ax.plot([0.85, 1.15], [2.6, 2.6], color=col, lw=lw) # short plate (-)
ax.plot([0.7, 1.3], [2.4, 2.4], color=col, lw=lw)   # long plate
ax.plot([0.85, 1.15], [2.2, 2.2], color=col, lw=lw) # short plate
wire(1.0, 2.2, 1.0, 1.5)  # bottom lead
ax.text(1.0, 1.1, 'OCV(SOC)', ha='center', va='center', fontsize=11)

#Top wire to R0
wire(1.0, 3.5, 2.5, 3.5)
# R0 (series resistor as a box)
ax.add_patch(Rectangle((2.5, 3.3), 1.1, 0.4, fill=False, edgecolor=col, lw=lw))
ax.text(3.05, 3.95, r'$R_0$', ha='center', va='center', fontsize=12)
wire(3.6, 3.5, 4.8, 3.5) # wire out of R0 to the node

# Node splits into R1 and C1 parallel branch
node_x = 4.8
wire(node_x, 3.5, node_x, 4.2) # up to R1 branch
wire(node_x, 4.2, 5.5, 4.2)
ax.add_patch(Rectangle((5.5, 4.0), 1.1, 0.4, fill=False, edgecolor=col, lw=lw))
ax.text(6.05, 4.6, r'$R_1$', ha='center', va='center', fontsize=12)
wire(6.6, 4.2, 7.3, 4.2)

wire(node_x, 3.5, node_x, 2.8) # down to C1 branch
wire(node_x, 2.8, 5.7, 2.8)
ax.plot([5.7, 5.7], [2.55, 3.05], color=col, lw=lw)   # capacitor plate 1
ax.plot([6.05, 6.05], [2.55, 3.05], color=col, lw=lw) # capacitor plate 2
ax.text(5.87, 2.25, r'$C_1$', ha='center', va='center', fontsize=12)
wire(6.05, 2.8, 7.3, 2.8)

# Recombine branch
recomb_x = 7.3
wire(recomb_x, 4.2, recomb_x, 3.5)
wire(recomb_x, 2.8, recomb_x, 3.5)
wire(recomb_x, 3.5, 8.8, 3.5) # to positive terminal

# Bottom rail
wire(1.0, 1.5, 8.8, 1.5)

# Terminals
ax.plot(8.8, 3.5, 'ko', markersize=6)
ax.plot(8.8, 1.5, 'ko', markersize=6)
ax.text(9.1, 3.5, '+', ha='center', va='center', fontsize=14)
ax.text(9.1, 1.5, '$-$', ha='center', va='center', fontsize=14)
ax.text(9.5, 2.5, r'$V_t$', ha='center', va='center', fontsize=13)

# Current arrow
ax.annotate('', xy=(8.3, 3.85), xytext=(7.7, 3.85),
            arrowprops=dict(arrowstyle='->', lw=1.4, color=col))
ax.text(8.0, 4.1, r'$I$', ha='center', va='center', fontsize=12)

plt.tight_layout()
plt.savefig('fig1_thevenin.png', dpi=300, bbox_inches='tight')
plt.show()
print("Saved fig1_thevenin.png")
