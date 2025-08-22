# -*- mode: python ; coding: utf-8 -*-

import sys
sys.path.append('.')
from version import __version__

a = Analysis(
    ['model_manager.py'],
    pathex=[],
    binaries=[],
    datas=[('examples/config.json', 'examples'), ('assets/icon.icns', 'assets')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=2,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Claude Model Manager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['assets/icon.icns'],
)

app = BUNDLE(
    exe,
    name='Claude Model Manager.app',
    icon='assets/icon.icns',
    bundle_identifier='com.claude-cli.model-manager',
    version=__version__,
    info_plist={
        'CFBundleShortVersionString': __version__,
        'CFBundleVersion': __version__,
        'NSHumanReadableCopyright': '© 2025 Claude CLI Tools',
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '10.12',
    },
)
