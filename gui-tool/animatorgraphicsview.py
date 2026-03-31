import random

from PyQt5 import QtWidgets, QtCore, QtGui, uic

import menudata
import game
import easing


def lerp(a, b, x):
    return a + ((b-a) * x)


class PixmapAnimator(QtCore.QAbstractAnimation):
    def __init__(self, graphicsView, obj):
        super().__init__()
        self.graphicsView = graphicsView

        self.pixmapItem = QtWidgets.QGraphicsPixmapItem()
        self.graphicsView.scene().addItem(self.pixmapItem)

        self.fullPixmap = None
        self.obj = obj
        self.globalOffset = obj["offset"] if "offset" in obj else [0, 0]
        self.globalScale = obj["scale"] if "scale" in obj else [1, 1]

        self.frame = 0
        self.animDuration = 0
        self.currentLoopChanged.connect(self.onLoop)
        self.setLoopCount(-1)

        self.reloadSprite(game.getMenuPath(menudata.name)+"/sprites/"+obj["sprite"])
        self.reloadAnimation()

    def __del__(self):
        self.stop()
        self.obj = None
        self.graphicsView.scene().removeItem(self.pixmapItem)

    def setSprite(self, x, y, w, h):
        if not self.fullPixmap or self.fullPixmap.isNull():
            return
        if w < 0: w = self.fullPixmap.width() - x
        if h < 0: h = self.fullPixmap.height() - y
        self.pixmapItem.setPixmap(self.fullPixmap.copy(x, y, w, h))
        self.pixmapItem.setOffset(-w/2, -h/2)

    def reloadSprite(self, file):
        self.fullPixmap = QtGui.QPixmap(file)
        self.setSprite(0,0,0,0)

    def reloadAnimation(self):
        self.stop()
        if not self.obj: return

        self.animDuration = 0
        for frame in self.obj["frames"]:
            if "delay" in frame:
                self.animDuration += frame["delay"]*1000

        self.reloadSprite(game.getMenuPath(menudata.name)+"/sprites/"+self.obj["sprite"])
        self.setFrame(0)

    def setFrame(self, ind):
        self.frame = ind
        self.onFrameChange()

    def refresh(self):
        if not self.obj: return

        self.onFrameChange()
        self.animDuration = 0
        for frame in self.obj["frames"]:
            if "delay" in frame:
                self.animDuration += frame["delay"]*1000


    def onFrameChange(self):
        if not self.obj or self.frame < 0 or self.frame >= len(self.obj["frames"]):
            return False

        frame = self.obj["frames"][self.frame]

        offsetPos = [self.globalOffset[0], -self.globalOffset[1]]
        offsetPos[0] += frame["offset"][0] if "offset" in frame else 0
        offsetPos[1] -= frame["offset"][1] if "offset" in frame else 0

        angle = 0
        if "angle" in frame:
            angle = frame["angle"]
            if type(angle) == dict:
                angle = angle["degrees"]

        self.pixmapItem.resetTransform()
        self.pixmapItem.setPos(self.graphicsView.sceneRect().width()/2, self.graphicsView.sceneRect().height()/2)
        self.pixmapItem.setRotation(angle)
        self.pixmapItem.moveBy(*offsetPos)
        self.pixmapItem.setTransform(self.pixmapItem.transform().scale(
            self.globalScale[0] * (frame["scale"][0] if "scale" in frame else 1),
            self.globalScale[1] * (frame["scale"][1] if "scale" in frame else 1)
        ))

        if "color" in frame:
            self.pixmapItem.setOpacity(frame["color"][3]/255. if len(frame["color"]) >= 4 else 1)
        else:
            self.pixmapItem.setOpacity(1)


        spriteFrame = frame
        spriteFrameInd = self.frame
        while "frame" not in spriteFrame and spriteFrameInd > 0:
            spriteFrameInd -= 1
            spriteFrame = self.obj["frames"][spriteFrameInd]
        if "frame" in spriteFrame:
            self.setSprite(*spriteFrame["frame"])

        return True

    def interpolateFrames(self, x):
        if not self.obj:
            self.stop()
            return

        currAction = self.obj["frames"][self.frame]
        if currAction["delay"] <= 0: return

        xAngle = x
        if "interpolation" in currAction and currAction["interpolation"] in easing.Funcs:
            x = easing.Funcs[currAction["interpolation"]](x)

        nextAction = None
        if self.frame >= len(self.obj["frames"])-1:
            nextAction = self.obj["frames"][0] if self.loopCount() < 0 or self.currentLoop() < self.loopCount()-1 else currAction
        else:
            nextAction = self.obj["frames"][self.frame+1]


        colorLerp = [
            lerp(currAction["color"][0] if "color" in currAction else 255, nextAction["color"][0] if "color" in nextAction else 255, x),
            lerp(currAction["color"][1] if "color" in currAction else 255, nextAction["color"][1] if "color" in nextAction else 255, x),
            lerp(currAction["color"][2] if "color" in currAction else 255, nextAction["color"][2] if "color" in nextAction else 255, x),
            255
        ]
        currAlpha = currAction["color"][3] if ("color" in currAction and len(currAction["color"]) >= 4) else 255
        nextAlpha = nextAction["color"][3] if ("color" in nextAction and len(nextAction["color"]) >= 4) else 255
        colorLerp[3] = lerp(currAlpha, nextAlpha, x)


        currAngle = 0
        nextAngle = 0
        angleInterp = 0
        if "angle" in currAction:
            currAngle = currAction["angle"]
            if type(currAngle) == dict:
                angleInterp = currAngle["interpolation"]
                currAngle = currAngle["degrees"]
        if "angle" in nextAction:
            nextAngle = nextAction["angle"]
            if type(nextAngle) == dict:
                nextAngle = nextAngle["degrees"]

        angleLerp = lerp(
            currAngle,
            nextAngle,
            easing.Funcs[angleInterp](xAngle)
        )

        scaleLerp = [
            self.globalScale[0] * lerp(
                currAction["scale"][0] if "scale" in currAction else 1,
                nextAction["scale"][0] if "scale" in nextAction else 1,
                x
            ),
            self.globalScale[1] * lerp(
                currAction["scale"][1] if "scale" in currAction else 1,
                nextAction["scale"][1] if "scale" in nextAction else 1,
                x
            )
        ]

        offsetLerp = [
            self.globalOffset[0] + lerp(
                currAction["offset"][0] if "offset" in currAction else 0,
                nextAction["offset"][0] if "offset" in nextAction else 0,
                x
            ),
            -self.globalOffset[1] + lerp(
                -currAction["offset"][1] if "offset" in currAction else 0,
                -nextAction["offset"][1] if "offset" in nextAction else 0,
                x
            )
        ]

        self.pixmapItem.resetTransform()
        self.pixmapItem.setPos(self.graphicsView.sceneRect().width()/2, self.graphicsView.sceneRect().height()/2)
        self.pixmapItem.setRotation(angleLerp)
        self.pixmapItem.moveBy(*offsetLerp)
        self.pixmapItem.setTransform(self.pixmapItem.transform().scale(*scaleLerp))
        self.pixmapItem.setOpacity(colorLerp[3]/255.)

    def getTimeFrames(self):
        if not self.obj:
            self.stop()
            return 0, 0

        timeToNextFrame = 0
        timeFromLastFrame = 0
        for i in range(self.frame+1):
            if i >= len(self.obj["frames"]): break
            frame = self.obj["frames"][i]
            if "delay" in frame:
                timeToNextFrame += frame["delay"]*1000
                if i != self.frame: timeFromLastFrame += frame["delay"]*1000
        return timeToNextFrame, timeFromLastFrame

    def duration(self):
        return self.animDuration

    def updateState(self, oldState, newState):
        if newState == 0:
            self.frame = 0
            self.onFrameChange()

    def updateCurrentTime(self, currentTime):
        if not self.obj:
            self.stop()
            return

        timeToNextFrame, timeFromLastFrame = self.getTimeFrames()

        if "interpolate" not in self.obj or self.obj["interpolate"]:
            a = currentTime - timeFromLastFrame
            b = timeToNextFrame - timeFromLastFrame
            if b != 0:
                self.interpolateFrames(a/b)

        while currentTime >= timeToNextFrame:
            self.frame += 1
            if not self.onFrameChange(): return
            timeToNextFrame, timeFromLastFrame = self.getTimeFrames()

    def onLoop(self):
        self.frame = 0
        self.onFrameChange()


