import cv2
import sys
import traceback
from pymemcache.client.base import Client
import ArducamSDK
import argparse
import time
import signal
from Arducam import *
from ImageConvert import *
import time





'''
apiPreference    preferred Capture API backends to use. 
Can be used to enforce a specific reader implementation 
if multiple are available: 
e.g. cv2.CAP_MSMF or cv2.CAP_DSHOW.
'''
# open video0

def returnCameraIndexes():
    # checks the first 10 indexes.
    index = 0
    arr = []
    i = 10
    while i > 0:
        cap = cv2.VideoCapture(index)
        if cap.read()[0]:
            arr.append(index)
            cap.release()
        index += 1
        i -= 1
    return arr
#print(returnCameraIndexes())

def frameCheck(fr):
   #0 - low brightness, 1 - good, 2 - too high brightness
    f = 0
    (h, w) = fr.shape[:2]
    for i in range(h):
        for j in range(w):
            pix = fr[i][j]
            if pix[0] == 255 or pix[1] == 255 or pix[2] == 255:
                f = 2
                break
            elif 240 <= pix[0] <= 254 or 240 <= pix[1] <= 254 or 240 <= pix[2] <= 254:
                f = 1
        if f == 2:
            break
    return f

def brightnessSelect(cap):
    lp = 0
    rp = 255
    mp = 127
    while rp - lp > 1:
        cap1.set(cv2.CAP_PROP_BRIGHTNESS, mp)
        ret, frame = cap.read()
        check_rez = frameCheck(frame)
        if check_rez == 0:
            lp = mp
            mp = (rp + lp) / 2
        elif check_rez == 2:
            rp = mp
            mp = (lp + rp) /2
        elif check_rez == 2:
            break
    return mp

#NOT WORK
parser = argparse.ArgumentParser()
parser.add_argument('-f', '--config-file', type=str, required=True, help='Specifies the configuration file.')
parser.add_argument('-v', '--verbose', action='store_true', required=False, help='Output device information.')
parser.add_argument('--preview-width', type=int, required=False, default=-1, help='Set the display width')
parser.add_argument('-n', '--nopreview', action='store_true', required=False, help='Disable preview windows.')


args = parser.parse_args()
config_file = args.config_file
verbose = args.verbose
preview_width = args.preview_width
no_preview = args.nopreview

camera = ArducamCamera()

if not camera.openCamera(config_file):
    raise RuntimeError("Failed to open camera.")
print('camera.handle')  
print(camera.handle)    
REG = 0x3028, 0x0010
if verbose:
    camera.dumpDeviceInfo()
camera.start()
print('ArducamSDK.Py_ArduCam_readSensorReg')
print(ArducamSDK.Py_ArduCam_readSensorReg(camera.handle,0x3012))
scale_width = preview_width
ind = 1


#//NOT WORK

#work ok
client = Client(('127.0.0.1', 11211))
#cap = cv2.VideoCapture(0, cv2.CAP_MSMF)
#print('cap'+str(cap))
# set width and height

#cap1.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
#cap1.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

# set fps

run_num = 1 #номер рана
frame_cup = 1
frame_inter = 0.5 #500 милисекунд
run_inter = 0.5
run_error = 0


print(ArducamSDK.FORMAT_MODE_JPG)
print(ArducamSDK.FORMAT_MODE_YUV)
print(ArducamSDK.FORMAT_MODE_RGB)
print(ArducamSDK.FORMAT_MODE_MON)
print(ArducamSDK.FORMAT_MODE_RAW)


while(True):
    try:
        if run_error!=0:
            run_error = 0
            if not camera.openCamera(config_file):
                raise RuntimeError("Failed to open camera.")
            print('camera.handle')  
            print(camera.handle)    
            REG = 0x3028, 0x0010
            if verbose:
                camera.dumpDeviceInfo()
            camera.start()


        sendValue = client.get('Value')
        print('sendValue=')
        print(sendValue)
        sendValue = int(sendValue)
        print('sendValue=',str(sendValue))
        if sendValue and sendValue > 0:
            br = sendValue
            flag = 1
        else:
            flag = 0
        print(flag, br)




        ss = 0
        ArducamSDK.Py_ArduCam_writeSensorReg(camera.handle,0x3012,br)
        for i in range(frame_cup):
            ret, data, cfg = camera.read()
            print(str(cfg))
            arr = np.frombuffer(data,dtype=np.uint16)

            print(type(arr))
            print(str(arr))


    #        display_fps(0)

            if ret:
                image = convert_image(data, cfg, camera.color_mode)

                # if scale_width != -1:
                #     scale = scale_width / image.shape[1]
                #     image = cv2.resize(image, None, fx=scale, fy=scale)

    #            cv2.imwrite("Arducam%.4d.png"%(ind), image)
            else:
                print("timeout")
            ind += 10
            # key = cv2.waitKey(1)
            # if key == ord('q'):
            #     exit_ = True
            # elif key == ord('s'):
            #     np.array(data, dtype=np.uint8).tofile("image.raw")

            w1 = image.shape[1]
            h1 = image.shape[0]
            frame = image
            print(str(ret)+' '+"%dX%d"%(w1,h1) ) #+str(frame)
            tm = time.gmtime()
            file_name = str(tm.tm_year) + '-' + str(tm.tm_mon) + '-' + str(tm.tm_mday) + '_' + str(tm.tm_hour) + '-' + '%.5d'%(run_num) + '-' + str(i + 1) + '_' + str(ss) + '_' + str(br)
            cv2.imwrite(file_name+'.png', frame)
            cv2.imwrite('last.png', frame)
            ss += frame_inter
            if flag == 0:
                br+=10;
                print('up to', br)
            # time.sleep(frame_inter)
        run_num += 1
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        # print('sleep')
        flag = 0
        # print('sleep end')
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
