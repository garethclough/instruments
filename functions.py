import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
import time
import redpitaya_scpi as scpi


def simulate_sine_wave(frequency=1.0, amplitude=1.0,
                       variation=0.02,
                       duration=10.0, sample_rate=1000):
    """
    Simulate a constant-frequency sine wave with slowly
    varying random amplitude.

    frequency:   Constant sine wave frequency (Hz)
    amplitude:   Nominal amplitude
    variation:   Maximum relative amplitude variation (0.02 = 2%)
    duration:    Duration of the signal (seconds)
    sample_rate: Samples per second
    """
    t = np.linspace(0, duration, int(duration * sample_rate),
                    endpoint=False)

    # Generate slowly varying random amplitude changes
    variation_samples = max(1, int(sample_rate * 0.1))
    random_variations = np.random.uniform(
        -variation, variation,
        int(np.ceil(len(t) / variation_samples))
    )

    amplitude_variation = np.interp(
        np.arange(len(t)),
        np.arange(len(random_variations)) * variation_samples,
        random_variations
    )

    varying_amplitude = amplitude * (1 + amplitude_variation)

    # Constant frequency; only amplitude varies
    signal = varying_amplitude * np.sin(2 * np.pi * frequency * t)

    return t, signal

def get_peak_to_peak_per_cycle(t, signal):
    # Find peaks and troughs
    peaks, _ = find_peaks(signal, 0.5)
    troughs, _ = find_peaks(-signal, 0.5)

    results = []

    for i in range(len(troughs) - 1):
        start = troughs[i]
        end = troughs[i + 1]

        # Find the positive peak within this cycle
        cycle_peaks = peaks[(peaks > start) & (peaks < end)]

        if len(cycle_peaks) == 0:
            continue

        peak = cycle_peaks[np.argmax(signal[cycle_peaks])]

        results.append({
            "start_time": t[start],
            "peak_time": t[peak],
            "end_time": t[end],
            "peak_to_peak": np.ptp(signal[start:end + 1])
        })

    return results

def rolling_average_peak_to_peak(results, window_size=10):
    averages = []

    for i in range(len(results) - window_size + 1):
        window = results[i:i + window_size]

        averages.append({
            "start_time": window[0]["start_time"],
            "end_time": window[-1]["end_time"],
            "peak_to_peak": np.mean([
                cycle["peak_to_peak"] for cycle in window
            ])
        })

    return averages



IP = '10.209.3.92'
AMPL = 0.5          # Generator amplitude [V] -> Vin peak-to-peak = 1 V
FS = 125e6           # Red Pitaya sampling frequency [Hz]
N = 16384            # Acquisition buffer size [samples]
HV = 20              # IN2 jumper set to HV -> signal attenuated 20 times


F_MIN = 10           # Minimum sweep frequency [Hz]
F_MAX = 3000          # Maximum sweep frequency [Hz]
freqs = np.round(np.logspace(np.log10(F_MIN), np.log10(F_MAX), 25))


# ===== CONNECTION =====
def connect():
    """Establish the SCPI connection to the Red Pitaya."""
    return scpi.scpi(IP)


def _clear_pending_responses(rp):
    """Discard pending responses (e.g. 'ERR!' after SOUR1:VOLT)."""
    rp._socket.settimeout(0.3)
    try:
        while rp._socket.recv(65536):
            pass
    except Exception:
        pass
    rp._socket.settimeout(None)


# ===== SIGNAL GENERATION (OUT1 = Vin) =====
def generate(rp, freq):
    """Configure and enable a sine wave on output OUT1."""
    rp.tx_txt('GEN:RST')
    rp.tx_txt('SOUR1:FUNC SINE')
    rp.tx_txt(f'SOUR1:FREQ:FIX {freq}')
    rp.tx_txt(f'SOUR1:VOLT {AMPL}')
    rp.tx_txt('OUTPUT1:STATE ON')
    rp.tx_txt('SOUR1:TRig:INT')
    time.sleep(0.3)
    _clear_pending_responses(rp)


# ===== ACQUISITION (IN2 = Vout) =====
def choose_decimation(freq, periods=10):
    """Choose the decimation factor so the buffer contains about 10 signal periods."""
    ideal = FS * periods / (N * freq)
    for d in [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384]:
        if d >= ideal:
            return d
    return 16384


def get_voltage(rp, freq=1000):
    """Acquire IN2 and return its mean voltage in volts."""
    t, voltage = acquire(rp, freq)
    return np.mean(voltage)

