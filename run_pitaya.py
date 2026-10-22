import functions

rp = functions.connect()

try:
    functions.generate(rp, 1000)

    while True:
        average_vpp = functions.measure_peak_to_peak_cycles(
            rp,
            freq=1000,
            number_of_cycles=10
        )

except KeyboardInterrupt:
    print("\nMeasurement interrupted by user.")

finally:
    rp.tx_txt('OUTPUT1:STATE OFF')
    rp.close()