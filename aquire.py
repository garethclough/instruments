#!/usr/bin/env python3

import sys
import redpitaya_scpi as scpi
import matplotlib.pyplot as plot

IP = "10.209.3.92"
rp = scpi.scpi(IP)

rp.tx_txt('ACQ:RST')

rp.tx_txt('ACQ:DEC:CH2 4')
rp.tx_txt('ACQ:START')
rp.tx_txt('ACQ:TRig NOW')

while 1:
    rp.tx_txt('ACQ:TRig:STAT?')
    if rp.rx_txt() == 'TD':
        break

## ! OS 2.00 or higher only ! ##
while 1:
    rp.tx_txt('ACQ:TRig:FILL?')
    if rp.rx_txt() == '1':
        break

rp.tx_txt('ACQ:SOUR2:DATA?')
buff_string = rp.rx_txt()
buff_string = buff_string.strip('{}\n\r').replace("  ", "").split(',')
buff = list(map(float, buff_string))

print(buff)

plot.plot(buff)
plot.ylabel('Voltage')
plot.show()