# -*- coding: utf-8 -*- 
# @Time : 2019/7/22 16:12 
# @Author : limbor.liu
# @File : sense_pairs.py 
# @Software: PyCharm
import numpy as np
import sys, os
import time ,psutil, gc
from collections import  Counter
from itertools import combinations
import  random
from scipy.special import comb ,perm

def sense_count_pairs(persons, label_ix, multiple = 2):
    count = Counter(persons)
    ####正样本
    pairs_txt = []
    pairslistT = []
    for t in count:
        num = 0
        person = []
        for labelix in label_ix:
            label = labelix[0]
            # ix = labelix.split('+')[1]
            if  t == label:
                person.append(labelix)
                num+=1
            if num == count[t]:
                break
        pairsT = list(combinations(person,2))
        pairslistT.extend(pairsT)
    # print(type(pairslistT),len(pairslistT), pairslistT)
    ####负样本
    pairslistF = []
    for t in count:
        personT = []
        personF = []
        combnum = int(comb(count[t],2))*multiple
        if combnum == 0 :
            continue
        for labelix in label_ix:
            label = labelix[0]
            # ix = labelix.split('+')[1]
            if  t == label:
                personT.append(labelix)
            else:
                personF.append(labelix)
        pairsF = []
        for personme in personT:
            for i in range(combnum):
                personanother = random.choice(personF)
                pairsF.append((personme, personanother))
        pairsF = random.sample(pairsF,combnum)
        pairslistF.extend(pairsF)
    # print(len(pairslistT),len(pairslistF))
    pairslist = pairslistT + pairslistF
    return  pairslistT, pairslistF

def pairs_to_file(dir, pairsT, pairsF):
    testsuit = os.path.split(dir)[1]
    # print(testsuit)
    pairsfile = open( './' + 'sensetime_pairs_' + testsuit + '.txt', 'w')
    # for pairs in pairsT:
    #     if pairs[0][0] == pairs[1][0]:
    #         pairsfile.write(pairs[0][0] + '    ' + pairs[0][1] + '    ' + pairs[1][1] + '\n')
    #     elif pairs[0][0] != pairs[1][0]:
    #         pairsfile.write(pairs[0][0] + '    ' + pairs[0][1] + '    ' + pairs[1][0] + '    ' + pairs[1][1] + '\n')
    #     else:
    #         print(" CHECK ERROR")
    for pairs in pairsT:
        pairsfile.write(pairs[0][0] + '    ' + pairs[0][1] + '    ' + pairs[1][1] + '\n')
    for pairs in pairsF:
        pairsfile.write(pairs[0][0] + '    ' + pairs[0][1] + '    ' + pairs[1][0] + '    ' + pairs[1][1] + '\n')
    pairsfile.close()
    print(time.strftime('[%H:%M:%S]'),'样本配对写入txt结束 run pairs_to_file over ！')


def sense_get_lables(path_in):
    # output_dir = os.path.expanduser(args.output_dir)
    # if not os.path.exists(output_dir):
    #     os.makedirs(output_dir)
    # if (args.mode == 'pairs'):
    #     pass
    print(time.strftime('[%H:%M:%S]') +'测试集路径==>>' +  path_in)  # LLBadd
    imagesFileName = path_in
    personFileName = os.listdir(imagesFileName)  ##LLBadd获取人名文件夹列表
    persons = []
    images = []
    for person in personFileName:
        personDir = imagesFileName + '/' + person  ##LLBadd
        imagesList = os.listdir(personDir)
        for image in imagesList:
            persons.append(person)
            images.append([person,image])
    pairs = sense_count_pairs(persons, images)
    pairsT ,pairsF = pairs
    print(time.strftime('[%H:%M:%S]') + '求取pairs结束，开始写入txt,正负样本数 ==>> %s %s  '%(len(pairsT),len(pairsF)))  # LLBadd
    pairs_to_file(path_in,pairsT,pairsF)
    # return persons, images

def parse_arguments(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_dir', default='D:/Faces_DataSet/ShangTangPic/lfw', type=str,
                        help='Directory with unaligned images.')
    parser.add_argument('--output_dir', default='D:/Faces_DataSet/ShangTangPairs/lfw', type=str,
                        help='Directory with aligned face thumbnails.')
    parser.add_argument('--mode', default='pairs', type=str, help='gen_pairs.')
    return parser.parse_args(argv)

if __name__ == '__main__':
    # pares = parse_arguments(sys.argv[1:])
    # print(pares)
    # dir_pic = "D:/py_ModelCompare/test_picture/Model_comparison/shenzhen_out_image1"
    dir_pic  = "D:/Faces_DataSet/ShangTangPic/stpictest" #D:\Faces_DataSet\ShangTangPic\MegaFace
    dir_pic = "D:\CodePython\py_ModelCompare\\test_picture\MegaFace_dataset001_082"
    sense_get_lables(dir_pic)