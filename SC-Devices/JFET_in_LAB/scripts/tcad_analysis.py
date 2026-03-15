import numpy as np
import matplotlib.pyplot as plt
import os
import re

# Set up matplotlib style for a professional "magazine" look
plt.style.use('seaborn-v0_8-paper')
plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'Palatino', 'serif'],
    'axes.labelsize': 11,
    'axes.titlesize': 12,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'lines.linewidth': 1.8,
    'grid.alpha': 0.45,
    'grid.linestyle': '--'
})

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
TEXT_FILE = os.path.join(BASE_DIR, 'TCAD', 'OutputCharacteristics.txt')
IMG_DIR = os.path.join(BASE_DIR, 'images')

with open(TEXT_FILE, 'r') as f:
    lines = f.readlines()

ids_blocks = []
current_block = []
in_ids_block = False

for line in lines:
    line = line.strip()
    if 'Ids vs Vds' in line:
        pass
    if re.match(r'Vds \(V\) \(#\d+\), Ids \(A\) \(#\d+\)', line):
        if current_block:
            ids_blocks.append(np.array(current_block))
        current_block = []
        in_ids_block = True
    elif re.match(r'Vds \(V\) \(#\d+\), Gds \(S\) \(#\d+\)', line):
        if current_block:
            ids_blocks.append(np.array(current_block))
        current_block = []
        in_ids_block = False
    elif in_ids_block and line and not line.startswith('-'):
        try:
            v, i = line.split(',')
            current_block.append([float(v), float(i)])
        except:
            pass

if current_block:
    ids_blocks.append(np.array(current_block))

# Filter empty blocks
ids_blocks = [blk for blk in ids_blocks if len(blk) > 0]

V_GS_values = [0, -0.5, -1.0, -1.5, -2.0]
COLORS = ['#002F6C', '#007A7A', '#B8860B', '#8B0000', '#4B0082']

plt.figure(figsize=(6.5, 4.5))

error_lines = []
error_lines.append("TCAD vs Experimental Comparison Analysis:")

# Theoretical target parameters from main.tex
V_GS_off = -1.68
I_DSS = 2.0  # mA

sum_squared_error = 0
total_points = 0

for idx, (vgs, color) in enumerate(zip(V_GS_values, COLORS)):
    if idx >= len(ids_blocks):
        break
        
    data = ids_blocks[idx]
    vds = data[:, 0]
    ids_mA = data[:, 1] * 1000  # Convert A to mA
    
    plt.plot(vds, ids_mA, color=color, linestyle='-', marker='o', markersize=3, label=rf'TCAD $V_{{GS}} = {vgs}$ V')
    
    # Calculate Shockley theoretical for this Vgs
    # We will compute the MSE between TCAD and Shockley for the same vds points
    theory_ids = np.zeros_like(vds)
    if vgs > V_GS_off:
        for k, v in enumerate(vds):
            if v < (vgs - V_GS_off):
                theory_ids[k] = I_DSS * (2 * (1 - vgs/V_GS_off) * (v / (-V_GS_off)) - (v / V_GS_off)**2)
            else:
                theory_ids[k] = I_DSS * (1 - vgs/V_GS_off)**2 * (1 + 0.02 * (v - (vgs - V_GS_off)))
                
    # Plot Theoretical as well for comparison
    plt.plot(vds, theory_ids, color=color, linestyle='--', alpha=0.6)
    
    # Error calculation
    diff = ids_mA - theory_ids
    mse = np.mean(diff**2)
    sum_squared_error += np.sum(diff**2)
    total_points += len(diff)
    
    # Max current at VDS=10V
    tcad_sat = ids_mA[-1]
    theory_sat = theory_ids[-1]
    
    if theory_sat > 0.01:
        pct_err = abs(tcad_sat - theory_sat) / theory_sat * 100
    else:
        pct_err = abs(tcad_sat - theory_sat) / 2.0 * 100 # relative to IDSS
        
    error_lines.append(f"Vgs = {vgs}V: TCAD Sat I = {tcad_sat:.3f} mA | Theory Sat I = {theory_sat:.3f} mA (Error: {pct_err:.1f}%)")

rmse = np.sqrt(sum_squared_error / total_points) if total_points > 0 else 0
error_lines.append(f"\nOverall Root Mean Square Error (RMSE) across all points: {rmse:.3f} mA")
error_lines.append(f"RMSE relative to I_DSS (2.0mA): {rmse / 2.0 * 100:.1f}%")

# Save Error metrics to a text file
with open(os.path.join(BASE_DIR, 'TCAD', 'error_analysis.txt'), 'w') as f:
    f.write('\n'.join(error_lines))

plt.title('TCAD Simulation vs Shockley Model')
plt.xlabel(r'Drain-Source Voltage, $V_{DS}$ (V)')
plt.ylabel(r'Drain Current, $I_{D}$ (mA)')
plt.grid(True)
# Custom legend to avoid duplicating entries
from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], color='k', ls='-', marker='o', ms=3, label='TCAD Physical Mod.'),
    Line2D([0], [0], color='k', ls='--', label='Macro/Theory (Shockley)'),
]
for i, vgs in enumerate(V_GS_values):
    legend_elements.append(Line2D([0], [0], color=COLORS[i], lw=2, label=rf'$V_{{GS}} = {vgs}$ V'))

plt.legend(handles=legend_elements, loc='upper right', framealpha=0.9, fontsize=8)
plt.xlim(0, 15)
plt.ylim(0, 2.5)

plt.tight_layout()
plt.savefig(os.path.join(IMG_DIR, 'tcad_verification.pdf'), bbox_inches='tight')
plt.close()

print("TCAD plot and error analysis generated successfully.")
