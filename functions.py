import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks

import numpy as np

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