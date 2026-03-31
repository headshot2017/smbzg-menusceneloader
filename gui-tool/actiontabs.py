import os
import webbrowser

from PyQt5 import QtWidgets, QtCore, QtGui, uic

import game
import menudata


class BaseActionTab(QtWidgets.QWidget):
    valueChanged = QtCore.pyqtSignal()

    def __init__(self, parent, jsonEditorRoot):
        super().__init__(parent)

        self.jsonEditorRoot = jsonEditorRoot

    def setupForCharacter(self, jsonRoot):
        pass


class ActionTab_General(BaseActionTab):
    def __init__(self, parent, jsonEditorRoot, anim):
        super().__init__(parent, jsonEditorRoot)
        uic.loadUi("ui/actiontab_general.ui", self)

        self.anim = anim

        self.checkbox_interpolate.setChecked(anim["interpolate"] if "interpolate" in anim else True)
        self.checkbox_filter.setChecked(anim["filter"] if "filter" in anim else True)
        self.spinbox_offsetX.setValue(anim["offset"][0] if "offset" in anim else 0)
        self.spinbox_offsetY.setValue(anim["offset"][1] if "offset" in anim else 0)
        self.spinbox_scaleX.setValue(anim["scale"][0] if "scale" in anim else 1)
        self.spinbox_scaleY.setValue(anim["scale"][1] if "scale" in anim else 1)

        self.combobox_spritelist.currentTextChanged.connect(self.onChangeSprite)
        self.btn_refresh.clicked.connect(self.onRefresh)
        self.checkbox_interpolate.stateChanged.connect(self.onSetInterpolate)
        self.checkbox_filter.stateChanged.connect(self.onSetFilter)
        self.spinbox_offsetX.valueChanged.connect(self.onChangeOffsetX)
        self.spinbox_offsetY.valueChanged.connect(self.onChangeOffsetY)
        self.spinbox_scaleX.valueChanged.connect(self.onChangeScaleX)
        self.spinbox_scaleY.valueChanged.connect(self.onChangeScaleY)

        self.refreshSpriteList()

    def refreshSpriteList(self):
        self.combobox_spritelist.blockSignals(True)
        self.combobox_spritelist.clear()
        for i in range(len(menudata.sprites)):
            self.combobox_spritelist.addItem(menudata.sprites[i])
            if menudata.sprites[i] == self.anim["sprite"] or not self.anim["sprite"]:
                self.combobox_spritelist.setCurrentIndex(i)
                if not self.anim["sprite"]: self.anim["sprite"] = menudata.sprites[i]
        self.combobox_spritelist.blockSignals(False)

    @QtCore.pyqtSlot(str)
    def onChangeSprite(self, value):
        self.anim["sprite"] = value
        self.valueChanged.emit()

    @QtCore.pyqtSlot()
    def onRefresh(self):
        menudata.reloadSprites()
        self.refreshSpriteList()

    @QtCore.pyqtSlot(int)
    def onSetInterpolate(self, value):
        self.anim["interpolate"] = value > 0
        self.valueChanged.emit()

    @QtCore.pyqtSlot(int)
    def onSetFilter(self, value):
        self.anim["filter"] = value > 0
        self.valueChanged.emit()

    @QtCore.pyqtSlot(int)
    def onChangeOffsetX(self, value):
        if "offset" not in self.anim: self.anim["offset"] = [0, 0]
        self.anim["offset"][0] = value
        self.valueChanged.emit()

    @QtCore.pyqtSlot(int)
    def onChangeOffsetY(self, value):
        if "offset" not in self.anim: self.anim["offset"] = [0, 0]
        self.anim["offset"][1] = value
        self.valueChanged.emit()

    @QtCore.pyqtSlot(float)
    def onChangeScaleX(self, value):
        if "scale" not in self.anim: self.anim["scale"] = [1, 1]
        self.anim["scale"][0] = value
        self.valueChanged.emit()

    @QtCore.pyqtSlot(float)
    def onChangeScaleY(self, value):
        if "scale" not in self.anim: self.anim["scale"] = [1, 1]
        self.anim["scale"][1] = value
        self.valueChanged.emit()


class ActionTab_Frame(BaseActionTab):
    def __init__(self, parent, jsonEditorRoot, actionInfo, action):
        super().__init__(parent, jsonEditorRoot)

        uic.loadUi("ui/actiontab_frame.ui", self)

        self.actionInfo = actionInfo
        self.action = action

        self.spinbox_x.setValue(actionInfo[0])
        self.spinbox_y.setValue(actionInfo[1])
        self.spinbox_w.setValue(actionInfo[2])
        self.spinbox_h.setValue(actionInfo[3])

        self.spinbox_x.valueChanged.connect(self.onChangeX)
        self.spinbox_y.valueChanged.connect(self.onChangeY)
        self.spinbox_w.valueChanged.connect(self.onChangeW)
        self.spinbox_h.valueChanged.connect(self.onChangeH)

    @QtCore.pyqtSlot(int)
    def onChangeX(self, value):
        self.actionInfo[0] = value
        self.valueChanged.emit()

    @QtCore.pyqtSlot(int)
    def onChangeY(self, value):
        self.actionInfo[1] = value
        self.valueChanged.emit()

    @QtCore.pyqtSlot(int)
    def onChangeW(self, value):
        self.actionInfo[2] = value
        self.valueChanged.emit()

    @QtCore.pyqtSlot(int)
    def onChangeH(self, value):
        self.actionInfo[3] = value
        self.valueChanged.emit()


