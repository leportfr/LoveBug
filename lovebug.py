from functions import LoveBug
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
from time import clock, sleep
import numpy as np
from recorder import InputRecorder

class LBViewer(QtGui.QWidget):
    def __init__(self, path):
        super(LBViewer,self).__init__()
        
        print('PATH PATH PATH',path)
        
        self.frametimer = clock()
        
        self.input_recorder = InputRecorder()
        self.cycle = 'Cycle'
        self.cycle_means = 0
        
        self.framerate = 30
        self.lovebug = LoveBug(input_recorder=self.input_recorder, fullShell=False, framerate=self.framerate, path=('../' if len(path) == 1 else path[1]))
        self.showlist = ['Hearts','Mandel','Triangles','Rainbow Glow','Fire Glow','Yellow Glow',
                         'Purple Glow','Snow','Rainbow Animals','Plants','Flowers','Sunrise','Fire','Bigger Fire',
                         'Fast Rainbow','Pineapples','Bananas','Reactive Spots']
        self.numCycle = 15
        self.lightshow = self.showlist[0] #set default light show
        
        self.init_ui()
        self.qt_connections()
        
        self.shell = gl.GLScatterPlotItem(pos = self.lovebug.get3DPoints(), size = 20.0, pxMode = False)
        self.shell.setGLOptions('additive')
        self.view.addItem(self.shell)
        
        self.t = QtCore.QTimer()
        self.t.timeout.connect(self.update)
        self.t.start(1)
        
    def init_ui(self):
        self.setWindowTitle('Love Bug')
        vbox = QtGui.QVBoxLayout()
        self.setLayout(vbox)

        self.view = gl.GLViewWidget()
        #self.view.setGeometry(0, 0, 1280, 820)
        self.view.opts['distance'] = 850
        self.view.opts['elevation'] = 10
        self.view.opts['azimuth'] = 30
        self.view.opts['fov'] = 90
        self.view.opts['viewport'] = [-475,-345,1500,1000]
        vbox.addWidget(self.view)
        
        hbox = QtGui.QHBoxLayout()
        vbox.addLayout(hbox)
        
        self.ShowSelect = QtGui.QComboBox(self)
        for selection in self.showlist:
            if selection == 'Pineapples': self.ShowSelect.insertSeparator(1000)
            self.ShowSelect.addItem(selection)
        self.ShowSelect.setMaxVisibleItems(100)
            
        self.SpeedSelect = QtGui.QComboBox(self)
        self.SpeedSelect.addItem('15 FPS')
        self.SpeedSelect.addItem('30 FPS')
        self.SpeedSelect.addItem('45 FPS')
        self.SpeedSelect.setCurrentIndex(1)
        
        self.CycleSelect = QtGui.QComboBox(self)
        self.CycleSelect.addItem('Cycle')
        self.CycleSelect.addItem('Manual')

        hbox.addWidget(self.ShowSelect)
        hbox.addWidget(self.SpeedSelect)
        hbox.addWidget(self.CycleSelect)

        self.setGeometry(0, 0, 600, 400)
        self.show()
        
    def qt_connections(self):
        self.ShowSelect.activated[str].connect(self.show_choice)
        self.SpeedSelect.activated[int].connect(self.speed_choice)
        self.CycleSelect.activated[str].connect(self.cycle_choice)
        
    def show_choice(self, text):
        self.lightshow = text
        
    def speed_choice(self, val):
        self.framerate = (val+1)*15
        self.lovebug.framerate = self.framerate
            
    def cycle_choice(self, text):
        self.cycle = text
    
    def update(self):
#        sleep(1/framerate - (clock()-self.frametimer) if (clock()-self.frametimer) < 1/framerate else 0)
#        print('frame rate: ',1/(clock()-self.frametimer))
        self.frametimer=clock()
        
        if self.cycle == 'Cycle': #except if 'cycle slow' is selected
            try: 
                self.input_recorder.record_once() #then record some sound 
                xs, ys = self.input_recorder.fft()
                self.cycle_means = self.cycle_means + 1 if np.mean(ys) < 5 else 0
                print(np.mean(ys), self.cycle_means)
                if self.cycle_means == 3*self.framerate: #and look for a 3-sec pause, to determine song change, then cycle
                    shownum = np.random.randint(0,self.numCycle)
                    self.ShowSelect.setCurrentIndex(shownum)
                    self.lightshow = self.showlist[shownum]
            except:
                print('audio error, will try again')
                self.input_recorder.close()
                self.input_recorder = InputRecorder()
                
        color = self.lovebug.getVideoFrame(self.lightshow)
        self.shell.setData(color = color/255)

if __name__ == '__main__':
    import sys
    
    app = QtGui.QApplication([])
    app.setApplicationName('Love Bug')
    ex = LBViewer(sys.argv)
    sys.exit(app.exec_())