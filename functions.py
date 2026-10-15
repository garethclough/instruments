import numpy as np
import matplotlib.pyplot as plt

def simulate_sine_wave(frequency=1.0, amplitude=1.0,
                       modulation_frequency=0.1,
                       duration=10.0, sample_rate=1000):
    """
    Simulate a sine wave with varying amplitude.

    frequency:             Frequency of the sine wave (Hz)
    amplitude:             Maximum amplitude
    modulation_frequency:  Frequency of amplitude variation (Hz)
    duration:              Duration of the signal (seconds)
    sample_rate:            Samples per second
    """
    t = np.linspace(0, duration, int(duration * sample_rate),
                    endpoint=False)

    # Vary the amplitude sinusoidally
    varying_amplitude = amplitude * (
        1 + np.sin(2 * np.pi * modulation_frequency * t)
    ) / 2

    # Generate the sine wave
    signal = varying_amplitude * np.sin(2 * np.pi * frequency * t)

    return t, signal