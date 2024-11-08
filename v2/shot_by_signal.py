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
import os
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
color_mode = -1000
def camera_initFromFile(fileName,index):
    global cfg,Width,Height,color_mode,save_raw
    #load config file
    config = arducam_config_parser.LoadConfigFile(fileName)

    camera_parameter = config.camera_param.getdict()
    Width = camera_parameter["WIDTH"]
    Height = camera_parameter["HEIGHT"]

    BitWidth = camera_parameter["BIT_WIDTH"]
    ByteLength = 1
    if BitWidth > 8 and BitWidth <= 16:
        ByteLength = 2
        save_raw = True
    FmtMode = camera_parameter["FORMAT"][0]
    color_mode = camera_parameter["FORMAT"][1]

    I2CMode = camera_parameter["I2C_MODE"]
    I2cAddr = camera_parameter["I2C_ADDR"]
    TransLvl = camera_parameter["TRANS_LVL"]
    cfg = {"u32CameraType":0x00,
            "u32Width":Width,"u32Height":Height,
            "usbType":0,
            "u8PixelBytes":ByteLength,
            "u16Vid":0,
            "u32Size":0,
            "u8PixelBits":BitWidth,
            "u32I2cAddr":I2cAddr,
            "emI2cMode":I2CMode,
            "emImageFmtMode":FmtMode,
            "u32TransLvl":TransLvl }

    # ArducamSDK.
    ret,handle,rtn_cfg = ArducamSDK.Py_ArduCam_open(cfg,index)
    #ret,handle,rtn_cfg = ArducamSDK.Py_ArduCam_autoopen(cfg)
    if ret == 0:
       
        #ArducamSDK.Py_ArduCam_writeReg_8_8(handle,0x46,3,0x00)
        usb_version = rtn_cfg['usbType']
        #print("USB VERSION:",usb_version)
        configs = config.configs
        configs_length = config.configs_length
        for i in range(configs_length):
            type = configs[i].type
            if ((type >> 16) & 0xFF) != 0 and ((type >> 16) & 0xFF) != usb_version:
                continue
            if type & 0xFFFF == arducam_config_parser.CONFIG_TYPE_REG:
                ArducamSDK.Py_ArduCam_writeSensorReg(handle, configs[i].params[0], configs[i].params[1])
            elif type & 0xFFFF == arducam_config_parser.CONFIG_TYPE_DELAY:
                time.sleep(float(configs[i].params[0])/1000)
            elif type & 0xFFFF == arducam_config_parser.CONFIG_TYPE_VRCMD:
                configBoard(handle, configs[i])

        rtn_val,datas = ArducamSDK.Py_ArduCam_readUserData(handle,0x400-16, 16)
        print("Serial: %c%c%c%c-%c%c%c%c-%c%c%c%c"%(datas[0],datas[1],datas[2],datas[3],
                                                    datas[4],datas[5],datas[6],datas[7],
                                                    datas[8],datas[9],datas[10],datas[11]))

        ArducamSDK.Py_ArduCam_registerCtrls(handle, config.controls, config.controls_length)
        # ArducamSDK.Py_ArduCam_setCtrl(handle, "setFramerate", 5)
        # ArducamSDK.Py_ArduCam_setCtrl(handle, "setExposure", 5)
        # ArducamSDK.Py_ArduCam_setCtrl(handle, "setExposureTime", 33000)
        # ArducamSDK.Py_ArduCam_setCtrl(handle, "setGain", 5)
        # ArducamSDK.Py_ArduCam_setCtrl(handle, "setAnalogueGain", 100)

        return handle
    else:
        print("open fail,ret_val = ",ret)
        return None




def getAndDisplaySingleFrame(handle,index):
    global running,Width,Height,save_flag,cfg,color_mode,totalFrames,save_raw
    global COLOR_BayerGB2BGR,COLOR_BayerRG2BGR,COLOR_BayerGR2BGR,COLOR_BayerBG2BGR
    count = 0
    totalFrame = totalFrames
    time0 = time.time()
    time1 = time.time()
    #data = {}
    windowName = "ArduCam%d"%index
    # cv2.namedWindow(windowName,1)
    
    save_path = "images%d"%index
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    
    # print("Take picture.")
    display_time = time.time()
    rtn_val,data,rtn_cfg = ArducamSDK.Py_ArduCam_getSingleFrame(handle)
    
    if rtn_val != 0:
        print("Take picture fail,ret_val = ",rtn_val)
        return
        
    datasize = rtn_cfg['u32Size']
    if datasize == 0:
        print("data length zero!")
        return

    image = convert_image(data,rtn_cfg,color_mode)

    time1 = time.time()
    if time1 - time0 >= 1:
        print("%s %d %s\n"%("fps:",count,"/s"))
        count = 0
        time0 = time1
    count += 1
    if save_flag:
        # cv2.imwrite("%s/image%d.jpg"%(save_path,totalFrame),image)
        # print("Camera%d,save image%d"%(index,totalFrame))
        # if save_raw:
        #     with open("%s/image%d.raw"%(save_path,totalFrame), 'wb') as f:
        #         f.write(data)
        totalFrames += 1
        
    image = cv2.resize(image,(640,482),interpolation = cv2.INTER_LINEAR)

    cv2.imshow(windowName,image)
    cv2.waitKey(10)
    print("End display.")
    #print("------------------------display time:",(time.time() - display_time))




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


