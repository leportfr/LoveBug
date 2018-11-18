import time
import opc
import cv2
import numpy as np
from numba import jit 

width = int(640)
height = int(360)

#@jit(nopython=True)
def heartmanip(image, newimage, count, countnum):
    for rownum in range(len(image)):
        pixelnum = 0
        for pixelnum in range(len(image[rownum])):
            pixel = image[rownum,pixelnum]
            amt2 = 0.1*np.sin(3.14159*count/countnum*4)*np.sin(100*(3.14159*((pixelnum+10*rownum)%len(image[rownum])))/len(image[rownum]))
            amt = 0.2 + amt2
            newimage[rownum,pixelnum] = ([pixel[2],0,int(amt*255-(pixel[2]))] if pixel[0]+pixel[2] < 255*amt else [pixel[2],0,pixel[0]])
#        print([pixel[2],int(255*amt2) if int(255*amt2) > 0 else 0,int(amt*255-(pixel[2]))])

#@jit(nopython=True)
def buildColors(shell1Colors, shell2Colors, backflapColors, snoutColors, stripLens):
    ledcount = 0   
    colors = np.zeros((5120,3))
    
    for i,strip in enumerate(stripLens):
        if i<32:
            colors[i*64:i*64 + strip] = shell1Colors[ledcount:ledcount+strip]
        elif 32<=i<64:
            if i == 32: ledcount=0
            colors[i*64:i*64 + strip] = shell2Colors[ledcount:ledcount+strip]
        elif 64<=i<69:
            if i == 64: ledcount=0
            colors[i*64:i*64 + strip] = snoutColors[ledcount:ledcount+strip]
        elif 72<=i:
            if i == 72: ledcount=0
            colors[i*64:i*64 + strip] = backflapColors[ledcount:ledcount+strip]
        
        
        ledcount = ledcount + strip
        
    return colors

class LoveBug():
    def __init__(self, input_recorder=None, fullShell=False, framerate=15, path='../'):
        #set path
        self.path = path
        
        #open fadecandy client connection
        self.client = opc.Client('localhost:7890')
        
        #load default video files
        self.framerate = framerate
        self.reactframerate = 1000
        self.show = 'Hearts'
        self.switch = 0
        self.loadVideoFile(shell=True, back=True, snout=True)
        self.video = True
        self.z = 0
        self.totmax = 0
        
        #load audio recorder
        self.input_recorder = input_recorder

        #load strip lens
        self.stripLens = np.loadtxt(self.path+"LoveBug/StripLens.csv",delimiter=',').astype(int)

        #load 2d point mapping
        self.shellPoints2d = np.loadtxt(self.path+"LoveBug/LED2DPoints.csv",delimiter=',').astype(int)
        self.shellPoints2d2 = np.loadtxt(self.path+"LoveBug/LED2DPoints2.csv",delimiter=',').astype(int)
        self.backflap2d = np.loadtxt(self.path+"LoveBug/BackFlap2D.csv",delimiter=',').astype(int)
        self.snout2d = np.loadtxt(self.path+"LoveBug/Snout2D.csv",delimiter=',').astype(int)
        self.fullShell = fullShell
        
        #create color matrix for sending to LEDs
