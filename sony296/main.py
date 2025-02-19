import cv2
import time
import numpy as np
from picamera2 import Picamera2, Preview
from matplotlib import pyplot as plt

picam2 = Picamera2()
controls = {'ExposureTime': 500000, 'AnalogueGain': 1.5}
config = picam2.create_still_configuration(controls=controls)
picam2.start(config)
startTime = time.time()
picam2.set_controls({"FrameRate": 40})
for i in range(10):
    img = picam2.capture_array("raw")
print(type(img))	
data8 = picam2.capture_array('raw')
data16 = data8.view(np.uint16)
plt.imshow(data16, cmap='gray')
cv2.imshow('8', data8)
cv2.imshow('16', data16)
print(data8.shape)
print(data16.shape)
print(1 / (time.time() - startTime) * 100)
plt.show()