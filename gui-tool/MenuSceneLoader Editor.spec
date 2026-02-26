# -*- mode: python ; coding: utf-8 -*-


import UnityPy, archspec, fmod_toolkit, os

module_path_func = lambda module: lambda path: os.path.join(
    os.path.dirname(module.__file__), path
)

unitypy_path = module_path_func(UnityPy)
archspec_path = module_path_func(archspec)
fmod_toolkit_path = module_path_func(fmod_toolkit)
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[(fmod_toolkit_path("libfmod"), "fmod_toolkit/libfmod")],
    datas=[
        (unitypy_path("resources/*"), "UnityPy/resources"),
        (archspec_path('json'), 'archspec/json')
    ],
    hiddenimports=['colorgraphicsview', 'animatorwidgets', 'animatorgraphicsview'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='MenuSceneLoader Editor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
