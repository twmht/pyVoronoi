# -*- coding: utf-8 -*-
from PyQt4 import QtGui, QtCore, uic
from layout import Canvas
import sys
uifile = 'layout.ui'
form, base = uic.loadUiType(uifile)

class CreateLayout(base,form):
    def __init__(self):
        super(base,self).__init__()
        self.setupUi(self)
        self.PaintPanel = Canvas(self)
        self.canvas.insertWidget(0,self.PaintPanel)
        self.canvas.setCurrentWidget(self.PaintPanel)
        self.data_info= QtGui.QLabel()
        self.scrollArea.setWidget(self.data_info)

        self.output_info = QtGui.QLabel()
        self.output_area.setWidget(self.output_info)

        self.Establish_Connections()

    def Establish_Connections(self):
        QtCore.QObject.connect(self.Run_button, QtCore.SIGNAL("clicked()"),self.PaintPanel.Run)
        QtCore.QObject.connect(self.clear_button, QtCore.SIGNAL("clicked()"),self.PaintPanel.drawDisplay.ClearCanvas)
        QtCore.QObject.connect(self.open_button, QtCore.SIGNAL("clicked()"),self.PaintPanel.IOData.ReadFile)
        QtCore.QObject.connect(self.next_data, QtCore.SIGNAL("clicked()"),self.PaintPanel.IOData.next_data)
        QtCore.QObject.connect(self.step_button, QtCore.SIGNAL("clicked()"),self.PaintPanel.step_by_step)
        QtCore.QObject.connect(self.output_button, QtCore.SIGNAL("clicked()"),self.PaintPanel.IOData.output_data)
        QtCore.QObject.connect(self.reload_output, QtCore.SIGNAL("clicked()"),self.PaintPanel.IOData.read_output)
        self.next_data.setEnabled(False)



def main():
    app = QtGui.QApplication(sys.argv)
    ex = CreateLayout()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
