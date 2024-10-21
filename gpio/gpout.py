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
    outp.on()
    print(time.time())
    print(time.time_ns())
    print(perf_counter())
    outp.off()
    print(perf_counter())
    print(time.time())
    print(time.time_ns())
    time.sleep(1)



