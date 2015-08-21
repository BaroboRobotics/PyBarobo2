# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dialog.ui'
#
# Created: Fri Aug 21 13:08:35 2015
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

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

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(480, 640)
        self.gridLayout = QtGui.QGridLayout(Dialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label_3 = QtGui.QLabel(Dialog)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.label = QtGui.QLabel(Dialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.m1b = QtGui.QLineEdit(Dialog)
        self.m1b.setObjectName(_fromUtf8("m1b"))
        self.gridLayout.addWidget(self.m1b, 2, 1, 1, 1)
        self.m1f = QtGui.QLineEdit(Dialog)
        self.m1f.setObjectName(_fromUtf8("m1f"))
        self.gridLayout.addWidget(self.m1f, 0, 1, 1, 1)
        self.label_2 = QtGui.QLabel(Dialog)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.m1fl = QtGui.QLineEdit(Dialog)
        self.m1fl.setObjectName(_fromUtf8("m1fl"))
        self.gridLayout.addWidget(self.m1fl, 1, 1, 1, 1)
        self.label_8 = QtGui.QLabel(Dialog)
        self.label_8.setObjectName(_fromUtf8("label_8"))
        self.gridLayout.addWidget(self.label_8, 10, 0, 1, 1)
        self.label_6 = QtGui.QLabel(Dialog)
        self.label_6.setObjectName(_fromUtf8("label_6"))
        self.gridLayout.addWidget(self.label_6, 11, 0, 1, 1)
        self.label_5 = QtGui.QLabel(Dialog)
        self.label_5.setObjectName(_fromUtf8("label_5"))
        self.gridLayout.addWidget(self.label_5, 12, 0, 1, 1)
        self.m1bl = QtGui.QLineEdit(Dialog)
        self.m1bl.setObjectName(_fromUtf8("m1bl"))
        self.gridLayout.addWidget(self.m1bl, 3, 1, 1, 1)
        self.m2f = QtGui.QLineEdit(Dialog)
        self.m2f.setObjectName(_fromUtf8("m2f"))
        self.gridLayout.addWidget(self.m2f, 6, 1, 1, 1)
        self.label_4 = QtGui.QLabel(Dialog)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 3, 0, 1, 1)
        self.label_7 = QtGui.QLabel(Dialog)
        self.label_7.setObjectName(_fromUtf8("label_7"))
        self.gridLayout.addWidget(self.label_7, 6, 0, 1, 1)
        self.m2fl = QtGui.QLineEdit(Dialog)
        self.m2fl.setObjectName(_fromUtf8("m2fl"))
        self.gridLayout.addWidget(self.m2fl, 10, 1, 1, 1)
        self.m2b = QtGui.QLineEdit(Dialog)
        self.m2b.setObjectName(_fromUtf8("m2b"))
        self.gridLayout.addWidget(self.m2b, 11, 1, 1, 1)
        self.label_9 = QtGui.QLabel(Dialog)
        self.label_9.setObjectName(_fromUtf8("label_9"))
        self.gridLayout.addWidget(self.label_9, 14, 0, 1, 1)
        self.m2bl = QtGui.QLineEdit(Dialog)
        self.m2bl.setObjectName(_fromUtf8("m2bl"))
        self.gridLayout.addWidget(self.m2bl, 12, 1, 1, 1)
        self.lineEdit_status = QtGui.QLineEdit(Dialog)
        self.lineEdit_status.setObjectName(_fromUtf8("lineEdit_status"))
        self.gridLayout.addWidget(self.lineEdit_status, 14, 1, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.pushButton_start = QtGui.QPushButton(Dialog)
        self.pushButton_start.setObjectName(_fromUtf8("pushButton_start"))
        self.horizontalLayout.addWidget(self.pushButton_start)
        self.pushButton_quit = QtGui.QPushButton(Dialog)
        self.pushButton_quit.setObjectName(_fromUtf8("pushButton_quit"))
        self.horizontalLayout.addWidget(self.pushButton_quit)
        self.gridLayout.addLayout(self.horizontalLayout, 15, 0, 1, 2)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 13, 1, 1, 1)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Dialog", None))
        self.label_3.setText(_translate("Dialog", "M1 Backward Speed:", None))
        self.label.setText(_translate("Dialog", "M1 Forward Speed:", None))
        self.label_2.setText(_translate("Dialog", "M1 Forward Linearity:", None))
        self.label_8.setText(_translate("Dialog", "M2 Forward Linearity", None))
        self.label_6.setText(_translate("Dialog", "M2 Backward Speed", None))
        self.label_5.setText(_translate("Dialog", "M2 Backward Linearity", None))
        self.label_4.setText(_translate("Dialog", "M1 Backward Linearity: ", None))
        self.label_7.setText(_translate("Dialog", "M2 Forward Speed:", None))
        self.label_9.setText(_translate("Dialog", "Status:", None))
        self.pushButton_start.setText(_translate("Dialog", "Start", None))
        self.pushButton_quit.setText(_translate("Dialog", "Quit", None))

