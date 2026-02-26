# MenuSceneLoader

Custom menu scenario loader for SMBZ-G.

Requires [MelonLoader](https://github.com/LavaGang/MelonLoader/releases)

## Custom menu scenes folder structure
```
└── SMBZ-G_Data
    └── StreamingAssets
        └── MenuScenes
            └── (Menu scene name)
                ├── sprites/
                │   └── .png files
                ├── intro.ogg (OPTIONAL)
                ├── loop.ogg (OPTIONAL)
                └── menu.json
```

* **sprites:** Folder containing PNG files that can be used as the sprites for the menu scene's objects.
* **intro.ogg**: Optional music file that can be used as the menu scene's intro music.
* **loop.ogg**: Optional music file that can be used as the menu scene's looping music.
* **menu.json**: Contains the data for the menu scene.

It's recommended to use the MenuSceneLoader Editor program for animating the menu scene instead of editing menu.json by hand.

## Third-party libraries

* [TinyJSON](https://github.com/pbhogan/TinyJSON)
