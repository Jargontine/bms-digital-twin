import numpy as np

# Fault detection layer (ISO 26262 threshold monitoring)

# Safety thresholds (from digest / Table)
V_OVER  = 4.25    # overvoltage limit, V
V_UNDER = 2.80    # undervoltage limit, V
DTDT_MAX = 2.0    # max temperature rise rate, °C/s

def check_faults(cell_voltages, cell_temps, prev_temps, dt):
#Evaluate all fault conditions for one control cycle.
    # cell_voltages: array of per-cell voltages this cycle
    # cell_temps: array of per-cell temperatures this cycle
    # prev_temps: array of per-cell temperatures last cycle
    # dt: control cycle time (s)
    # Returns a dict of triggered faults (empty if none).

    faults = {}

    #  Level checks (single reading)
    over  = np.where(cell_voltages > V_OVER)[0]
    under = np.where(cell_voltages < V_UNDER)[0]

    # Rate check (need two readings)
    dtdt = (cell_temps - prev_temps) / dt        # °C per second, per cell
    thermal = np.where(dtdt > DTDT_MAX)[0]

    if len(over) > 0:
        faults['overvoltage'] = {'cells': over.tolist(),
                                 'values': cell_voltages[over].tolist()}
    if len(under) > 0:
        faults['undervoltage'] = {'cells': under.tolist(),
                                  'values': cell_voltages[under].tolist()}
    if len(thermal) > 0:
        faults['thermal'] = {'cells': thermal.tolist(),
                             'rates': dtdt[thermal].tolist()}

    return faults

# Fault injection test: prove each fault triggers within one cycle
if __name__ == "__main__":
    dt = 0.1   #control cycle
    N = 12

    # Start with a healthy pack
    volts = np.full(N, 3.7)
    temps = np.full(N, 25.0)
    prev  = np.full(N, 25.0)

    print("Healthy pack:", check_faults(volts, temps, prev, dt) or "no faults")

    # Inject overvoltage on cell 3
    volts_ov = volts.copy(); volts_ov[3] = 4.30
    print("Overvoltage:", check_faults(volts_ov, temps, prev, dt))

    # Inject undervoltage on cell 7
    volts_uv = volts.copy(); volts_uv[7] = 2.70
    print("Undervoltage:", check_faults(volts_uv, temps, prev, dt))

    # Inject thermal runaway on cell 5: +0.3°C in one 0.1s cycle = 3 °C/s
    temps_th = temps.copy(); temps_th[5] = 25.3
    print("Thermal:", check_faults(volts, temps_th, prev, dt))
