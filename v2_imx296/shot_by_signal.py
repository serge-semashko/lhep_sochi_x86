import cv2
import sys
import traceback
from pymemcache.client.base import Client
import argparse
import time
import signal
import time
import os
from picamera2 import Picamera2, Preview

if not os.path.exists("images"):
    os.makedirs("images")

#import gpiozero as gp
#btn = gp.DigitalInputDevice("BOARD15",pull_up=True)

handles = []
totalFrames = 0
color_mode = ''




'''
apiPreference    preferred Capture API backends to use. 
Can be used to enforce a specific reader implementation 
if multiple are available: 
e.g. cv2.CAP_MSMF or cv2.CAP_DSHOW.
'''
# open video0
picam2 = Picamera2()




ind = 1


#//NOT WORK

#work ok
client = Client(('127.0.0.1', 11211))

run_num = 1 #номер рана
frame_cup = 1
frame_inter = 0.5 #500 милисекунд
run_inter = 0.5
run_error = 0
frame_err = 0


f_count=0
f_time=time.time()
save_flag=False
f_count=0
f_time=time.time()

while(True):
    if frame_err>5:
        pass
    try:
        sendValue = client.get('Value')
    except Exception as e:
        sendValue = None
        print(f"Error occurred while getting value from client: {e}")


    # print('sendValue=')
    # print(sendValue, type(sendValue))
    if sendValue == None:
        sendValue = 10
    sendValue = int(sendValue)
    
    if sendValue and sendValue > 0:
        br = sendValue
        flag = 1
    else:
        flag = 0
        # print(flag, br)







    try:
        t1 = time.time()
        controls = {'ExposureTime': br, 'AnalogueGain': 1.0, 'FrameRate': 40}
        config = picam2.create_still_configuration(controls=controls)
        picam2.start(config)
        data = picam2.capture_array()
        picam2.stop()
            

        f_count += 1
        if f_count == 10:
            print('================FPS=%f'%(10/ (time.time() - f_time)))
            f_count = 0
            f_time = time.time()

        image = data
        w1 = image.shape[1]
        h1 = image.shape[0]
        frame = image
        tm = time.localtime()
        file_name = '%.4d_%.2d_%.2d'%(tm.tm_year, tm.tm_mon, tm.tm_mday) + '-' +  '%.2d_%.2d_%.2d'%(tm.tm_hour, tm.tm_min, tm.tm_sec)+ '-' + '%.5d'%(run_num) + '-' +  str(br)
        image1 = cv2.resize(frame,(640,480),interpolation = cv2.INTER_LINEAR)
        cv2.imwrite('images/tmp.png', frame)
        os.rename('images/tmp.png','images/'+file_name+'.png')
        
        print(file_name)
        run_num += 1
        # print('sleep')
        flag = 0
        # print('sleep end')
        windowName = "GELIKOSOFIYA "
        # cv2.namedWindow(windowName,1)
        # image = cv2.resize(image,(640,480),interpolation = cv2.INTER_LINEAR)

        # cv2.imshow(windowName,image)
        # cv2.waitKey(10)

    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print("*** print_tb:")
        traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
        print("*** format_exc, first and last line:")
        res_data = traceback.format_exc().splitlines()
        print(res_data)
        run_error = 1

    time.sleep(run_inter)
# When everything done, release the capture
cv2.destroyAllWindows()
