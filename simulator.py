import functions
import numpy as np
import matplotlib.pyplot as plt

t, signal = functions.simulate_sine_wave(
    frequency=20,
    amplitude=5,
    variation=0.2,
    duration=1,
    sample_rate= 100
)

plt.plot(t, signal)
plt.xlabel("Time (s)")
plt.ylabel("Amplitude")
plt.title("Sine Wave with Varying Amplitude")
plt.grid(True)
plt.show()