#        self.colors = np.zeros((5120,3))
        
    def loadVideoFile(self, shell=False, back=False, snout=False):
        if self.show == 'Hearts':
            if shell: self.vidcap = cv2.VideoCapture(self.path+'Movies_reduced/free-loops_Color_Heart_Pop_Up_H264_reduce.mpeg')
            if back: self.vidcapBack = cv2.VideoCapture(self.path+'Movies_reduced/free-loops_Color_Heart_Pop_Up_H264_reduce2.mpeg')
            if snout: self.vidcapSnout = cv2.VideoCapture(self.path+'Movies_reduced/free-loops_Color_Heart_Pop_Up_H264_reduce2.mpeg')
            self.video = True
        elif self.show == 'Fire':
            if shell: self.vidcap = cv2.VideoCapture(self.path+'Movies_reduced/free-loops_Fire_3_reduce.mpeg')
            if back: self.vidcapBack = cv2.VideoCapture(self.path+'Movies_reduced/free-loops_Fire_3_reduce.mpeg')
            if snout: self.vidcapSnout = cv2.VideoCapture(self.path+'Movies_reduced/free-loops_Fire_3_reduce.mpeg')
            self.video = True
        elif self.show == 'Bigger Fire':
            if shell: self.vidcap = cv2.VideoCapture(self.path+'Movies_reduced/free-loops_Fire_5_reduce.mpeg')
            if back: self.vidcapBack = cv2.VideoCapture(self.path+'Movies_reduced/free-loops_Fire_5_reduce.mpeg')
            if snout: self.vidcapSnout = cv2.VideoCapture(self.path+'Movies_reduced/free-loops_Fire_5_reduce.mpeg')
            self.video = True
        elif self.show == 'Fire Glow':
            if shell: self.vidcap = cv2.VideoCapture(self.path+'Movies_reduced/free-loops_Fire_Background_reduce.mpeg')
            if back: self.vidcapBack = cv2.VideoCapture(self.path+'Movies_reduced/free-loops_Fire_Background_reduce.mpeg')
            if snout: self.vidcapSnout = cv2.VideoCapture(self.path+'Movies_reduced/free-loops_Fire_Background_reduce.mpeg')
            self.video = True
        elif self.show == 'Mandel':
            if shell: self.vidcap = cv2.VideoCapture(self.path+'Movies_reduced/mandelzoom2_reduce.mpeg')
            if back: self.vidcapBack = cv2.VideoCapture(self.path+'Movies_reduced/mandelzoom2_reduce.mpeg')
            if snout: self.vidcapSnout = cv2.VideoCapture(self.path+'Movies_reduced/mandelzoom2_reduce.mpeg')
            self.video = True
        elif self.show == 'Triangles':
            if shell: self.vidcap = cv2.VideoCapture(self.path+'Movies_reduced/free-loops_Triangles_Motion_Background_2_reduce.mpeg')
            if back: self.vidcapBack = cv2.VideoCapture(self.path+'Movies_reduced/free-loops_Triangles_Motion_Background_2_reduce.mpeg')
            if snout: self.vidcapSnout = cv2.VideoCapture(self.path+'Movies_reduced/free-loops_Triangles_Motion_Background_2_reduce.mpeg')
            self.video = True
        elif self.show == 'Pineapples':
            if shell: self.vidcap = cv2.VideoCapture(self.path+'Movies_reduced/free-loops_Pineapples_Dancing_reduce.mpeg')
            if back: self.vidcapBack = cv2.VideoCapture(self.path+'Movies_reduced/free-loops_Pineapples_Dancing_reduce.mpeg')
            if snout: self.vidcapSnout = cv2.VideoCapture(self.path+'Movies_reduced/free-loops_Pineapples_Dancing_reduce.mpeg')
            self.video = True
        elif self.show == 'Bananas':
            if shell: self.vidcap = cv2.VideoCapture(self.path+'Movies_reduced/free-loops_Textured_Bananas_reduce.mpeg')
            if back: self.vidcapBack = cv2.VideoCapture(self.path+'Movies_reduced/free-loops_Textured_Bananas_reduce.mpeg')
            if snout: self.vidcapSnout = cv2.VideoCapture(self.path+'Movies_reduced/free-loops_Textured_Bananas_reduce.mpeg')
            self.video = True
        elif self.show == 'Fast Rainbow':
            if shell: self.vidcap = cv2.VideoCapture(self.path+'Movies_reduced/free-loops_Rainbow_Fishes_Frontal_Shine_H264_reduce.mpeg')
            if back: self.vidcapBack = cv2.VideoCapture(self.path+'Movies_reduced/free-loops_Color_Exploder_4_H264_reduce.mpeg')
            if snout: self.vidcapSnout = cv2.VideoCapture(self.path+'Movies_reduced/free-loops_Color_Exploder_4_H264_reduce.mpeg')
            self.video = True
        elif self.show == 'Rainbow Glow':
            if shell: self.vidcap = cv2.VideoCapture(self.path+'Movies_reduced/free-loops_Spiritual_Particle_Background_3_reduce.mpeg')
            if back: self.vidcapBack = cv2.VideoCapture(self.path+'Movies_reduced/free-loops_Spiritual_Particle_Background_3_reduce.mpeg')
            if snout: self.vidcapSnout = cv2.VideoCapture(self.path+'Movies_reduced/free-loops_Spiritual_Particle_Background_3_reduce.mpeg')
            self.video = True
        elif self.show == 'Yellow Glow':
            if shell: self.vidcap = cv2.VideoCapture(self.path+'Movies_reduced/free-loops_Spiritual_Particle_Background_5_reduce.mpeg')
            if back: self.vidcapBack = cv2.VideoCapture(self.path+'Movies_reduced/free-loops_Spiritual_Particle_Background_5_reduce.mpeg')
            if snout: self.vidcapSnout = cv2.VideoCapture(self.path+'Movies_reduced/free-loops_Spiritual_Particle_Background_5_reduce.mpeg')
            self.video = True
        elif self.show == 'Purple Glow':
            if shell: self.vidcap = cv2.VideoCapture(self.path+'Movies_reduced/free-loops_Cosmic_Power_Rays_2_reduce.mpeg')
            if back: self.vidcapBack = cv2.VideoCapture(self.path+'Movies_reduced/free-loops_Spiritual_Terrain_Background_2_reduce.mpeg')
            if snout: self.vidcapSnout = cv2.VideoCapture(self.path+'Movies_reduced/free-loops_Spiritual_Terrain_Background_2_reduce.mpeg')
            self.video = True
        elif self.show == 'Snow':
            if shell: self.vidcap = cv2.VideoCapture(self.path+'Movies_reduced/free-loops_Snowflakes_Blue_Small_H264_reduce.mpeg')
            if back: self.vidcapBack = cv2.VideoCapture(self.path+'Movies_reduced/free-loops_Snowflakes_Blue_Big_H264_reduce.mpeg')
            if snout: self.vidcapSnout = cv2.VideoCapture(self.path+'Movies_reduced/free-loops_Snowflakes_Blue_Big_H264_reduce.mpeg')
            self.video = True
        elif self.show == 'Rainbow Animals':
            if shell: self.vidcap = cv2.VideoCapture(self.path+'Movies_reduced/free-loops_Spirit_Animals_Deer_H264_reduce.mpeg')
            if back: self.vidcapBack = cv2.VideoCapture(self.path+'Movies_reduced/free-loops_Spiritual_Particle_Background_3_reduce.mpeg')
            if snout: self.vidcapSnout = cv2.VideoCapture(self.path+'Movies_reduced/free-loops_Spiritual_Particle_Background_3_reduce.mpeg')
            self.video = True
        elif self.show == 'Plants':
            if shell: self.vidcap = cv2.VideoCapture(self.path+'Movies_reduced/free-loops_Motion_Plant_Base_2_H264_reduce.mpeg')
            if back: self.vidcapBack = cv2.VideoCapture(self.path+'Movies_reduced/free-loops_Motion_Plant_Green_H264_reduce.mpeg')
            if snout: self.vidcapSnout = cv2.VideoCapture(self.path+'Movies_reduced/free-loops_Motion_Plant_Green_H264_reduce.mpeg')
            self.video = True
        elif self.show == 'Flowers':
            if shell: self.vidcap = cv2.VideoCapture(self.path+'Movies_reduced/free-loops_Flowers_Rain_2_H264_reduce.mpeg')
            if back: self.vidcapBack = cv2.VideoCapture(self.path+'Movies_reduced/free-loops_Spiritual_Particle_Background_5_reduce.mpeg')
            if snout: self.vidcapSnout = cv2.VideoCapture(self.path+'Movies_reduced/free-loops_Spiritual_Particle_Background_5_reduce.mpeg')
            self.video = True
        elif self.show == 'Sunrise':
            if shell: self.vidcap = cv2.VideoCapture(self.path+'Movies_reduced/free-loops_Red_Planet_Sunrise_H264_reduce.mpeg')
            if back: self.vidcapBack = cv2.VideoCapture(self.path+'Movies_reduced/free-loops_Outline_Triangles_reduce.mpeg')
            if snout: self.vidcapSnout = cv2.VideoCapture(self.path+'Movies_reduced/free-loops_Outline_Triangles_reduce.mpeg')
            self.video = True
        elif self.show == 'Fireworks':
            if shell: self.vidcap = cv2.VideoCapture(self.path+'Movies_reduced/free-loops_Fireworks_1_reduce.mpeg')
            if back: self.vidcapBack = cv2.VideoCapture(self.path+'Movies_reduced/free-loops_Fireworks_Blue_and_Green_reduce.mpeg')
            if snout: self.vidcapSnout = cv2.VideoCapture(self.path+'Movies_reduced/free-loops_Fireworks_Blue_and_Green_reduce.mpeg')
            self.video = True
        elif self.show == 'Water':
            if shell: self.vidcap = cv2.VideoCapture(self.path+'Movies_reduced/Silky_Blue_4K_Motion_Background_Loop_reduce.mpeg')
            if back: self.vidcapBack = cv2.VideoCapture(self.path+'Movies_reduced/Silky_Blue_4K_Motion_Background_Loop_reduce.mpeg')
            if snout: self.vidcapSnout = cv2.VideoCapture(self.path+'Movies_reduced/Silky_Blue_4K_Motion_Background_Loop_reduce.mpeg')
            self.video = True
        elif self.show == 'Rainbow Galaxy':
            if shell: self.vidcap = cv2.VideoCapture(self.path+'Movies_reduced/Galaxy_Storm_4K_Motion_Background_Loop_reduce.mpeg')
            if back: self.vidcapBack = cv2.VideoCapture(self.path+'Movies_reduced/Galaxy_Storm_4K_Motion_Background_Loop_reduce.mpeg')
            if snout: self.vidcapSnout = cv2.VideoCapture(self.path+'Movies_reduced/Galaxy_Storm_4K_Motion_Background_Loop_reduce.mpeg')
            self.video = True
        elif self.show == 'Rainbow Molecule':
            if shell: self.vidcap = cv2.VideoCapture(self.path+'Movies_reduced/Molecular_Plex_4K_Motion_Background_Loop_reduce.mpeg')
            if back: self.vidcapBack = cv2.VideoCapture(self.path+'Movies_reduced/Molecular_Plex_4K_Motion_Background_Loop_reduce.mpeg')
            if snout: self.vidcapSnout = cv2.VideoCapture(self.path+'Movies_reduced/Molecular_Plex_4K_Motion_Background_Loop_reduce.mpeg')
            self.video = True
        elif self.show == 'Reactive Spots':
            self.video = False
    
         
    def sendVideoFrame(self, shell1Colors, shell2Colors, backflapColors, snoutColors, framerate=15):
        colors = buildColors(shell1Colors, shell2Colors, backflapColors, snoutColors, self.stripLens)
        
        time.sleep(1/framerate - 1/45)
        self.client.put_pixels(colors)
            
    def getVideoFrame(self, show):
        #if show choice changes, fade out over the next second, then fade into the new show over the following second
        if show != self.show and self.switch == 0:
            self.switch = self.framerate*2    
        
        if self.switch > 0:
            self.switch = self.switch - 1
        
        if self.switch == self.framerate:
            self.show = show
            self.loadVideoFile(shell=True, back=True, snout=True)
        
        image = None
        
        #loop the shows
        if self.video:
            success,image = self.vidcap.read()    
            if (not success):
                self.loadVideoFile(shell=True) #loop back to beginning
                success,image = self.vidcap.read()
                
            successBack,imageBack = self.vidcapBack.read()    
            if (not successBack):
                self.loadVideoFile(back=True) #loop back to beginning
                successback,imageBack = self.vidcapBack.read()
                
            successSnout,imageSnout = self.vidcapSnout.read()    
            if (not successSnout):
                self.loadVideoFile(snout=True) #loop back to beginning
                successSnout,imageSnout = self.vidcapSnout.read()
                
            sendframerate = self.framerate
        else:
