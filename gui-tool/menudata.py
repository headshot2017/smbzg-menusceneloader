import os
import shutil
import json
import copy

from pygame import mixer

import game


name = ""
jsonFile = None
sprites = []

__defaultaction = {
    "frame": [0, 0, 0, 0],
	"delay": 0,
    "offset": [0, 0],
    "scale": [1, 1],
    "angle": 0,
    "color": [255, 255, 255, 255],
    "interpolation": 0
}

def defaultAction(name):
    return copy.deepcopy(__defaultaction[name]) if name in __defaultaction else None

def defaultObject(name):
    return {
        "name": name,
        "sprite": "",
        "filter": False,
        "offset": [0, 0],
        "scale": [1, 1],
        "frames": []
    }

def defaultMenuData():
    return {
        "version": 1,
        "editor": {},
        "backgroundColor": [255, 255, 255],
        "objects": []
    }

def getObject(name):
    for obj in jsonFile["objects"]:
        if obj["name"] == name: return obj
    return None

def getObjectIndex(name):
    for i in range(len(jsonFile["objects"])):
        if jsonFile["objects"][i]["name"] == name: return i
    return -1

def reset(defaultName=""):
    global name, jsonFile
    name = defaultName
    jsonFile = defaultMenuData()
    reloadSprites()

def reloadSprites():
    sprites.clear()
    if not name: return
    for f in os.listdir(game.getMenuPath(name)+"/sprites"):
        sprites.append( os.path.splitext(os.path.basename(game.getMenuPath(name)+"/sprites/"+f))[0] )

def load(menuName):
    global name, jsonFile

    reset()

    path = game.getMenuPath(menuName)

    name = menuName
    jsonFile = json.load(open("%s/menu.json" % path))

    reloadSprites()

    return jsonFile

def save():
    if not name:
        return False

    path = game.getMenuPath(name)
    json.dump(jsonFile, open("%s/menu.json" % path, "w"), indent=2)

    return True
