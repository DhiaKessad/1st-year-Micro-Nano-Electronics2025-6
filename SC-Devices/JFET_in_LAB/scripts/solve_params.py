import math

q = 1.602e-19
eps_s = 11.7 * 8.854e-14
a = 0.45e-4
V_GS_off = 1.68
N_A = 1e18
n_i = 1e10
V_T = 0.02585
I_DSS_target = 2.0e-3 # 2.0 mA

# Bisection method to find N_D
low = 1e15
high = 1e17
N_D = 0
for _ in range(100):
    mid = (low + high) / 2
    phi_0 = V_T * math.log(N_A * mid / n_i**2)
    V_p_calculated = (q * mid * a**2) / (2 * eps_s)
    if V_p_calculated > (phi_0 + V_GS_off):
        high = mid
    else:
        low = mid
N_D = (low + high) / 2
phi_0 = V_T * math.log(N_A * N_D / n_i**2)

print(f"Refined N_D: {N_D:.2e} cm^-3")
print(f"phi_0: {phi_0:.4f} V")
V_P = phi_0 + V_GS_off
print(f"V_P: {V_P:.4f} V")

# Mobility model (Masetti/Caughey-Thomas for electrons in Si)
mu_min = 65.0
mu_max = 1330.0
N_ref = 8.5e16
alpha = 0.72
mu_n = mu_min + (mu_max - mu_min) / (1 + (N_D / N_ref)**alpha)
print(f"Doping-dependent mobility mu_n: {mu_n:.2f} cm^2/Vs")

# Exact Shockley relation
I_P_over_ZL = (mu_n * q**2 * N_D**2 * a**3) / (3 * eps_s)
I_DSS_exact_over_ZL = I_P_over_ZL * (1 - 3*(phi_0/V_P) + 2*(phi_0/V_P)**1.5)

Z_over_L_exact = I_DSS_target / I_DSS_exact_over_ZL
print(f"Exact Z/L for 2.0 mA (1D theory): {Z_over_L_exact:.2f}")

# The TCAD suppression factor observed: 1.32 mA simulated vs 2.33 mA theoretical.
Z_over_L_compensated = Z_over_L_exact * (2.33 / 1.32)
print(f"TCAD Pre-compensated Z/L: {Z_over_L_compensated:.2f}")
