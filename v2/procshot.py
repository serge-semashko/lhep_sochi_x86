import matplotlib.pyplot as plt
import pathlib
import os
import matplotlib
matplotlib.use('agg')
import cv2
from scipy import ndimage
import numpy as np
import sys
import time
import math
t1 = time.time()

def get_color(mean):
    return [mean // 3, mean // 3, mean //3]

def getpiececoords(x_piece_range, y_piece_range, center_x, center_y, yu, xl, yd ,xr):

    print([yu + y_piece_range * 0 - yu, xl + x_piece_range * 5 - xl], [yu + y_piece_range * (0 + 1) - 1 - yu, xl + x_piece_range * (5 + 1) - 1 - xl])

    pieces = []

    x_lines = [center_x]
    y_lines = [center_y]

    x_cur = center_x
    y_cur = center_y
    while x_cur > xl:
        x_cur -= x_piece_range
        if x_cur >= xl:
            if x_cur == xl:
                x_cur += 1
            x_lines.append(x_cur)
    x_cur = center_x
    while x_cur < xr:
        x_cur += x_piece_range
        if x_cur <= xr:
            if x_cur == xr:
                x_cur -= 1
            x_lines.append(x_cur)

    while y_cur > yu:
        y_cur -= y_piece_range
        if y_cur >= yu:
            if y_cur == yu:
                y_cur += 1
            y_lines.append(y_cur)
    y_cur = center_y
    while y_cur < yd:
        y_cur += y_piece_range
        if y_cur <= yd:
            if y_cur == yd:
                y_cur -=1
            y_lines.append(y_cur)

    x_lines.sort()
    y_lines.sort()

    for i in range(len(y_lines) - 1):
        for j in range(len(x_lines) - 1):
            pieces.append([[y_lines[i], x_lines[j]], [y_lines[i + 1], x_lines[j + 1]]])

    # for j in range(ny):
    #     for i in range(nx):
    #         lu = [yu + y_piece_range * j - yu, xl + x_piece_range * i - xl]
    #
    #         piece_xr = xl + x_piece_range * (i + 1) - 1 - xl
    #         # if i != nx - 1:
    #         #     piece_xr = xl + x_piece_range * (i + 1) - 1 - xl
    #         # else:
    #         #     piece_xr = xr - xl
    #
    #         if piece_xr == xr:
    #             piece_xr -= 1
    #
    #         piece_yd = yu + y_piece_range * (j + 1) - 1 - yu
    #         # if j != ny - 1:
    #         #     piece_yd = yu + y_piece_range * (j + 1) - 1 - yu
    #         # else:
    #         #     piece_yd = yd - yu
    #
    #         if piece_yd == yd:
    #             piece_yd -= 1
    #
    #         rd = [piece_yd, piece_xr]
    #
    #         pieces.append([lu, rd])
    return pieces, len(x_lines) - 1, len(y_lines) - 1

def getsrminmax(piece_coord, rect):
    s = 0
    k = 0
    mmin = 1000000000000
    mmax = 0
    x1 = piece_coord[0][1]
    x2 = piece_coord[1][1]
    y1 = piece_coord[0][0]
    y2 = piece_coord[1][0]
    # print(x1, x2, y1, y2)
    # # print(piece_coord, x1, x2, y1, y2)
    for i in range(x1, x2 + 1):
        for j in range(y1, y2 + 1):
            el = sum(rect[j][i])
            s += el
            k += 1
            if el > mmax:
                mmax = el
            if el < mmin:
                mmin = el
    sr = s // k
    return [mmin, sr, mmax]

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

def process_shot(kx, ky, xl, yu, xr, yd, xdlin, ydlin, nx, ny, filename, thick_center, thick_cm, thick_5mm, mark=1):
    import matplotlib.pyplot as plt

    img = cv2.imread(filename)
    onlyname = os.path.dirname(filename)+'/'+pathlib.Path(filename).stem;

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

    print('------------------', xr, yd, '---------------------')

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
    pmm_x = math.trunc(xrange / xdlin)
    pmm_y = math.trunc(yrange / ydlin)
    range_cm = math.trunc(pmm * 10)
    range_mm = math.trunc(pmm * 5)
    print('pix/cm x=%d y=%d'%(math.trunc(pmm_x * 10), math.trunc(pmm_y * 10)))

    ################################VOVA
    # 1cmХ1cm - range_cm
    # 0.5cmХ0.5cm - range_mm
    # 0.01cmХ0.01cm - pmm
    # Mean min max
    # Матрица в картинку 
    # ячейка окрашена в цвет градиент - пока в сумму /3

    print(yrange, range_cm)

    # nx0 = math.trunc(xrange / (range_cm * 5))
    # ny0 = math.trunc(yrange / (range_cm * 5))

    pieces_0, nx0, ny0 = getpiececoords(range_cm * 5, range_cm * 5, center_x, center_y, yu, xl, yd, xr)

    print(len(pieces_0))

    print(nx0, ny0)

    rezmatr0 = np.zeros([ny0, nx0, 3], dtype=int)

    rmin0 = 10000000000000000000
    rmax0 = 0

    for i in range(len(pieces_0)):
        print(pieces_0[i])
        sr = getsrminmax(pieces_0[i], rabrect)

        if rmin0 > sr[0]:
            rmin0 = sr[0]
        if rmax0 < sr[2]:
            rmax0 = sr[2]

        rezy = i // nx0
        rezx = i % nx0

        print(ny0, rezy, rezx, rezmatr0.shape, len(pieces_0))

        rezmatr0[rezy][rezx] = sr

    print('=================================rezmatr0=====================================')
    print(rezmatr0)
    print()
    f = open('rezmatr_5cm.txt', 'w',encoding='utf-8')
    if rmax0 > 0:
        ravn = ((rmax0 - rmin0) / rmax0)
    else:
        ravn = 1
    f.write(u'Равномерность - ' + str(ravn) + '\n')
    f.write('[')
    for j in range(rezmatr0.shape[0]):
        f.write('[')
        for i in range(rezmatr0.shape[1]):
            f.write('[' + str(rezmatr0[j][i][0]) + ', ' + str(rezmatr0[j][i][1]) + ', ' + str(rezmatr0[j][i][2]) + '],')
        f.write('],')
    f.write(']')
    f.close()

    rezimg0 = np.zeros([yrange, xrange, 3], dtype=int)

    print(rezimg0.shape)
    for i in range(rezmatr0.shape[1]):
        for j in range(rezmatr0.shape[0]):
            sr0 = get_color(rezmatr0[j][i][1])
            print(sr0)

            p_i = nx0 * j + i
            p = pieces_0[p_i]
            yu0 = p[0][0]
            xl0 = p[0][1]
            yd0 = p[1][0]
            xr0 = p[1][1]

            print(yu0, yd0, xl0, xr0)

            for a in range(yu0, yd0):
                for b in range(xl0, xr0):
                    rezimg0[a][b] = sr0
    cv2.line(rezimg0, (center_x, yu), (center_x, yd), (0, 0, 0), thickness=thick_center)
    cv2.line(rezimg0, (xl, center_y), (xr, center_y), (0, 0, 0), thickness=thick_center)
    cv2.imwrite(onlyname +  '-5cm.png', rezimg0)

    # nx1 = math.trunc(xrange / range_cm)
    # nx2 = math.trunc(xrange / range_mm)
    # nx3 = math.trunc(xrange / pmm_x)
    #
    # ny1 = math.trunc(yrange / range_cm)
    # ny2 = math.trunc(yrange / range_mm)
    # ny3 = math.trunc(yrange / pmm_y)

    pieces_1, nx1, ny1 = getpiececoords(range_cm, range_cm, center_x, center_y, yu, xl, yd, xr)
    pieces_2, nx2, ny2 = getpiececoords(range_mm, range_mm, center_x, center_y, yu, xl, yd, xr)
    pieces_3, nx3, ny3 = getpiececoords(pmm_x, pmm_y, center_x, center_y, yu, xl, yd, xr)

    print('=======================================')
    print(nx1, ny1)
    print(nx2, ny2)
    print(nx3, ny3)
    print('=======================================')

    # for i in pieces_1:
    #     print(i[0], i[1])
    #     cv2.rectangle(img, [i[0][1], i[0][0]], [i[1][1], i[1][0]], [0, 0, 255])
    #
    # cv2.rectangle(img, [0, 168], [41, 209], [0, 255, 0], thickness=1)
    # cv2.rectangle(img, [0, 210], [41, 261], [0, 255, 0], thickness=1)
    #
    # cv2.imwrite('t.png', img)

    rmin1 = 10000000000000000000
    rmax1 = 0

    rezmatr1 = np.zeros([ny1, nx1, 3], dtype=int)
    for i in range(len(pieces_1)):
        print(pieces_1[i])
        sr = getsrminmax(pieces_1[i], rabrect)

        rezy = i // nx1
        rezx = i % nx1

        if rmin0 > sr[0]:
            rmin0 = sr[0]
        if rmax0 < sr[2]:
            rmax0 = sr[2]

        # print(ny1, rezy, rezx, rezmatr1.shape, len(pieces_1))

        rezmatr1[rezy][rezx] = sr

    print('=================================rezmatr1=====================================')
    print(rezmatr1)
    print()

    f = open('rezmatr_1cm.txt', 'w',encoding='utf-8')
    if rmax1 > 0:
        ravn = ((rmax1 - rmin1) / rmax1)
    else:
        ravn = 1
    f.write(u'Равномерность - ' + str(ravn) + '\n')
    f.write('[')
    for j in range(rezmatr1.shape[0]):
        f.write('[')
        for i in range(rezmatr1.shape[1]):
            f.write('[' + str(rezmatr1[j][i][0]) + ', ' + str(rezmatr1[j][i][1]) + ', ' + str(rezmatr1[j][i][2]) + '],')
        f.write('],')
    f.write(']')
    f.close()

    rezimg1 = np.zeros([yrange, xrange, 3], dtype=int)

    print(rezimg1.shape)

    for i in range(rezmatr1.shape[1]):
        for j in range(rezmatr1.shape[0]):
            sr1 = get_color(rezmatr1[j][i][1])
            # print(sr1)

            p_i = nx1 * j + i
            p = pieces_1[p_i]
            yu1 = p[0][0]
            xl1 = p[0][1]
            yd1 = p[1][0]
            xr1 = p[1][1]

            # print(yu1, yd1, xl1, xr1)

            for a in range(yu1, yd1):
                for b in range(xl1, xr1):
                    rezimg1[a][b] = sr1
    cv2.line(rezimg1, (center_x, yu), (center_x, yd), (0, 0, 0), thickness=thick_center)
    cv2.line(rezimg1, (xl, center_y), (xr, center_y), (0, 0, 0), thickness=thick_center)

    if mark == 1:
        print('marking 1 cm')
        for i in range(center_x, xl, -1 * range_cm):
            cv2.line(rezimg1, (i, yu), (i, yd), (0, 0, 0), thickness=thick_5mm)
        for i in range(center_x, xr, range_cm):
            cv2.line(rezimg1, (i, yu), (i, yd), (0, 0, 0), thickness=thick_5mm)

        for i in range(center_y, yu, -1 * range_cm):
            cv2.line(rezimg1, (xl, i), (xr, i), (0, 0, 0), thickness=thick_5mm)
        for i in range(center_y, yd, range_cm):
            cv2.line(rezimg1, (xl, i), (xr, i), (0, 0, 0), thickness=thick_5mm)

    cv2.imwrite(onlyname +'-1cm.png', rezimg1)

    rmin2 = 10000000000000000000
    rmax2 = 0

    rezmatr2 = np.zeros([ny2, nx2, 3], dtype=int)
    for i in range(len(pieces_2)):
        sr = getsrminmax(pieces_2[i], rabrect)

        rezy = i // nx2
        rezx = i % nx2

        if rmin2 > sr[0]:
            rmin2 = sr[0]
        if rmax2 < sr[2]:
            rmax2 = sr[2]

        # print(rezy, rezx, rezmatr2.shape)

        rezmatr2[rezy][rezx] = sr

    print('=================================rezmatr2=====================================')
    print(rezmatr2)
    print()

    f = open('rezmatr_5mm.txt', 'w',encoding='utf-8')
    if rmax2 > 0:
        ravn = ((rmax2 - rmin2) / rmax2)
    else:
        ravn = 1
    f.write(u'Равномерность - ' + str(ravn) + '\n')
    f.write('[')
    for j in range(rezmatr2.shape[0]):
        f.write('[')
        for i in range(rezmatr2.shape[1]):
            f.write('[' + str(rezmatr2[j][i][0]) + ', ' + str(rezmatr2[j][i][1]) + ', ' + str(rezmatr2[j][i][2]) + '],')
        f.write('],')
    f.write(']')
    f.close()

    rezimg2 = np.zeros([yrange, xrange, 3], dtype=int)

    print(rezimg2.shape)
    for i in range(rezmatr2.shape[1]):
        for j in range(rezmatr2.shape[0]):
            sr2 = get_color(rezmatr2[j][i][1])
            # print(sr2)

            p_i = nx2 * j + i
            p = pieces_2[p_i]
            yu2 = p[0][0]
            xl2 = p[0][1]
            yd2 = p[1][0]
            xr2 = p[1][1]

            # print(yu2, yd2, xl2, xr2, rezimg2.shape)

            for a in range(yu2, yd2):
                for b in range(xl2, xr2):
                    rezimg2[a][b] = sr2
    cv2.line(rezimg2, (center_x, yu), (center_x, yd), (0, 0, 0), thickness=thick_center)
    cv2.line(rezimg2, (xl, center_y), (xr, center_y), (0, 0, 0), thickness=thick_center)
    if mark == 1:
        print('marking 5mm')
        for i in range(center_x, xl, -1 * range_mm):
            cv2.line(rezimg2, (i, yu), (i, yd), (0, 0, 0), thickness=thick_5mm)
        for i in range(center_x, xr, range_mm):
            cv2.line(rezimg2, (i, yu), (i, yd), (0, 0, 0), thickness=thick_5mm)

        for i in range(center_y, yu, -1 * range_mm):
            cv2.line(rezimg2, (xl, i), (xr, i), (0, 0, 0), thickness=thick_5mm)
        for i in range(center_y, yd, range_mm):
            cv2.line(rezimg2, (xl, i), (xr, i), (0, 0, 0), thickness=thick_5mm)
    cv2.imwrite(onlyname +'-5mm.png', rezimg2)

    xinfo2 = []
    for i in range(rezmatr2.shape[1]):
        s = 0
        for j in range(rezmatr2.shape[0]):
            s += rezmatr2[j][i][1]
        xinfo2.append(s // rezmatr2.shape[0])

    yinfo2 = []
    for j in range(rezmatr2.shape[0]):
        s2 = 0
        k2 = 0
        for i in range(rezmatr2.shape[1]):
            s2 += rezmatr2[j][i][1]
            k2 += 1
        yinfo2.append(s2 // k2)
    x = [((i - nx2 / 2)) for i in range(nx2)]
    y = [((i - ny2 / 2)) for i in range(ny2)]

    plt.bar(x, xinfo2, width=0.5)
    plt.savefig(filename.split('.')[0] + '-5mm-bar.png')
    plt.clf()

    fig, ax = plt.subplots()

    print(y, yinfo2, ny2, rezmatr2.shape)

    ax.barh(y, yinfo2, height=0.5)
    ax.invert_yaxis()


    plt.savefig(filename.split('.')[0] + '-5mm-barh.png')
    plt.clf()


    rmin3 = 10000000000000000000
    rmax3 = 0

    rezmatr3 = np.zeros([ny3, nx3, 3], dtype=int)
    for i in range(len(pieces_3)):
        sr = getsrminmax(pieces_3[i], rabrect)

        rezy = i // nx3
        rezx = i % nx3

        if rmin3 > sr[0]:
            rmin3 = sr[0]
        if rmax3 < sr[2]:
            rmax3 = sr[2]

        rezmatr3[rezy][rezx] = sr

    print('=================================rezmatr3=====================================')
    print(rezmatr3)
    print()

    f = open('rezmatr_1mm.txt', 'w',encoding='utf-8')
    if rmax3 > 0:
        ravn = ((rmax3 - rmin3) / rmax3)
    else:
        ravn = 1
    f.write(u'Равномерность - ' + str(ravn) + '\n')
    f.write('[')
    for j in range(rezmatr3.shape[0]):
        f.write('[')
        for i in range(rezmatr3.shape[1]):
            f.write('[' + str(rezmatr3[j][i][0]) + ', ' + str(rezmatr3[j][i][1]) + ', ' + str(rezmatr3[j][i][2]) + '],')
        f.write('],')
    f.write(']')
    f.close()

    rezimg3 = np.zeros([yrange, xrange, 3], dtype=int)

    print(rezimg3.shape)
    for i in range(rezmatr3.shape[1]):
        for j in range(rezmatr3.shape[0]):
            sr3 = get_color(rezmatr3[j][i][1])
            # print(sr3)

            p_i = nx3 * j + i
            p = pieces_3[p_i]
            yu3 = p[0][0]
            xl3 = p[0][1]
            yd3 = p[1][0]
            xr3 = p[1][1]

            # print(yu3, yd3, xl3, xr3)

            for a in range(yu3, yd3):
                for b in range(xl3, xr3):
                    rezimg3[a][b] = sr3
    cv2.line(rezimg3, (center_x, yu), (center_x, yd), (0, 0, 0), thickness=thick_center)
    cv2.line(rezimg3, (xl, center_y), (xr, center_y), (0, 0, 0), thickness=thick_center)
    if mark == 1:
        print('marking 1 mm')
        for i in range(center_x, xl, -1 * pmm_y):
            cv2.line(rezimg3, (i, yu), (i, yd), (0, 0, 0), thickness=thick_5mm)
        for i in range(center_x, xr, pmm_y):
            cv2.line(rezimg3, (i, yu), (i, yd), (0, 0, 0), thickness=thick_5mm)

        for i in range(center_y, yu, -1 * pmm_y):
            cv2.line(rezimg3, (xl, i), (xr, i), (0, 0, 0), thickness=thick_5mm)
        for i in range(center_y, yd, pmm_y):
            cv2.line(rezimg3, (xl, i), (xr, i), (0, 0, 0), thickness=thick_5mm)
    cv2.imwrite(onlyname +'-1mm.png', rezimg3)

    xinfo3 = []
    for i in range(rezmatr3.shape[1]):
        s = 0
        for j in range(rezmatr3.shape[0]):
            s += rezmatr3[j][i][1]
        xinfo3.append(s // rezmatr3.shape[0])

    yinfo3 = []
    for j in range(rezmatr3.shape[0]):
        s3 = 0
        k3 = 0
        for i in range(rezmatr3.shape[1]):
            s3 += rezmatr3[j][i][1]
            k3 += 1
        yinfo3.append(s3 // k3)
    x = [((i - nx3 / 2)) for i in range(nx3)]
    y = [((i - ny3 / 2)) for i in range(ny3)]

    plt.bar(x, xinfo3, width=0.5)
    plt.savefig(filename.split('.')[0] + '-1mm-bar.png')
    plt.clf()

    fig, ax = plt.subplots()

    ax.barh(y, yinfo3, height=0.5)
    ax.invert_yaxis()

    plt.savefig(filename.split('.')[0] + '-1mm-barh.png')
    plt.clf()

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
    file = open(filename.split('.')[0]+'_tbl.html', 'w',encoding='utf-8')
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

    # cv2.rectangle(img, (xl, yu), (xr, yd), (0, 0, 0), thickness=thick_center)
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
    file = open(filename.split('.')[0]+'.txt', 'w',encoding='utf-8')
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
    file = open(filename.split('.')[0]+'.html', 'w',encoding='utf-8')
    file.write(restbl)
    file.close()


    return rezmatr
kx =1#(1* (2 ** 0.5) )/ 2
ky =1# 1/2 
xl=538
yu=358
xr=800
yd=600
x_len=80
y_len=57
x_tab=8
y_tab=6
w1=4
w2=1
w3=1


if __name__ == "__main__":
    # imname = sys.argv[1]
    imname = 'lumi.png'
    mark = 1
    # print(str(sys.argv))

    #imname = 'photo_2024-10-11_11-29-01.jpg'
    #1 - коэффициент деформации по х, 2 - коэффициент деформации по у, 3 - левая граница по x, 4 - верхняя граница по y, 5 - правая граница по x, 6 - нижняя граница по y,
    #7 - Длина границы х в мм, 8 - длина границы у в мм, 9 - количество ячеек по x, 10 - количество ячеек по y, 11 - название обрабатываемого файла
    #12 - толщина центрального креста, 13 - толщина крестов через каждый сантиметр, 14 - толщина крестов через каждые 5 мм, 15 - отрисовывать ли сетку на результирующих изображениях

    t1 = time.time()

    print('rezult -', process_shot(kx, ky, xl, yu, xr, yd, x_len, y_len, x_tab, y_tab, imname, w1, w2, w3, mark))
    print(time.time()-t1);
