import cv2
from FileOperate import *
from InitMotion import *
import TkGui

SizeRound = (20, 5, 50, 20)
#MaxWeight, MinWeight, MaxHight, MinHight
OrderThresholds = (10, 10)
# XaxisStep, YaxisStep

ClusterTemp = []
#用来保存矩形聚类使用的变量
FinalBox = []
#最终找出的符合条件的矩形

def initImg(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # 转换成灰度图片
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    #blurred = gray
    # 去除噪声(高斯滤波)
    '''
    gradX = cv2.Sobel(gray, ddepth=cv2.CV_32F, dx=1, dy=0)
    gradY = cv2.Sobel(gray, ddepth=cv2.CV_32F, dx=0, dy=1)
    gradient = cv2.subtract(gradX, gradY)
    gradient = cv2.convertScaleAbs(gradient)
    '''
    # 提取图像梯度(不需要)
    (_, thresh) = cv2.threshold(blurred, 90, 255, cv2.THRESH_BINARY)
    # 二值化，这里是函数的详解
    '''
    原型 retval, dst = cv.threshold( src, thresh, maxval, type[, dst] ) 
    函数功能： 去掉噪，例如过滤很小或很大像素值的图像点。
    src：原图像。
    dst：结果图像。
    retval, thresh：当前阈值.
    maxVal：最大阈值，一般为255.
    '''
    mean = sum(cv2.mean(thresh))
    # 计算均值用于判断图片是白底还是黑底
    #print(mean)
    if mean < 90:
        thresh = ~thresh
    # 如果是黑底则反相，这一步要求所有图片都是白底黑字
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    # 可以修改卷积核大小来增加腐蚀效果，越大腐蚀越强
    thresh = cv2.erode(thresh, kernel)
    return thresh

def mat_inter(box1, box2):
    # 判断两个矩形是否相交
    # box=(xA,yA,xB,yB)
    x01, y01, w0, h0 = box1
    x11, y11, w1, h1 = box2
    x02 = x01 + w0
    y02 = y01 + h0
    x12 = x11 + w1
    y12 = y11 + h1
    if(x11>x02 or x12<x01 or y11>y02 or y12<y01):
        return False
    else:
        return True

def DelLapped(boxes):
    delist = []
    # 重叠的矩形列表
    for boxa in boxes:
        for boxb in boxes:
            if boxa == boxb:
                continue
            if (mat_inter(boxa, boxb)):
                delist.append(boxa)
    ret_list = [item for item in boxes if item not in delist]
    # 不重叠的方框列表
    return ret_list

def DelWrongSize(Boxes, SizeRoundIN):
    #去掉大小不合适的矩形，以及高大于宽的矩形(字母不会是扁的)
    MaxW = SizeRoundIN[0]
    MinW = SizeRoundIN[1]
    MaxH = SizeRoundIN[2]
    MinH = SizeRoundIN[3]
    NewList = Boxes.copy()
    for box in range(len(Boxes)):
        x, y, w, h = Boxes[box]
        if(w>MaxW or h>MaxH or w<MinW or h<MinH or w>h):
            if(Boxes[box] in NewList):
                NewList.remove(Boxes[box])
    return NewList

def IsXsegmentation(box1, box2, Thresholds):
    x1, y1, w1, h1 = box1
    x2, y2, w2, h2 = box2
    if(box1==box2):
        return False
    # 如果是同一个矩形则不予考虑
    if( abs(y1-y2) < Thresholds[1] ):
        if( abs((x1+w1)-x2) < Thresholds[0] ):
            return True
    # 先判断横向高度是否满足，再判断左侧间距是否满足
    return False

def IsYsegmentation(box1, box2, Thresholds):
    x1, y1, w1, h1 = box1
    x2, y2, w2, h2 = box2
    if (box1 == box2):
        return False
    #如果是同一个矩形则不予考虑
    if( abs(x1-x2) < Thresholds[0] ):
        if( abs((y1+h1)-y2) < Thresholds[1] ):
            return True
    # 先判断纵向宽度是否满足，再判断下侧间距是否满足
    return False

def FindOrderedBox(box, Boxes, Thresholds):
    global ClusterTemp,FinalBox
    #从Boxes中找出与box相邻的box2，将聚类信息存放在全局变量ClusterTemp中
    for box2 in Boxes:
        if(IsXsegmentation(box, box2, Thresholds)):
            ClusterTemp.append(box)
            FindOrderedBox(box2, Boxes, Thresholds)
            break
    if(len(ClusterTemp)==4 or len(ClusterTemp) == 6):
        #符合条件的排列集合
        FinalBox += ClusterTemp
    ClusterTemp = []

def gogogo(Boxes, Thresholds):
    for bbb in Boxes:
        FindOrderedBox(bbb, Boxes, Thresholds)

if __name__ == "__main__":
    gui = TkGui.initGUI('集装箱')
    #GUI初始化
    TkGui.PutText(gui, '程序初始化中')
    ShowProgress('程序初始化中', 100)
    img_path = r'1.jpg'
    ImgDirPath = './data/'
    ImgNameList = eachJpgName(ImgDirPath)#识别结果集
    ImgNameRawNameList = eachJpg(ImgDirPath)
    TkGui.PutText(gui, '加载目录中')
    ShowProgress('加载目录中', 100)
    TkGui.PutText(gui, '加载模型中')
    ShowProgress('加载模型中', 500)
    for ImgRawName in ImgNameRawNameList:
        #对所有图片进行识别
        img_path = r'./data/'+ImgRawName
        img = cv2.imread(img_path)
        # 测试用的图片路径，使用cv读取图片
        TkGui.PutPic(gui, img_path)
        UniType = initImg(img)
        # 初始化图片(去噪二值化等)
        mser = cv2.MSER_create(_min_area=100, _max_area=700,)
        regions, boxes = mser.detectRegions(UniType)
        boxes = boxes.tolist()
        #使用MSER算法找出焦点区域，后面两个参数限定方框大小范围
        '''for box in boxes:
            x, y, w, h = box
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)'''
        #在原图中画出所有的框框
        ret_list = DelLapped(boxes)
        #去除重叠的矩形
        ret_list = DelWrongSize(ret_list, SizeRound)
        #去掉大小和形状不合适的矩形
        #gogogo(ret_list, OrderThresholds)

        '''
        finallist = []
        for box in ret_list:
            BlockAccount = len(clusterCount(box, boxes, 10, 'X'))
            if(BlockAccount == 4 or BlockAccount == 6):
                finallist+=clusterCount(box, boxes, 10, 'X')
        '''
        for box in ret_list:
            x, y, w, h = box
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        #将不重叠的矩形画出来
        #cv2.imshow("hhh",UniType)
        #cv2.imshow("DEMO  20190529", img)

        for result in ImgNameList:
            if(result in img_path):
                print("集装箱", result, "已进场！")
                result = result+' IN!'
                TkGui.PutText(gui, result)
                break
        #打印集装箱进场信息
        cv2.waitKey(2000)

