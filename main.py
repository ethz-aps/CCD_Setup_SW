#######################################
# Author Email: dorfer@aps.ee.ethz.ch
#######################################

import threading
import sys, traceback
from time import sleep, time
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

	scope_result = pyqtSignal(tuple)
	scope_progress_callback = pyqtSignal(int)
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
		self.fn = fn
		self.args = args
		self.kwargs = kwargs
		self.signals = WorkerSignals()

	@pyqtSlot()
	def run(self):
		try:
			self.fn(*self.args, **self.kwargs)
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

	def __init__(self, fn, *args, **kwargs):
		super(ScopeWorker, self).__init__()
		self.fn = fn
		self.signals = WorkerSignals()
		self.args = args
		self.kwargs = kwargs

		self.kwargs['scope_progress_callback'] = self.signals.scope_progress_callback


	@pyqtSlot()
	def run(self):
		try:
			#wait for data and get data asynchrously
			result = self.fn(*self.args, **self.kwargs)
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

		print(f"{threading.get_ident()} MAIN")

		self.conf = ConfigObj('config.ini') #load config

		#XY-Stage
		self.stage = Kinesis(self.conf)

		self.initializeValues() #fill gui values

		#data handling class
		self.dh = DataHandler(self.conf, self.hvPlot, self.wfPlot)

		#High Voltage Supply
		self.hv = KeithleyK2470(self.conf)

		#Oscilloscope/Digitizer
		self.scope = KeysightDSOX3034T(self.conf)

		self.threadpool = QThreadPool()
		self.threadpool.setExpiryTimeout(-1) #threads that do nothing never expire

		self.hv_timer = QTimer()
		self.hv_timer.timeout.connect(self.hv_polling)




############################ Start Stage Stuff ############################

	def centerStageSlot(self):
		[xmin, xval, xmax, ymin, yval, ymax] = self.stage.center_stage()
		self.xAxisSlider.setMinimum(xmin)
		self.xAxisSlider.setMaximum(xmax)
		self.xAxisSlider.setValue(xval)
		self.xAxisPos.display(xval)
		self.yAxisSlider.setMinimum(ymin)
		self.yAxisSlider.setMaximum(ymax)
		self.yAxisSlider.setValue(yval)
		self.yAxisPos.display(yval)

		conf = self.conf['PositionControl']
		conf['x_min'] = xmin
		conf['x_max'] = xmax
		conf['x_pos'] = xval
		conf['y_min'] = ymin
		conf['y_max'] = ymax
		conf['y_pos'] = yval
		self.conf.write()


	def lockStageSlot(self):
		if self.lockStage.text() == 'Lock Stage':
			self.xAxisSlider.setEnabled(False)
			self.yAxisSlider.setEnabled(False)
			self.centerStage.setEnabled(False)
			self.xAxisIncrement.setEnabled(False)
			self.yAxisIncrement.setEnabled(False)
			self.lockStage.setText('Unlock Stage')
			self.stage.lock_state = True

		else:
			self.xAxisSlider.setEnabled(True)
			self.yAxisSlider.setEnabled(True)
			self.centerStage.setEnabled(True)
			self.xAxisIncrement.setEnabled(True)
			self.yAxisIncrement.setEnabled(True)
			self.lockStage.setText('Lock Stage')
			self.stage.lock_state = False
		
		self.conf['PositionControl']['lock_state'] = self.stage.lock_state
		self.conf.write()


	def stageDxChangeSlot(self, val):
		self.xAxisSlider.setPageStep(val)
		self.xAxisSlider.setTickInterval(val)
		self.conf['PositionControl']['x_step'] = val
		self.conf.write()

	def stageDyChangeSlot(self, val):
		self.yAxisSlider.setPageStep(val)
		self.yAxisSlider.setTickInterval(val)
		self.conf['PositionControl']['y_step'] = val
		self.conf.write()


	def stageXMoveSlot(self, val):
		self.stage.move_x(val)
		self.xAxisPos.display(val)
		self.conf['PositionControl']['x_pos'] = val
		self.conf.write()

	def stageYMoveSlot(self, val):
		self.stage.move_y(val)
		self.yAxisPos.display(val)
		self.conf['PositionControl']['y_pos'] = val
		self.conf.write()


############################ End Stage Stuff ############################


	def startRunSlot(self):
		self.startRun.setEnabled(False)

		#set config values
		conf = self.conf['PositionControl']
		conf['x_pos'] = self.xAxisSlider.value()
		conf['x_step'] = self.xAxisIncrement.value()
		conf['y_pos'] = self.yAxisSlider.value()
		conf['y_step'] = self.yAxisIncrement.value()

		conf = self.conf['RunSettings']
		conf['events_per_run'] = self.eventsPerRun.value()
		conf['excitation_source'] = self.excitationSource.currentText()
		conf['last_sample'] = self.sampleName.text()
		conf['amplifier_serial_nr'] = self.ampSerialNumber.value()
		conf['trigger_scint_voltage'] = self.triggerScintVoltage.value()
		conf['veto_scint_voltage'] = self.triggerScintVoltage.value()
		self.conf.write()


		configured = self.scope.configure()
		self.scope.stop = False
		scope_config =  self.scope.read_premable()
		self.dh.createFile(scope_config=scope_config)

		#create a thread with a callback for a progress bar
		scope_worker = ScopeWorker(self.scope.read_dummy_data) 
		scope_worker.signals.scope_result.connect(self.process_scope_data)
		scope_worker.signals.scope_progress_callback.connect(self.progress_bar)
		self.threadpool.start(scope_worker)

		self.stopRun.setEnabled(True)






	def stopRunSlot(self):
		self.stopRun.setEnabled(False)
		self.scope.stop = True
		#self.dh.closeFile()
		self.startRun.setEnabled(True)





	def process_scope_data(self, res):
		(tax, wf_data) = res
		ts = time()
		self.dh.addData(ts, 1, 1, tax, wf_data, final=self.scope.stop)

		if not self.scope.stop:
			scope_worker = ScopeWorker(self.scope.read_dummy_data) 
			scope_worker.signals.scope_result.connect(self.process_scope_data)
			scope_worker.signals.scope_progress_callback.connect(self.progress_bar)
			self.threadpool.start(scope_worker)
		

	def progress_bar(self, val):
		self.scope_progress.setValue(val)


	def process_scope_error(self, exc):
		exctype, value, tracebk = exception
		self.scope.close()
		self.hv.open_connection()
		self.hv.configure()


