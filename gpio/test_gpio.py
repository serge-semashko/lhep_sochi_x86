import gpiozero as gp
import time
from time import (
    process_time,
    perf_counter,
    sleep
)
def act():
	a = time.time_ns()
	print(a)
def wact():
        btn.wait_for_active()
        print(perf_counter())
        a = time.time()
        print(a)
btn = gp.DigitalInputDevice("BOARD15",pull_up=True)
#btn.when_activated = act

while 1==1:
	wact()
	time.sleep(1)
	continue
	a = time.time()
	# print(a)


