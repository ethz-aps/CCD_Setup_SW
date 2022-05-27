#######################################
# Author Email: dorfer@aps.ee.ethz.ch
#######################################

import sys
from time import sleep
from PyQt5.QtCore import QThread, QTimer
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication

import gui
from configobj import ConfigObj
from data_handler import DataHandler
from keithley2470 import KeithleyK2470
from kinesis import Kinesis
from keysight_dsox3034t import KeysightDSOX3034T


class WorkerThread(QThread):
    #https://stackoverflow.com/questions/52036021/qtimer-on-a-qthread
    def __init__(self, hv, scope, dh, **kwds):
        super().__init__(**kwds)

        self.hv = hv
        self.scope = scope
        self.dh = dh

        self.kill = False
        self.hv_polling = False

    def run(self):
        def data_acquisition_and_display():
            print('timer call')
            if self.kill:
                print('stopped the timer..')
                timer.stop()
                print('killing myself..')
                self.quit()
                return

            if self.hv_polling:
                print('HV polling')
                curr = self.hv.getDummyCurrent()
                self.dh.setHVData(1, curr)
                print('done hv polling')


            
        timer = QTimer()
        timer.timeout.connect(data_acquisition_and_display)
        timer.start(500)
        self.exec_()









class CCD_Control(QtWidgets.QMainWindow, gui.Ui_MainWindow):
    def __init__(self, parent=None):
        super(CCD_Control, self).__init__(parent)
        self.setupUi(self)

        self.conf = ConfigObj('config.ini') #load config

        #data handling class
        self.dh = DataHandler(self.conf, self.hvPlot)

        #High Voltage Supply
        self.hv = KeithleyK2470(self.conf)

        #XY-Stage
        self.stage = Kinesis(self.conf)

        #Oscilloscope/Digitizer
        self.scope = KeysightDSOX3034T(self.conf)

        self.worker = WorkerThread(self.hv, self.scope, self.dh) #removed self from arguments
        self.worker.hv_polling = False
        self.worker.start()


    def centerStageSlot(self):
        self.stage.center_stage()
        self.xAxisSlider.setValue(50)
        self.yAxisSlider.setValue(50)

    def lockStageSlot(self):
        if self.stage.get_lock_state():
            self.xAxisSlider.setEnabled(True)
            self.yAxisSlider.setEnabled(True)
            self.centerStage.setEnabled(True)
            self.xAxisIncrement.setEnabled(True)
            self.yAxisIncrement.setEnabled(True)
            self.lockStage.setText('Lock Stage')
            self.stage.set_lock_state(False)
        else:
            self.xAxisSlider.setEnabled(False)
            self.yAxisSlider.setEnabled(False)
            self.centerStage.setEnabled(False)
            self.xAxisIncrement.setEnabled(False)
            self.yAxisIncrement.setEnabled(False)
            self.lockStage.setText('Unlock Stage')
            self.stage.set_lock_state(True)

    def stageDxChangeSlot(self, double_val):
        print(f"stageDxChangeSlot {double_val}")

    def stageDyChangeSlot(self, double_val):
        print(f"stageDyChangeSlot {double_val}")

    def stageXMoveSlot(self, int_val):
        print(f"stageXMoveSlot: {int_val}")

    def stageYMoveSlot(self, int_val):
        print(f"stageXMoveSlot {int_val}")


    def setHVValuesSlot(self):
        print('setHVValuesSlot')
        self.hv.setBias(1)
        #set compliance
        #abort on compliance

    def biasOnSlot(self):
        print('BiasOnSlot')
        self.hv.toggleOutput(on=True)
        self.worker.hv_polling = True

    def biasOffSlot(self):
        print('BiasOffSlot')
        self.hv.toggleOutput(on=False)
        self.worker.hv_polling = False


    def startRunSlot(self):
        print('startRunSlot')
        x_time=[1,2,3,4,5,6,7,8,9]
        y_amplitude1 = [2, 2, 2, 3, 4, 5, 6, 6, 6]
        y_amplitude2 = [1, 1, 6, 3, 4, 7, 6, 8, 9]


        wfs = [y_amplitude1, y_amplitude2, x_time]

        self.wfPlot.updatePlot(x_time, wfs)

        self.signalPlot.updatePlot(y_amplitude2)

    def pauseRunSlot(self):
        print('pauseRunSlot')


    def stopRunSlot(self):
        print('stopRunSlot')
        #self.worker.kill = True

    def closeEvent(self, event):
        self.worker.kill = True
        sleep(0.505)
        print('Stopped the thread!')





def main():
    app = QApplication(sys.argv)
    form = CCD_Control()
    form.show()
    app.exec_()
    sys.exit(0)

if __name__ == '__main__':
    main()