config_file_name = ""
if len(sys.argv) > 1:
    config_file_name = sys.argv[1]

    if not os.path.exists(config_file_name):
        print("Config file does not exist.")
        exit()
else:
    print('usage <prg> <config file>')
    exit()


devices_num,index,serials = ArducamSDK.Py_ArduCam_scan()
print("Found %d devices"%devices_num)
for i in range(devices_num):
    datas = serials[i]
    serial = "%c%c%c%c-%c%c%c%c-%c%c%c%c"%(datas[0],datas[1],datas[2],datas[3],
                                        datas[4],datas[5],datas[6],datas[7],
                                        datas[8],datas[9],datas[10],datas[11])
    print("Index:",index[i],"Serial:",serial)
    
time.sleep(2)

handle = camera_initFromFile(config_file_name,0)
if handle != None:
    ret_val = ArducamSDK.Py_ArduCam_setMode(handle,ArducamSDK.EXTERNAL_TRIGGER_MODE)
    if(ret_val == ArducamSDK.USB_BOARD_FW_VERSION_NOT_SUPPORT_ERROR):
        print("USB_BOARD_FW_VERSION_NOT_SUPPORT_ERROR")
        exit(0)
    print('handle addad ', handle, ret_val)    
f_count=0
f_time=time.time()





REG = 0x3028, 0x0010
print('ArducamSDK.Py_ArduCam_readSensorReg')
print(ArducamSDK.Py_ArduCam_readSensorReg(handle,0x3012))




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


# print(ArducamSDK.FORMAT_MODE_JPG)
# print(ArducamSDK.FORMAT_MODE_YUV)
# print(ArducamSDK.FORMAT_MODE_RGB)
# print(ArducamSDK.FORMAT_MODE_MON)
# print(ArducamSDK.FORMAT_MODE_RAW)
f_count=0
f_time=time.time()
save_flag=False
ArducamSDK.Py_ArduCam_setMode(handle,ArducamSDK.EXTERNAL_TRIGGER_MODE)
f_count=0
f_time=time.time()

while(True):
    if frame_err>5:
        ArducamSDK.Py_ArduCam_close(handle)
        
        handle = camera_initFromFile(config_file_name,0)
        if handle == None:
            time.sleep(0.3)
            continue
        ret_val = ArducamSDK.Py_ArduCam_setMode(handle,ArducamSDK.EXTERNAL_TRIGGER_MODE)
        if(ret_val == ArducamSDK.USB_BOARD_FW_VERSION_NOT_SUPPORT_ERROR):
            print("USB_BOARD_FW_VERSION_NOT_SUPPORT_ERROR")
            time.sleep(0.5)
            continue
        print('handle addad ', handle, ret_val)    
        ArducamSDK.Py_ArduCam_setMode(handle,ArducamSDK.EXTERNAL_TRIGGER_MODE)
        frame_err = 0
    sendValue = client.get('Value')

    # print('sendValue=')
    # print(sendValue, type(sendValue))
    if sendValue == None:
        sendValue = 1000
    sendValue = int(sendValue)
    
    if sendValue and sendValue > 0:
        br = sendValue
        flag = 1
    else:
        flag = 0
        # print(flag, br)

    ArducamSDK.Py_ArduCam_writeSensorReg(handle,0x3012,br)


    aa = ArducamSDK.Py_ArduCam_isFrameReady(handle)
    if aa < 1:
        continue
    print('trigger ', aa)

    # getAndDisplaySingleFrame(handle,1)
    # continue





    try:
        rtn_val,data,rtn_cfg = ArducamSDK.Py_ArduCam_getSingleFrame(handle)
        
        if rtn_val != 0:
            print("Take picture fail,ret_val = ",rtn_val)
            frame_err += 1
            continue
            
        datasize = rtn_cfg['u32Size']
        if datasize == 0:
            print("data length zero!")
            frame_err += 1
            continue

        f_count += 1
        if f_count == 10:
            print('================FPS=%f'%(10/ (time.time() - f_time)))
            f_count = 0
            f_time = time.time()

        # print('ok   !!!!!!!!!!!!!!!', str(cfg))
        arr = np.frombuffer(data,dtype=np.uint16)

        # print(type(arr))
        # print(str(arr))



        
        print('color mode ',color_mode)
        image = convert_image(data, cfg, color_mode)


        w1 = image.shape[1]
        h1 = image.shape[0]
        frame = image
        print(str(ret_val)+' '+"%dX%d"%(w1,h1) ) #+str(frame)
        tm = time.localtime()
        file_name = '%.4d_%.2d_%.2d'%(tm.tm_year, tm.tm_mon, tm.tm_mday) + '-' +  '%.2d_%.2d_%.2d'%(tm.tm_hour, tm.tm_min, tm.tm_sec)+ '-' + '%.5d'%(run_num) + '-' +  str(br)
        image1 = cv2.resize(frame,(640,480),interpolation = cv2.INTER_LINEAR)
        # cv2.imshow('tmp.png', image1)
        cv2.imwrite('images/tmp.png', frame)
        os.rename('images/tmp.png','images/'+file_name+'.png')
        # cv2.imwrite(file_name+'.png', frame)
        
        print(file_name)
        if flag == 0:
            br+=10;
            print('up to', br)
        run_num += 1
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
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
