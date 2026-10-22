import sys
import redpitaya_scpi as scpi
import time
import redpitaya_scpi as scpi
import matplotlib.pyplot as plot
from collections import deque

IP = "10.209.3.92"
rp = scpi.scpi(IP)

wave_form = 'sine'
freq = 2000
ampl = 1

rp.tx_txt('GEN:RST')

rp.tx_txt('SOUR1:FUNC ' + str(wave_form).upper())
rp.tx_txt('SOUR1:FREQ:FIX ' + str(freq))
rp.tx_txt('SOUR1:VOLT ' + str(ampl))

# Enable output
rp.tx_txt('OUTPUT1:STATE ON')
rp.tx_txt('SOUR1:TRig:INT')

