from picamera2 import Picamera2, Preview
from libcamera import controls
from pprintpp import pprint as pp
import time


#PiCamera setup
picam2 = Picamera2() #instantiates a picamera
modes = picam2.sensor_modes
mode = modes[1]
print('mode selected: ', mode)
camera_config = picam2.create_still_configuration(raw={'format': mode['unpacked']}, sensor={'output_size': mode['size'], 'bit_depth': mode['bit_depth']})
picam2.configure(camera_config)
# Checking raw configuration
check = picam2.camera_configuration()['raw']
pp(check)
picam2.start()

# grab a RAW frame and save it as a np 16bit array.
raw = picam2.capture_array("raw").view(np.uint16)