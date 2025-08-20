#!/usr/bin/env python3
"""
Windows 平台打包脚本 - 生成 .exe 可执行文件
使用 PyInstaller 创建独立的 Windows 可执行文件
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

# 检查是否在 Windows 系统上运行
if sys.platform != "win32":
    print("⚠️  警告：此脚本专为 Windows 平台设计")
    print("   当前系统不是 Windows，继续执行可能会导致问题")
    response = input("是否继续？(y/N): ")
    if response.lower() not in ["y", "yes"]:
        sys.exit(1)


def check_requirements():
    """检查必要的依赖是否已安装"""
    print("🔍 检查依赖...")

    # 检查 PyInstaller
    try:
        import PyInstaller

        print("✅ PyInstaller 已安装")
    except ImportError:
        print("❌ PyInstaller 未安装，正在安装...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # 检查 PyQt6
    try:
        import PyQt6

        print("✅ PyQt6 已安装")
    except ImportError:
        print("❌ PyQt6 未安装，正在安装...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "PyQt6"])


def build_exe():
    """使用 PyInstaller 构建 Windows 可执行文件"""
    print("🚀 开始构建 Windows 可执行文件...")

    # 清理之前的构建
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")

    # PyInstaller 命令
    cmd = [
        "pyinstaller",
        "--onefile",  # 打包成单个文件
        "--windowed",  # 窗口程序（无控制台）
        "--name=ClaudeModelManager",  # 可执行文件名
        "--icon=assets/icon.ico",  # 图标文件（如果有的话）
        "--add-data=examples/config.json;examples",  # 添加配置文件
        "--clean",  # 清理临时文件
        "--noconfirm",  # 不确认覆盖
        "model_manager.py",  # 主程序文件
    ]

    # 如果没有图标文件，移除图标参数
    if not os.path.exists("assets/icon.ico"):
        cmd = [arg for arg in cmd if not arg.startswith("--icon=")]
        print("⚠️  未找到图标文件 assets/icon.ico，将使用默认图标")

    try:
        subprocess.check_call(cmd)
        print("✅ 构建完成！")

        # 获取生成的可执行文件路径
        exe_path = os.path.join("dist", "ClaudeModelManager.exe")
        if os.path.exists(exe_path):
            print(f"📁 可执行文件位置: {os.path.abspath(exe_path)}")
            print(f"📊 文件大小: {os.path.getsize(exe_path) / (1024*1024):.2f} MB")

            # 创建桌面快捷方式
            create_desktop_shortcut(exe_path)

            return exe_path
        else:
            print("❌ 构建失败：未找到生成的可执行文件")
            return None

    except subprocess.CalledProcessError as e:
        print(f"❌ 构建失败: {e}")
        return None


def create_desktop_shortcut(exe_path):
    """创建桌面快捷方式"""
    try:
        import winshell
        from win32com.client import Dispatch

        desktop = winshell.desktop()
        path = os.path.join(desktop, "Claude Model Manager.lnk")
        target = exe_path
        wDir = os.path.dirname(exe_path)

        shell = Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = target
        shortcut.WorkingDirectory = wDir
        shortcut.save()

        print("✅ 已在桌面创建快捷方式")

    except ImportError:
        print("⚠️  无法创建桌面快捷方式（缺少 winshell 或 pywin32）")
        print("   请手动创建快捷方式或安装: pip install winshell pywin32")
    except Exception as e:
        print(f"⚠️  创建快捷方式失败: {e}")


def create_installer():
    """创建 Windows 安装程序（可选）"""
    print("\n📦 是否创建 Windows 安装程序？")
    print("   这需要安装 NSIS (Nullsoft Scriptable Install System)")

    response = input("是否创建安装程序？(y/N): ")
    if response.lower() not in ["y", "yes"]:
        return

    # 检查 NSIS 是否安装
    nsis_path = None
    possible_paths = [
        "C:\\Program Files (x86)\\NSIS\\makensis.exe",
        "C:\\Program Files\\NSIS\\makensis.exe",
    ]

    for path in possible_paths:
        if os.path.exists(path):
            nsis_path = path
            break

    if not nsis_path:
        print("❌ 未找到 NSIS，请先安装 NSIS")
        print("   下载地址: https://nsis.sourceforge.io/Download")
        return

    # 创建 NSIS 脚本
    nsis_script = f"""
