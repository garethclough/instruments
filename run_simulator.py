import functions

try:
    while True:
        functions.measure_peak_to_peak_cycles(
            rp=None,
            freq=1000,
            number_of_cycles=100,
            acquire_fn=functions.acquire_simulated
        )
except KeyboardInterrupt:
    print("\nSimulation stopped.")