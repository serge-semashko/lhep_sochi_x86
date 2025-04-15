import glob

import sys
# import logging
import base64
import traceback
import json
import time
import threading 

# from pymemcache.client.base import Client
import os
from os import listdir
from flask import request
from flask import Flask
from flask import make_response
from procshot import *
tm = time.gmtime()
if not os.path.exists("images"):
    os.makedirs("images")

# file_name = 'log'+str(tm.tm_year) + '-' + str(tm.tm_mon) + '-' + str(tm.tm_mday) + '_' + str(tm.tm_hour) + '#' + str(tm.tm_min) + '#'+ str(tm.tm_sec)+'.txt'
# logging.basicConfig(level=logging.INFO, filename=file_name,filemode="w",
#                     format="%(asctime)s %(levelname)s %(message)s")

app = Flask(__name__)
# client = Client(('127.0.0.1', 11211))
if os.path.isfile('last_br.txt'):
    fbr = open('last_br.txt', 'r',encoding='utf-8')
     
    b = int(fbr.readlines()[0])
    # client = Client(('127.0.0.1', 11211))
    # client.set('Value', b)
    fbr.close()
else:
    br = 1000
    # client.set('Value', br)
    fbr = open('last_br.txt', 'w')
    fbr.write(str(br))
    fbr.close()

# #print(b)



@app.route('/set_brightness', methods=['GET'])
def set_bright():
    #print("connect")
    params = {}
    for i in request.args:
        params[str(i)] = request.args[i]
    inprm = str(params)
    #print("connect 1" + inprm)
    try:
        br = int(params['brightness'])
        # client = Client(('127.0.0.1', 11211))
        # client.set('Value', br)
        fbr = open('last_br.txt', 'w')
        fbr.write(str(br))
        fbr.close()
        resp = make_response('OK', 200)
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        #print("*** print_tb:")
        traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
        #print("*** format_exc, first and last line:")
        res_data = traceback.format_exc().splitlines()
        #print(res_data)
        resp = make_response(res_data, 400)
    resp.headers['content-type'] = 'text/html'
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    return resp

@app.route('/get_brightness', methods=['GET'])
def get_brightness():
    try:
        # client = Client(('127.0.0.1', 11211))
        # br = client.get('Value')
        resp = make_response(str(br), 200)
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        #print("*** print_tb:")
        traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
        #print("*** format_exc, first and last line:")
        res_data = traceback.format_exc().splitlines()
        #print(res_data)
        resp = make_response(res_data, 400)
    resp.headers['content-type'] = 'text/html'
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    return resp



@app.route('/delete_frames', methods=['GET'])
def del_frames():
    #print('connect')
    try:
        flist = listdir('.')
        for file_name in flist:
            if file_name.endswith('.png'):
                os.remove(file_name)
        resp = make_response('OK', 200)
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        #print("*** print_tb:")
        traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
        #print("*** format_exc, first and last line:")
        res_data = traceback.format_exc().splitlines()
        #print(res_data)
        resp = make_response(res_data, 400)
    resp.headers['content-type'] = 'text/html'
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    return resp


@app.route('/', methods=['GET'])
def get_index():
    try:
        file_name = 'frames_brightness.html' 
        ff = open(file_name, 'r',encoding='utf-8')
        bin = ff.read()
        #print(str(bin))
        # bin = bin.decode('cp1251').encode('utf8')
        resp = make_response(bin, 200)
        #print(bin)
        #print(resp)

    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        #print("*** print_tb:")
        traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
        #print("*** format_exc, first and last line:")
        res_data = traceback.format_exc().splitlines()
        #print(res_data)
        resp = make_response(res_data, 400)
    resp.headers['content-type'] = 'text/html'
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    return resp



# /get_frame?file=shot.png
# <>
@app.route('/get_frame', methods=['GET'])
def get_frame():
    #print("connect get frame")
    params = {}
    for i in request.args:
        params[str(i)] = request.args[i]
    inprm = str(params)
    #print("parm=" + inprm)
    # try:
    file_name = 'MV-A7170MG200_CK60609AAK00003/'+params['file']
    #print('open '+str(file_name))
    ff = open(file_name, 'rb')
    bin = ff.read()
    #print('str(bin)')
    #print(str(bin))
    ff.close()
    resp = make_response(bin, 200)
    # except Exception as e:
    #     exc_type, exc_value, exc_traceback = sys.exc_info()
    #     #print("*** print_tb:")
    #     traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
    #     #print("*** format_exc, first and last line:")
    #     res_data = traceback.format_exc().splitlines()
    #     #print(res_data)
    #     resp = make_response(res_data, 400)
    resp.headers['content-type'] = 'image/png'
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    return resp

