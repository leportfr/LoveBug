import time
import opc
import cv2
import numpy as np
from numba import jit 
from recorder import InputRecorder

width = int(640)
height = int(360)

@jit(nopython=True)
def heartmanip(image, newimage, count, countnum):
    for rownum in range(len(image)):
        pixelnum = 0
        for pixelnum in range(len(image[rownum])):
            pixel = image[rownum,pixelnum]
            amt2 = 0.1*np.sin(3.14159*count/countnum*4)*np.sin(100*(3.14159*((pixelnum+10*rownum)%len(image[rownum])))/len(image[rownum]))
            amt = 0.2 + amt2
            newimage[rownum,pixelnum] = ([pixel[2],0,int(amt*255-(pixel[2]))] if pixel[0]+pixel[2] < 255*amt else [pixel[2],0,pixel[0]])
#        print([pixel[2],int(255*amt2) if int(255*amt2) > 0 else 0,int(amt*255-(pixel[2]))])

class LoveBug():
    def __init__(self, fullShell=False, framerate=15):
        #open fadecandy client connection
        self.client = opc.Client('localhost:7890')
        
        #load default video files
        self.framerate = framerate
        self.reactframerate = 1000
        self.show = 'Hearts'
        self.switch = 0
        self.loadVideoFile()
        self.video = True
        self.z = 0
        
        #load audio recorder
        self.input_recorder = InputRecorder()

        #load strip lens
        self.stripLens = np.loadtxt("./StripLens.csv",delimiter=',').astype(int)

        #load 2d point mapping
        self.shellPoints2d = np.loadtxt("./LED2DPoints.csv",delimiter=',').astype(int)
        self.shellPpoints2d2 = np.loadtxt("./LED2DPoints2.csv",delimiter=',').astype(int)
        self.backflap2d = np.loadtxt("./BackFlap2D.csv",delimiter=',').astype(int)
        self.snout2d = np.loadtxt("./Snout2D.csv",delimiter=',').astype(int)
        self.fullShell = fullShell
        
    def loadVideoFile(self):
        if self.show == 'Hearts':
            self.vidcap = cv2.VideoCapture('../Movies_reduced/free-loops_Color_Heart_Pop_Up_H264_reduce.mpeg')
            self.vidcapBack = cv2.VideoCapture('../Movies_reduced/free-loops_Color_Heart_Pop_Up_H264_reduce2.mpeg')
            self.vidcapSnout = cv2.VideoCapture('../Movies_reduced/free-loops_Color_Heart_Pop_Up_H264_reduce2.mpeg')
            self.video = True
        elif self.show == 'Fire':
            self.vidcap = cv2.VideoCapture('../Movies_reduced/free-loops_Fire_3_reduce.mpeg')
            self.vidcapBack = cv2.VideoCapture('../Movies_reduced/free-loops_Fire_3_reduce.mpeg')
            self.vidcapSnout = cv2.VideoCapture('../Movies_reduced/free-loops_Fire_3_reduce.mpeg')
            self.video = True
        elif self.show == 'Mandel':
            self.vidcap = cv2.VideoCapture('../Movies_reduced/mandelzoom2_reduce.mpeg')
            self.vidcapBack = cv2.VideoCapture('../Movies_reduced/mandelzoom2_reduce.mpeg')
            self.vidcapSnout = cv2.VideoCapture('../Movies_reduced/mandelzoom2_reduce.mpeg')
            self.video = True
        elif self.show == 'Triangles':
            self.vidcap = cv2.VideoCapture('../Movies_reduced/free-loops_Triangles_Motion_Background_2_reduce.mpeg')
            self.vidcapBack = cv2.VideoCapture('../Movies_reduced/free-loops_Triangles_Motion_Background_2_reduce.mpeg')
            self.vidcapSnout = cv2.VideoCapture('../Movies_reduced/free-loops_Triangles_Motion_Background_2_reduce.mpeg')
            self.video = True
        elif self.show == 'Pineapples':
            self.vidcap = cv2.VideoCapture('../Movies_reduced/free-loops_Pineapples_Dancing_reduce.mpeg')
            self.vidcapBack = cv2.VideoCapture('../Movies_reduced/free-loops_Pineapples_Dancing_reduce.mpeg')
            self.vidcapSnout = cv2.VideoCapture('../Movies_reduced/free-loops_Pineapples_Dancing_reduce.mpeg')
            self.video = True
        elif self.show == 'Fast Rainbow':
            self.vidcap = cv2.VideoCapture('../Movies_reduced/free-loops_Rainbow_Fishes_Kaleida_2_H264_reduce.mpeg')
            self.vidcapBack = cv2.VideoCapture('../Movies_reduced/free-loops_Rainbow_Fishes_Kaleida_2_H264_reduce.mpeg')
            self.vidcapSnout = cv2.VideoCapture('../Movies_reduced/free-loops_Rainbow_Fishes_Kaleida_2_H264_reduce.mpeg')
            self.video = True
        elif self.show == 'Reactive Spots':
            self.video = False
             
    def sendVideoFrame(self, shell1Colors, shell2Colors, backflapColors, snoutColors, framerate=15):
        colors = np.zeros((5120,3))
        
        ledcount = 0
        for i,strip in enumerate(self.stripLens):
            if i<32:
                colors[i*64:i*64 + strip] = shell1Colors[ledcount:ledcount+strip]
            elif i<64:
                if i == 32: ledcount=0
                colors[i*64:i*64 + strip] = shell2Colors[ledcount:ledcount+strip]
            elif i<70:
                if i == 64: ledcount=0
                colors[i*64:i*64 + strip] = backflapColors[ledcount:ledcount+strip]
            else:
                if i == 70: ledcount=0
                colors[i*64:i*64 + strip] = snoutColors[ledcount:ledcount+strip]
            
            ledcount = ledcount + strip
        
        time.sleep(1/framerate)
        self.client.put_pixels(colors)
            
    def getVideoFrame(self, show):
        #if show choice changes, fade out over the next second, then fade into the new show over the following second
        if show != self.show:
            self.switch = self.framerate*2
            self.show = show
            
        if self.switch > 0:
            self.switch = self.switch - 1
        
        if self.switch == self.framerate:
            self.loadVideoFile()
        
        image = None
        
        #loop the shows
        if self.video:
            success,image = self.vidcap.read()    
            if (not success):
                self.loadVideoFile() #loop back to beginning
                success,image = self.vidcap.read()
                
            successBack,imageBack = self.vidcapBack.read()    
            if (not successBack):
                self.loadVideoFile() #loop back to beginning
                successback,imageBack = self.vidcapBack.read()
                
            successSnout,imageSnout = self.vidcapSnout.read()    
            if (not successSnout):
                self.loadVideoFile() #loop back to beginning
                successSnout,imageSnout = self.vidcapSnout.read()
                
            sendframerate = self.framerate
        else:
            self.input_recorder.record_once()
            xs, ys = self.input_recorder.fft()
            bassmax = np.max(ys[:4])
            totmax = np.sum(ys)/len(ys)
            zmax = 2*bassmax/totmax
            self.z = self.z - 1 if self.z > 0 else 0
            self.z = (np.amax((np.clip(zmax,0,30), self.z)) if totmax > 0 else 0) if zmax - 15 > self.z else self.z
            print(zmax, round(self.z))
            image = cv2.imread("/Users/leportfr/Desktop/Lovebug/LEDs/Movies_reduced/ladybug spots/ladybug" + str(int(round(self.z))) + ".jpg")
            image = cv2.resize(image,(width,height))
            imageBack = cv2.imread("/Users/leportfr/Desktop/Lovebug/LEDs/Movies_reduced/ladybug spots/ladybug" + str(int(round(self.z))) + ".jpg")
            imageBack = cv2.resize(imageBack,(width,height))
            imageSnout= cv2.imread("/Users/leportfr/Desktop/Lovebug/LEDs/Movies_reduced/ladybug spots/ladybug" + str(int(round(self.z))) + ".jpg")
            imageSnout = cv2.resize(imageSnout,(width,height))
            
            sendframerate = self.reactframerate
        
        #flip and resize images
        image = np.flip(image,axis=2)
        imageBack = np.flip(imageBack,axis=2)
        imageSnout = np.flip(imageSnout,axis=2)
        
        shell1Colors = image.reshape([height*width,3])[self.shellPoints2d]
        shell2Colors = image.reshape([height*width,3])[self.shellPpoints2d2]
        backflapColors = imageBack.reshape([height*width,3])[self.backflap2d]
        snoutColors = imageSnout.reshape([height*width,3])[self.snout2d]
        
        #send color values to LEDs
        self.sendVideoFrame(shell1Colors, shell2Colors, backflapColors, snoutColors, framerate=sendframerate)
        
        #send color values to simulator
        if(self.fullShell):
            return np.concatenate((shell1Colors, shell2Colors, backflapColors, snoutColors))*abs(self.switch/self.framerate - 1)
        else:
            return np.concatenate((shell1Colors, backflapColors, snoutColors))*abs(self.switch/self.framerate - 1)
        
    def get3DPoints(self):
        shellPoints = np.loadtxt("./LEDPoints.csv",delimiter=',')
        backflapPoints = np.loadtxt("./BackFlap.csv",delimiter=',')
        snoutPoints = np.loadtxt("./Snout.csv",delimiter=',')
        
        if(self.fullShell):
            return np.concatenate((shellPoints,backflapPoints,snoutPoints))
        else:
            return np.concatenate((shellPoints[:len(self.shellPoints2d)],backflapPoints,snoutPoints))
    
    def test8(self):
        print('loading colors')
        white = [(255,255,255)]
        blue = [(0,0,255)]
        green = [(0,255,0)]
        yellow = [(255,255,0)]
        orange = [(255,165,0)]
        red = [(255,0,0)]
        purple = [(255,0,255)]
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
        
    def reduceVideoFile(self, file):
        vidcap = cv2.VideoCapture('../Movies/' + file + '.mp4')
        vw = cv2.VideoWriter('../Movies_reduced/' + file + '_reduce.mpeg',0,cv2.VideoWriter_fourcc(*'MPEG'),30,(width,height))
    
        success,image = vidcap.read()  
        while success:
            image = np.array(image*0.75, dtype=np.uint8)
            vw.write(cv2.resize(image,(width,height)))
            vw.write(cv2.resize(image,(width,height)))
            success,image = vidcap.read()       
        
    def createHearts(self):
        file = 'free-loops_Color_Heart_Pop_Up_H264'
        
        vidcap = cv2.VideoCapture('../Movies/' + file + '.mp4')
        vw = cv2.VideoWriter('../Movies_reduced/' + file + '_reduce.mpeg',0,cv2.VideoWriter_fourcc(*'MPEG'),30,(width,height))
    
        success,image = vidcap.read()    
        counter = 0
        
        while success:
            if True:
                print(counter)
                
                wzoom = 1920
                hzoom = 1080
                image = cv2.resize(image,(width,height))
                newimage = np.zeros_like(image, dtype=np.uint8)
                
                heartmanip(image, newimage, counter, 480)
                
                vw.write(newimage)
            success,image = vidcap.read()
            counter = counter+1
        
        vidcap = cv2.VideoCapture('../Movies/' + file + '.mp4')
        vw = cv2.VideoWriter('../Movies_reduced/' + file + '_reduce2.mpeg',0,cv2.VideoWriter_fourcc(*'MPEG'),30,(width,height))
    
        success,image = vidcap.read()    
        counter = 0
        
        loopcount = 0
        while success:
            if (counter > 2*30 and counter < 6*30) or (counter > 10*30 and counter < 14*30):
                print(counter)
                
                wzoom = int((1920-width)/2*1.2)
                hzoom = int((1080-height)/2*1.2)
                newimage = np.zeros((hzoom,wzoom,3), dtype=np.uint8)
                
                heartmanip(image[:hzoom,:wzoom], newimage, loopcount, 480)
                
                vw.write(cv2.resize(newimage,(width,height)))
            success,image = vidcap.read()
            counter = counter+1
            loopcount = loopcount+1
            
if __name__ == '__main__':
    lb = LoveBug()
    
    lb.reduceVideoFile('free-loops_Rainbow_Fishes_Kaleida_2_H264')
#    lb.createHearts()