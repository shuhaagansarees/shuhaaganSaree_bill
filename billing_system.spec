# -*- mode: python ; coding: utf-8 -*-
# Build with:  pyinstaller billing_system.spec --clean

from PyInstaller.utils.hooks import collect_all

pil_datas, pil_binaries, pil_hidden = collect_all('PIL')
rl_datas, rl_binaries, rl_hidden = collect_all('reportlab')
qr_datas, qr_binaries, qr_hidden = collect_all('qrcode')

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[] + pil_binaries + rl_binaries + qr_binaries,
    datas=[('assets', 'assets')] + pil_datas + rl_datas + qr_datas,
    hiddenimports=[
        'billing',
        'config',
        'flask',
        'jinja2',
        'werkzeug',
        'openpyxl',
        'waitress',
    ] + pil_hidden + rl_hidden + qr_hidden,
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
    [],
    exclude_binaries=True,
    name='billing_system',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,   # keep the console window: it now shows real status/errors
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
    name='billing_system',
)
