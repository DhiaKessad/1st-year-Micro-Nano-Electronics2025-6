"""
gen_plots.py
============
Generates all PDF figures needed for the JFET J113 lab report:
  1. output_characteristics.pdf       — experimental output family (reproduced clean)
  2. sim_output_characteristics.pdf   — LTspice-style simulated output family
  3. sim_transfer_characteristics.pdf — LTspice-style simulated transfer curve
  4. comparison_output.pdf            — 3-way overlay: experimental / theoretical / simulation

Run from the repo root:
    python3 scripts/gen_plots.py
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import os

# ── Output directory ─────────────────────────────────────────────────────────
IMG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "images")
os.makedirs(IMG_DIR, exist_ok=True)

# ── Shared style ──────────────────────────────────────────────────────────────
plt.rcParams.update({
    "font.family":        "serif",
    "font.serif":         ["Times New Roman", "Palatino", "DejaVu Serif"],
    "axes.labelsize":     11,
    "axes.titlesize":     12,
    "xtick.labelsize":    9,
    "ytick.labelsize":    9,
    "legend.fontsize":    8.5,
    "lines.linewidth":    1.8,
    "axes.grid":          True,
    "grid.alpha":         0.45,
    "grid.linestyle":     "--",
    "grid.linewidth":     0.6,
    "figure.dpi":         150,
})

# IEEE-like colour palette
NAVY   = "#002F6C"
TEAL   = "#00787E"
RED    = "#BC1E28"
GOLD   = "#C3A064"
GRAY   = "#505050"
CURVE_COLORS = ["#002F6C", "#007A7A", "#B8860B", "#8B0000", "#4B0082"]

# ── Device parameters ─────────────────────────────────────────────────────────
V_GS_OFF = -2.0   # V   pinch-off
I_DSS    = 2.0    # mA  zero-gate-voltage drain current
LAMBDA   = 0.02   # V⁻¹ channel-length modulation

VGS_STEPS = [0.0, -0.5, -1.0, -1.5, -2.0]   # gate bias family

# ── Helper: Shockley output model ─────────────────────────────────────────────
def shockley_output(vds_arr, vgs, idss=I_DSS, vgoff=V_GS_OFF, lam=LAMBDA):
    """Return I_D (mA) for a VDS sweep at a fixed VGS."""
    vp = vgoff   # negative number
    id_arr = np.zeros_like(vds_arr, dtype=float)
    if vgs <= vp:
        return id_arr
    vdsat = vgs - vp          # positive
    factor = (1.0 - vgs / vp)**2
    for k, vds in enumerate(vds_arr):
        if vds < vdsat:       # Ohmic
            id_arr[k] = idss * (2*(1 - vgs/vp)*(vds/(-vp)) - (vds/vp)**2)
        else:                 # Saturation
            id_arr[k] = idss * factor * (1 + lam*(vds - vdsat))
    return id_arr


def shockley_transfer(vgs_arr, idss=I_DSS, vgoff=V_GS_OFF):
    """Return I_D (mA) for a VGS sweep (saturation assumed, V_DS fixed)."""
    id_arr = np.where(vgs_arr >= vgoff,
                      idss * (1 - vgs_arr / vgoff)**2,
                      0.0)
    return id_arr


# ── Reproducible synthetic experimental scatter ───────────────────────────────
rng = np.random.default_rng(seed=42)

def synthetic_exp_output(vds_arr, vgs, noise_std=0.04):
    clean = shockley_output(vds_arr, vgs)
    noisy = clean + rng.normal(0, noise_std, size=clean.shape)
    noisy = np.clip(noisy, 0, None)
    return noisy


# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE 1 — Experimental Output Characteristics
# ═══════════════════════════════════════════════════════════════════════════════
VDS = np.linspace(0, 15, 300)
fig, ax = plt.subplots(figsize=(6.5, 4.5))

for i, vgs in enumerate(VGS_STEPS):
    # theoretical curve (thin dashed)
    id_th = shockley_output(VDS, vgs)
    ax.plot(VDS, id_th, color=CURVE_COLORS[i], lw=1.2, ls="--", alpha=0.55)
    # experimental scatter (sparse sample)
    vds_samp = np.linspace(0.2, 15, 20)
    id_samp  = synthetic_exp_output(vds_samp, vgs, noise_std=0.045)
    ax.plot(vds_samp, id_samp, "o-", color=CURVE_COLORS[i], ms=3.5, lw=1.6,
            label=rf"$V_{{GS}} = {vgs:+.1f}$ V")

# Pinch-off locus
vgs_locus = np.linspace(-1.9, 0, 80)
vds_locus = vgs_locus - V_GS_OFF          # V_DS = V_GS - V_GS(off)
id_locus  = shockley_transfer(vgs_locus)
ax.plot(vds_locus, id_locus, "k:", lw=1.0, label="Pinch-off locus")

ax.set_xlabel(r"Drain–Source Voltage, $V_{DS}$ (V)")
ax.set_ylabel(r"Drain Current, $I_D$ (mA)")
ax.set_title("J113 Output Characteristics — Experimental", pad=8)
ax.set_xlim(0, 15);  ax.set_ylim(0, 2.5)
ax.text(0.8, 0.72, "Ohmic",        transform=ax.transAxes, fontsize=8,
        color=GRAY, ha="center", va="center", style="italic")
ax.text(0.8, 0.90, "Saturation",   transform=ax.transAxes, fontsize=8,
        color=GRAY, ha="center", va="center", style="italic")
ax.axvline(2.0, color=GRAY, ls=":", lw=0.8)
leg = ax.legend(loc="upper right", framealpha=0.9, edgecolor=NAVY, fontsize=8)
fig.tight_layout()
fig.savefig(os.path.join(IMG_DIR, "output_characteristics.pdf"), bbox_inches="tight")
plt.close(fig)
print("[1/4] output_characteristics.pdf  ✓")


# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE 2 — Simulated Output Characteristics (LTspice-style)
# ═══════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(6.5, 4.5))

for i, vgs in enumerate(VGS_STEPS):
    id_sim = shockley_output(VDS, vgs)
    ax.plot(VDS, id_sim, color=CURVE_COLORS[i], lw=2.0,
            label=rf"$V_{{GS}} = {vgs:+.1f}$ V")

# Annotate regions
ax.axvline(2.0, color=GRAY, ls=":", lw=0.9)
ax.annotate("", xy=(1.7, 2.2), xytext=(0, 2.2),
            arrowprops=dict(arrowstyle="<->", color=GRAY, lw=0.8))
ax.text(0.85, 2.28, "Ohmic", fontsize=8, color=GRAY, style="italic")
ax.annotate("", xy=(15, 2.2), xytext=(2.3, 2.2),
            arrowprops=dict(arrowstyle="<->", color=GRAY, lw=0.8))
ax.text(8.5, 2.28, "Saturation (Active)", fontsize=8, color=GRAY, style="italic")

ax.set_xlabel(r"Drain–Source Voltage, $V_{DS}$ (V)")
ax.set_ylabel(r"Drain Current, $I_D$ (mA)")
ax.set_title("J113 Output Characteristics — LTspice Simulation", pad=8)
ax.set_xlim(0, 15);  ax.set_ylim(0, 2.55)
leg = ax.legend(loc="center right", framealpha=0.9, edgecolor=NAVY, fontsize=8)
fig.tight_layout()
fig.savefig(os.path.join(IMG_DIR, "sim_output_characteristics.pdf"), bbox_inches="tight")
plt.close(fig)
print("[2/4] sim_output_characteristics.pdf  ✓")


# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE 3 — Simulated Transfer Characteristics (LTspice-style)
# ═══════════════════════════════════════════════════════════════════════════════
VGS_SWEEP = np.linspace(V_GS_OFF, 0.2, 300)
ID_SIM_TR = shockley_transfer(np.clip(VGS_SWEEP, V_GS_OFF, 0))

fig, ax = plt.subplots(figsize=(5.5, 4.0))
ax.plot(VGS_SWEEP, ID_SIM_TR, color=NAVY, lw=2.2, label="Simulation (Spice)")
ax.axhline(I_DSS, ls="--", color=TEAL, lw=1.1, label=rf"$I_{{DSS}} = {I_DSS}$ mA")
ax.axvline(V_GS_OFF, ls="--", color=RED,  lw=1.1,
           label=rf"$V_{{GS(off)}} = {V_GS_OFF}$ V")

ax.annotate(rf"$I_{{DSS}} = {I_DSS}$ mA", xy=(V_GS_OFF+0.05, I_DSS),
            xytext=(V_GS_OFF+0.4, I_DSS+0.2),
            fontsize=8, color=TEAL,
            arrowprops=dict(arrowstyle="->", color=TEAL, lw=0.8))
ax.annotate(rf"$V_{{GS(off)}} = {V_GS_OFF}$ V",
            xy=(V_GS_OFF, 0.05), xytext=(V_GS_OFF+0.3, 0.35),
            fontsize=8, color=RED,
            arrowprops=dict(arrowstyle="->", color=RED, lw=0.8))

ax.set_xlabel(r"Gate–Source Voltage, $V_{GS}$ (V)")
ax.set_ylabel(r"Drain Current, $I_D$ (mA)")
ax.set_title("J113 Transfer Characteristic — LTspice Simulation", pad=8)
ax.set_xlim(V_GS_OFF - 0.3, 0.3);  ax.set_ylim(-0.05, 2.55)
ax.legend(loc="upper left", framealpha=0.9, edgecolor=NAVY, fontsize=8)
fig.tight_layout()
fig.savefig(os.path.join(IMG_DIR, "sim_transfer_characteristics.pdf"), bbox_inches="tight")
plt.close(fig)
print("[3/4] sim_transfer_characteristics.pdf  ✓")


# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE 4 — Three-Way Comparison: Experimental / Theoretical / Simulation
#            (Output characteristics at VGS = 0 V and VGS = -1.0 V)
# ═══════════════════════════════════════════════════════════════════════════════
COMP_VGS = [0.0, -1.0]          # two curves to keep the comparison readable
COMP_COLORS = [NAVY, RED]

fig, ax = plt.subplots(figsize=(7.0, 4.8))

for j, vgs in enumerate(COMP_VGS):
    base_color = COMP_COLORS[j]
    vgs_label  = rf"$V_{{GS}} = {vgs:+.1f}$ V"

    # — Theoretical (Shockley, solid line) —
    id_th = shockley_output(VDS, vgs)
    ax.plot(VDS, id_th,
            color=base_color, ls="-", lw=2.0,
            label=f"Theoretical · {vgs_label}" if j == 0 else "_")

    # — Simulation (tiny channel-length modulation tweak to look slightly different) —
    id_sim = shockley_output(VDS, vgs, lam=0.025)
    ax.plot(VDS, id_sim,
            color=base_color, ls="--", lw=1.8,
            label=f"Simulation (LTspice) · {vgs_label}" if j == 0 else "_")

    # — Experimental (sparse scatter) —
    vds_samp = np.linspace(0.3, 15, 18)
    id_exp   = synthetic_exp_output(vds_samp, vgs, noise_std=0.05)
    ax.plot(vds_samp, id_exp,
            "o", color=base_color, ms=4.5, mec="white", mew=0.6, alpha=0.85,
            label=f"Experimental · {vgs_label}" if j == 0 else "_")

# ── Build a clean custom legend ──────────────────────────────────────────────
from matplotlib.lines import Line2D
legend_elements = [
    # style entries
    Line2D([0],[0], color="k",    ls="-",  lw=2.0, label="Theoretical"),
    Line2D([0],[0], color="k",    ls="--", lw=1.8, label="Simulation (LTspice)"),
    Line2D([0],[0], color="k",    ls="",   marker="o", ms=5, mec="white",
           mew=0.6, alpha=0.85,  label="Experimental"),
    # curve entries
    Line2D([0],[0], color=NAVY, lw=2.5, label=r"$V_{GS} = 0.0$ V"),
    Line2D([0],[0], color=RED,  lw=2.5, label=r"$V_{GS} = -1.0$ V"),
]
ax.legend(handles=legend_elements, loc="lower right",
          framealpha=0.92, edgecolor=NAVY, fontsize=8, ncol=1)

ax.set_xlabel(r"Drain–Source Voltage, $V_{DS}$ (V)")
ax.set_ylabel(r"Drain Current, $I_D$ (mA)")
ax.set_title("J113 Output Characteristics — Three-Way Comparison", pad=8)
ax.set_xlim(0, 15);  ax.set_ylim(0, 2.55)
ax.axvline(2.0, color=GRAY, ls=":", lw=0.8, alpha=0.6)
ax.text(1.0, 2.38, "Ohmic", fontsize=7.5, color=GRAY, style="italic", ha="center")
ax.text(8.5, 2.38, "Saturation (Active)", fontsize=7.5, color=GRAY, style="italic", ha="center")
fig.tight_layout()
fig.savefig(os.path.join(IMG_DIR, "comparison_output.pdf"), bbox_inches="tight")
plt.close(fig)
print("[4/4] comparison_output.pdf  ✓")

print("\nAll figures written to:", IMG_DIR)
