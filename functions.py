import time
import opc
import cv2
import numpy as np
import pandas as pd

width = int(1920*2/3)
height = int(1080*2/3)

class LoveBug():
    def __init__(self, fullShell=False):
        #open fadecandy client connection
        self.client = opc.Client('localhost:7890')
        
        #load video files
        self.vidcap = cv2.VideoCapture('../Movies/free-loops_Color_Heart_Pop_Up_H264.mp4')
        self.vidcapBack = cv2.VideoCapture('../Movies/free-loops_Valentine_Heart_Outline_Chromatic_H264.mp4')

        #load strip lens
        self.shellStripLens = np.loadtxt("./ShellStripLens.csv",delimiter=',').astype(int)

        #load 2d point mapping
        self.shellPoints2d = np.loadtxt("./LED2DPoints.csv",delimiter=',').astype(int)
        self.shellPpoints2d2 = np.loadtxt("./LED2DPoints2.csv",delimiter=',').astype(int)
        self.backflap2d = np.loadtxt("./BackFlap2D.csv",delimiter=',').astype(int)
        self.fullShell = fullShell
            
    def getVideoFrame(self):
        success,image = self.vidcap.read()    
        if (not success):
            self.vidcap.set(1, 0) #loop back to beginning
            success,image = self.vidcap.read()
            
        successback,imageback = self.vidcapBack.read()    
        if (not successback):
            self.vidcapBack.set(1, 0) #loop back to beginning
            successback,imageback = self.vidcapBack.read()
            
        image = np.flip(cv2.resize(image,(width,height)),axis=2)
        imageback = np.flip(cv2.resize(imageback,(width,height)),axis=2)
        
        shell1Colors = image.reshape([height*width,3])[self.shellPoints2d]
        shell2Colors = image.reshape([height*width,3])[self.shellPpoints2d2]
        backflapColors = imageback.reshape([height*width,3])[self.backflap2d]
        
        if(self.fullShell):
            return np.concatenate((shell1Colors, shell2Colors, backflapColors))
        else:
            return np.concatenate((shell1Colors, backflapColors))
        
    def get3DPoints(self):
        shellPoints = np.loadtxt("./LEDPoints.csv",delimiter=',')
        backflapPoints = np.loadtxt("./BackFlap.csv",delimiter=',')
        
        if(self.fullShell):
            return np.concatenate((shellPoints,backflapPoints))
        else:
            return np.concatenate((shellPoints[:len(self.shellPoints2d)],backflapPoints))
    
    def test8(self):
        print('loading colors')
        white = [(255,255,255)]
        blue = [(0,0,255)]
        green = [(0,255,0)]
        yellow = [(255,255,0)]
        orange = [(255,165,0)]
        red = [(255,0,0)]
        purple = [(255,0,255)]
        brown = [(255,126,35)]
        black = [(0,0,0)]
        gray = [(125,125,125)]
        
        print('building pixels')
        num = 10
        colors = black*512*(num-1) + (white*64 + blue*64 + green*64 + yellow*64 + orange*64 + red*64 + purple*64 + gray*64) + black*512*(10-num)
#        print(colors)
#        colors = red*5120
        
        print('clearing pixels')
        time.sleep(1)
        self.client.put_pixels(black*5120)
        time.sleep(1)
        self.client.put_pixels(colors)
        
#        def rotate(l, n):
#            return l[-n:] + l[:-n]
#        
#        print('sending and rotating pixels')
#        i=0;
#        while True:
#            time.sleep(1/60)
#            self.client.put_pixels(colors)#rotate(colors,i%512*0))
#            i+=1

if __name__ == '__main__':
    lb = LoveBug()
    lb.test8()