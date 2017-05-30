import sys
from PyQt4 import QtGui

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
# from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

import numpy as np
from matplotlib import animation

import random
import time
import serial

class Window(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        # self.ser = serial.Serial("/dev/ttyACM0", 115200)

        # a figure instance to plot on
        self.figure = plt.figure()

        # fig = plt.figure()
        self.ax = plt.axes(xlim=(0, 100), ylim=(-50, 1200))
        self.line, = self.ax.plot([], [], lw=2)

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)

        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        # self.toolbar = NavigationToolbar(self.canvas, self)

        # Just some button connected to `plot` method
        self.button = QtGui.QPushButton('Plot')
        self.button.clicked.connect(self.plot)

        self.buttonS = QtGui.QPushButton('Stop')
        self.buttonS.clicked.connect(self.stop)

        # set the layout
        layout = QtGui.QVBoxLayout()
        # layout.addWidget(self.toolbar)
        # layout.addWidget(self.canvas)
        layout.addWidget(self.button)
        layout.addWidget(self.buttonS)
        self.setCentralWidget(self.canvas)
        # self.setLayout(layout)

        # while True:
        #     try:
        #         data = self.ser.readline().rstrip()
        #         data.replace("\r\n", "")
        #         data = int(data)
        #         # data = (float(data)/1000)
        #         print "This is data :" + str(data)
        #     except ValueError:
        #         print "Data Error"
        #         pass
        #     time.sleep(1)



    def init(self):
        # x_val = np.linspace(1, 100)
        # self.line.set_data([5]*100, [5]*100)
        self.line.set_data([], [])
        return self.line,

    # animation function.  This is called sequentially
    def animate(self, i):
        x = np.linspace(0, 2, 100)
        # print x
        # print len(x)
        # y = [10] * len(x)
        # print y
        y = np.sin(2 * np.pi * (x - 0.01 * i))
        # print (x, y)
        # x = [0.5]*500
        # y = [0.5]*500
        # y = 0.5
        self.line.set_data(x, y)
        # print dir(self.line)

        return self.line,

    def plot(self):
        # call the animator.  blit=True means only re-draw the parts that have changed.
        self.anim = animation.FuncAnimation(self.figure, self.animate, init_func=self.init,
                                            frames=200, interval=20, blit=True)
        # refresh canvas
        self.canvas.draw()

    def stop(self):
        self.anim.event_source.stop()
        # self.canvas.stop()
        pass


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)

    main = Window()
    main.show()

    sys.exit(app.exec_())