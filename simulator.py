import functions
import numpy as np
import matplotlib.pyplot as plt

t, signal = functions.simulate_sine_wave(
    frequency=1,
    amplitude=5,
    variation=0.2,
    duration=10,
    sample_rate= 100
)

plt.ion()

fig, ax = plt.subplots(figsize=(12, 5))

# Create the lines once
signal_line, = ax.plot(t, signal, label="Signal")
peaks_line, = ax.plot([], [], "o-", label="Peak-to-peak")
average_line, = ax.plot([], [], "r--", label="Rolling Average")

ax.set_xlabel("Time (s)")
ax.set_ylabel("Amplitude")
ax.set_title("Peak-to-Peak Amplitude Variation")
ax.grid(True)
ax.legend()

plt.show(block=False)

cycle = 0

try:
    while True:
        results = functions.get_peak_to_peak_per_cycle(t, signal)
        averages = functions.rolling_average_peak_to_peak(results, window_size=3)
        resultAtTime = []
        currentAverageIndex = 0
        for time in t:
            currentAverage = averages[currentAverageIndex]
            currentResult = 0
            if time >= currentAverage["start_time"] and time < currentAverage["end_time"]:
                currentResult = currentAverage["peak_to_peak"]
                currentResult = currentResult + cycle * 0.1  # Add a small increment for each cycle
            elif time >= currentAverage["end_time"] and currentAverageIndex < len(averages) - 1:
                currentAverageIndex += 1
                currentAverage = averages[currentAverageIndex]
                if time >= currentAverage["start_time"] and time < currentAverage["end_time"]:
                    currentResult = currentAverage["peak_to_peak"]
                    currentResult = currentResult + cycle * 0.1  # Add a small increment for each cycle
            resultAtTime.append(currentResult)
        cycle += 1  # Increment the cycle count for the next iteration
        print(averages)

        average_times = [
            (item["start_time"] + item["end_time"]) / 2
            for item in averages
        ]

        average_values = [
            item["peak_to_peak"] for item in averages
        ]

        print(average_values)

        peak_times = [cycle["peak_time"] for cycle in results]
        amplitudes = [cycle["peak_to_peak"] for cycle in results]

        # Update the existing lines
        peaks_line.set_data(peak_times, amplitudes)
        average_line.set_data(t, resultAtTime)

        ax.relim()
        ax.autoscale_view()

        fig.canvas.draw_idle()
        plt.pause(1)

except KeyboardInterrupt:
    print("\nRecording stopped.")

finally:
    plt.ioff()
    plt.show()