
#Cell physics engine + Extended Kalman Filter for SOC estimation.
#First-order Thevenin ECM driven by a US06-equivalent current profile, with an EKF estimating SOC from noisy terminal voltage, compared against
#open-loop Coulomb counting. Generates Fig. 2 of the accompanying paper.


import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl

# OCV-SOC curve: 7th-order polynomial fit
# INR21700-50E low-current discharge data

soc_points = np.array([0.000, 0.082, 0.184, 0.286, 0.388, 0.490,
                       0.592, 0.694, 0.796, 0.898, 1.000])
ocv_points = np.array([2.70, 3.10, 3.35, 3.42, 3.52, 3.62,
                       3.72, 3.82, 3.92, 4.02, 4.17])
ocv_coeffs = np.polyfit(soc_points, ocv_points, 7)

def ocv_from_soc(soc):
    #Open-circuit voltage for a given state of charge
    return np.polyval(ocv_coeffs, soc)

# Table 1: Cell parameters 

R0 = 0.025       # series resistance, in ohms
R1 = 0.018       # diffusion resistance, in ohms
C1 = 2500.0      # diffusion capacitance,in farads
Q  = 5.0 * 3600  # nominal capacity, in ampere-seconds

# US06 current profile

def make_us06_current(duration_s, dt):
    #US06 profile: base cruise + moderate accelerate/regen transients
    n = int(duration_s / dt)
    t = np.arange(n) * dt
    rng = np.random.default_rng(seed=42)
    base  = 5.0 * np.ones(n)
    accel = 4.0 * (rng.random(n) < 0.03)
    regen = -3.0 * (rng.random(n) < 0.02)
    noise = rng.normal(0, 0.4, n)
    return t, base + accel + regen + noise

# Cell physics engine (constant and dynamic runs)

def run_engine(current_array, dt):
    #Run the ECM over a current array. Returns (time, soc, vt) arrays.
    soc, v_rc = 1.0, 0.0
    time_log, soc_log, vt_log = [], [], []
    for k in range(len(current_array)):
        I = current_array[k]
        vt = ocv_from_soc(soc) - I * R0 - v_rc                             # eq 1
        time_log.append(k * dt); soc_log.append(soc); vt_log.append(vt)
        v_rc = v_rc + (-v_rc / (R1 * C1) + I / C1) * dt                    # eq 2
        soc  = soc - (I * dt) / Q                                          # eq 3
    return np.array(time_log), np.array(soc_log), np.array(vt_log)

# Extended Kalman Filter: SOC estimation

def run_ekf(measured_vt, current_array, dt, soc_init):
    #EKF estimating [SOC, V_RC] from noisy terminal voltage + current.
    x = np.array([soc_init, 0.0])                       # state: [SOC, V_RC]
    P = np.array([[0.1, 0.0], [0.0, 0.1]])              # error covariance
    Q_noise = np.array([[1e-7, 0.0], [0.0, 1e-6]])      # process noise
    R_noise = (0.010)**2                                # measurement noise (10 mV)^2

    a_rc = 1 - dt/(R1*C1)
    A = np.array([[1.0, 0.0], [0.0, a_rc]])    # state transition
    B = np.array([-dt/Q, dt/C1])               # input matrix

    soc_est_log = []
    for k in range(len(current_array)):
        I = current_array[k]

        # Predict
        x = A @ x + B * I                       # eq 4
        P = A @ P @ A.T + Q_noise               # eq 5

        # Correct
        soc_pred, v_rc_pred = x[0], x[1]
        vt_expected = ocv_from_soc(soc_pred) - I*R0 - v_rc_pred
        slope = np.polyval(np.polyder(ocv_coeffs), soc_pred)           # OCV slope
        C = np.array([slope, -1.0])                                    # observation matrix
        S = C @ P @ C.T + R_noise
        K = (P @ C.T) / S                                              # eq 6: Kalman gain
        x = x + K * (measured_vt[k] - vt_expected)                     # equation 7
        P = P - np.outer(K, C) @ P # eq 8: covariance update

        soc_est_log.append(x[0])
    return np.array(soc_est_log)

# Run: dynamic US06 profile, EKF vs Coulomb counting

dt = 0.1
t_prof, i_prof = make_us06_current(600, dt)
t2, soc2, vt2 = run_engine(i_prof, dt)

# Add 10 mV measurement noise and a -15% initialization error
rng_meas = np.random.default_rng(seed=7)
measured_vt = vt2 + rng_meas.normal(0, 0.010, len(vt2))
soc_guess = soc2[0] - 0.15
soc_ekf = run_ekf(measured_vt, i_prof, dt, soc_guess)

# Coulomb counting from the wrong start (open-loop baseline)
soc_cc = [soc_guess]
for k in range(len(i_prof)-1):
    soc_cc.append(soc_cc[-1] - (i_prof[k]*dt)/Q)
soc_cc = np.array(soc_cc)

# Report errors
mae_ekf = np.mean(np.abs(soc_ekf - soc2)) * 100
mae_cc  = np.mean(np.abs(soc_cc  - soc2)) * 100
settle = int(60 / dt)
mae_ekf_settled = np.mean(np.abs(soc_ekf[settle:] - soc2[settle:])) * 100
print(f"EKF MAE (full run):            {mae_ekf:.3f}%")
print(f"EKF MAE (post-convergence):    {mae_ekf_settled:.3f}%")
print(f"Coulomb-counting MAE:          {mae_cc:.3f}%")

# Figure 2: EKF vs Coulomb counting
mpl.rcParams.update({
    'font.size': 10, 'font.family': 'serif', 'axes.linewidth': 0.8,
    'axes.grid': True, 'grid.alpha': 0.3, 'grid.linewidth': 0.5,
    'lines.linewidth': 1.3, 'legend.frameon': True,
    'legend.framealpha': 0.9, 'figure.dpi': 150,
})

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(6, 6), sharex=True)

ax1.plot(t2, soc2*100, 'k-', label='True SOC', linewidth=1.6)
ax1.plot(t2, soc_ekf*100, 'b--', label='EKF estimate', linewidth=1.2)
ax1.plot(t2, soc_cc*100, 'r:', label='Coulomb counting', linewidth=1.4)
ax1.set_ylabel('State of Charge (%)')
ax1.set_title('(a) SOC estimation under US06-equivalent discharge')
ax1.legend(loc='upper right', fontsize=9)
ax1.set_ylim(65, 102)

ax2.plot(t2, np.abs(soc_ekf - soc2)*100, 'b-',
         label=f'EKF (MAE = {mae_ekf_settled:.2f}%)', linewidth=1.2)
ax2.plot(t2, np.abs(soc_cc - soc2)*100, 'r-',
         label=f'Coulomb counting (MAE = {mae_cc:.1f}%)', linewidth=1.2)
ax2.axhline(2.0, color='gray', linestyle='--', linewidth=0.8, label='2% threshold')
ax2.set_xlabel('Time (s)')
ax2.set_ylabel('Absolute error (%)')
ax2.set_title('(b) Absolute SOC estimation error')
ax2.legend(loc='upper right', fontsize=9)
ax2.set_ylim(0, 18)

plt.tight_layout()
plt.savefig('fig2_ekf_vs_cc.png', dpi=300, bbox_inches='tight')
plt.show()
print("Saved fig2_ekf_vs_cc.png")
