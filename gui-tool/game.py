import os

import clr
import System
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

    try:
        assembly = clr.AddReference("%s/SMBZ-G_Data/Managed/Assembly-CSharp" % smbzgPath)
    except System.IO.FileLoadException:
        QtWidgets.QMessageBox.critical(None, "Error",
            "Failed to open Assembly-CSharp.dll!\n" +
            "\n" +
            "If you're on Windows, try this to fix the problem:\n" +
            "1. Open 'SMBZ-G\\SMBZ-G_Data\\Managed' on the file explorer\n" +
            "2. Right-click 'Assembly-CSharp.dll', select Properties\n" +
            "3. Click 'Unblock' at the bottom right, then save"
        )

    return assembly != None

def getMenuPath(name):
    return "%s/%s" % (customMenusPath, name)

def askGamePath():
    fileName, type = QtWidgets.QFileDialog.getOpenFileName(None, "Find SMBZ-G.exe", ".", "SMBZ-G.exe")
    print("Game path: %s" % os.path.dirname(fileName))
    return os.path.dirname(fileName)
