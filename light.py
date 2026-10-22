#!/usr/bin/env python3

import sys
import time
import redpitaya_scpi as scpi

IP = "10.209.3.92"
rp = scpi.scpi(IP)

rp.tx_txt('DIG:PIN LED0,0')
rp.tx_txt('DIG:PIN LED1,0')

#if (len(sys.argv) > 2):
#    led = int(sys.argv[2])
#else:
#    led = 0

#print ("Blinking LED["+str(led)+"]")

#period = 1 # seconds

#while 1:
#    time.sleep(period/2.0)
#    rp.tx_txt('DIG:PIN LED' + str(led) + ',' + str(1))
#    time.sleep(period/2.0)
#    rp.tx_txt('DIG:PIN LED' + str(led) + ',' + str(0))

#rp.close()