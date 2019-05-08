# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'WindowDialog.ui'
#
# Created: Sat Mar 18 12:22:41 2017
#      by: PyQt4 UI code generator 4.11.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui
# from time import sleep
from PySide.QtCore import QObject,Signal

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Communicate2(QObject):
    setItem = Signal(str)

class Ui_Dialog(QtGui.QDialog):
    signals = Communicate2()
    def setupUi(self,listaNameCap):
        self.items = str()
        self.listaNameCap = listaNameCap
        self.setObjectName(_fromUtf8("Dialog"))
        self.resize(397, 399)
        self.treeWidget2 = QtGui.QTreeWidget(self)
        self.treeWidget2.setGeometry(QtCore.QRect(40, 81, 321, 241))
        self.treeWidget2.setObjectName(_fromUtf8("treeWidget2"))
        self.treeWidget2.headerItem().setTextAlignment(0, QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter|QtCore.Qt.AlignCenter)
        self.pushButton = QtGui.QPushButton(self)
        self.pushButton.setGeometry(QtCore.QRect(40, 330, 85, 27))
        self.pushButton.setObjectName(_fromUtf8("pushButton"))
        self.pushButton_2 = QtGui.QPushButton(self)
        self.pushButton_2.setGeometry(QtCore.QRect(280, 330, 85, 27))
        self.pushButton_2.setObjectName(_fromUtf8("pushButton_2"))
        self.graphicsView = QtGui.QGraphicsView(self)
        self.graphicsView.setGeometry(QtCore.QRect(70, -10, 261, 111))
        self.graphicsView.setStyleSheet(_fromUtf8("border-image: url(img/animeyt.png);"))
        self.graphicsView.setObjectName(_fromUtf8("graphicsView"))
        QtCore.QMetaObject.connectSlotsByName(self)
        self.setWindowTitle(_translate("Dialog", "Dialog", None))
        self.treeWidget2.headerItem().setText(0, _translate("Dialog", "Lista de Capitulos & especiales", None))
        __sortingEnabled = self.treeWidget2.isSortingEnabled()
        self.treeWidget2.setSortingEnabled(False)

        for x in range(len(self.listaNameCap)):
            item_0 = QtGui.QTreeWidgetItem(self.treeWidget2)
            i = self.listaNameCap[x]
            self.treeWidget2.topLevelItem(x).setText(0, _translate("Dialog", i, None))

        self.treeWidget2.setSortingEnabled(__sortingEnabled)
        self.pushButton.setText(_translate("Dialog", "Descargar", None))
        self.pushButton_2.setText(_translate("Dialog", "volver", None))
        self.pushButton.clicked.connect(self.showItem)

        self.pushButton_2.clicked.connect(self.close)

    def showItem(self):

        self.items =  self.treeWidget2.currentItem().text(0)
        # self.emit(QObject('setItem'),self.items)
        self.signals.setItem.emit(self.items)





# app = QtGui.QApplication(sys.argv)
# main = Ui_Dialog()
# main.setupUi(list())
# main.show()
# sys.exit(app.exec_())