class ActionTab_Delay(BaseActionTab):
    def __init__(self, parent, jsonEditorRoot, actionInfo, action):
        super().__init__(parent, jsonEditorRoot)
        uic.loadUi("ui/actiontab_delay.ui", self)

        self.actionInfo = actionInfo
        self.action = action

        self.spinbox_delay.setValue(actionInfo)
        self.spinbox_delay.valueChanged.connect(self.onChange)

    @QtCore.pyqtSlot(float)
    def onChange(self, value):
        self.action["delay"] = value
        self.valueChanged.emit()


class ActionTab_Offset(BaseActionTab):
    def __init__(self, parent, jsonEditorRoot, actionInfo, action):
        super().__init__(parent, jsonEditorRoot)
        uic.loadUi("ui/actiontab_offset.ui", self)

        self.actionInfo = actionInfo
        self.action = action

        self.spinbox_x.setValue(actionInfo[0])
        self.spinbox_y.setValue(actionInfo[1])

        self.spinbox_x.valueChanged.connect(self.onChangeX)
        self.spinbox_y.valueChanged.connect(self.onChangeY)

    @QtCore.pyqtSlot(int)
    def onChangeX(self, value):
        self.actionInfo[0] = value
        self.valueChanged.emit()

    @QtCore.pyqtSlot(int)
    def onChangeY(self, value):
        self.actionInfo[1] = value
        self.valueChanged.emit()


class ActionTab_Scale(BaseActionTab):
    def __init__(self, parent, jsonEditorRoot, actionInfo, action):
        super().__init__(parent, jsonEditorRoot)
        uic.loadUi("ui/actiontab_scale.ui", self)

        self.actionInfo = actionInfo
        self.action = action

        self.spinbox_x.setValue(actionInfo[0])
        self.spinbox_y.setValue(actionInfo[1])

        self.spinbox_x.valueChanged.connect(self.onChangeX)
        self.spinbox_y.valueChanged.connect(self.onChangeY)

    @QtCore.pyqtSlot(float)
    def onChangeX(self, value):
        self.actionInfo[0] = value
        self.valueChanged.emit()

    @QtCore.pyqtSlot(float)
    def onChangeY(self, value):
        self.actionInfo[1] = value
        self.valueChanged.emit()


class ActionTab_Angle(BaseActionTab):
    def __init__(self, parent, jsonEditorRoot, actionInfo, action):
        super().__init__(parent, jsonEditorRoot)
        uic.loadUi("ui/actiontab_angle.ui", self)

        self.actionInfo = actionInfo
        self.action = action

        if type(actionInfo) == int or type(actionInfo) == float:
            self.spinbox_angle.setValue(actionInfo)
            self.action["angle"] = {"degrees": actionInfo, "interpolation": 0}
            self.actionInfo = self.action["angle"]
        else:
            self.spinbox_angle.setValue(actionInfo["degrees"])
            self.combobox_interp.setCurrentIndex(actionInfo["interpolation"])

        self.spinbox_angle.valueChanged.connect(self.onChangeAngle)
        self.combobox_interp.currentIndexChanged.connect(self.onChangeInterpolation)

    @QtCore.pyqtSlot(float)
    def onChangeAngle(self, value):
        self.actionInfo["degrees"] = value
        self.valueChanged.emit()

    @QtCore.pyqtSlot(int)
    def onChangeInterpolation(self, value):
        self.actionInfo["interpolation"] = value
        self.valueChanged.emit()


class ActionTab_Color(BaseActionTab):
    def __init__(self, parent, jsonEditorRoot, actionInfo, action):
        super().__init__(parent, jsonEditorRoot)
        uic.loadUi("ui/actiontab_color.ui", self)

        self.actionInfo = actionInfo
        self.action = action

        self.colorView.setColor(QtGui.QColor(actionInfo[0], actionInfo[1], actionInfo[2]))
        self.colorView.changed.connect(self.onChange)
        self.colorView.allowAlpha = True

    @QtCore.pyqtSlot(QtGui.QColor)
    def onChange(self, color):
        self.action["color"] = [color.red(), color.green(), color.blue(), color.alpha()]
        self.valueChanged.emit()


class ActionTab_Interpolation(BaseActionTab):
    def __init__(self, parent, jsonEditorRoot, actionInfo, action):
        super().__init__(parent, jsonEditorRoot)
        uic.loadUi("ui/actiontab_interpolation.ui", self)

        self.actionInfo = actionInfo
        self.action = action

        self.combobox_interp.setCurrentIndex(actionInfo)
        self.combobox_interp.currentIndexChanged.connect(self.onChangeInterpolation)

    @QtCore.pyqtSlot(int)
    def onChangeInterpolation(self, value):
        self.action["interpolation"] = value
        self.valueChanged.emit()


class ActionDialog(QtWidgets.QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        uic.loadUi("ui/actiondialog.ui", self)

        for action in actionTabsDict:
            self.comboBox.addItem(action)


actionTabsDict = {
	"frame": ActionTab_Frame,
	"delay": ActionTab_Delay,
    "offset": ActionTab_Offset,
    "scale": ActionTab_Scale,
    "angle": ActionTab_Angle,
    "color": ActionTab_Color,
    "interpolation": ActionTab_Interpolation
}