#            self.input_recorder.record_once()
#            xs, ys = self.input_recorder.fft()
#            bassmax = np.max(ys[:4])
#            self.totmax = np.amax((np.mean(ys),self.totmax-2))
#            zmax = 2*bassmax/self.totmax
#            self.z = self.z - 1 if self.z > 1 else 0
#            self.z = (np.amax((np.clip(zmax,0,30), self.z)) if self.totmax > 0 else 0) if zmax - 3 > self.z else self.z
#            #print(self.totmax, zmax, round(self.z))
#            image = cv2.imread("../Movies_reduced/ladybug spots/ladybug" + str(int(round(self.z))) + ".jpg")
#            image = cv2.resize(image,(width,height))
#            imageBack = cv2.imread("../Movies_reduced/ladybug spots/ladybug" + str(int(round(self.z))) + ".jpg")
#            imageBack = cv2.resize(imageBack,(width,height))
#            imageSnout= cv2.imread("../Movies_reduced/ladybug spots/ladybug" + str(int(round(self.z))) + ".jpg")
#            imageSnout = cv2.resize(imageSnout,(width,height))
            
            image = cv2.imread(self.path+"Movies_reduced/heartpic.png")
#            print('hi',image)
            image = cv2.resize(image,(width,height))
            imageBack = cv2.imread(self.path+"Movies_reduced/heartpic.png")
            imageBack = cv2.resize(imageBack,(width,height))
            imageSnout= cv2.imread(self.path+"Movies_reduced/heartpic.png")
            imageSnout = cv2.resize(imageSnout,(width,height))
            
