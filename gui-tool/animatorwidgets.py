import os
import copy

from PyQt5 import QtWidgets, QtCore, QtGui, uic

import game
import menudata
import actiontabs
import frameClipboard
import preview


class VanillaBgDialog(QtWidgets.QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        uic.loadUi("ui/scrollbgdialog.ui", self)

        for f in game.assembly.GetType("CustomScrollingBackground").GetFields():
            if f.Name == "ScrollThisOne": continue

            self.comboBox.addItem(f.Name)
            if menudata.jsonFile["scrollBg"]["vanilla"] == f.Name:
                self.comboBox.setCurrentIndex(self.comboBox.count()-1)


class BaseAnimatorWidget(QtWidgets.QWidget):
    def __init__(self, file):
        super().__init__()
        uic.loadUi(file, self)

        self.btn_stop.clicked.connect(self.onStop)
        self.btn_play.clicked.connect(self.onPlay)
        self.btn_preview.clicked.connect(self.onPreview)
        self.btn_zoomIn.clicked.connect(self.onZoomIn)
        self.btn_zoomOut.clicked.connect(self.onZoomOut)
        self.btn_zoomReset.clicked.connect(self.onZoomReset)

    def reset(self):
        self.objectsTree.clear()
        self.actionTabs.clear()

        self.animatorView.reloadObjects()

    def populateGeneralTab(self, animName):
        pass

    def populateAnimTabs(self, animName, frameInd):
        pass


    @QtCore.pyqtSlot()
    def onActionTabValueChange(self):
        self.animatorView.refresh()

    @QtCore.pyqtSlot()
    def onStop(self):
        self.animatorView.stop()

    @QtCore.pyqtSlot()
    def onPlay(self):
        self.animatorView.stop()
        self.animatorView.resetToStart()
        self.animatorView.start()

    @QtCore.pyqtSlot()
    def onPreview(self):
        w = preview.PreviewWindow()
        w.show()
        loop = QtCore.QEventLoop()
        w.hidden.connect(loop.quit)
        loop.exec() # wait ...
        w.stop()
        del w

    @QtCore.pyqtSlot()
    def onZoomIn(self):
        self.animatorView.scale(1.25, 1.25)

    @QtCore.pyqtSlot()
    def onZoomOut(self):
        self.animatorView.scale(0.8, 0.8)

    @QtCore.pyqtSlot()
    def onZoomReset(self):
        self.animatorView.resetTransform()


class MenuAnimatorWidget(BaseAnimatorWidget):
    def __init__(self):
        super().__init__("ui/animatorwidget.ui")

        self.objectsTree.currentItemChanged.connect(self.onAnimationTreeChange)
        self.objectsTree.itemDoubleClicked.connect(self.onAnimationTreeDoubleClick)
        self.objectsTree.customContextMenuRequested.connect(self.onAnimationTreeContextMenu)

        self.checkbox_scrollBgFilter.stateChanged.connect(self.onSetScrollBgFilter)
        self.btn_useScrollPng.clicked.connect(self.onUseScrollBg)
        self.btn_setVanillaBg.clicked.connect(self.onSetVanillaBg)

        #self.btn_reloadSprite.clicked.connect(self.onRefresh)

    def reset(self):
        super().reset()

        addAnim = QtWidgets.QTreeWidgetItem(self.objectsTree, ["Add object..."])
        addAnim.itemLevel = -1

    def populateGeneralTab(self, objName):
        thisObj = menudata.getObject(objName)
        if not thisObj: return

        self.actionTabs.clear()

        general = actiontabs.ActionTab_General(self.actionTabs, menudata.jsonFile["editor"], thisObj)
        general.valueChanged.connect(self.onActionTabValueChange)
        self.actionTabs.addTab(general, thisObj["name"])

        graphicsObj = self.animatorView.getObject(thisObj)
        if graphicsObj: graphicsObj.reloadAnimation()

    def populateAnimTabs(self, objName, frameInd):
        thisObj = menudata.getObject(objName)
        if not thisObj: return

        actions = thisObj["frames"][frameInd]
        
        self.actionTabs.clear()
        for action in actions:
            if action in actiontabs.actionTabsDict:
                widget = actiontabs.actionTabsDict[action](self.actionTabs, menudata.jsonFile["editor"], actions[action], actions)
                widget.valueChanged.connect(self.onActionTabValueChange)
                widget.setupForCharacter(menudata.jsonFile)
                self.actionTabs.addTab(widget, action)

        graphicsObj = self.animatorView.getObject(thisObj)
        if graphicsObj:
            graphicsObj.reloadAnimation()
            graphicsObj.setFrame(frameInd)

    def addObject(self, objName):
        animTree = QtWidgets.QTreeWidgetItem([objName])
        animTree.itemLevel = 0
        addFrame = QtWidgets.QTreeWidgetItem(animTree, ["Add frame..."])
        addFrame.itemLevel = -2
        self.objectsTree.insertTopLevelItem(self.objectsTree.topLevelItemCount()-1, animTree)

        menudata.jsonFile["objects"].append(menudata.defaultObject(objName))
        self.animatorView.reloadObjects()
        return animTree

    def addFrame(self, animTree):
        objName = animTree.text(0)
        thisObj = menudata.getObject(objName)
        if not thisObj: return None

        frameInd = animTree.childCount()-1
        rootFrameTree = QtWidgets.QTreeWidgetItem([ "Frame %d" % (frameInd+1) ])
        rootFrameTree.itemLevel = 1
        rootFrameTree.frame = frameInd
        animTree.insertChild(frameInd, rootFrameTree)
        addAction = QtWidgets.QTreeWidgetItem(rootFrameTree, ["Add action..."])
        addAction.itemLevel = -3

        thisObj["frames"].append({})

        self.addAction("delay", rootFrameTree)
        if len(thisObj["frames"]) == 1:
            self.addAction("frame", rootFrameTree)

        return rootFrameTree

    def addAction(self, actionName, rootFrameTree):
        animTree = rootFrameTree.parent()
        frameInd = animTree.indexOfChild(rootFrameTree)
        objName = animTree.text(0)

        thisObj = menudata.getObject(objName)
        if not thisObj: return None

        if actionName in thisObj["frames"][frameInd]:
            return None

        thisFrameTree = QtWidgets.QTreeWidgetItem([actionName])
        thisFrameTree.itemLevel = 2
        rootFrameTree.insertChild(rootFrameTree.childCount()-1, thisFrameTree)

        theAction = menudata.defaultAction(actionName)
        #if actionName == "delay":
            #theAction = menudata.jsonFile["editor"]["defaultDelay"]

        thisObj["frames"][frameInd][actionName] = theAction
        return thisFrameTree

    def reloadTree(self):
        expanded = {}
        for i in range(self.objectsTree.topLevelItemCount()):
            animItem = self.objectsTree.topLevelItem(i)
            if not animItem.isExpanded(): continue

            expanded[animItem.text(0)] = {}
            for j in range(animItem.childCount()):
                frameItem = animItem.child(j)
                if not frameItem.isExpanded(): continue

                expanded[animItem.text(0)][frameItem.text(0)] = False

        self.objectsTree.clear()

        addAnim = QtWidgets.QTreeWidgetItem(self.objectsTree, ["Add object..."])
        addAnim.itemLevel = -1

        for obj in menudata.jsonFile["objects"]:
            objName = obj["name"]
            animTree = QtWidgets.QTreeWidgetItem([objName])
            animTree.itemLevel = 0

            if "frames" in obj:
                frames = obj["frames"]
                for frameInd in range(len(frames)):
                    frameDict = frames[frameInd]
                    rootFrameTree = QtWidgets.QTreeWidgetItem(animTree, [ "Frame %d" % (frameInd+1) ] )
                    rootFrameTree.itemLevel = 1
                    for frameName in frameDict:
                        frame = frameDict[frameName]
                        thisFrameTree = QtWidgets.QTreeWidgetItem(rootFrameTree, [frameName])
                        thisFrameTree.itemLevel = 2

                    if objName in expanded and rootFrameTree.text(0) in expanded[objName]:
                        expanded[objName][rootFrameTree.text(0)] = rootFrameTree

                    addAction = QtWidgets.QTreeWidgetItem(rootFrameTree, ["Add action..."])
                    addAction.itemLevel = -3

            addFrame = QtWidgets.QTreeWidgetItem(animTree, ["Add frame..."])
            addFrame.itemLevel = -2
            self.objectsTree.insertTopLevelItem(self.objectsTree.topLevelItemCount()-1, animTree)

            if objName in expanded:
                animTree.setExpanded(True)
                for k in expanded[objName]:
                    if not expanded[objName][k]: continue
                    expanded[objName][k].setExpanded(True)


    @QtCore.pyqtSlot(int)
    def onSetScrollBgFilter(self, value):
        menudata.jsonFile["scrollBg"]["filter"] = value > 0

    @QtCore.pyqtSlot()
    def onUseScrollBg(self):
        menudata.jsonFile["scrollBg"]["vanilla"] = ""

    @QtCore.pyqtSlot()
    def onSetVanillaBg(self):
        dialog = VanillaBgDialog(self)
        if dialog.exec():
            bgName = dialog.comboBox.currentText()
            menudata.jsonFile["scrollBg"]["vanilla"] = bgName

    @QtCore.pyqtSlot(QtWidgets.QTreeWidgetItem, QtWidgets.QTreeWidgetItem)
    def onAnimationTreeChange(self, current, previous):
        if not current or current.itemLevel < 0: return

        if current.itemLevel == 0:
            self.populateGeneralTab(current.text(0))
        if current.itemLevel == 1:
            animTree = current.parent()
            frameInd = animTree.indexOfChild(current)
            objName = animTree.text(0)
            self.populateAnimTabs(objName, frameInd)
        if current.itemLevel == 2:
            rootFrameTree = current.parent()
            animTree = rootFrameTree.parent()
            actionInd = rootFrameTree.indexOfChild(current)
            frameInd = animTree.indexOfChild(rootFrameTree)
            objName = animTree.text(0)
            self.populateAnimTabs(objName, frameInd)
            self.actionTabs.setCurrentIndex(actionInd)

    @QtCore.pyqtSlot(QtWidgets.QTreeWidgetItem, int)
    def onAnimationTreeDoubleClick(self, item, column):
        if not item or item.itemLevel > 0: return

        if item.itemLevel == -1:
            objName, ok = QtWidgets.QInputDialog.getText(self, "Add object", "Enter a name for the object")
            if ok:
                for obj in menudata.jsonFile["objects"]:
                    if obj["name"] == objName:
                        QtWidgets.QMessageBox.warning(self, "Error", "Object '%s' already exists" % objName)
                        return

                self.addObject(objName)

        if item.itemLevel == -2:
            animTree = item.parent()
            self.addFrame(animTree)

        if item.itemLevel == -3:
            actionDialog = actiontabs.ActionDialog(self)
            if actionDialog.exec():
                actionName = actionDialog.comboBox.currentText()
                rootFrameTree = item.parent()
                animTree = rootFrameTree.parent()
                frameInd = animTree.indexOfChild(rootFrameTree)
                objName = animTree.text(0)

                actionTree = self.addAction(actionName, rootFrameTree)
                if not actionTree:
                    QtWidgets.QMessageBox.warning(self, "Error", "Action '%s' already exists" % actionName)
                    return

                self.populateAnimTabs(objName, frameInd)
                self.actionTabs.setCurrentIndex(rootFrameTree.indexOfChild(actionTree))

    @QtCore.pyqtSlot(QtCore.QPoint)
    def onAnimationTreeContextMenu(self, point):
        item = self.objectsTree.itemAt(point)
        if item.itemLevel < 0 and item.itemLevel != -2: return

        menu = QtWidgets.QMenu()
        if item.itemLevel == 0:
            actionRename = menu.addAction("Rename")
            actionDuplicate = menu.addAction("Duplicate")
            menu.addSeparator()
            actionMoveTop = menu.addAction("Move to top")
            actionMoveUp = menu.addAction("Move up")
            actionMoveDown = menu.addAction("Move down")
            actionMoveBottom = menu.addAction("Move to bottom")
            menu.addSeparator()

            actionRename.triggered.connect(self.onMenuActionRename)
            actionDuplicate.triggered.connect(self.onMenuActionDuplicateObj)
            actionMoveTop.triggered.connect(self.onMenuActionMoveObjectTop)
            actionMoveUp.triggered.connect(self.onMenuActionMoveObjectUp)
            actionMoveDown.triggered.connect(self.onMenuActionMoveObjectDown)
            actionMoveBottom.triggered.connect(self.onMenuActionMoveObjectBottom)

            actionRename.setData(item)
            actionDuplicate.setData(item)
            actionMoveTop.setData(item)
            actionMoveUp.setData(item)
            actionMoveDown.setData(item)
            actionMoveBottom.setData(item)

        elif item.itemLevel == 1:
            actionCut = menu.addAction("Cut")
            actionCopy = menu.addAction("Copy")
            actionPaste = menu.addAction("Paste")
            actionDuplicate = menu.addAction("Duplicate")
            menu.addSeparator()
            actionMoveTop = menu.addAction("Move to top")
            actionMoveUp = menu.addAction("Move up")
            actionMoveDown = menu.addAction("Move down")
            actionMoveBottom = menu.addAction("Move to bottom")
            menu.addSeparator()

            actionCut.triggered.connect(self.onMenuActionCut)
            actionCopy.triggered.connect(self.onMenuActionCopy)
            actionPaste.triggered.connect(self.onMenuActionPaste)
            actionDuplicate.triggered.connect(self.onMenuActionDuplicateFrame)
            actionMoveTop.triggered.connect(self.onMenuActionMoveFrameTop)
            actionMoveUp.triggered.connect(self.onMenuActionMoveFrameUp)
            actionMoveDown.triggered.connect(self.onMenuActionMoveFrameDown)
            actionMoveBottom.triggered.connect(self.onMenuActionMoveFrameBottom)

            actionCut.setData(item)
            actionCopy.setData(item)
            actionPaste.setData(item)
            actionMoveTop.setData(item)
            actionMoveUp.setData(item)
            actionMoveDown.setData(item)
            actionMoveBottom.setData(item)
            actionDuplicate.setData(item)

        elif item.itemLevel == -2:
            actionPaste = menu.addAction("Paste")
            actionPaste.triggered.connect(self.onMenuActionPaste)
            actionPaste.setData(item)

        if item.itemLevel >= 0:
            actionDelete = menu.addAction("Delete")
            actionDelete.triggered.connect(self.onMenuActionDelete)
            actionDelete.setData(item)

        menu.exec(self.objectsTree.mapToGlobal(point))

    @QtCore.pyqtSlot()
    def onMenuActionRename(self):
        item = self.sender().data()
        oldName = item.text(0)
        newName, ok = QtWidgets.QInputDialog.getText(self, "Rename object", "Rename the object '%s' to..." % oldName)
        if not ok or not newName: return

        for obj in menudata.jsonFile["objects"]:
            if obj["name"] != oldName: continue
            obj["name"] = newName
            break

        self.reloadTree()

    @QtCore.pyqtSlot()
    def onMenuActionDuplicateObj(self):
        item = self.sender().data()
        oldName = item.text(0)
        newName, ok = QtWidgets.QInputDialog.getText(self, "Duplicate object", "Enter a name for the duplicated object")
        if not ok or not newName: return

        for i in range(len(menudata.jsonFile["objects"])):
            obj = menudata.jsonFile["objects"][i]
            if obj["name"] != oldName: continue

            newObj = copy.deepcopy(obj)
            newObj["name"] = newName
            menudata.jsonFile["objects"].insert(i+1, newObj)
            break

        self.reloadTree()
        self.animatorView.reloadObjects()

    @QtCore.pyqtSlot()
    def onMenuActionCut(self):
        item = self.sender().data()
        animTree = item.parent()
        objName = animTree.text(0)
        frameInd = animTree.indexOfChild(item)

        thisObj = menudata.getObject(objName)
        frameClipboard.current = copy.deepcopy(thisObj["frames"][frameInd])
        del thisObj["frames"][frameInd]
        self.reloadTree()

    @QtCore.pyqtSlot()
    def onMenuActionCopy(self):
        item = self.sender().data()
        animTree = item.parent()
        objName = animTree.text(0)
        frameInd = animTree.indexOfChild(item)

        thisObj = menudata.getObject(objName)
        frameClipboard.current = copy.deepcopy(thisObj["frames"][frameInd])

    @QtCore.pyqtSlot()
    def onMenuActionPaste(self):
        if not frameClipboard.current:
            return

        item = self.sender().data()
        animTree = item.parent()
        objName = animTree.text(0)
        frameInd = animTree.indexOfChild(item)

        thisObj = menudata.getObject(objName)
        thisObj["frames"].insert(frameInd, copy.deepcopy(frameClipboard.current))

        self.reloadTree()

    @QtCore.pyqtSlot()
    def onMenuActionDuplicateFrame(self):
        item = self.sender().data()
        animTree = item.parent()
        objName = animTree.text(0)
        frameInd = animTree.indexOfChild(item)

        thisObj = menudata.getObject(objName)
        duplicatedFrame = copy.deepcopy(thisObj["frames"][frameInd])
        thisObj["frames"].insert(frameInd, duplicatedFrame)

        self.reloadTree()

    @QtCore.pyqtSlot()
    def onMenuActionMoveObjectTop(self):
        item = self.sender().data()
        objName = item.text(0)
        i = menudata.getObjectIndex(objName)
        if i == 0: return

        anim = menudata.jsonFile["objects"].pop(i)
        menudata.jsonFile["objects"].insert(0, anim)

        self.reloadTree()
        self.animatorView.reloadObjects()

    @QtCore.pyqtSlot()
    def onMenuActionMoveObjectUp(self):
        item = self.sender().data()
        objName = item.text(0)
        i = menudata.getObjectIndex(objName)
        if i == 0: return

        anim = menudata.jsonFile["objects"].pop(i)
        menudata.jsonFile["objects"].insert(i-1, anim)

        self.reloadTree()
        self.animatorView.reloadObjects()

    @QtCore.pyqtSlot()
    def onMenuActionMoveObjectDown(self):
        item = self.sender().data()
        objName = item.text(0)

        i = menudata.getObjectIndex(objName)
        if i >= len(menudata.jsonFile["objects"])-1: return

        anim = menudata.jsonFile["objects"].pop(i)
        menudata.jsonFile["objects"].insert(i+1, anim)

        self.reloadTree()
        self.animatorView.reloadObjects()

    @QtCore.pyqtSlot()
    def onMenuActionMoveObjectBottom(self):
        item = self.sender().data()
        objName = item.text(0)

        i = menudata.getObjectIndex(objName)
        if i >= len(menudata.jsonFile["objects"])-1: return

        anim = menudata.jsonFile["objects"].pop(i)
        menudata.jsonFile["objects"].append(anim)

        self.reloadTree()
        self.animatorView.reloadObjects()

    @QtCore.pyqtSlot()
    def onMenuActionMoveFrameTop(self):
        item = self.sender().data()
        animTree = item.parent()
        objName = animTree.text(0)
        frameInd = animTree.indexOfChild(item)
        if frameInd == 0: return

        thisObj = menudata.getObject(objName)
        anim = thisObj["frames"].pop(frameInd)
        thisObj["frames"].insert(0, anim)

        self.reloadTree()

    @QtCore.pyqtSlot()
    def onMenuActionMoveFrameUp(self):
        item = self.sender().data()
        animTree = item.parent()
        objName = animTree.text(0)
        frameInd = animTree.indexOfChild(item)
        if frameInd == 0: return

        thisObj = menudata.getObject(objName)
        anim = thisObj["frames"].pop(frameInd)
        thisObj["frames"].insert(frameInd-1, anim)

        self.reloadTree()

    @QtCore.pyqtSlot()
    def onMenuActionMoveFrameDown(self):
        item = self.sender().data()
        animTree = item.parent()
        objName = animTree.text(0)
        frameInd = animTree.indexOfChild(item)

        thisObj = menudata.getObject(objName)
        if frameInd >= len(thisObj["frames"])-1: return

        anim = thisObj["frames"].pop(frameInd)
        thisObj["frames"].insert(frameInd+1, anim)

        self.reloadTree()

    @QtCore.pyqtSlot()
    def onMenuActionMoveFrameBottom(self):
        item = self.sender().data()
        animTree = item.parent()
        objName = animTree.text(0)
        frameInd = animTree.indexOfChild(item)

        thisObj = menudata.getObject(objName)
        if frameInd >= len(thisObj["frames"])-1: return

        anim = thisObj["frames"].pop(frameInd)
        thisObj["frames"].append(anim)

        self.reloadTree()
        

    @QtCore.pyqtSlot()
    def onMenuActionDelete(self):
        message = ""
        item = self.sender().data()

        if item.itemLevel == 0:
            objName = item.text(0)
            message = "You are about to delete the object '%s'.\nAre you sure?" % objName
        elif item.itemLevel == 1:
            animTree = item.parent()
            objName = animTree.text(0)
            message = "You are about to delete %s from the object '%s'.\nAre you sure?" % (item.text(0), objName)
        elif item.itemLevel == 2:
            rootFrameTree = item.parent()
            frameName = rootFrameTree.text(0)
            animTree = rootFrameTree.parent()
            objName = animTree.text(0)
            message = "You are about to delete action '%s' from %s of the object '%s'.\nAre you sure?" % (item.text(0), frameName, objName)

        result = QtWidgets.QMessageBox.warning(self, "Warning", message,
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )

        if result != QtWidgets.QMessageBox.Yes: return

        if item.itemLevel == 0:
            del menudata.jsonFile["objects"][menudata.getObjectIndex(item.text(0))]
        elif item.itemLevel == 1:
            animTree = item.parent()
            objName = animTree.text(0)
            frameInd = animTree.indexOfChild(item)
            thisObj = menudata.getObject(objName)
            del thisObj["frames"][frameInd]
        elif item.itemLevel == 2:
            rootFrameTree = item.parent()
            animTree = rootFrameTree.parent()
            objName = animTree.text(0)
            frameInd = animTree.indexOfChild(rootFrameTree)
            thisObj = menudata.getObject(objName)
            del thisObj["frames"][frameInd][item.text(0)]

        self.reloadTree()
        self.animatorView.reloadObjects()

    @QtCore.pyqtSlot()
    def onRefresh(self):
        self.animatorView.reloadObjects()

        if "scrollBg" not in menudata.jsonFile:
            menudata.jsonFile["scrollBg"] = menudata.defaultScrollBg()
        scrollBg = menudata.jsonFile["scrollBg"]

        self.checkbox_scrollBgFilter.setChecked(scrollBg["filter"] if "filter" in scrollBg else False)