############################ Start HV ############################

	def setHVValuesSlot(self):
		conf = self.conf['HighVoltageControl']

		bias_voltage = self.biasVoltage.value()
		self.hv.set_bias(bias_voltage)
		self.conf['HighVoltageControl']['bias_voltage'] = bias_voltage
		
		current_compliance = self.complianceCurrent.value()*10**(-9) #in nA
		self.hv.set_compliance(current_compliance)
		conf['current_compliance'] = current_compliance

		abort_on_compliance = self.abortOnCompliance.isChecked()
		self.hv.abort_on_compliance = True
		conf['abort_on_compliance'] = abort_on_compliance

		self.conf.write()


	def biasOnSlot(self):
		self.biasOn.setEnabled(False)
		self.hv.toggle_output(on=True)
		self.hv_timer.start(1000)
		self.biasOff.setEnabled(True)

	def biasOffSlot(self):
		self.biasOff.setEnabled(False)
		self.hv.toggle_output(on=False)
		self.hv_timer.stop()
		self.biasOn.setEnabled(True)

	def hv_polling(self):
		hv_worker = HVWorker(self.hv)
		hv_worker.signals.hv_result.connect(self.process_hv_data)
		hv_worker.signals.hv_error.connect(self.process_hv_error)
		self.threadpool.start(hv_worker)

	def process_hv_data(self, res):
		(voltage, current) = res
		bg_worker = BackgroundWork(self.dh.setHVData, voltage, current)
		self.threadpool.start(bg_worker)

	def process_hv_error(self, exc):
		exctype, value, tracebk = exception
		self.hv.close()
		self.hv.open_connection()
		self.hv.configure()

############################ End HV ############################

	def initializeValues(self):
		#stage
		conf = self.conf['PositionControl']
		self.xAxisIncrement.setValue(conf.as_int('x_step'))
		self.xAxisSlider.setMinimum(conf.as_int('x_min'))
		self.xAxisSlider.setMaximum(conf.as_int('x_max'))
		self.xAxisSlider.setSingleStep(conf.as_int('x_step'))
		self.xAxisSlider.setValue(conf.as_int('x_pos'))
		self.xAxisPos.display(conf.as_int('x_pos'))

		self.yAxisIncrement.setValue(conf.as_int('y_step'))
		self.yAxisSlider.setMinimum(conf.as_int('y_min'))
		self.yAxisSlider.setMaximum(conf.as_int('y_max'))
		self.yAxisSlider.setSingleStep(conf.as_int('y_step'))
		self.yAxisSlider.setValue(conf.as_int('y_pos'))
		self.yAxisPos.display(conf.as_int('y_pos'))

		if conf.as_bool('lock_state'):
			self.stage.lock_state = True
			self.xAxisSlider.setEnabled(False)
			self.yAxisSlider.setEnabled(False)
			self.centerStage.setEnabled(False)
			self.xAxisIncrement.setEnabled(False)
			self.yAxisIncrement.setEnabled(False)
			self.lockStage.setText('Unlock Stage')


		#HV
		conf = self.conf['HighVoltageControl']

		self.biasVoltage.setMinimum(conf.as_float('bias_voltage_min'))
		self.biasVoltage.setMaximum(conf.as_float('bias_voltage_max'))
		self.biasVoltage.setValue(conf.as_float('bias_voltage'))

		self.complianceCurrent.setMinimum(conf.as_float('current_compliance_nA_min'))
		self.complianceCurrent.setMaximum(conf.as_float('current_compliance_nA_max'))
		self.complianceCurrent.setValue(conf.as_float('current_compliance_nA'))

		self.abortOnCompliance.setChecked(conf.as_bool('abort_on_compliance'))


		#run controls
		conf = self.conf['RunSettings']
		self.eventsPerRun.setValue(conf.as_int('events_per_run'))

		#set default values to QComboBox
		self.excitationSource.addItems(conf['possible_excitation_sources'])
		self.excitationSource.setCurrentText(conf['excitation_source'])
		self.sampleName.setText(conf['last_sample'])

		self.ampSerialNumber.setValue(conf.as_int('amplifier_serial_nr'))
		self.triggerScintVoltage.setValue(conf.as_float('trigger_scint_voltage'))
		self.vetoScintVoltage.setValue(conf.as_float('veto_scint_voltage'))







	def closeEvent(self, event):
		#deal with HV device
		self.hv_timer.stop()
		self.hv.set_bias(0) #fixme: ask
		self.hv.toggle_output(on=False)
		self.hv.close()


def main():
	app = QApplication(sys.argv)
	form = CCD_Control()
	form.show()
	app.exec_()
	sys.exit(0)

if __name__ == '__main__':
	main()