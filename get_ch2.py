import time
import numpy as np
import redpitaya_scpi as scpi

IP = '10.209.3.92'
HV = 20  # IN2 HV jumper correction

rp = scpi.scpi(IP)


try:
    rp.tx_txt('ACQ:DATA:FORMAT ASCII')
    rp.tx_txt('ACQ:DATA:UNITS VOLTS')
    rp.tx_txt('ACQ:DEC 128')

    while True:
        rp.tx_txt('ACQ:START')
        rp.tx_txt('ACQ:TRig NOW')

        # Wait for acquisition to complete
        while True:
            rp.tx_txt('ACQ:TRig:STAT?')
            if rp.rx_txt().strip() == 'TD':
                break
            time.sleep(0.01)

        # Read the voltage samples
        rp.tx_txt('ACQ:SOUR2:DATA?')
        response = rp.rx_txt().strip()

        voltage = np.array(
            response.strip('{}').split(','),
            dtype=float
        ) * HV

        v_min = np.min(voltage)
        v_max = np.max(voltage)
        v_pp = v_max - v_min

        print(
            f'Min: {v_min:.4f} V | '
            f'Max: {v_max:.4f} V | '
            f'Peak-to-peak: {v_pp:.4f} V'
        )

except KeyboardInterrupt:
    print('\nMeasurement stopped.')

finally:
    rp.close()