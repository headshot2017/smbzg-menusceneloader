import os
import webbrowser

from PyQt5 import QtWidgets, QtCore, QtGui, uic

import game
import menudata

class MusicDialog(QtWidgets.QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        uic.loadUi("ui/musicdialog.ui", self)

        for f in game.assembly.GetType("SoundCache").GetFields():
            if f.Name.startswith("BGM_"):
                name = f.Name[4:]
                self.comboBox.addItem(name)
                if "vanillaMusic" in menudata.jsonFile and menudata.jsonFile["vanillaMusic"] == name:
                    self.comboBox.setCurrentIndex(self.comboBox.count()-1)
                

class GUIToolMainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/form.ui", self)

        self.setCentralWidget(self.centralwidget)

        self.actionNew.triggered.connect(self.onActionNew)
        self.actionOpen.triggered.connect(self.onActionOpen)
        self.actionSave.triggered.connect(self.onActionSave)
        self.actionSaveAs.triggered.connect(self.onActionSaveAs)
        self.actionOpenExplorer.triggered.connect(self.onActionOpenFolder)
        self.actionBgColor.triggered.connect(self.onActionBgColor)
        self.actionVanillaMusic.triggered.connect(self.onActionVanillaMusic)
        self.actionPrintJson.triggered.connect(self.onActionPrintJson)
        self.actionQuit.triggered.connect(self.onActionQuit)

        self.reset()

        for i in range(1, self.tabWidget.count()):
            self.tabWidget.setTabEnabled(i, False)

    def reset(self, charName=""):
        menudata.reset(charName)

        self.tab_anims.animatorView.setBackgroundColor(QtGui.QColorConstants.Svg.white)
        self.tab_anims.reset()

        for i in range(self.tabWidget.count()):
            self.tabWidget.setTabEnabled(i, True)

    def loadMenu(self, name):
        if not os.path.exists("%s/menu.json" % game.getMenuPath(name)):
            return

        self.reset()

        jsonFile = menudata.load(name)

        # v1.6: CharLoader Editor specifics
        if "editor" not in jsonFile:
            jsonFile["editor"] = menudata.defaultMenuData()["editor"]
        else:
            #self.spinbox_defaultDelay.setValue(menudata.jsonFile["editor"].get("defaultDelay", 0.0))
            pass

        if "backgroundColor" in jsonFile:
            self.tab_anims.animatorView.setBackgroundColor(QtGui.QColor(*jsonFile["backgroundColor"]))

        if "objects" in jsonFile:
            self.tab_anims.reloadTree()

        self.tab_anims.onRefresh()


    @QtCore.pyqtSlot()
    def onActionNew(self):
        menuName, ok = QtWidgets.QInputDialog.getText(self, "New menu scene", "Enter a name for the menu scene.")
        if not ok: return

        path = game.getMenuPath(menuName)

        if os.path.exists(path) and os.path.exists(path+"/menu.json"):
            result = QtWidgets.QMessageBox.warning(self, "Warning",
                "The menu scene '%s' already exists in your menu scenes folder.\n\nDo you want to continue and replace it?" % menuName,
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )

            if result != QtWidgets.QMessageBox.Yes:
                return

        elif not os.path.exists(path):
            os.makedirs(path)

        extraPaths = [
            path+"/sprites",
        ]
        for extraPath in extraPaths:
            if not os.path.exists(extraPath): os.mkdir(extraPath)

        self.reset(menuName)

        self.actionSave.setEnabled(True)
        self.actionSaveAs.setEnabled(True)
        self.actionOpenExplorer.setEnabled(True)
        self.actionBgColor.setEnabled(True)
        self.actionVanillaMusic.setEnabled(True)

        if self.tabWidget.tabText(0) == "Welcome":
            self.tabWidget.removeTab(0)

        menudata.save()

        QtWidgets.QMessageBox.information(self, "Done",
            "Menu scene '%s' created.\n" % (menuName) +
            "Remember to do the following:\n" +
            "* Add sprites to your menu scene's 'sprites' directory\n" +
            "* OPTIONAL: Add custom music to the menu scene's directory (start.ogg and/or loop.ogg)\n"
        )

        self.statusbar.showMessage("Created menu scene '%s'" % menuName, 3000)

    @QtCore.pyqtSlot()
    def onActionOpen(self):
        fileName, type = QtWidgets.QFileDialog.getOpenFileName(self, "Open menu.json", game.customMenusPath, "JSON (*.json)")
        if not fileName: return

        menuName = os.path.basename(os.path.dirname(fileName))
        self.loadMenu(menuName)

        self.actionSave.setEnabled(True)
        self.actionSaveAs.setEnabled(True)
        self.actionOpenExplorer.setEnabled(True)
        self.actionBgColor.setEnabled(True)
        self.actionVanillaMusic.setEnabled(True)

        if self.tabWidget.tabText(0) == "Welcome":
            self.tabWidget.removeTab(0)

        self.statusbar.showMessage("Loaded menu scene '%s'" % menuName, 3000)

    @QtCore.pyqtSlot()
    def onActionSave(self):
        menudata.save()
        self.statusbar.showMessage("Saved menu scene '%s'" % menudata.name, 3000)

    @QtCore.pyqtSlot()
    def onActionSaveAs(self):
        menuName, ok = QtWidgets.QInputDialog.getText(self, "Save menu scene", "Enter a name for the menu scene.")
        if not ok: return

        menudata.name = menuName
        menudata.save()
        self.statusbar.showMessage("Saved menu scene '%s'" % menudata.name, 3000)

    @QtCore.pyqtSlot()
    def onActionOpenFolder(self):
        webbrowser.open(game.getMenuPath(menudata.name))

    @QtCore.pyqtSlot()
    def onActionBgColor(self):
        color = QtWidgets.QColorDialog.getColor(QtGui.QColor(*menudata.jsonFile["backgroundColor"]), self)
        if color.isValid():
            menudata.jsonFile["backgroundColor"] = [color.red(), color.green(), color.blue()]
            self.tab_anims.animatorView.setBackgroundColor(color)

    @QtCore.pyqtSlot()
    def onActionVanillaMusic(self):
        dialog = MusicDialog(self)
        if dialog.exec():
            musicName = dialog.comboBox.currentText()
            menudata.jsonFile["vanillaMusic"] = musicName

    @QtCore.pyqtSlot()
    def onActionPrintJson(self):
        print("menu.json:")
        print(menudata.jsonFile)

    @QtCore.pyqtSlot()
    def onActionQuit(self):
        quit()
