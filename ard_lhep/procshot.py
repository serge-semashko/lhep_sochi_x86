import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('agg')
import cv2
from scipy import ndimage
import numpy as np
import sys
import time
import math
t1 = time.time()
def getsr(piece_coord, rect):
    s = 0
    k = 0
    x1 = piece_coord[0][1]
    x2 = piece_coord[1][1]
    y1 = piece_coord[0][0]
    y2 = piece_coord[1][0]
    # print(x1, x2, y1, y2)
    # # print(piece_coord, x1, x2, y1, y2)
    for i in range(x1, x2 + 1):
        for j in range(y1, y2 + 1):
            s += sum(rect[j][i])
            k += 1
    sr = s // k
    return sr

def process_shot(kx, ky, xl, yu, xr, yd, xdlin, ydlin, nx, ny, filename, thick_center, thick_cm, thick_5mm):
    import matplotlib.pyplot as plt

    img = cv2.imread(filename)
    # print(img.shape)
    img = img[yu:yd+1, xl:xr+1]
    # print(img.shape)
    xr=xr-xl
    xl=0
    yd=yd-yu
    yu=0

    # cv2.imwrite('cat_'+filename, img)

    # cv2.resize(img, cv2.INTER_AREA)

    fin_width = math.trunc(img.shape[1] * kx)
    fin_height = math.trunc(img.shape[0] * ky)
    print('shape1 ', img.shape)
    dim = (fin_width, fin_height)

    img = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
    print('shape1 ', img.shape)

    # print(img.shape)
    # print(time.time()-t1);
    #пересчет координат
    # xl = int(xl * kx)
    # xr = int(xr * kx)
    # yu = int(yu * ky)
    # yd = int(yd * ky)
    xl = 0
    xr = img.shape[1]
    yu = 0
    yd = img.shape[0]

    center_x = (xl + xr) // 2
    center_y = (yu + yd) // 2

    # print(img.shape)
    # print(xl,yu,xr,yd)

    np.set_printoptions(threshold=sys.maxsize)
    # rabrect = img[yu : yd + 1, xl : xr + 1]
    rabrect = img
    # print(img.shape)
    # # print(str(img[:,:,1]))
    # # print('rabrect')
    # # print(rabrect)

    xrange = xr
    yrange = yd
    # # print(xrange, yrange)

    #рассчет сколько пикселей в 5мм и 1см
    pmm = yrange / ydlin
    pmm_x = xrange / xdlin
    pmm_y = yrange / ydlin
    range_cm = math.trunc(pmm * 10)
    range_mm = math.trunc(pmm * 5)
    print('pix/cm x=%d y=%d'%(math.trunc(pmm_x * 10), math.trunc(pmm_y * 10)))

    ################################VOVA
    # 1cmХ1cm
    # 0.5cmХ0.5cm
    # 0.01cmХ0.01cm
    # Mean min max
    # Матрица в картинку 
    # ячейка окрашена в цвет градиент - пока в сумму /3

    

    x_piece_range = math.trunc(xrange / nx)
    y_piece_range = math.trunc(yrange / ny)
    # print(x_piece_range, y_piece_range)
    quad = []
    
    y_c = rabrect.shape[0]/2
    x_c = rabrect.shape[1]/2
    
    bw = cv2.cvtColor(rabrect, cv2.COLOR_BGR2GRAY)
    qtbl = '<table border=1 style="border-collapse: collapse;">'
    qtbl +='<tr><td>Size</td><td>Min</td><td>Max</td><td>Неодн.</td><td>Mean</td><td>Std</td><td>Ц.М.</td></tr>'
    for i in range(5):
        qtbl +='<tr><td>'+str((i+1)*10)+'мм</td>'
        q_range = math.trunc(pmm * (i+1)*10/2)
    
        y1 = math.trunc(y_c - q_range)
        y2 = math.trunc(y_c + q_range)
        x1 = math.trunc(x_c - q_range)
        x2 = math.trunc(x_c + q_range)
        
        bwt = bw[y1:y2+1,x1:x2+1] 
        y_c1 = bwt.shape[0]/2
        x_c1 = bwt.shape[1]/2
        
        # bw = cv2.rectangle(bw,(x1,y1),(x2,y2),(255,255,255),1)
        
        # bw = cv2.rectangle(bw,(x1,y1),(x2,y2),(255,255,255),1)
        # cv2.imwrite(str(i)+'.png',bwt)
        cm = ndimage.measurements.center_of_mass(bwt)
        # if i==2:
            # print(str(str(i)+'.png'))
            # print(str(bwt))
        # print(str(str(i)+'.png'))
        a_x= np.sum(bwt, axis = 0)
        a_y= np.sum(bwt, axis = 1)
        cm_x = ndimage.measurements.center_of_mass(a_x)[0]
        cm_y = ndimage.measurements.center_of_mass(a_y)[0]
        # print(str(a_x))
        # print(str(cm_x))    
        # print(str(a_y))
        # print(str(cm_y))    
        min = np.min(bwt)
        max = np.max(bwt)
        if max>0:
            uni = (max-min)/max
        else:
            uni=0 
        mrow = (round(y_c1-cm[0])) /pmm
        mcol = round(x_c1-cm[1])/pmm   
        # qtbl += '<tr><td>Center='+str(x_c1)+'</td><td>'+str(y_c1)+'</td><td> '+str(cm)+'</td><td> %.2f,  %.2f '%(mcol,mrow)+'</td></tr>'
        qtbl += '<td>'+str(min)+'</td><td>'+str(max)+'</td><td>%.2f'%(uni)+'</td><td>%.2f'%(np.mean(bwt)) + '</td><td>%.2f'%(np.std(bwt))
        
        qtbl +='</td><td>(%.2f, %.2f)'%(mcol, mrow)+'</td></tr>'
    file = open(filename.split('.')[0]+'_tbl.html', 'w')
    file.write(qtbl)        
    file.close()        
        
        

    pieces = []
    for i in range(nx):
        for j in range(ny):
            lu = [yu + y_piece_range * j - yu, xl + x_piece_range * i - xl]
            if i != nx - 1:
                piece_xr = xl + x_piece_range * (i + 1) - 1 - xl
            else:
                piece_xr = xr - xl

            if piece_xr == img.shape[1]:
                piece_xr -= 1

            if j != ny - 1:
                piece_yd = yu + y_piece_range * (j + 1) - 1 - yu
            else:
                piece_yd = yd - yu

            if piece_yd == img.shape[0]:
                piece_yd -= 1

            rd = [piece_yd, piece_xr]

            pieces.append([lu, rd])
    # print(time.time()-t1);
    rezmatr = np.zeros([nx, ny], dtype=int)
    for i in range(len(pieces)):
        sr = getsr(pieces[i], rabrect)

        rezy = i % ny
        rezx = i // ny

        rezmatr[rezx][rezy] = sr

    # print(rezmatr)

    xinfo = []
    for i in rezmatr:
        xinfo.append(sum(i) // len(rezmatr))
    # print(xinfo)

    yinfo = []
    for j in range(len(rezmatr[0])):
        s = 0
        k = 0
        for i in range(len(rezmatr)):
            s += rezmatr[i][j]
            k += 1
        yinfo.append(s // k)
    # print(yinfo)

    # x = [((xl + (x_piece_range * (i + 1))) - center_x)  for i in range(nx)]
    # y = [((yu + (y_piece_range * (i + 1))) - center_y)  for i in range(ny)]
    x = [((  i - nx/2) )  for i in range(nx)]
    y = [ ((  i - ny/2) ) for i in range(ny)]
    
    # print(x)
    # print(y)
    # print(time.time()-t1);
    # plt.margins(0,0)
    # plt.gca().set_axis_off()
    # plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
    # plt.margins(0,0)
    # plt.gca().xaxis.set_major_locator(plt.NullLocator())
    # plt.gca().yaxis.set_major_locator(plt.NullLocator())
# Сохраняем изображение, исключив ненужные элементы
    plt.bar(x, xinfo, width=0.5)
    # fig.suptitle('Распределение по X')
    # plt.savefig(sys.argv[1].split('.')[0]+'-hist.png')
    plt.savefig(filename.split('.')[0] + '-bar.png')
    plt.clf()

    fig, ax = plt.subplots()
    # ax.set_frame_on(False)

    
    ax.barh(y, yinfo, height=0.5)
    ax.invert_yaxis()
    # fig.suptitle('Распределение по Y')
    # plt.margins(0,0)
    # plt.gca().set_axis_off()
    # plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
    # plt.margins(0,0)
    # plt.gca().xaxis.set_major_locator(plt.NullLocator())
    # plt.gca().yaxis.set_major_locator(plt.NullLocator())

    plt.savefig(filename.split('.')[0] + '-barh.png')
    plt.clf()
    # print(time.time()-t1);

    cv2.rectangle(img, (xl, yu), (xr, yd), (0, 0, 0), thickness=thick_center)
    cv2.line(img, (center_x, yu), (center_x, yd), (0, 0, 0), thickness=thick_center)
    cv2.line(img, (xl, center_y), (xr, center_y), (0, 0, 0), thickness=thick_center)

    for i in range(center_x, xl, -1 * range_cm):
        cv2.line(img, (i, yu), (i, yd), (0, 0, 0), thickness=thick_cm)
    for i in range(center_x, xr, range_cm):
        cv2.line(img, (i, yu), (i, yd), (0, 0, 0), thickness=thick_cm)

    for i in range(center_y, yu, -1 * range_cm):
        cv2.line(img, (xl, i), (xr, i), (0, 0, 0), thickness=thick_cm)
    for i in range(center_y, yd, range_cm):
        cv2.line(img, (xl, i), (xr, i), (0, 0, 0), thickness=thick_cm)

    # for i in range(center_x, xl, -1 * range_mm):
    #     cv2.line(img, (i, yu), (i, yd), (0, 0, 0), thickness=thick_5mm)
    # for i in range(center_x, xr, range_mm):
    #     cv2.line(img, (i, yu), (i, yd), (0, 0, 0), thickness=thick_5mm)

    # for i in range(center_y, yu, -1 * range_mm):
    #     cv2.line(img, (xl, i), (xr, i), (0, 0, 0), thickness=thick_5mm)
    # for i in range(center_y, yd, range_mm):
    #     cv2.line(img, (xl, i), (xr, i), (0, 0, 0), thickness=thick_5mm)

    cv2.imwrite(filename.split('.')[0] + '-markup.png', img)
    # print(img.shape)
    rezmatr = rezmatr.transpose()
    file = open(filename.split('.')[0]+'.txt', 'w')
    resstr = ''
    cm = ndimage.center_of_mass(rezmatr)
    min = np.min(rezmatr)
    max = np.max(rezmatr)
    if max>0:
        uni = (max-min)/max
    else:
        uni=0 
    mrow = round(cm[0])
    mcol = round(cm[1])   
    restbl = 'Min='+str(min)+' Max='+str(max)+' Неоднородность=%.2f'%(uni)+' Среднее=%.2f'%(np.mean(rezmatr)) + ' ст.Откл.=%.2f'%(np.std(rezmatr))
    restbl +='<br>Ц.м.=(%.2f, %.2f)'%(cm[0], cm[1])+' ('+str(round(cm[0]))+', '+str(round(cm[1]))+')<br><table border=1 style="border-collapse: collapse;padding:5px;">'
    
    for i in range(ny):
        restbl +='<tr>'
        for j in range(nx):
            if i == mrow and  j == mcol:
                restbl +='<td style="color:#FF0000;font- padding:0px 5px 0px  5px;" >' 
            else:
                restbl +='<td style="padding:0px 5px 0px  5px;" >' 
            restbl +=('%.3d')%(rezmatr[i,j]) + '</td>'
            resstr += ('%.3d')%(rezmatr[i,j])+', '
        resstr = resstr[:-2]
        restbl +='</tr>'
        resstr +='\n'
    # print(resstr)            
    file.write(resstr)
    # file.write(str(rezmatr))
    file.close()
    file = open(filename.split('.')[0]+'.html', 'w')
    file.write(restbl)
    file.close()


    return rezmatr
kx =1#(1* (2 ** 0.5) )/ 2
ky =1# 1/2 
xl=538
yu=358
xr=799
yd=600
x_len=80
y_len=57
x_tab=8
y_tab=6
w1=4
w2=1
w3=1


if __name__ == "__main__":
    imname = sys.argv[1]
    # print(str(sys.argv))

    #imname = 'photo_2024-10-11_11-29-01.jpg'
    #1 - коэффициент деформации по х, 2 - коэффициент деформации по у, 3 - левая граница по x, 4 - верхняя граница по y, 5 - правая граница по x, 6 - нижняя граница по y,
    #7 - Длина границы х в мм, 8 - длина границы у в мм, 9 - количество ячеек по x, 10 - количество ячеек по y, 11 - название обрабатываемого файла
    #12 - толщина центрального креста, 13 - толщина крестов через каждый сантиметр, 14 - толщина крестов через каждые 5 мм

    t1 = time.time()

    print('rezult -', process_shot(kx, ky, xl, yu, xr, yd, x_len, y_len, x_tab, y_tab, imname, w1, w2, w3))
    print(time.time()-t1);
