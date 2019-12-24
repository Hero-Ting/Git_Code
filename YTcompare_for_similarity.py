# coding:utf-8

import os,threading
import json
import urllib.request
import urllib.parse
import base64

systemip = "http://15.112.20.250:11180"


'''
Connection: keep-alive
Content-Length: 94
Content-Type: text/plain
Host: 15.112.20.250:11180
User-Agent: Apache-HttpClient/4.5.7 (Java/1.8.0_161)
'''

def login_getsession_id():

    headers = {
        "Connection": "keep-alive",
        "Content-Type": "text/plain",
        "Host": "15.112.20.250:11180",
        "User-Agent": "Apache-HttpClient/4.5.7 (Java/1.8.0_161)"
    }
    try:
        personUrl = "{0}/business/api/login".format(systemip)
        # print(personUrl)
        reqdata = {"name":"yttest","password":"08f069d41f78c45bdb174f365888edd7","cluster_id":"YITU_1551608563"}
        data = json.dumps(reqdata).encode("utf-8")
        req=urllib.request.Request(url=personUrl,data=data,headers=headers)
        file = urllib.request.urlopen(req,timeout=1000)
        result = str(file.read(),encoding = "utf-8")
        #print(result)
        retjosn = json.loads(result) ##{"rtn":0,"message":"OK","session_id":"48493110@YITU_1551608563"}
        return retjosn['session_id']
    except Exception as e:
        print(e)
        print("请求/business/api/login失败\t")
        return '',None

def getImageBytes(fname):
    # print('getImageBytes==>>',fname)
    with open(fname, "rb") as rf:  # 转为二进制格式
        base64_data = base64.b64encode(rf.read())  # 使用base64进行加密
        base64_str = base64_data.decode('utf-8', 'ignore')
        imageByte = base64_str
    return imageByte

##
def getfilename_and_path(filepath = None):
    (filepath,tempfilename)=os.path.split(filepath)
    (filename,extension)=os.path.splitext(tempfilename)
    print(filepath,filename)
    return filepath,filename

##访问依图1:1请求地址获取相似度
#http://15.112.20.250:11180/business/api/face/verify
def verify_1to1_facecompare(fname1,fname2):
    try:
        personUrl = "{0}/business/api/face/verify".format(systemip)
        # print(personUrl)
        imageByte1 = getImageBytes(fname1)
        imageByte2 = getImageBytes(fname2)
        reqdata = {"image_base64_1":imageByte1,"image_base64_2":imageByte2}
        data = json.dumps(reqdata).encode("utf-8")
        req=urllib.request.Request(url=personUrl,data=data,headers=headers_sessionid)
        file = urllib.request.urlopen(req,timeout=1000)
        result = str(file.read(),encoding = "utf-8")
        retjosn = json.loads(result) ##{"rtn":0,"message":"OK","similarity":96.99629063904592}
        # print(retjosn)
        return retjosn['similarity']
    except Exception as e:
        print(e,"\t请求/business/api/face/verify失败\t")
        return retjosn['rtn']

###从集匹配好的正负样本集中，读取1:1图片名
def read_pairstxt(testsuitdir):
    dir,filename = getfilename_and_path(testsuitdir)
    similarlist = []
    with open(testsuitdir, encoding="utf-8") as f:
        for line in f.readlines():
            linelist = line.split('    ')
            if len(linelist) == 3:
                picpath1 = os.path.join(dir,os.path.join(linelist[0] ,linelist[1]))
                picpath2 = os.path.join(dir,os.path.join(linelist[0] ,linelist[2]))
                picpath1 = picpath1.replace("\\", "/").strip()
                picpath2 = picpath2.replace("\\", "/").strip()
                similar = verify_1to1_facecompare(picpath1, picpath2)
                similarlist.append(['True',str(similar)])
            elif len(linelist) == 4:
                picpath1 = os.path.join(dir,os.path.join(linelist[0] ,linelist[1]))
                picpath2 = os.path.join(dir,os.path.join(linelist[2] ,linelist[3]))
                picpath1 = picpath1.replace("\\", "/").strip()
                picpath2 = picpath2.replace("\\", "/").strip()
                similar = verify_1to1_facecompare(picpath1, picpath2)
                similarlist.append(['False',str(similar)])
            else:
                print(testsuitdir," pairslist include Error")
                similarlist.append(linelist)
            if len(similarlist) % 10000 == 0:
                print('执行测试集完成进度==>>',len(similarlist))

    with open(filename+"_similarlist.txt",'w') as ret:
        for simil in similarlist:
            ret.write(','.join(simil)+'\n')

    return similarlist

if __name__=="__main__":
    sessionid = login_getsession_id()
    headers_sessionid = {
        "Connection": "keep-alive",
        "Content-Type": "application/json;charset=UTF-8",
        "Host": "15.112.20.250:11180",
        "User-Agent": "Apache-HttpClient/4.5.7 (Java/1.8.0_161)",
        "Cookie": "session_id="+sessionid
        # "Cookie": "yt_cluster_id=YITU_1551608563; session_id=" + sessionid ##也可以
    }
    #pairtxtpath = "D:/FaceCompare_LLB/Data_Face/lfw/pairs_lfw.txt"
    #pairtxtpath = "D:/FaceCompare_LLB/Data_Face/shenzhen_0903_b/pairs_shenzhen_0903_b.txt"
    pairtxtpath = "D:/FaceCompare_LLB/Data_Face/ytf311/pairs_ytf311.txt"
    read_pairstxt(pairtxtpath)
