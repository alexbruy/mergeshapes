# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mergeshapesdialogbase.ui'
#
# Created: Tue Mar 30 20:24:38 2010
#      by: PyQt4 UI code generator 4.5.2
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_MergeShapesDialog(object):
    def setupUi(self, MergeShapesDialog):
        MergeShapesDialog.setObjectName("MergeShapesDialog")
        MergeShapesDialog.resize(377, 246)
        self.verticalLayout = QtGui.QVBoxLayout(MergeShapesDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtGui.QLabel(MergeShapesDialog)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.leInputDir = QtGui.QLineEdit(MergeShapesDialog)
        self.leInputDir.setObjectName("leInputDir")
        self.horizontalLayout.addWidget(self.leInputDir)
        self.btnSelectDir = QtGui.QPushButton(MergeShapesDialog)
        self.btnSelectDir.setObjectName("btnSelectDir")
        self.horizontalLayout.addWidget(self.btnSelectDir)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.label_2 = QtGui.QLabel(MergeShapesDialog)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.leOutShape = QtGui.QLineEdit(MergeShapesDialog)
        self.leOutShape.setObjectName("leOutShape")
        self.horizontalLayout_2.addWidget(self.leOutShape)
        self.btnSelectFile = QtGui.QPushButton(MergeShapesDialog)
        self.btnSelectFile.setObjectName("btnSelectFile")
        self.horizontalLayout_2.addWidget(self.btnSelectFile)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.chkAddToCanvas = QtGui.QCheckBox(MergeShapesDialog)
        self.chkAddToCanvas.setObjectName("chkAddToCanvas")
        self.verticalLayout.addWidget(self.chkAddToCanvas)
        self.progressFeatures = QtGui.QProgressBar(MergeShapesDialog)
        self.progressFeatures.setProperty("value", QtCore.QVariant(0))
        self.progressFeatures.setObjectName("progressFeatures")
        self.verticalLayout.addWidget(self.progressFeatures)
        self.progressFiles = QtGui.QProgressBar(MergeShapesDialog)
        self.progressFiles.setProperty("value", QtCore.QVariant(0))
        self.progressFiles.setObjectName("progressFiles")
        self.verticalLayout.addWidget(self.progressFiles)
        self.buttonBox = QtGui.QDialogButtonBox(MergeShapesDialog)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(MergeShapesDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), MergeShapesDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), MergeShapesDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(MergeShapesDialog)

    def retranslateUi(self, MergeShapesDialog):
        MergeShapesDialog.setWindowTitle(QtGui.QApplication.translate("MergeShapesDialog", "Merge shapefiles", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("MergeShapesDialog", "Input directory", None, QtGui.QApplication.UnicodeUTF8))
        self.btnSelectDir.setText(QtGui.QApplication.translate("MergeShapesDialog", "Browse", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("MergeShapesDialog", "Output shapefile", None, QtGui.QApplication.UnicodeUTF8))
        self.btnSelectFile.setText(QtGui.QApplication.translate("MergeShapesDialog", "Browse", None, QtGui.QApplication.UnicodeUTF8))
        self.chkAddToCanvas.setText(QtGui.QApplication.translate("MergeShapesDialog", "Add result to map canvas", None, QtGui.QApplication.UnicodeUTF8))

