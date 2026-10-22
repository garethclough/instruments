import sys
import redpitaya_scpi as scpi
import time
import redpitaya_scpi as scpi
import matplotlib.pyplot as plot
from collections import deque

IP = "10.209.3.92"
rp = scpi.scpi(IP)

# Read OUT1 settings
rp.tx_txt("SOUR1:FUNC?")
print("Waveform:", rp.rx_txt())

rp.tx_txt("SOUR1:FREQ:FIX?")
print("Frequency:", rp.rx_txt())

rp.tx_txt("SOUR1:VOLT?")
print("Amplitude:", rp.rx_txt())

rp.tx_txt("SOUR1:VOLT:OFFS?")
print("Offset:", rp.rx_txt())


rp.close()