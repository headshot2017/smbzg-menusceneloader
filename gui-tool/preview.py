import datetime
import io
import os

from pygame import mixer
from PyQt5 import QtWidgets, QtCore, QtGui, uic
import UnityPy
from UnityPy.helpers.TypeTreeGenerator import TypeTreeGenerator

import game
import menudata


class PreviewWindow(QtWidgets.QMainWindow):
    hidden = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        uic.loadUi("ui/preview.ui", self)

        self.action640x360.triggered.connect(self.onAction640x360)
        self.action1280x720.triggered.connect(self.onAction1280x720)
        self.action1920x1080.triggered.connect(self.onAction1920x1080)
        self.action640x480.triggered.connect(self.onAction640x480)
        self.action800x600.triggered.connect(self.onAction800x600)
        self.action1024x768.triggered.connect(self.onAction1024x768)

        self.setCentralWidget(self.graphicsView)
        self.setFixedSize(1280, 720+24)

        self.logo = QtWidgets.QGraphicsPixmapItem()
        self.graphicsView.theScene.addItem(self.logo)
        self.logo.setPixmap(QtGui.QPixmap("images/SMBZ_game_logo.png"))
        self.logo.setOffset(-self.logo.pixmap().width()/2, 0)
        self.logo.setScale(1.25)
        self.logo.setPos(1280/2, 0)
        self.logo.setZValue(100000)

        self.time = QtWidgets.QGraphicsTextItem(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        self.graphicsView.theScene.addItem(self.time)
        self.time.setScale(2)
        self.time.setPos(1280 - self.time.boundingRect().width()*2, 0)
        self.time.setZValue(100000)

        if "backgroundColor" in menudata.jsonFile:
            self.graphicsView.setBackgroundColor(QtGui.QColor(*menudata.jsonFile["backgroundColor"]))

        self.channel = None
        if os.path.exists(game.getMenuPath(menudata.name)+"/start.ogg"):
            mixer.init()
            self.intro = mixer.Sound(game.getMenuPath(menudata.name)+"/start.ogg")
            self.loop = mixer.Sound(game.getMenuPath(menudata.name)+"/loop.ogg")
            self.channel = self.intro.play()
            self.channel.queue(self.loop)
        elif os.path.exists(game.getMenuPath(menudata.name)+"/loop.ogg"):
            mixer.init()
            self.loop = mixer.Sound(game.getMenuPath(menudata.name)+"/loop.ogg")
            self.channel = self.loop.play(loops=-1)
        elif "vanillaMusic" in menudata.jsonFile:
            # extract the AudioClip from Unity game data
            assets = UnityPy.load(game.smbzgPath+"/SMBZ-G_Data/sharedassets0.assets")
            env = UnityPy.load(game.smbzgPath+"/SMBZ-G_Data/level0")

            generator = TypeTreeGenerator(env.file.unity_version)
            generator.load_local_game(game.smbzgPath)
            env.typetree_generator = generator

            # search for SoundCache class
            matches = [obj for obj in env.objects if obj.type.name == 'MonoBehaviour' and obj.parse_as_object().get_type() == 'SoundCache']
            if matches:
                soundcache = matches[0].parse_as_dict()

                # find the wanted AudioClip field in SoundCache
                name = menudata.jsonFile["vanillaMusic"]
                pathID = (soundcache.get(name) or soundcache.get("BGM_"+name))["m_PathID"]

                # use the path ID to get the actual audio clip from sharedassets0.assets
                matches = [obj for obj in assets.objects if obj.type.name == 'AudioClip' and obj.path_id == pathID]
                if matches:
                    clip = matches[0].parse_as_object()
                    for name, data in clip.samples.items(): # it's only one item
                        mixer.init(frequency=clip.m_Frequency, channels=clip.m_Channels, allowedchanges=0)
                        self.loop = mixer.Sound(buffer=data)
                        self.channel = self.loop.play(loops=-1)


        self.graphicsView.setBorderLines(False)
        self.graphicsView.reloadObjects()
        self.graphicsView.start()

    def hideEvent(self, event):
        self.hidden.emit()

    def stop(self):
        if self.channel: self.channel.stop()
        if mixer.get_init(): mixer.quit()
        self.graphicsView.stop()

    def resizePreview(self, w, h):
        self.setFixedSize(w, h+24)
        self.graphicsView.fitInView(self.graphicsView.theScene.sceneRect(), QtCore.Qt.KeepAspectRatio)

        r = h/w
        itemsHeight = 1280*r
        self.logo.setY(720 - itemsHeight)
        self.time.setY(720 - itemsHeight)

    @QtCore.pyqtSlot()
    def onAction640x360(self):
        self.resizePreview(640, 360)

    @QtCore.pyqtSlot()
    def onAction1280x720(self):
        self.resizePreview(1280, 720)

    @QtCore.pyqtSlot()
    def onAction1920x1080(self):
        self.resizePreview(1920, 1080)

    @QtCore.pyqtSlot()
    def onAction640x480(self):
        self.resizePreview(640, 480)

    @QtCore.pyqtSlot()
    def onAction800x600(self):
        self.resizePreview(800, 600)

    @QtCore.pyqtSlot()
    def onAction1024x768(self):
        self.resizePreview(1024, 768)
