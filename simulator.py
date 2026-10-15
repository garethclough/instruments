import functions
import numpy as np
import matplotlib.pyplot as plt

t, signal = functions.simulate_sine_wave(
    frequency=10,
    amplitude=5,
    modulation_frequency=0.5,
    duration=5
)

plt.plot(t, signal)
plt.xlabel("Time (s)")
plt.ylabel("Amplitude")
plt.title("Sine Wave with Varying Amplitude")
plt.grid(True)
plt.show()