; Claude Model Manager 安装程序
!define APP_NAME "Claude Model Manager"
!define APP_VERSION "1.0.0"
!define APP_PUBLISHER "Claude CLI Tools"
!define APP_URL "https://github.com/liuyihua2015/claude-other-ai-large-model-tool"
!define APP_EXE "ClaudeModelManager.exe"

OutFile "ClaudeModelManager_Setup.exe"
InstallDir "$PROGRAMFILES\\Claude Model Manager"
InstallDirRegKey HKLM "Software\\Claude Model Manager" "Install_Dir"
RequestExecutionLevel admin

; 包含现代界面
!include "MUI2.nsh"

; 定义界面设置
!define MUI_ABORTWARNING
!define MUI_ICON "assets\\icon.ico"
!define MUI_UNICON "assets\\icon.ico"

; 页面
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; 卸载页面
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; 语言
!insertmacro MUI_LANGUAGE "English"

Section "主程序" SecMain
    SetOutPath "$INSTDIR"
    File /r "dist\\*.*"
    
    ; 创建桌面快捷方式
    CreateShortCut "$DESKTOP\\Claude Model Manager.lnk" "$INSTDIR\\ClaudeModelManager.exe"
    
    ; 创建开始菜单快捷方式
    CreateDirectory "$SMPROGRAMS\\Claude Model Manager"
    CreateShortCut "$SMPROGRAMS\\Claude Model Manager\\Claude Model Manager.lnk" "$INSTDIR\\ClaudeModelManager.exe"
    CreateShortCut "$SMPROGRAMS\\Claude Model Manager\\卸载.lnk" "$INSTDIR\\uninstall.exe"
    
    ; 写入注册表
    WriteRegStr HKLM "Software\\Claude Model Manager" "Install_Dir" "$INSTDIR"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Claude Model Manager" "DisplayName" "Claude Model Manager"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Claude Model Manager" "UninstallString" '"$INSTDIR\\uninstall.exe"'
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Claude Model Manager" "NoModify" 1
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Claude Model Manager" "NoRepair" 1
    
    ; 创建卸载程序
    WriteUninstaller "uninstall.exe"
SectionEnd

Section "卸载"
    Delete "$INSTDIR\\*.*"
    RMDir "$INSTDIR"
    Delete "$DESKTOP\\Claude Model Manager.lnk"
    Delete "$SMPROGRAMS\\Claude Model Manager\\*.*"
    RMDir "$SMPROGRAMS\\Claude Model Manager"
    DeleteRegKey HKLM "Software\\Claude Model Manager"
    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\Claude Model Manager"
SectionEnd
"""

    # 保存 NSIS 脚本
    with open("installer.nsi", "w", encoding="utf-8") as f:
        f.write(nsis_script)

    # 运行 NSIS 编译
    try:
        subprocess.check_call([nsis_path, "installer.nsi"])
        print("✅ 安装程序创建完成: ClaudeModelManager_Setup.exe")
    except subprocess.CalledProcessError as e:
        print(f"❌ 安装程序创建失败: {e}")


def main():
    """主函数"""
    print("🪟 Windows 平台打包脚本")
    print("=" * 50)

    # 检查依赖
    check_requirements()

    # 构建可执行文件
    exe_path = build_exe()

    if exe_path:
        print("\n🎉 打包成功！")
        print("📁 可执行文件位置:", os.path.abspath(exe_path))

        # 询问是否创建安装程序
        create_installer()
    else:
        print("\n❌ 打包失败，请检查错误信息")
        sys.exit(1)


if __name__ == "__main__":
    main()
