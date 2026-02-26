import os

import clr
from PyQt5 import QtWidgets


assembly = None
smbzgPath = ""
customMenusPath = ""


def init():
    global assembly, smbzgPath, customMenusPath

    if os.path.exists("smbzg-path.txt"):
        smbzgPath = open("smbzg-path.txt").read()

    if not smbzgPath or not os.path.exists(smbzgPath):
        smbzgPath = askGamePath()

        if not smbzgPath:
            return False

        open("smbzg-path.txt", "w").write(smbzgPath)

    customMenusPath = "%s/SMBZ-G_Data/StreamingAssets/MenuScenes" % smbzgPath

    assembly = clr.AddReference("%s/SMBZ-G_Data/Managed/Assembly-CSharp" % smbzgPath)
    if not assembly:
        return False

    return True

def getMenuPath(name):
    return "%s/%s" % (customMenusPath, name)

def askGamePath():
    fileName, type = QtWidgets.QFileDialog.getOpenFileName(None, "Find SMBZ-G.exe", ".", "SMBZ-G.exe")
    print("Game path: %s" % os.path.dirname(fileName))
    return os.path.dirname(fileName)
