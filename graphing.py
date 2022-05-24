import time
import numpy as np
import pyqtgraph as pg
from pyqtgraph import PlotWidget, DateAxisItem


class BiasGraph(PlotWidget):

	def __init__(self, parent=None, background='default', plotItem=None, **kargs):
		super(BiasGraph, self).__init__(parent=parent, background=background, plotItem=plotItem, axisItems = {'bottom': DateAxisItem()}, **kargs)


		#example: https://github.com/pyqtgraph/pyqtgraph/blob/develop/examples/MultiplePlotAxes.py
		self.setLabel('bottom', 'Time', units ='sec')
		self.voltage = self.plotItem
		self.voltage.setLabel('left', 'Applied Bias Voltage', units ='V', color='#33B2FF')

		self.current = pg.ViewBox()
		self.voltage.showAxis('right')
		self.voltage.scene().addItem(self.current)
		self.voltage.getAxis('right').linkToView(self.current)
		self.current.setXLink(self.voltage)
		self.voltage.getAxis('right').setLabel('Leakage Current', units='nA', color='#FF0000')

		def updateViews():
		    self.current.setGeometry(self.voltage.vb.sceneBoundingRect())
		    self.current.linkedViewChanged(self.voltage.vb, self.current.XAxis)

		updateViews()
		self.voltage.vb.sigResized.connect(updateViews)

		x_time=[1,2,3,4,5,6,7,8,9]
		y_amplitude1 = [2, 2, 2, 3, 4, 5, 6, 6, 6]
		y_amplitude2 = [1, 1, 6, 3, 4, 7, 6, 8, 9]
		self.updateBiasGraph(x_time, y_amplitude1, y_amplitude2)

	def updateBiasGraph(self, t_arr, v_arr, i_arr):
		self.voltage.plot(t_arr, v_arr, pen='#33B2FF')
		self.current.addItem(pg.PlotCurveItem(t_arr, i_arr, pen='#FF0000'))


class SignalWaveforms(PlotWidget):
	def __init__(self, parent=None, background='default', plotItem=None, **kargs):
		super(SignalWaveforms, self).__init__(parent=parent, background=background, plotItem=plotItem, **kargs)
		self.setLabel('bottom', 'Time', units ='sec')
		self.setLabel('left', 'Signals', units ='V')
		self.wfs = self.plotItem
		


class SignalHisto(PlotWidget):
	def __init__(self, parent=None, background='default', plotItem=None, **kargs):
		super(SignalHisto, self).__init__(parent=parent, background=background, plotItem=plotItem, **kargs)
		self.setLabel('bottom', 'Signal', units ='a.u.')
		self.setLabel('left', 'Entries', units =' ')


		self.hist = self.plotItem
		## make interesting distribution of values
		vals = np.hstack([np.random.normal(size=500), np.random.normal(size=260, loc=4)])

		## compute standard histogram
		y,x = np.histogram(vals, bins=np.linspace(-3, 8, 40))

		## Using stepMode="center" causes the plot to draw two lines for each sample.
		## notice that len(x) == len(y)+1
		self.hist.plot(x, y, stepMode="center", fillLevel=0, fillOutline=True, brush=(0,0,255,150))