class AnimatorGraphicsView(QtWidgets.QGraphicsView):
    def __init__(self, theParent):
        super().__init__(theParent)

        self.theScene = QtWidgets.QGraphicsScene()
        self.theScene.setSceneRect(0, 0, 1280, 720)
        self.setScene(self.theScene)

        self.objects = []

        self.borderLines = [
            QtWidgets.QGraphicsLineItem(-1,   -1, 1280,  -1),
            QtWidgets.QGraphicsLineItem(1280, -1, 1280, 720),
            QtWidgets.QGraphicsLineItem(-1,   -1,   -1, 720),
            QtWidgets.QGraphicsLineItem(-1,  720, 1280, 720)
        ]

        self.borderLines[0].setPen(QtGui.QPen(QtGui.QColorConstants.Svg.red))
        for l in self.borderLines:
            l.setZValue(100000)
            self.theScene.addItem(l)

    def __del__(self):
        self.stop()
        for obj in self.objects:
            obj.obj = None

    def setBackgroundColor(self, color):
        self.setBackgroundBrush(QtGui.QBrush(color))

    def setBorderLines(self, on):
        for l in self.borderLines: l.setVisible(on)

    def reloadObjects(self):
        self.objects.clear()
        for i in range(len(menudata.jsonFile["objects"])):
            obj = menudata.jsonFile["objects"][i]
            pixmapObj = PixmapAnimator(self, obj)
            pixmapObj.pixmapItem.setZValue(i)
            self.objects.append(pixmapObj)

    def getObject(self, obj):
        for graphicsObj in self.objects:
            if graphicsObj.obj == obj: return graphicsObj
        return None

    def stop(self):
        for obj in self.objects: obj.stop()

    def resetToStart(self):
        for obj in self.objects: obj.setFrame(0)

    def start(self):
        for obj in self.objects: obj.start()

    def refresh(self):
        for obj in self.objects: obj.reloadAnimation()
