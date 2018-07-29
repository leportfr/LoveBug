from functions import LoveBug
from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
import numpy as np

app = QtGui.QApplication([])
view = gl.GLViewWidget()
view.setGeometry(0, 0, 1280, 720)
view.opts['distance'] = 450
view.opts['elevation'] = 10
view.opts['azimuth'] = 30
view.opts['fov'] = 90
view.opts['viewport'] = [-750,-625,3000,2000]
view.setWindowTitle('Love Bug')
view.show()

lovebug = LoveBug(fullShell=False) 

shell = gl.GLScatterPlotItem(pos = lovebug.get3DPoints(), size = 20.0, pxMode = False)
shell.setGLOptions('additive')
view.addItem(shell)

def update():
    global sp2
    
    color = lovebug.getVideoFrame()
    shell.setData(color = color/255+0.05)
    
t = QtCore.QTimer()
t.timeout.connect(update)
t.start(66)

## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()