def ret_color(mean):
    return (mean// 3, mean// 3,mean// 3 )

@app.route('/get_file', methods=['GET'])
def get_file():
    #print("connect get_file")
    params = {}
    for i in request.args:
        params[str(i)] = request.args[i]
    inprm = str(params)
    #print("connect 1" + inprm)
    try:
        file_name = params['file']
        # ff = open('MV-A7170MG200_CK60609AAK00003/'+file_name, 'r',encoding='utf-8')
        ff = open('MV-A7170MG200_CK60609AAK00003/'+file_name, 'rb')
        bin = ff.read()
        resp = make_response(bin, 200)
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        #print("*** print_tb:")
        traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
        #print("*** format_exc, first and last line:")
        res_data = traceback.format_exc().splitlines()
        #print(res_data)
        resp = make_response(res_data, 400)
    resp.headers['content-type'] = ' text/html; charset=utf-8'
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    return resp

@app.route('/get_oneshot', methods=['GET'])
def get_oneshot():
    #print("connect")
    params = {}
    for i in request.args:
        params[str(i)] = request.args[i]
    inprm = str(params)
    #print("connect 1" + inprm)
    try:
        file_name = params['file']
        shot_src = file_name.split('.')[0]
        file_name = 'one_shot.html'
        ff = open(file_name, 'r',encoding='utf-8')
        bin = ff.read()
        bin = bin%(shot_src)
        resp = make_response(bin, 200)
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        #print("*** print_tb:")
        traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
        #print("*** format_exc, first and last line:")
        res_data = traceback.format_exc().splitlines()
        #print(res_data)
        resp = make_response(res_data, 400)
    resp.headers['content-type'] = ' text/html; charset=utf-8'
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    return resp
# "storage-driver": "/dev/sdb1"

@app.route('/get_all_shots', methods=['GET'])
def get_all_shots():
    #print("connect")
    import subprocess
    process = subprocess.Popen('zip all_arch MV-A7170MG200_CK60609AAK00003/*', shell=True, stdout=subprocess.PIPE)
    process.wait()
    #print(process.returncode)
    file_name = 'all_arch.zip'
    try:
        ff = open(file_name, 'rb')
        bin = ff.read()
        resp = make_response(bin, 200)
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        #print("*** print_tb:")
        traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
        #print("*** format_exc, first and last line:")
        res_data = traceback.format_exc().splitlines()
        #print(res_data)
        resp = make_response(res_data, 400)

    resp.headers['content-type'] = 'application/zip'
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    return resp




@app.route('/get_shot/<file_name>', methods=['GET'])
def get_shot(file_name):
    #print("connect")
    try:
        ff = open('MV-A7170MG200_CK60609AAK00003/'+file_name, 'rb')
        bin = ff.read()
        resp = make_response(bin, 200)
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        #print("*** print_tb:")
        traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
        #print("*** format_exc, first and last line:")
        res_data = traceback.format_exc().splitlines()
        #print(res_data)
        resp = make_response(res_data, 400)
    resp.headers['content-type'] = 'image/png'
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    return resp

@app.route('/get_frames_list', methods=['GET'])
def get_frames_list():
    t1 = time.time()
    try:
        # flist = listdir('./MV-A7170MG200_CK60609AAK00003/')
        flist  = glob.glob('./MV-A7170MG200_CK60609AAK00003/Pic*.txt')

        # print(" Get frame list. all files %s"%(str(flist)))

        rez_arr = []
        rez_arr = flist
        rez_arr.sort(reverse=True)
        rez_arr = rez_arr[0:25]
        for i in range(len(rez_arr)):
            a = rez_arr[i].split('\\')
            rez_arr[i] = a[len(a)-1]
        
        rr = str(rez_arr).replace('\'', '\"')
        resp = make_response(json.dumps(rr), 200)
        print('get_frames_list %s sec'%(str(time.time()-t1)))
    except Exception as e:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        #print("*** print_tb:")
        traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
        #print("*** format_exc, first and last line:")
        res_data = traceback.format_exc().splitlines()
        #print(res_data)
        resp = make_response('{"rc":-1}', 200)
    resp.headers['content-type'] = 'text/html'
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'

    return resp


def process_shots():
    global cycle_run
    print(f"process_shots() {cycle_run}")
    cycle_run = True
    files_ok = []
    cyc = 0
    while 1==1:
        # print(f"cycle start {cyc}")
        cyc +=1
        try:
            a=1
            flist  = glob.glob('./MV-A7170MG200_CK60609AAK00003/*.bmp')
            # flist.sort(reverse=False)
            # print(str(flist[0:2]))
            flist.sort(reverse=True)
            print('!!!!!!for proc '+str(len(flist))+'   '+str(flist[0:10]))
            for i in flist:
                i = i.split('\\')
                i = i[len(i)-1]

                if i[-3:] != 'bmp':
                    continue
                if not i[len(i)-5].isnumeric():
                    continue
                

                if i[1:4] !='ic_':
                        continue
                if i.find('bar') >-1:
                        continue
                if i.find('mark') >-1:
                        continue
                if i in files_ok:
                    continue
                fname ='MV-A7170MG200_CK60609AAK00003/'+ i.split('.')[0]
                if os.path.isfile(fname+'-bar.png') and os.path.isfile(fname+'-barh.png') and  os.path.isfile(fname+'-markup.png') and os.path.isfile(fname+'.txt'):
                    continue
                time0=time.time()
                print(f"{kx},{ky},{xl}, {yu}, {xr}, {yd}, {x_len}, {y_len}, {x_tab}, {y_tab}, {fname}, {w1}, {w2}, {w3},'' ")
                process_shot(kx, ky, xl, yu, xr, yd, x_len, y_len, x_tab, y_tab, fname+'.bmp' , w1, w2, w3,'' )
                # aaa()
                files_ok.append(i)    
                print('processed(%.1f sec) %s'%(time.time()-time0,i))
                break
            time.sleep(0.21)
            # print(f"cycle end {cyc}")

        except Exception as e:
            print(f"cycle end error {cyc}")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            print("*** print_tb:")
            traceback.print_tb(exc_traceback, limit=1, file=sys.stdout)
            #print("*** format_exc, first and last line:")
            res_data = traceback.format_exc().splitlines()
            print(res_data)

# process_shots()
cycle_run = False
pro_shots  = threading.Thread(target=process_shots, args=(),daemon=True)
pro_shots.start()
app.run(debug=True, host="0.0.0.0", port=88)


