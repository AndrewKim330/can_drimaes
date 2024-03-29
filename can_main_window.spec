# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['can_main_window.py'],
    pathex=[],
    binaries=[],
    hiddenimports=[],
    hookspath=None,
    hooksconfig={},
    runtime_hooks=None,
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    Tree('..\\can_drimaes\\src', prefix='src\\'),
    a.zipfiles,
    a.datas,
    [],
    name='can_new_devide',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='./src/drimaes_icon.ico',
)
