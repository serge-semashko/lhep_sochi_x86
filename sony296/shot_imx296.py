import cv2
import time
import numpy as np
from picamera2 import Picamera2, Preview
from matplotlib import pyplot as plt

picam2 = Picamera2()
controls = {'ExposureTime': 50000, 'AnalogueGain': 1.0, 'FrameRate': 40}
config = picam2.create_still_configuration(controls=controls)
picam2.start(config)
startTime = time.time()
picam2.set_controls({"FrameRate": 40})
# for i in range(10):
#     img = picam2.capture_array("raw")
# print(type(img))	
request = picam2.capture_request()
request.save("main", "image.png")
print(request.get_metadata()) # this is the metadata for this image
request.release()
data8 = picam2.capture_array()
print(data8.shape)
cv2.imwrite('8.png', data8)

picam2.stop()

controls = {'ExposureTime': 10000, 'AnalogueGain': 1.0, 'FrameRate': 40}
config = picam2.create_still_configuration(controls=controls)
data8 = picam2.switch_mode_and_capture_array(config, "main")
cv2.imwrite('8_hi.png', data8)
quit()


picam2 = Picamera2()
controls = {'ExposureTime': 5000, 'AnalogueGain': 1.0, 'FrameRate': 40}
config = picam2.create_still_configuration(controls=controls)
picam2.start(config)
startTime = time.time()
picam2.set_controls({"FrameRate": 40})
# for i in range(10):
#     img = picam2.capture_array("raw")
# print(type(img))	
request = picam2.capture_request()
request.save("mainlow", "image.png")
print(request.get_metadata()) # this is the metadata for this image
request.release()
picam2.stop()

picam2 = Picamera2()
controls = {'ExposureTime': 100000, 'AnalogueGain': 1.0, 'FrameRate': 40}
config = picam2.create_still_configuration(controls=controls)
picam2.start(config)
startTime = time.time()
picam2.set_controls({"FrameRate": 40})
request = picam2.capture_request()
request.save("mainhi", "image.png")
print(request.get_metadata()) # this is the metadata for this image
request.release()
picam2.stop()

quit()
# data8 = picam2.capture_array('raw')
data8 = picam2.capture_array()
print(data8.shape)
plt.imsave('plt8.png', data8, cmap='gray')
cv2.imwrite('8.png', data8)

data16 = data8.view(np.uint16)
plt.imsave('plt16.png', data16, cmap='gray')
cv2.imwrite('16.png', data16)
# cv2.imshow('8', data8)
# plt.imshow(data8, cmap='gray')
# plt.show()
print(data8.shape)
print(data16.shape)
w,h = data8.shape
bw = np.zeros((w // 2, h), dtype=np.uint8)
# fbin = open('data8.bin', 'wb')
# for y in range(h):
#     for x in range(w):
#         bw[x // 2][y] = data8[x][y]
#         fbin.write(data8[x][y])
# fbin.close()
# f = open('data8.txt', 'w')
# for y in range(h):
#     for x in range(w):
#         f.write(str(data8[x][y]) + ' ')
#     f.write('\n')   
# f.close()
# for x in range(w):
#     res = ''
#     for y in range(h):
#         res += '%.3d'%(data8[x][y]) + ' '
#     res += '\n'
# print(1 / (time.time() - startTime) * 100)
