# -*- coding: UTF-8 -*-

'''
1、读取指定目录下的所有文件
2、读取指定文件，输出文件内容
3、创建一个文件并保存到指定目录
'''
import os


# 遍历指定目录，显示目录下的所有文件名
def eachJpg(filepath):
    NewList = []
    pathDir = os.listdir(filepath)
    for file in pathDir:
        if('.jpg' in file  or  '.JPEG' in file):
            NewList.append(file)
    return NewList

def eachJpgName(filepath):
    #这里对所有提取出的Jpg文件读取识别结果
    ImgList = eachJpg(filepath)
    NameList = []
    for eachImg in ImgList:
        NameList.append(eachImg[:-7])
    return NameList