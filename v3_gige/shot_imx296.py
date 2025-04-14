import cv2
import time
import numpy as np
from picamera2 import Picamera2, Preview
from matplotlib import pyplot as plt

picam2 = Picamera2()
t1 = time.time()
controls = {'ExposureTime': 50000//4, 'AnalogueGain': 1.0, 'FrameRate': 40}
config = picam2.create_still_configuration(controls=controls)
picam2.start(config)
# request = picam2.capture_request()
# request.save("main", "image.png")
# print(request.get_metadata()) # this is the metadata for this image
# request.release()
data8 = picam2.capture_array()
cv2.imwrite('1.png', data8)
picam2.stop()
print(time.time()-t1)
controls = {'ExposureTime': 50000//4, 'AnalogueGain': 2.0, 'FrameRate': 40}
config = picam2.create_still_configuration(controls=controls)
picam2.start(config)
data8 = picam2.capture_array()
cv2.imwrite('2.png', data8)
picam2.stop()
print(time.time()-t1)
controls = {'ExposureTime': 50000//4, 'AnalogueGain': 4.0, 'FrameRate': 40}
config = picam2.create_still_configuration(controls=controls)
picam2.start(config)
data8 = picam2.capture_array()
cv2.imwrite('4.png', data8)
picam2.stop()
print(time.time()-t1)


