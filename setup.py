"""
macOS 应用程序打包配置
使用 py2app 创建 macOS 应用程序包
"""

from setuptools import setup

APP = ["model_manager.py"]
DATA_FILES = [
    ("examples", ["examples/config.json"]),
]
OPTIONS = {
    "argv_emulation": False,
    "iconfile": "assets/icon.icns",  # macOS 图标文件
    "plist": {
        "CFBundleName": "Claude Model Manager",
        "CFBundleDisplayName": "Claude Model Manager",
        "CFBundleGetInfoString": "Claude CLI 模型管理工具",
        "CFBundleIdentifier": "com.claude-cli.model-manager",
        "CFBundleVersion": "1.0.2",
        "CFBundleShortVersionString": "1.0.2",
        "NSHumanReadableCopyright": "Copyright © 2024-2025, Claude CLI Tools, All Rights Reserved",
        "NSHighResolutionCapable": True,
        "LSUIElement": False,  # 显示在 Dock 中
        "NSPrincipalClass": "NSApplication",
        "LSApplicationCategoryType": "public.app-category.utilities",
        "NSApplicationAppleMenu": True,
        "NSApplicationSupportsAutomaticTermination": True,
        "NSAppTransportSecurity": True,
    },
    "packages": ["PyQt6"],
    "includes": ["PyQt6.QtCore", "PyQt6.QtGui", "PyQt6.QtWidgets", "jaraco.text"],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=["py2app"],
)
