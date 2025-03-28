import gpiozero as gp
import time
from time import (
    process_time,
    perf_counter,
    sleep
)
op = "BOARD11"
ip = "BOARD15"
outp = gp.LED("BOARD11")
while 1==1:
    print(perf_counter())
    outp.on()
    time.sleep(0.0001)
    outp.off()
    time.sleep(0.2)