def acquire(rp, freq):
    """Configure acquisition and return the time [s] and IN2 voltage [V]."""
    dec = choose_decimation(freq)
    buffer_time = N * dec / FS  # Buffer fill time [s]

    _clear_pending_responses(rp)
    rp.tx_txt('ACQ:RST')
    rp.tx_txt('ACQ:DATA:FORMAT ASCII')
    rp.tx_txt('ACQ:DATA:UNITS VOLTS')
    rp.tx_txt(f'ACQ:DEC {dec}')
    rp.tx_txt('ACQ:START')
    time.sleep(buffer_time + 0.1)
    rp.tx_txt('ACQ:TRig NOW')

    for _ in range(200):  # Wait for the trigger
        rp.tx_txt('ACQ:TRig:STAT?')
        if 'TD' in rp.rx_txt():
            break

    time.sleep(buffer_time + 0.1)
    rp.tx_txt('ACQ:SOUR2:DATA?')
    response = rp.rx_txt().strip()

    while not response.startswith('{'):  # Ignore responses that are not data
        response = rp.rx_txt().strip()

    voltage = (
        np.array(response.strip('{}').replace('  ', '').split(','), dtype=float)
        * HV
    )

    t = np.arange(len(voltage)) * dec / FS
    return t, voltage


def acquire_simulated(rp, freq):
    dec = choose_decimation(freq)

    duration = N * dec / FS
    sample_rate = FS / dec

    t, voltage = simulate_sine_wave(
        frequency=freq,
        amplitude=AMPL,
        variation=0.02,
        duration=duration,
        sample_rate=sample_rate
    )

    return t, voltage

# ===== SIGNAL PROCESSING =====
def fit_sine(t, v, freq):
    """Fit a sine wave using least squares; return peak-to-peak amplitude and R²."""
    M = np.column_stack([
        np.sin(2 * np.pi * freq * t),
        np.cos(2 * np.pi * freq * t),
        np.ones_like(t)
    ])

    coef = np.linalg.lstsq(M, v, rcond=None)[0]
    residuals = v - M @ coef
    r2 = 1 - np.var(residuals) / np.var(v) if np.var(v) > 0 else 0

    return 2 * np.hypot(coef[0], coef[1]), r2


def measure(rp, freq, attempts=5):
    """Measure Vout peak-to-peak at a frequency, retrying if acquisition is invalid."""
    generate(rp, freq)

    for _ in range(attempts):
        t, v = acquire(rp, freq)
        v_pp, r2 = fit_sine(t, v, freq)

        if r2 > 0.9:
            break

    return v_pp, r2


def frequency_sweep(freqs):
    """Sweep frequencies and return the gain G = Vout/Vin in dB."""
    rp = connect()
    G_dB = []

    for f in freqs:
        vout, r2 = measure(rp, f)
        vin = 2 * AMPL  # Peak-to-peak voltage of the signal generated on OUT1

        gain = 20 * np.log10(vout / vin)
        G_dB.append(gain)

        error_flag = '' if r2 > 0.9 else '   <-- INVALID MEASUREMENT'

        print(
            f'{f:7.0f} Hz | Vout pp = {vout:.3f} V | '
            f'G = {gain:6.2f} dB{error_flag}'
        )

    rp.tx_txt('OUTPUT1:STATE OFF')
    rp.close()

    return np.array(G_dB)

def bode_plot():
    results = {}
    level = 'level'  # 'lowLevel'
    results[level] = frequency_sweep(freqs)


    # ===== NOTEBOOK 4 =====
    for name, G in results.items():
        plt.semilogx(freqs, G, 'o-', label=name)

    plt.xlim(F_MIN, F_MAX)
    plt.xlabel('Frequency [Hz]')
    plt.ylabel('Gain [dB]')
    plt.legend()
    plt.grid(which='both')
    plt.savefig('bode.png', dpi=200)
    plt.show()


    if len(results) >= 2:
        table = np.array(list(results.values()))
        spread = table.max(axis=0) - table.min(axis=0)

        print(
            f'Frequency with maximum difference: '
            f'{freqs[np.argmax(spread)]:.0f} Hz '
            f'(Difference between levels: {spread.max():.2f} dB)'
        )

def measure_peak_to_peak_cycles(rp, freq, number_of_cycles=10, acquire_fn=None):
    total_vpp = 0.0
    cycles_measured = 0

    if acquire_fn is None:
        acquire_fn = acquire

    while cycles_measured < number_of_cycles:
        t, voltage = acquire_fn(rp, freq)
        cycles = get_peak_to_peak_per_cycle(t, voltage)

        for cycle in cycles:
            total_vpp += cycle["peak_to_peak"]
            cycles_measured += 1

            if cycles_measured >= number_of_cycles:
                break

    average_vpp = total_vpp / cycles_measured

    print(
        f"Average peak-to-peak voltage over "
        f"{cycles_measured} cycles: {average_vpp:.4f} V"
    )

    return average_vpp