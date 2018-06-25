# -*- coding: utf-8 -*-

#******************************************************************************
#
# MergeShapes
# ---------------------------------------------------------
# Create points from coordinates
#
# Copyright (C) 2010-2013 Alexander Bruy (alexander.bruy@gmail.com)
#
# This source is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# This code is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# A copy of the GNU General Public License is available on the World Wide Web
# at <http://www.gnu.org/copyleft/gpl.html>. You can also obtain it by writing
# to the Free Software Foundation, Inc., 59 Temple Place - Suite 330, Boston,
# MA 02111-1307, USA.
#
#******************************************************************************


from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *
from qgis.gui import *

from ui.ui_mergeshapesdialogbase import Ui_MergeShapesDialog


class MergeShapesDialog(QDialog, Ui_MergeShapesDialog):
    def __init__(self, iface):
        QDialog.__init__(self)
        self.setupUi(self)
        self.iface = iface

        self.mergeThread = None
        self.inputFiles = None
        self.outFileName = None
        self.inEncoding = None

        self.btnOk = self.buttonBox.button(QDialogButtonBox.Ok)
        self.btnClose = self.buttonBox.button(QDialogButtonBox.Close)

        self.btnSelectDir.clicked.connect(self.inputDir)
        self.btnSelectFile.clicked.connect(self.outFile)
        self.chkListMode.stateChanged.connect(self.changeMode)
        self.leOutShape.editingFinished.connect(self.updateOutFile)

    def inputDir(self):
        inDir = QFileDialog.getExistingDirectory(self,
                                                 self.tr("Select directory with shapefiles to merge"),
                                                 ".")

        if inDir == "":
            return

        workDir = QDir(inDir)
        workDir.setFilter(QDir.Files | QDir.NoSymLinks | QDir.NoDotAndDotDot)
        nameFilter = ["*.shp", "*.SHP"]
        workDir.setNameFilters(nameFilter)
        self.inputFiles = workDir.entryList()
        if len(self.inputFiles) == 0:
            QMessageBox.warning(self,
                                self.tr("No shapes found"),
                                self.tr("There are no shapefiles in this directory. Please select another one."))
            self.inputFiles = None
            return

        self.leInputDir.setText(inDir)

    def outFile(self):
        (self.outFileName, self.outEncoding) = self.saveDialog(self)
        if self.outFileName is None or self.outEncoding is None:
            return
        self.leOutShape.setText(self.outFileName)

    def inputFile(self):
        (files, encoding) = selopenDialog(self)
        if files.isEmpty() or encoding is None:
            self.inputFiles = None
            return

        self.inEncoding = encoding
        self.inputFiles = []
        for f in files:
            fileName = QFileInfo(f).fileName()
            self.inputFiles.append(fileName)

        self.progressFiles.setRange(0, len(self.inputFiles))
        self.leInputDir.setText(";".join(files))

    def changeMode(self):
        if self.chkListMode.isChecked():
            self.label.setText(self.tr("Input files"))
            self.btnSelectDir.clicked.disconnect(self.inputDir)
            self.btnSelectDir.clicked.connect(self.inputFile)
            self.lblGeometry.setEnabled(False)
            self.cmbGeometry.setEnabled(False)
        else:
            self.label.setText(self.tr("Input directory"))
            self.btnSelectDir.clicked.disconnect(self.inputFile)
            self.btnSelectDir.clicked.connect(self.inputDir)
            self.lblGeometry.setEnabled(True)
            self.cmbGeometry.setEnabled(True)

    def updateOutFile(self):
        self.outFileName = self.leOutShape.text()
        settings = QSettings()
        self.outEncoding = settings.value("/UI/encoding")

    def reject(self):
        QDialog.reject(self)

    def accept(self):
        if self.inputFiles is None:
            workDir = QDir(self.leInputDir.text())
            workDir.setFilter(QDir.Files | QDir.NoSymLinks | QDir.NoDotAndDotDot)
            nameFilter = ["*.shp", "*.SHP"]
            workDir.setNameFilters(nameFilter)
            self.inputFiles = workDir.entryList()
            if len(self.inputFiles) == 0:
                QMessageBox.warning(self,
                                    self.tr("No shapes found"),
                                    self.tr("There are no shapefiles in this directory. Please select another one."))
                self.inputFiles = None
                return

        if self.chkListMode.isChecked():
            files = self.leInputDir.text().split(";")
            baseDir = QFileInfo(files[0]).absolutePath()
        else:
            baseDir = self.leInputDir.text()
            # look for shapes with specified geometry type
            self.inputFiles = self.getShapesByGeometryType(baseDir, self.inputFiles, self.cmbGeometry.currentIndex())

        self.progressFiles.setRange(0, len(self.inputFiles))

        if self.outFileName is None:
            QMessageBox.warning(self,
                                self.tr("No output file selected"),
                                self.tr("Please specify output filename."))
            return

        outFile = QFile(self.outFileName)
        if outFile.exists():
            if not QgsVectorFileWriter.deleteShapeFile(self.outFileName):
                QMessageBox.warning(self,
                                    self.tr("Delete error"),
                                    self.tr("Can't delete file %1").arg(self.outFileName))
                return

        QApplication.setOverrideCursor(QCursor(Qt.WaitCursor))
        self.btnOk.setEnabled(False)

        if self.inEncoding is None:
            self.inEncoding = "System"

        self.mergeThread = ShapeMergeThread(baseDir,
                                            self.inputFiles,
                                            self.inEncoding,
                                            self.outFileName,
                                            self.outEncoding,
                                            self.chkAddFileName.isChecked(),
                                            self.chkAddFilePath.isChecked())
        self.mergeThread.rangeChanged.connect(self.setProgressRange)
        self.mergeThread.checkStarted.connect(self.setFeatureProgressFormat)
        self.mergeThread.checkFinished.connect(self.resetFeatureProgressFormat)
        self.mergeThread.fileNameChanged.connect(self.setShapeProgressFormat)
        self.mergeThread.featureProcessed.connect(self.featureProcessed)
        self.mergeThread.shapeProcessed.connect(self.shapeProcessed)
        self.mergeThread.processingFinished.connect(self.processingFinished)
        self.mergeThread.processingInterrupted.connect(self.processingInterrupted)

        self.btnClose.setText(self.tr("Cancel"))
        self.buttonBox.rejected.disconnect(self.reject)
        self.btnClose.clicked.connect(self.stopProcessing)

        self.mergeThread.start()

    def setProgressRange(self, maxVal):
        self.progressFeatures.setRange(0, maxVal)
        self.progressFeatures.setValue(0)

    def setFeatureProgressFormat(self):
        self.progressFeatures.setFormat("Checking files: %p% ")

    def resetFeatureProgressFormat(self):
        self.progressFeatures.setFormat("%p% ")

    def featureProcessed(self):
        self.progressFeatures.setValue(self.progressFeatures.value() + 1)

    def setShapeProgressFormat(self, fileName):
        self.progressFiles.setFormat("%p% " + fileName)

    def shapeProcessed(self):
        self.progressFiles.setValue(self.progressFiles.value() + 1)

    def processingFinished(self):
        self.stopProcessing()


        if self.chkAddToCanvas.isChecked():
            if not self.addShapeToCanvas(unicode(self.outFileName)):
                QMessageBox.warning(self,
                                    self.tr("Merging"),
                                    self.tr("Error loading output shapefile:\n%s") % (unicode(self.outFileName)))

        self.restoreGui()

    def processingInterrupted(self):
        self.restoreGui()

    def stopProcessing(self):
        if self.mergeThread is not None:
            self.mergeThread.stop()
            self.mergeThread = None

    def restoreGui(self):
        self.progressFiles.setFormat("%p%")
        self.progressFeatures.setRange(0, 100)
        self.progressFeatures.setValue(0)
        self.progressFiles.setValue(0)
        QApplication.restoreOverrideCursor()
        self.buttonBox.rejected.connect(self.reject)
        self.btnClose.setText(self.tr("Close"))
        self.btnOk.setEnabled(True)

    def saveDialog(self, parent):
        settings = QSettings()
        dirName = settings.value("/UI/lastShapefileDir")
        filtering = "Shapefiles (*.shp)"
        encode = settings.value("/UI/encoding")
        title = QCoreApplication.translate("MergeShapesDialog", "Save output shapefile")
        fileDialog = QgsEncodingFileDialog(parent, title, dirName, filtering, encode)
        fileDialog.setDefaultSuffix("shp")
        fileDialog.setFileMode(QFileDialog.AnyFile)
        fileDialog.setAcceptMode(QFileDialog.AcceptSave)
        fileDialog.setConfirmOverwrite(True)
        if not fileDialog.exec_() == QDialog.Accepted:
            return None, None
        files = fileDialog.selectedFiles()
        settings.setValue("/UI/lastShapefileDir", QFileInfo(unicode(files[0])).absolutePath())
        return (unicode(files[0]), unicode(fileDialog.encoding()))

    def openDialog(self, parent):
        settings = QSettings()
        dirName = settings.value("/UI/lastShapefileDir")
        filtering = "Shapefiles (*.shp)"
        encode = settings.value("/UI/encoding")
        title = QCoreApplication.translate("MergeShapesDialog", "Open input shapefile(s)")
        fileDialog = QgsEncodingFileDialog(parent, title, dirName, filtering, encode)
        fileDialog.setFileMode(QFileDialog.ExistingFiles)
        fileDialog.setAcceptMode(QFileDialog.AcceptOpen)
        if not fileDialog.exec_() == QDialog.Accepted:
            return None, None
        files = fileDialog.selectedFiles()
        settings.setValue("/UI/lastShapefileDir", QFileInfo(unicode(files[0])).absolutePath())
        # save file names as unicode
        openedFiles = []
        for f in files:
            openedFiles.append(unicode(f))
        return (openedFiles, unicode(fileDialog.encoding()))

    def addShapeToCanvas(self, shapefile_path):
        file_info = QFileInfo(shapefile_path)
        if file_info.exists():
            layer_name = file_info.completeBaseName()
        else:
            return False
        vlayer_new = QgsVectorLayer(shapefile_path, layer_name, "ogr")
        if vlayer_new.isValid():
            QgsMapLayerRegistry.instance().addMapLayer(vlayer_new)
            return True
        else:
            return False

    def getShapesByGeometryType(self, baseDir, inShapes, geomType):
        outShapes = []
        for fileName in inShapes:
            layerPath = QFileInfo(baseDir + "/" + fileName).absoluteFilePath()
            vLayer = QgsVectorLayer(layerPath, QFileInfo(layerPath).baseName(), "ogr")
            if not vLayer.isValid():
                continue
            layerGeometry = vLayer.geometryType()
            if layerGeometry == QGis.Polygon and geomType == 0:
                outShapes.append(fileName)
            elif layerGeometry == QGis.Line and geomType == 1:
                outShapes.append(fileName)
            elif layerGeometry == QGis.Point and geomType == 2:
                outShapes.append(fileName)

        if len(outShapes) == 0:
            return None

        return outShapes


