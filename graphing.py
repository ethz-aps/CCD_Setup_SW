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


	def updateGraph(self, t_arr, v_arr, i_arr):
		self.voltage.plot(t_arr, v_arr, pen='#33B2FF')
		self.current.addItem(pg.PlotCurveItem(t_arr, i_arr, pen='#FF0000'))


class SignalWaveforms(PlotWidget):
	def __init__(self, parent=None, background='default', plotItem=None, **kargs):
		super(SignalWaveforms, self).__init__(parent=parent, background=background, plotItem=plotItem, **kargs)
		self.setLabel('bottom', 'Time', units ='sec')
		self.setLabel('left', 'Signals', units ='V')
		self.wfs = self.plotItem

		#prepare colorbar
		self.cm = pg.colormap.get('CET-L9')


	def updateGraph(self, time_axis, wf_arr):
		nWfs = len(wf_arr)
		colors = self.colormap.getLookupTable(0, nWfs, nPts=nWfs)
		for idx in range(nWfs)
			self.wfs.plot(time_axis, wf, pen=colors[idx])
		

class SignalHisto(PlotWidget):
	def __init__(self, parent=None, background='default', plotItem=None, **kargs):
		super(SignalHisto, self).__init__(parent=parent, background=background, plotItem=plotItem, **kargs)
		self.setLabel('bottom', 'Signal', units ='a.u.')
		self.setLabel('left', 'Entries', units =' ')
		self.hist = self.plotItem
		
		def updateGraph(self, vals):
			xmin = int(min(vals)-1)
			xmax = int(max(vals)+1)
			y,x = np.histogram(vals, bins=np.linspace(xmin, xmax, 100))
			self.hist.plot(x, y, stepMode="center", fillLevel=0, fillOutline=True, brush=(0,0,255,150))

