import numpy as np
import matplotlib.pyplot as plt

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