#AnimIO_UI.py

"""
Made by Lucas Santos

A UI that allows for the export and import of FBX animation.
"""

from AnimIO import animCurveIO

from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *
from shiboken2 import wrapInstance

from maya import OpenMayaUI as omui
from maya import cmds

import os

# Get the main window as a PySide object
MAYA_POINTER_ADDRESS = int(omui.MQtUtil.mainWindow())
MAYA_MAIN_WINDOW = wrapInstance(MAYA_POINTER_ADDRESS, QWidget)

class animCurveIO_UI(QWidget, animCurveIO):    
    def __init__(self) -> None:
        super(animCurveIO_UI, self).__init__()
        animCurveIO.__init__(self)

        # Place widget under Maya's main window
        self.setParent(MAYA_MAIN_WINDOW)
        self.setWindowFlags(Qt.Window)

        # Window settings
        self.setObjectName('animCurveIO_UI_id')
        self.setWindowTitle('Anim Export/Import')
        self.setStyleSheet('#animCurveIO_UI_id {background-color:#383838;}')
        x, y, w, h = 50, 50, 300, 350
        windowSizeAndPosition = QRect(x, y, w, h)
        windowSizeAndPosition.moveCenter(MAYA_MAIN_WINDOW.geometry().center())
        self.setGeometry(windowSizeAndPosition)

        # Create the widgets
        self.mainWidget()
        self.exportWidget()
        self.importWidget()

        self.showWindow()
            

    def showWindow(self):
        """Closes any existing windows prior to showing a new instance."""
        existingInstances = MAYA_MAIN_WINDOW.findChildren(QWidget, 'animCurveIO_UI_id')
        for window in existingInstances:
            window.close()
            del window
            
        self.show()


    def mainWidget(self) -> None:
        """Create the main widget for the UI.
        This is a separate function, in case future tools are needed, such as a menuBar."""
        self.main_lyt = QVBoxLayout(self)


    def exportWidget(self) -> None:
        """Create the widget pertaining to the export tool."""
        export_wgt = QFrame()
        export_wgt.setFixedHeight(100)
        export_wgt.setFrameStyle(QFrame.Box|QFrame.Sunken)
        export_wgt.setMidLineWidth(1)
        export_wgt.setStyleSheet('QFrame {background-color:#4D4D4D;}')
        self.main_lyt.addWidget(export_wgt)
        export_lyt = QVBoxLayout(export_wgt)

        openExportFolderCheckboxName = '&Open folder after export'
        openExportFolderToolTip = 'If checked, opens the directory to the exported file. (Alt + O)'
        self.openExportFolder_chk = QCheckBox(openExportFolderCheckboxName)
        self.openExportFolder_chk.setToolTip(openExportFolderToolTip)
        export_lyt.addWidget(self.openExportFolder_chk)

        exportButtonName = '&Export Animation'
        exportButtonToolpTip = 'Select a direectory to save the animation to. (Alt + E)'
        exportButtonFunction = self.exportAnimation
        export_btn = QPushButton(exportButtonName)
        export_btn.setFixedHeight(50)
        export_btn.setToolTip(exportButtonToolpTip)
        export_btn.clicked.connect(exportButtonFunction)
        export_lyt.addWidget(export_btn)


    def importWidget(self) -> None:
        """Create the widget pertaining to the import tool."""
        import_wgt = QFrame()
        import_wgt.setFrameStyle(QFrame.Box|QFrame.Sunken)
        import_wgt.setMidLineWidth(1)
        import_wgt.setStyleSheet('QFrame {background-color:#4D4D4D;}')
        self.main_lyt.addWidget(import_wgt)
        import_lyt = QVBoxLayout(import_wgt)

        keyEdits_lyt = QVBoxLayout()
        import_lyt.addLayout(keyEdits_lyt)

        offset_lyt = QHBoxLayout()
        keyEdits_lyt.addLayout(offset_lyt)

        offsetLabelName = 'Offset Start:'
        offset_lbl = QLabel(offsetLabelName)
        offset_lbl.setFixedWidth(60)
        offset_lyt.addWidget(offset_lbl)

        offsetSpinBoxToolTip = 'Starts the animation at the specified frame. Default: 0.00'
        offsetSpinBoxValueMin, offsetSpinBoxValueMax = -99999, 99999
        self.offset_txt = QDoubleSpinBox()
        self.offset_txt.setRange(offsetSpinBoxValueMin, offsetSpinBoxValueMax)
        self.offset_txt.setToolTip(offsetSpinBoxToolTip)
        offset_lyt.addWidget(self.offset_txt)

        scale_lyt = QHBoxLayout()
        keyEdits_lyt.addLayout(scale_lyt)

        scaleLabelName = 'Scale Keys:'
        scale_lbl = QLabel(scaleLabelName)
        scale_lbl.setFixedWidth(60)
        scale_lyt.addWidget(scale_lbl)

        scaleSpinBoxToolTip = 'Scales the animation by the specified value. Does not snap keys to whole values. If value is 1.00, keys remain unchanged. Default: 1.00'
        self.scale_txt = QDoubleSpinBox()
        self.scale_txt.setRange(1, 99999)
        self.scale_txt.setToolTip(scaleSpinBoxToolTip)
        scale_lyt.addWidget(self.scale_txt)
        
        timePivot_lyt = QHBoxLayout()
        keyEdits_lyt.addLayout(timePivot_lyt)
        
        timePivotLabelName = 'Time Pivot:'
        timePivot_lbl = QLabel(timePivotLabelName)
        timePivot_lbl.setFixedWidth(60)
        timePivot_lyt.addWidget(timePivot_lbl)
        
        timePivotSpinBoxToolTip = 'The anchor frame where the keyframes scale from. If scale value is 1.00, the value set here does nothing. Default: 0'
        self.timePivot_txt = QDoubleSpinBox()
        self.timePivot_txt.setRange(0, 99999)
        self.timePivot_txt.setToolTip(timePivotSpinBoxToolTip)
        timePivot_lyt.addWidget(self.timePivot_txt)

        importButtonName = '&Import Animation'
        importButtonToolpTip = 'Select a file with animation to import. (Alt + I)'
        importButtonFunction = self.importAnimation
        import_btn = QPushButton(importButtonName, import_wgt)
        import_btn.setFixedHeight(50)
        import_btn.setToolTip(importButtonToolpTip)
        import_btn.clicked.connect(importButtonFunction)   
        import_lyt.addWidget(import_btn)


    def fileDialog(self, file = False) -> str:
        """Opens a window to select a file or directory.
        
        Args:
            file (bool) : Determines if the user searches for one file or a folder; folder by default.

        Returns:
            selection (str) : The selected file or folder.
        """
        currentProject = cmds.workspace(fullName=1) 

        if file:
            title = 'Select JSON Animation Data for Import'
            fileFilter = "JSON (*.json);; All Files (*)"
            startingDirectory = currentProject
            selection, filter = QFileDialog.getOpenFileName(self,
                title,
                startingDirectory,
                fileFilter
            ) 
        else:
            title = 'Select Save Location for JSON Animation Data Export'
            fileFilter = "JSON (*.json);; All Files (*)"
            sceneName = os.path.splitext(cmds.file(q=1, sceneName=1, shortName=1))[0]
            startingDirectory = os.path.join(currentProject, f'{sceneName}.json')
            selection, filter = QFileDialog.getSaveFileName(self,
                title,
                startingDirectory,
                fileFilter
            )

        if not selection:
            # Must be deferred or it does not appear in the command response bar.
            cmds.evalDeferred('cmds.error("Nothing selected by user.", noContext=1)')

        return selection


    def openDirectory(self, file:str) -> None:
        """Opens the directory to a file.
        
        Args:
            file (str) : The absolute path to a file.
        """
        directory, file = os.path.split(file)
        os.startfile(directory)
        
        
    def importAnimation(self) -> None:
        """Imports the animation
        """
        print(end='IMPORTING ANIMATION DATA. . . ')
        
        file = self.fileDialog(file=True)
        offsetFactor = float(self.offset_txt.text())
        scaleFactor = float(self.scale_txt.text())
        timePivot = float(self.timePivot_txt.text())
        
        self.importAnimData(file=file, offsetFactor=offsetFactor, scaleFactor=scaleFactor, timePivot=timePivot)
        
        print(end='Import successful')
        
        
        
    def exportAnimation(self) -> None:
        """Exports the animation.
        """
        print(end='EXPORTING ANIMATION DATA. . . ')
        
        exportDir = self.fileDialog()
        self.exportAnimData(exportDir)
        
        print(end='Export successful')
        
        if self.openExportFolder_chk.isChecked():
            self.openDirectory(exportDir)
            
            
 
