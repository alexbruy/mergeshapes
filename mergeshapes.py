# -*- coding: utf-8 -*-

#******************************************************************************
#
# MergeShapes
# ---------------------------------------------------------
# Merge multiple shapefiles to a single shapefile
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


import os
import ConfigParser

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from qgis.core import *
from qgis.gui import *

import mergeshapesdialog
import aboutdialog

import resources_rc


class MergeShapesPlugin(object):
    def __init__(self, iface):
        self.iface = iface

        self.qgsVersion = unicode(QGis.QGIS_VERSION_INT)

        # For i18n support
        userPluginPath = QFileInfo(QgsApplication.qgisUserDbFilePath()).path() + "/python/plugins/mergeshapes"
        systemPluginPath = QgsApplication.prefixPath() + "/python/plugins/mergeshapes"

        overrideLocale = bool(QSettings().value("locale/overrideFlag", False))
        if not overrideLocale:
            localeFullName = QLocale.system().name()
        else:
            localeFullName = QSettings().value("locale/userLocale", "")

        if QFileInfo(userPluginPath).exists():
            translationPath = userPluginPath + "/i18n/mergeshapes_" + localeFullName + ".qm"
        else:
            translationPath = systemPluginPath + "/i18n/mergeshapes_" + localeFullName + ".qm"

        self.localePath = translationPath
        if QFileInfo(self.localePath).exists():
            self.translator = QTranslator()
            self.translator.load(self.localePath)
            QCoreApplication.installTranslator(self.translator)

    def initGui(self):
        if int(self.qgsVersion) < 10900:
            qgisVersion = self.qgsVersion[0] + "." + self.qgsVersion[2] + "." + self.qgsVersion[3]
            QMessageBox.warning(self.iface.mainWindow(), "MergeShapes",
                                QCoreApplication.translate("MergeShapes", "QGIS version detected: ") + qgisVersion +
                                QCoreApplication.translate("MergeShapes", "This version of MergeShapes requires at least QGIS version 2.0\nPlugin will not be enabled."))
            return None

        self.actionRun = QAction(QIcon(":/icons/mergeshapes.png"), "MergeShapes", self.iface.mainWindow())
        self.actionRun.setStatusTip(QCoreApplication.translate("MergeShapes", "Merge multiple shapefiles to one"))
        self.actionRun.setWhatsThis(QCoreApplication.translate("MergeShapes", "Merge multiple shapefiles to one"))
        self.actionAbout = QAction(QIcon(":/icons/about.png"), "About", self.iface.mainWindow())

        self.actionRun.triggered.connect(self.run)
        self.actionAbout.triggered.connect(self.about)

        self.iface.addPluginToVectorMenu(QCoreApplication.translate("MergeShapes", "MergeShapes"), self.actionRun)
        self.iface.addPluginToVectorMenu(QCoreApplication.translate("MergeShapes", "MergeShapes"), self.actionAbout)
        self.iface.addVectorToolBarIcon(self.actionRun)

    def unload(self):
        self.iface.removePluginVectorMenu(QCoreApplication.translate("MergeShapes", "MergeShapes"), self.actionRun)
        self.iface.removePluginVectorMenu(QCoreApplication.translate("MergeShapes", "MergeShapes"), self.actionAbout)
        self.iface.removeVectorToolBarIcon(self.actionRun)

    def run(self):
        dlg = mergeshapesdialog.MergeShapesDialog(self.iface)
        dlg.exec_()

    def about(self):
        d = aboutdialog.AboutDialog()
        d.exec_()
