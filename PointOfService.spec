from PyInstaller.utils.hooks import collect_data_files

# -*- mode: python ; coding: utf-8 -*-

datas = collect_data_files("escpos")

datas += [
    ("D:/doc/PycharmProjects/PointOfService/ui/*.ui", "ui"),
]
datas += [
    ("D:/doc/PycharmProjects/PointOfService/assets/logo.png", "assets"),
]
datas += [
    ("D:/doc/PycharmProjects/PointOfService/assets/mPos.db", "assets"),
]
datas += [
    ("D:/doc/PycharmProjects/PointOfService/config/config.json", "config"),
]
datas += [
    ("D:/doc/PycharmProjects/PointOfService/config/version.json", "config"),
]
a = Analysis(
    ['D:\\doc\\PycharmProjects\\PointOfService\\src\\main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='PointOfService',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PointOfService',
)
