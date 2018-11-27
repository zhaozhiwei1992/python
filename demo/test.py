# -*- coding: utf-8 -*-
import cv2
##导入cv2模板，这个模块中含有很多图片处理的方法，可以参考https://www.cnblogs.com/shizhengwen/p/8719062.html
  
clicked = False  
def onMouse(event, x, y, flags, param):  
    global clicked  
    if event == cv2.EVENT_LBUTTONUP:  ##点击左键  http://blog.51cto.com/devops2016/2084084
        clicked = True  
  
cameraCapture = cv2.VideoCapture(0)  ##VideoCapture()中参数是0，表示打开笔记本的内置摄像头，参数是视频文件路径则打开视频，如cap = cv2.VideoCapture("../test.avi")
cameraCapture.set(3, 100)  
cameraCapture.set(4, 100) # 帧宽度和帧高度都设置为100像素  
cv2.namedWindow('MyWindow')  
cv2.setMouseCallback('MyWindow', onMouse)  
  
print('showing camera feed. Click window or press and key to stop.')  
success, frame = cameraCapture.read()  
print(success)  
count = 0  
while success and cv2.waitKey(1)==-1 and not clicked:  
    cv2.imshow('MyWindow', cv2.flip(frame,0))  
    success, frame = cameraCapture.read()  
    name = 'images/image'+str(count)+'.jpg'  
    cv2.imwrite(name,frame)  
    count+=1  
cv2.destroyWindow('MyWindow')  
cameraCapture.release()  

##解释全脚本的博客https://blog.csdn.net/m0_37511026/article/details/73159416
