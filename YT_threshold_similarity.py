#!/usr/bin/python
# -*- coding: utf-8 -*- 
# @Time   : 2019/12/19 15:31 
# @Author : limbor.liu
# @File   : YT_threshold.py 
# @Product:PyCharm
#
import os,sys
import numpy as np
import time
import  random
from datetime import datetime
from xlwt import Workbook
from functools import partial

def getsimilar_fromtxt(filedir):
    similarity = []
    rejection = 0
    with open(filedir) as f:
        similarlist = f.readlines()
        Truenum = len(similarlist) // 3
        Falsenum = len(similarlist) * 2 // 3
        for similar in similarlist:
            actual_issame = similar.strip().split(',')
            if actual_issame[1] != "-10302":  ##接口请求拒识的返回码
                similarity.append(float(actual_issame[1]))
            else:
                if actual_issame[0] == 'True':
                    Truenum-=1
                if actual_issame[0] == 'False':
                    Falsenum-=1
                rejection+=1
    actual_issame = []
    for x in range(0, Truenum):
        actual_issame.append(True)
    for x in range(0, Falsenum):
        actual_issame.append(False)
    print('系统拒检测 Rejection Rate: ',rejection/len(similarity), Truenum, Falsenum)
    return  actual_issame, similarity, Truenum, Falsenum

##
def calculate_accuracy(threshold, actual_issameList, distList):
    ##注意：此处需要根据接口返回相似度的评判标准进行选择，依图用np.greater，欧式距离则用np.less
    # predict_issame = np.less(distList, threshold)  #反余弦/pi 表示 distList,与相似度相反，比小为相似，KC用
    predict_issame = np.greater(distList, threshold)  #直接用余弦距离表示distList,可看作相似度，比大为相似，依图用
    tp = np.sum(np.logical_and(predict_issame, actual_issameList))
    fp = np.sum(np.logical_and(predict_issame, np.logical_not(actual_issameList)))
    tn = np.sum(np.logical_and(np.logical_not(predict_issame), np.logical_not(actual_issameList)))
    fn = np.sum(np.logical_and(np.logical_not(predict_issame), actual_issameList))

    tpr = 0 if (tp + fn == 0) else float(tp) / float(tp + fn)  ##所有正类中，有多少被预测成正类（正类预测正确）
    recall = tpr
    fpr = 0 if (fp + tn == 0) else float(fp) / float(fp + tn) ##所有反类中，有多少被预测成正类（正类预测错误）；类间总数为分母，来计算误识率
    acc = float(tp + tn) / len(distList)  ##准确率
    precision =  0 if (tp + fp == 0) else float(tp) / float(tp + fp)  ##精准率

    tnr =  0 if (tn + fp == 0) else float(tn) / float(tn + fp) ##反类预测正确：错的识别成错的
    fnr =  0 if (tp + fn == 0) else float(fn) / float(tp + fn) ##反类预测错误：对的识别成错的
    fnmr = 1 - tpr

    return recall, precision, acc, tnr, fpr,fnr,tpr,fnmr

def dislist_threshold(actual_issamelis,distlist,Pnum, Nnum, model_name,testsuite,cosin_oushi ='similarity'):
    to = time.time()
    if cosin_oushi.find('similarity')> 0 :
        thresholds = np.arange(0.01, 1.01, 0.01)
    elif cosin_oushi.find('oushi')> 0 :
        thresholds = np.arange(0.01, 3.21, 0.01)
    else:
        thresholds = np.arange(0.01, 1.01, 0.01)

    file_name = model_name + '_' + testsuite + cosin_oushi  ## 模型+测试集命名
    book = Workbook(encoding='utf-8')
    sheet1 = book.add_sheet('sheet1',cell_overwrite_ok=True)
    ## 表示将[x:x+m]行[y:y+n]列的矩阵合并成一个单元格。存放第五个参数的内容，同理，style参数可以不传参
    sheet1.write_merge(0, 0, 0, 4, '测试日期:' + now)
    sheet1.write_merge(0, 0, 5, 8, '测试模型:' + model_name)
    sheet1.write_merge(1, 1, 0, 4, '测试数据:' + testsuite+' 本模型提取特征数%s'%picNum)
    sheet1.write_merge(1, 1, 5, 8, '相似距离 '+ cosin_oushi)
    sheet1.write_merge(2, 2, 0, 4, '正测试单元数量:' + str(Pnum))
    sheet1.write_merge(2, 2, 5, 8, '负测试单元数量:' + str(Nnum))

    #准确率(accuracy) =(TP+TN)/(TP+FN+FP+TN)
    title_col = ['threshold', 'recall','precision','acc','tnr','fpr','fnr','tpr','fnmr']
    for ti in range(len(title_col)):
        sheet1.write(3, ti, title_col[ti])
    row = 4
    for threshold in thresholds:
        result_accuracy = calculate_accuracy(threshold*100,actual_issamelis, distlist)
        res_accuracy = list(map(myRound,result_accuracy))
        ##写入xls
        res_accuracy.insert(0,threshold)
        for col in range(len(res_accuracy)):
            sheet1.write(row, col , res_accuracy[col])
        row+=1
    book.save('./' + file_name+ now + '.xls')
    print(time.strftime('[%H:%M:%S]'),'本次调用 dislist_threshold %s 运行耗时耗时(秒)==>> %f' % (cosin_oushi,time.time() - to))

if __name__=='__main__':
    model_name = 'YiTu上海'
    now = datetime.strftime(datetime.now(),'%Y-%m-%d-%H-%M-%S')
    print(now,datetime.now())
    myRound = partial(round,ndigits=9)
    root = './'
    for dirpath, dirname,filenames  in os.walk(root):
        for file in filenames:
            if 'similarlist' in file:
                testsuite = file.split('_')[1]
                if testsuite.find('MegaFace') > -1:
                    picNum = 1002
                elif testsuite.find('lfw') > -1:
                    picNum = 13233
                elif testsuite.find('shenzhen') > -1:
                    picNum = 30346
                elif testsuite.find('ytf') > -1:
                    picNum = 32504
                else:
                    picNum = 'NotSure'
                print(testsuite,picNum)
                actual_issamelis, cosdistlis, Pnum, Nnum= getdistance_fromnpy = getsimilar_fromtxt(file)
                dislist_threshold(actual_issamelis, cosdistlis, Pnum, Nnum, model_name, testsuite, 'similarity')