class ShapeMergeThread(QThread):
    rangeChanged = pyqtSignal(int)
    checkStarted = pyqtSignal()
    featureProcessed = pyqtSignal()
    checkFinished = pyqtSignal()
    fileNameChanged = pyqtSignal(str)
    shapeProcessed = pyqtSignal()
    processingFinished = pyqtSignal()
    processingInterrupted = pyqtSignal()

    def __init__(self, dir, shapes, inputEncoding, outputFileName, outputEncoding, addFileName, addFilePath):
        QThread.__init__(self, QThread.currentThread())
        self.baseDir = dir
        self.shapes = shapes
        self.inputEncoding = inputEncoding
        self.outputFileName = outputFileName
        self.outputEncoding = outputEncoding
        self.addFileName = addFileName
        self.addFilePath = addFilePath

        self.mutex = QMutex()
        self.stopMe = 0

    def run(self):
        self.mutex.lock()
        self.stopMe = 0
        self.mutex.unlock()

        interrupted = False

        # create attribute list with uniquie fields
        # from all selected layers
        mergedFields = QgsFields()
        self.rangeChanged.emit(len(self.shapes))
        self.checkStarted.emit()
        for fileName in self.shapes:
            layerPath = QFileInfo(self.baseDir + "/" + fileName).absoluteFilePath()
            newLayer = QgsVectorLayer(layerPath, QFileInfo(layerPath).baseName(), "ogr")
            if not newLayer.isValid():
                continue
            vprovider = newLayer.dataProvider()
            layerFields = vprovider.fields()
            for layerField in layerFields:
                fieldFound = False
                for mergedField in mergedFields:
                    if (mergedField.name() == layerField.name()) and (mergedField.type() == layerField.type()):
                        fieldFound = True

                if not fieldFound:
                    mergedFields.append(layerField)
            self.featureProcessed.emit()
        self.checkFinished.emit()

        # get information about shapefiles
        layerPath = QFileInfo(self.baseDir + "/" + self.shapes[0]).absoluteFilePath()
        newLayer = QgsVectorLayer(layerPath, QFileInfo(layerPath).baseName(), "ogr")
        # TODO: check if layer valid?
        self.crs = newLayer.crs()
        self.geom = newLayer.wkbType()
        vprovider = newLayer.dataProvider()
        self.fields = mergedFields

        if self.addFileName:
            f = QgsField("filename", QVariant.String, "", 255)
            self.fNameIndex = len(self.fields) + 1
            self.fields.append(f)
            mergedFields.append(f)

        if self.addFilePath:
            f = QgsField("filepath", QVariant.String, "", 255)
            self.fields.append(f)
            mergedFields.append(f)

        writer = QgsVectorFileWriter(self.outputFileName,
                                     self.outputEncoding,
                                     self.fields,
                                     self.geom,
                                     self.crs)

        for fileName in self.shapes:
            layerPath = QFileInfo(self.baseDir + "/" + fileName).absoluteFilePath()
            newLayer = QgsVectorLayer(layerPath, QFileInfo(layerPath).baseName(), "ogr")
            if not newLayer.isValid():
                continue
            vprovider = newLayer.dataProvider()
            vprovider.setEncoding(self.inputEncoding)
            layerFields = vprovider.fields()

            nFeat = vprovider.featureCount()

            self.rangeChanged.emit(nFeat)
            self.fileNameChanged.emit(fileName)

            inFeat = QgsFeature()
            outFeat = QgsFeature()
            inGeom = QgsGeometry()
            for f in newLayer.getFeatures():
                outFeat.setFields(self.fields, True)
                # fill available attributes with values
                for layerField in layerFields:
                    for mergedField in self.fields:
                        if (mergedField.name() == layerField.name()) and (mergedField.type() == layerField.type()):
                            outFeat[mergedField.name()] = f[mergedField.name()]
                inGeom = QgsGeometry(f.geometry())
                outFeat.setGeometry(inGeom)

                if self.addFileName:
                    outFeat.setAttribute("filename", fileName)
                if self.addFilePath:
                    outFeat.setAttribute("filepath", QDir().toNativeSeparators(self.baseDir + "/" + fileName))

                writer.addFeature(outFeat)
                self.featureProcessed.emit()

            self.shapeProcessed.emit()
            self.mutex.lock()
            s = self.stopMe
            self.mutex.unlock()
            if s == 1:
                interrupted = True
                break

        del writer

        if not interrupted:
            self.processingFinished.emit()
        else:
            self.processingInterrupted.emit()

    def stop(self):
        self.mutex.lock()
        self.stopMe = 1
        self.mutex.unlock()

        QThread.wait(self)
