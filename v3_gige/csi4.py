import cv2
import time

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


# print(returnCameraIndexes())



cap1 = cv2.VideoCapture(0)
if cap1.isOpened():
    print("cap1 Work")
else:
    print("cap1 Don't work")
    quit()
print('cap1=' + str(cap1))
# cap = cv2.VideoCapture(0, cv2.CAP_MSMF)
# print('cap'+str(cap))
# set width and height
cap1.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap1.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# cap1.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
# cap1.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

# set fps
cap1.set(cv2.CAP_PROP_FPS, 260)
br = 60;
cap1.set(cv2.CAP_PROP_BRIGHTNESS, br)

num = 1
sttime = time.time()
while True:
    # Capture frame-by-frame
    ret, frame = cap1.read()
    # Display the resulting frame
    w1 = cap1.get(cv2.CAP_PROP_FRAME_WIDTH)
    h1 = cap1.get(cv2.CAP_PROP_FRAME_HEIGHT)
    print('fps=%f'%(num/(time.time()-sttime))+' '+str(ret) + ' ' + "%dX%d" % (w1, h1))  # +str(frame)

    cv2.imwrite(str(br)+ '.jpg', frame)
    num += 1
    if br == 220:
        quit()
    #    cv2.imshow('frame', frame)
    br += 1;
    cap1.set(cv2.CAP_PROP_BRIGHTNESS, br)
    #    cap1.set(cv2.CAP_PROP_FRAME_WIDTH, w1+200)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
# When everything done, release the capture

cv2.destroyAllWindows()
