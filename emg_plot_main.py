import sys
import os
import glob
import json
from PyQt4 import QtGui
from PyQt4 import QtCore
import functools
import numpy as np
import random as rd
import matplotlib

matplotlib.use("Qt4Agg")
from matplotlib.figure import Figure
from matplotlib.animation import TimedAnimation
from matplotlib.lines import Line2D
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import threading
import serial
import serial.tools.list_ports
import time
# import winsound


# def setCustomSize(x, width, height):
#     sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
#     sizePolicy.setHorizontalStretch(0)
#     sizePolicy.setVerticalStretch(0)
#     sizePolicy.setHeightForWidth(x.sizePolicy().hasHeightForWidth())
#     x.setSizePolicy(sizePolicy)
#     x.setMinimumSize(QtCore.QSize(width, height))
#     x.setMaximumSize(QtCore.QSize(width, height))


''''''

flag_start = False

class ConfigureDialogue(QtGui.QDialog):
    
    def __init__(self):
        QtGui.QDialog.__init__(self)
        # super(ConfigureDialogue, self).__init__()

        self.lableInfo = QtGui.QLabel("Select appropriate port for the device.")
                    
        self.comPortItems = ["Select a device"]
        self.selectDevice = QtGui.QComboBox()

        self.selectDevice.addItems(self.comPortItems)
        # self.selectDevice.setStatusTip("Select EMG device")
        # self.layoutControls.addWidget(self.selectDevice)

        self.searchButton = QtGui.QPushButton('Search', self)        
        self.searchButton.clicked.connect(self.searchButtonAction)

        self.setButton = QtGui.QPushButton('Set', self)        
        self.setButton.clicked.connect(self.setButtonAction)

        self.layOutButtons = QtGui.QHBoxLayout()

        self.layOutButtons.addWidget(self.searchButton)
        self.layOutButtons.addWidget(self.setButton)


        self.mainConfLayout = QtGui.QVBoxLayout()
        self.mainConfLayout.addWidget(self.lableInfo)
        self.mainConfLayout.addWidget(self.selectDevice)
        self.mainConfLayout.addLayout(self.layOutButtons)
                
        self.setLayout(self.mainConfLayout)           
        # self.setGeometry(300, 300, 290, 150)
        self.setWindowTitle("Configure device port !")
        # self.show()

    def searchButtonAction(self):
        ports = ['COM%s' % (i + 1) for i in range(256)]        

        self.result = []        
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                self.result.append(port)
            except (OSError, serial.SerialException):
                pass                
        pass        
        # TODO remove duplicates
        for comPort in self.result:
            # print comPort
            if not comPort in self.comPortItems:
                self.comPortItems.append(comPort)

        self.selectDevice.addItems(self.comPortItems)

        print "Pressed Search"
        pass
    
    def setButtonAction(self):                
        comPort_dict = {
            "port" : str(self.selectDevice.currentText())
        }        
        with open ("config.json", "wb") as config_file:
            json.dump(comPort_dict, config_file)
            config_file.close()
        self.close()    
        pass    


'''  Global Variables  '''

class CustomMainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(CustomMainWindow, self).__init__()        

        # Create FRAME_A
        self.FRAME_A = QtGui.QFrame(self)
        self.FRAME_A.setStyleSheet("QWidget { background-color: %s }" % QtGui.QColor(210, 210, 235, 255).name())
        self.LAYOUT_A = QtGui.QVBoxLayout()
        self.FRAME_A.setLayout(self.LAYOUT_A)
        self.setCentralWidget(self.FRAME_A)


        # Place the matplotlib figure
        self.myFig = CustomFigCanvas()
        self.LAYOUT_A.addWidget(self.myFig)

        self.layoutControls = QtGui.QHBoxLayout()

        self.flag_pause = True

        self.searchButton = QtGui.QPushButton(text="Search")
        # setCustomSize(self.exitButton, 100, 50)
        self.searchButton.clicked.connect(self.searchButtonAction)
        self.searchButton.setStatusTip('Search for EMG hardware device. Make sure that bluetooth is turned on.')
        self.layoutControls.addWidget(self.searchButton)

        self.comPortItems = ["Select a device"]
        self.selectDevice = QtGui.QComboBox()
        self.selectDevice.addItems(self.comPortItems)
        self.selectDevice.setStatusTip("Select EMG device")
        self.layoutControls.addWidget(self.selectDevice)
        # self.selectDevice.addItems(self.pgm_lngs)

        # self.connectButton = QtGui.QPushButton(text="Connect")
        # # setCustomSize(self.exitButton, 100, 50)
        # self.connectButton.clicked.connect(self.connectButtonAction)
        # self.connectButton.setStatusTip('Connect EMG hardware device via bluetooth.')
        # self.layoutControls.addWidget(self.connectButton)

        self.ButtonStartPlot= QtGui.QPushButton(text = 'Start')
        # setCustomSize(self.ButtonStartPlot, 100, 50)
        self.ButtonStartPlot.clicked.connect(self.startPlot)
        self.ButtonStartPlot.setStatusTip('Start plotting')
        self.layoutControls.addWidget(self.ButtonStartPlot)

        self.ButtonStopPlot= QtGui.QPushButton(text = 'Stop')
        # setCustomSize(self.ButtonStopPlot, 100, 50)
        self.ButtonStopPlot.clicked.connect(self.stopPlot)
        self.ButtonStopPlot.setStatusTip('Pause plotting')
        self.layoutControls.addWidget(self.ButtonStopPlot)

        self.exitButton = QtGui.QPushButton(text="Exit")
        # setCustomSize(self.exitButton, 100, 50)
        self.exitButton.clicked.connect(self.exitButtonAction)
        self.exitButton.setStatusTip('Exit application')
        self.layoutControls.addWidget(self.exitButton)

        #TODO add clear button to clear canvas
        #TODO add status bar device status
        self.LAYOUT_A.addLayout(self.layoutControls)

        exitAction = QtGui.QAction('&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(sys.exit)


        configureAction = QtGui.QAction('&Configure Device', self)
        configureAction.setShortcut('Ctrl+P')
        configureAction.setStatusTip('Configure about device')
        configureAction.triggered.connect(self.actionConfigure)

        self.statusBar()

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')        
        fileMenu.addAction(exitAction)
        optionMenu = menubar.addMenu("&Option")
        optionMenu.addAction(configureAction)

        # Define the geometry of the main window
        self.setGeometry(300, 300, 800, 400)
        self.setWindowTitle("EMG Plot")

        # Add the callbackfunc to ..
        self.myDataLoop = threading.Thread(name='myDataLoop', target=dataSendLoop, args=(self.addData_callbackFunc,))
        self.myDataLoop.daemon = True        
        self.show()    
        # self.mySerial = None

    def zoomBtnAction(self):
        print("zoom in")
        self.myFig.zoomIn(5)

    ''''''

    def zoomBtnOutAction(self):
        print ("zoom out")
        self.myFig.zoomOut(5)
        pass

    def addData_callbackFunc(self, value):
        if not self.flag_pause:
            self.myFig.addData(value)
        else:
            pass

    def exitButtonAction(self):
        sys.exit()
        pass

    def startPlot(self):
        global flag_start

        if not flag_start:
            self.myDataLoop.start()
            flag_start = True

        self.ButtonStartPlot.setEnabled(False)
        self.ButtonStopPlot.setEnabled(True)
        self.flag_pause = False
        pass

    def stopPlot(self):
        self.ButtonStopPlot.setEnabled(False)
        self.ButtonStartPlot.setEnabled(True)
        self.flag_pause = True
        pass

    def searchButtonAction(self):
                
        ports = ['COM%s' % (i + 1) for i in range(256)]        

        self.result = []        
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                self.result.append(port)
            except (OSError, serial.SerialException):
                pass                
        pass        
        # TODO remove duplicates
        for comPort in self.result:
            # print comPort
            if not comPort in self.comPortItems:
                self.comPortItems.append(comPort)

        self.selectDevice.addItems(self.comPortItems)

    def actionConfigure(self):
        confg_dialogue = ConfigureDialogue()
        confg_dialogue.show()
        confg_dialogue.exec_()
        pass
                
    # def connectButtonAction(self):         
    #     self.serialPort = self.selectDevice.currentText()
    #     print "Selected Serial Port : " + str(self.serialPort)

    #     self.mySerial = serial.Serial(str(self.serialPort), 115200)

    #     print "single Data : " + str(self.mySerial.read())
    #     time.sleep(0.5)

    #     # print self.mySerial.isOpen()
    #     self.myDataLoop.start()
    #     print "Pressed Connect !"
    #     pass

# def getData():
#     data = self.mySerial.readline().rstrip()
#     data.replace("\r\n", "")
#     return data

''' End Class '''



class CustomFigCanvas(FigureCanvas, TimedAnimation):
    def __init__(self):

        self.addedData = []
        # print(matplotlib.__version__)

        # The data
        self.xlim = 200
        self.n = np.linspace(0, self.xlim - 1, self.xlim)

        self.y = (self.n * 0.0) + 50

        # The window
        self.fig = Figure(figsize=(5, 5), dpi=100)
        self.ax1 = self.fig.add_subplot(111)
        self.ax1.grid()

        # self.ax1 settings
        self.ax1.set_xticklabels([])        #remove numbering X-axis

        self.ax1.set_ylabel('EMG Value')
        self.line1 = Line2D([], [], color='blue')
        self.line1_tail = Line2D([], [], color='red', linewidth=2)
        self.line1_head = Line2D([], [], color='red', marker='o', markeredgecolor='r')
        self.ax1.add_line(self.line1)
        self.ax1.add_line(self.line1_tail)
        self.ax1.add_line(self.line1_head)
        self.ax1.set_xlim(0, self.xlim - 1)
        self.ax1.set_ylim(-10, 1200)

        FigureCanvas.__init__(self, self.fig)
        TimedAnimation.__init__(self, self.fig, interval=50, blit=True)

    def new_frame_seq(self):
        # x = iter(range(self.n.size))
        return iter(range(self.n.size))    

    def addData(self, value):
        self.addedData.append(value)   

    def _step(self, *args):
        # Extends the _step() method for the TimedAnimation class.
        try:
            TimedAnimation._step(self, *args)
        except Exception as e:
            self.abc += 1
            print(str(self.abc))
            TimedAnimation._stop(self)
            pass

    def _draw_frame(self, framedata):
        margin = 2
        while (len(self.addedData) > 0):
            self.y = np.roll(self.y, -1)
            self.y[-1] = self.addedData[0]
            del (self.addedData[0])

        self.line1.set_data(self.n[0: self.n.size - margin], self.y[0: self.n.size - margin])
        self.line1_tail.set_data(np.append(self.n[-10:-1 - margin], self.n[-1 - margin]),
                                 np.append(self.y[-10:-1 - margin], self.y[-1 - margin]))
        self.line1_head.set_data(self.n[-1 - margin], self.y[-1 - margin])
        self._drawn_artists = [self.line1, self.line1_tail, self.line1_head]


''' End Class '''

# You need to setup a signal slot mechanism, to
# send data to your GUI in a thread-safe way.
# Believe me, if you don't do this right, things
# go very very wrong..
class Communicate(QtCore.QObject):
    data_signal = QtCore.pyqtSignal(float)


''' End Class '''

def dataSendLoop(addData_callbackFunc):
    # Setup the signal-slot mechanism.
    mySrc = Communicate()
    mySrc.data_signal.connect(addData_callbackFunc)

    with open('config.json', 'rb') as config_file:
        config_raw = json.load(config_file)
        config_file.close()

    mySerial = serial.Serial(str(config_raw["port"]), 115200)
            
    while True: 
        try:                 
        # print int(mainWindw.getData())  
        # mySrc.data_signal.emit(int(mainWindw.getData()))                
            data = mySerial.readline().rstrip()
            data.replace("\r\n", "")
            mySrc.data_signal.emit(int(data))                
            # if(int(mySerial.getData()) > 500):
                # winsound.Beep(500, 1)      
            print   "data value : %d" %int(data)
        except ValueError:
            print "SerialException occured !"
            
        ##
###


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    QtGui.QApplication.setStyle(QtGui.QStyleFactory.create('Plastique'))
    myGUI = CustomMainWindow()

    sys.exit(app.exec_())

''''''
