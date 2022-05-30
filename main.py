#######################################
# Author Email: dorfer@aps.ee.ethz.ch
#######################################

import sys, traceback
from time import sleep
from PyQt5.QtCore import QTimer, QRunnable, QThreadPool, pyqtSignal, pyqtSlot, QObject
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication

import gui
from configobj import ConfigObj
from data_handler import DataHandler
from keithley2470 import KeithleyK2470
from kinesis import Kinesis
from keysight_dsox3034t import KeysightDSOX3034T




class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.
    Custom signals can only be defined on objects derived from QObject.
    QRunnable is not derived from QObject.
    '''

    hv_result = pyqtSignal(tuple)
    hv_error = pyqtSignal(tuple)

    scope_result = pyqtSignal(object)
    scope_error = pyqtSignal(tuple)

    bg_work_error = pyqtSignal(tuple) #fixme: add slot
    

class HVWorker(QRunnable):
    '''
    Template from:
    https://www.pythonguis.com/tutorials/multithreading-pyqt-applications-qthreadpool/
    Handles the readout from the HV device
    '''

    def __init__(self, hv_device, *args, **kwargs):
        super(HVWorker, self).__init__()
        self.hv = hv_device
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        try:
            result = self.hv.getDummyCurrent()
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.hv_error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.hv_result.emit(result)  # Return the result of the processing
        #finally:


class BackgroundWork(QRunnable):

    def __init__(self, fn, *args, **kwargs):
        super(BackgroundWork, self).__init__()
        self.bg_work_function = fn

    @pyqtSlot()
    def run(self):
        try:
            self.bg_work_function(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.bg_work_error.emit((exctype, value, traceback.format_exc()))
            pass


class ScopeWorker(QRunnable):
    '''
    Template from:
    https://www.pythonguis.com/tutorials/multithreading-pyqt-applications-qthreadpool/
    Handles the readout from the digitizer/oscilloscope
    '''

    def __init__(self, scope, *args, **kwargs):
        super(ScopeWorker, self).__init__()
        self.scope = scope
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        try:
            #wait for data and get data asynchrously
            result = self.dig.readDummyData()
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.scope_error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.scope_result.emit(result)  # Return the result of the processing
        #finally:





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


        self.threadpool = QThreadPool()
        self.threadpool.setExpiryTimeout(-1) #threads that do nothing never expire

        self.hv_timer = QTimer()
        self.hv_timer.timeout.connect(self.hv_polling)


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


    def startRunSlot(self):
        scope_worker = ScopeWorker(self.scope) 

        #arm scope, start thread to listen on new events, if there were new events start a new listener and process events  




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

    def closeEvent(self, event):
        #deal with HV device
        self.hv_timer.stop()
        self.hv.setBias(0) #fixme: ask
        self.hv.toggleOutput(on=False)
        self.hv.close()


    def process_scope_data(self, res):
        self.dh.addData(1,2,)

    def process_scope_error(self, exc):
        exctype, value, tracebk = exception
        self.scope.close()
        self.hv.open_connection()
        self.hv.configure()


############################ Start HV ############################

    def setHVValuesSlot(self):
        print('setHVValuesSlot')
        self.hv.setBias(1)
        #set compliance
        #abort on compliance

    def biasOnSlot(self):
        print('BiasOnSlot')
        self.hv.toggleOutput(on=True)
        self.hv_timer.start(100)

    def biasOffSlot(self):
        print('BiasOffSlot')
        self.hv.toggleOutput(on=False)
        self.hv_timer.stop()

    def hv_polling(self):
        hv_worker = HVWorker(self.hv)
        hv_worker.signals.hv_result.connect(self.process_hv_data)
        hv_worker.signals.hv_error.connect(self.process_hv_error)
        self.threadpool.start(hv_worker)

    def process_hv_data(self, res):
        (voltage, current) = res
        bg_worker = BackgroundWork(self.dh.setHVData(voltage, current))


    def process_hv_error(self, exc):
        exctype, value, tracebk = exception
        self.hv.close()
        self.hv.open_connection()
        self.hv.configure()

############################ End HV ############################


def main():
    app = QApplication(sys.argv)
    form = CCD_Control()
    form.show()
    app.exec_()
    sys.exit(0)

if __name__ == '__main__':
    main()