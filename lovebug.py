from functions import LoveBug
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
from time import clock, sleep
import numpy as np

framerate = 30

class LBViewer(QtGui.QWidget):
    def __init__(self):
        super(LBViewer,self).__init__()
        
        self.frametimer = clock()
        
        self.lovebug = LoveBug(fullShell=False, framerate=framerate)
        self.showlist = ['Hearts','Fire','Mandel','Triangles','Pineapples','Reactive Spots','Fast Rainbow']
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
        hbox = QtGui.QVBoxLayout()
        self.setLayout(hbox)

        self.view = gl.GLViewWidget()
        self.view.setGeometry(0, 0, 1280, 1000)
        self.view.opts['distance'] = 450
        self.view.opts['elevation'] = 10
        self.view.opts['azimuth'] = 30
        self.view.opts['fov'] = 90
        self.view.opts['viewport'] = [-750,-625,3000,2000]
        hbox.addWidget(self.view)
        
        self.ShowSelect = QtGui.QComboBox(self)
        for lightshow in self.showlist:
            self.ShowSelect.addItem(lightshow)

        hbox.addWidget(self.ShowSelect)

        self.setGeometry(0, 0, 1280, 720)
        self.show()
        
    def qt_connections(self):
        self.ShowSelect.activated[str].connect(self.show_choice)
        
    def show_choice(self, text):
        self.lightshow = text
    
    def update(self):
#        sleep(1/framerate - (clock()-self.frametimer) if (clock()-self.frametimer) < 1/framerate else 0)
#        print('frame rate: ',1/(clock()-self.frametimer))
#        self.frametimer=clock()
        color = self.lovebug.getVideoFrame(self.lightshow)
        self.shell.setData(color = color/255)
        
#        self.input_recorder.record_once()
#        xs, ys = self.input_recorder.fft()
#        sum1 = np.sum(ys[:25])
#        print (sum1/1000000)
#        self.shell.setData(color = [sum1/1000000,0,0,1] if sum1/1000000 > 0.5 else [0.1,0,0,1])

if __name__ == '__main__':
    import sys
    
    app = QtGui.QApplication([])
    app.setApplicationName('Love Bug')
    ex = LBViewer()
    sys.exit(app.exec_())