#            sendframerate = self.reactframerate
            sendframerate = self.framerate
        
        #flip and resize images
        image = np.flip(image,axis=2)
        imageBack = np.flip(imageBack,axis=2)
        imageSnout = np.flip(imageSnout,axis=2)
        
        shell1Colors = image.reshape([height*width,3])[self.shellPoints2d]
#        print('shellpoints2d',self.shellPoints2d.shape,'shell1colors',shell1Colors.shape)
        shell2Colors = image.reshape([height*width,3])[self.shellPoints2d2]
        backflapColors = imageBack.reshape([height*width,3])[self.backflap2d]
        snoutColors = imageSnout.reshape([height*width,3])[self.snout2d]
        
#        print(np.amax(shell1Colors))
        
        shell1Colors = shell1Colors * 255.0/(np.amax(shell1Colors) if np.amax(shell1Colors) > 0 else 255.0) 
        shell2Colors = shell2Colors * 255.0/(np.amax(shell2Colors) if np.amax(shell2Colors) > 0 else 255.0) 
        backflapColors = backflapColors * 255.0/(np.amax(backflapColors) if np.amax(backflapColors) > 0 else 255.0) 
        snoutColors = snoutColors * 255.0/(np.amax(snoutColors) if np.amax(snoutColors) > 0 else 255.0) 
        
        #send color values to LEDs
        self.sendVideoFrame(shell1Colors, shell2Colors, backflapColors, snoutColors, framerate=sendframerate)
        
        #send color values to simulator
        if(self.fullShell):
            return np.concatenate((shell1Colors, shell2Colors, backflapColors, snoutColors))*abs(self.switch/self.framerate - 1)
        else:
            return np.concatenate((shell1Colors, backflapColors, snoutColors))*abs(self.switch/self.framerate - 1)
        
    def get3DPoints(self):
        shellPoints = np.loadtxt(self.path+"LoveBug/LEDPoints.csv",delimiter=',')
        backflapPoints = np.loadtxt(self.path+"LoveBug/BackFlap.csv",delimiter=',')
        snoutPoints = np.loadtxt(self.path+"LoveBug/Snout.csv",delimiter=',')
        
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
#        colors = (white*64 + blue*64 + green*64 + yellow*64 + orange*64 + red*64 + purple*64 + gray*64)*8        
        print('clearing pixels')
        time.sleep(1)
        self.client.put_pixels(black*5120)
        time.sleep(1)
        self.client.put_pixels(colors)
        
    def reduceVideoFile(self, files, intensity=1.0, huechange=0, satchange=0, slow=False, delay=0):
        vw = cv2.VideoWriter(self.path+'Movies_reduced/' + files[0] + '_reduce.mpeg',0,cv2.VideoWriter_fourcc(*'MPEG'),30,(width,height))
        
        for file in files:
            count = 0
            vidcap = cv2.VideoCapture(self.path+'Movies/' + file + '.mp4')
            success,image = vidcap.read() 
            
            while success:
                if count > delay:
                    image = np.array(image*intensity, dtype=np.uint8)
                    
                    if huechange != 0 or satchange != 0:
                        hsv = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
                        hsv[:,:,0] -= huechange
                        hsv[:,:,1] += satchange
                        image = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
                    
                    vw.write(cv2.resize(image,(width,height)))
                    if slow: vw.write(cv2.resize(image,(width,height)))
                success,image = vidcap.read()
                count += 1
        
    def createHearts(self):
        file = 'free-loops_Color_Heart_Pop_Up_H264'
        
        vidcap = cv2.VideoCapture(self.path+'Movies/' + file + '.mp4')
        vw = cv2.VideoWriter(self.path+'Movies_reduced/' + file + '_reduce.mpeg',0,cv2.VideoWriter_fourcc(*'MPEG'),30,(width,height))
    
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
        
        vidcap = cv2.VideoCapture(self.path+'Movies/' + file + '.mp4')
        vw = cv2.VideoWriter(self.path+'Movies_reduced/' + file + '_reduce2.mpeg',0,cv2.VideoWriter_fourcc(*'MPEG'),30,(width,height))
    
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
    
    lb.test8()

#    lb.reduceVideoFile(['Molecular_Plex_4K_Motion_Background_Loop'], satchange=20)
#    lb.reduceVideoFile(['Galaxy_Storm_4K_Motion_Background_Loop'], satchange=50)    
#    lb.reduceVideoFile(['Silky_Blue_4K_Motion_Background_Loop'], satchange=50)
#    lb.reduceVideoFile(['mandelzoom2'],delay=5*30)
#    lb.reduceVideoFile(['free-loops_Spirit_Animals_Deer_H264','free-loops_Spirit_Animals_Elephant_H264','free-loops_Spirit_Animals_Lion_H264','free-loops_Spirit_Animals_Owl_H264'])
#    lb.reduceVideoFile(['free-loops_Outline_Triangles'],intensity=0.5,huechange=12,slow=True)
#    lb.createHearts()