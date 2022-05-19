from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication
import sys
import gui

class CCD_Control(QtWidgets.QMainWindow, gui.Ui_MainWindow):
    def __init__(self, parent=None):
        super(CCD_Control, self).__init__(parent)
        self.setupUi(self)

    def centerStageSlot(self):
    	print('centerStageSlot')

    def lockStageSlot(self):
    	print('lockStageSlot')

    def setHVValuesSlot(self):
    	print('setHVValuesSlot')

    def biasOnSlot(self):
    	print('BiasOnSlot')

    def biasOffSlot(self):
    	print('BiasOffSlot')


    def startRunSlot(self):
    	print('startRunSlot')

    def stopRunSlot(self):
    	print('stopRunSlot')

    def pauseRunSlot(self):
    	print('pauseRunSlot')

    def stageXMoveSlot(self, int_val):
    	print(f"stageXMoveSlot: {int_val}")

    def stageYMoveSlot(self, int_val):
    	print(f"stageXMoveSlot {int_val}")

    def stageDxChangeSlot(self, double_val):
    	print(f"stageDxChangeSlot {double_val}")

    def stageDyChangeSlot(self, double_val):
    	print(f"stageDyChangeSlot {double_val}")

    def biasVoltageValueChangeSlot(self, double_val):
    	print(f"biasVoltageValueChangeSlot: {double_val}")

    def complianceValueChangeSlot(self, double_val):
    	print(f"complianceValueChangeSlot {double_val}")

    def abortOnComplianceSlot(self, bool_val):
    	if bool_val:
    		print('toggled True')
    	else:
    		print('toggled False')

    def eventsPerRunSelectorSlot(self, int_val):
    	print(f"eventsPerRunSelectorSlot {int_val}")




def main():
    app = QApplication(sys.argv)
    form = CCD_Control()
    form.show()
    app.exec_()

if __name__ == '__main__':
    main()