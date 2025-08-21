#!/usr/bin/env python3
"""
Windows 平台打包脚本 - 使用 PyInstaller 生成 Windows 可执行文件
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


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


def safe_rmtree(path):
    """安全地删除目录，处理.DS_Store等隐藏文件"""
    if not os.path.exists(path):
        return

    def handle_remove_readonly(func, path, exc):
        """处理只读文件和权限问题"""
        import stat

        os.chmod(path, stat.S_IWRITE)
        func(path)

    try:
        shutil.rmtree(path, onerror=handle_remove_readonly)
    except PermissionError:
        print(f"⚠️ 权限不足，尝试使用 sudo 删除 {path}")
        subprocess.run(["sudo", "rm", "-rf", path])
    except Exception as e:
        print(f"⚠️ 删除 {path} 时出错: {e}")


def build_windows():
    """使用 PyInstaller 构建 Windows 可执行文件"""
    print("🚀 开始构建 Windows 应用程序（使用 PyInstaller）单文件模式 ...")

    # 清理之前的构建
    safe_rmtree("build")
    safe_rmtree("dist")
    safe_rmtree("spec")

    # PyInstaller 命令 - Windows 优化配置
    cmd = [
        "pyinstaller",
        "--onefile",  # 打包成单个文件
        "--windowed",  # 窗口程序（无控制台）
        "--name=Claude Model Manager",  # 应用程序名
        "--icon=assets/icon.ico",  # Windows 图标文件
        "--add-data=examples/config.json;examples",  # 添加配置文件，Windows路径分隔符为分号
        "--add-data=assets/icon.ico;assets",  # 添加图标文件
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
        print("✅ Windows 应用程序构建完成！")

        # 获取生成的可执行文件路径
        exe_path = os.path.join("dist", "Claude Model Manager.exe")
        if os.path.exists(exe_path):
            print(f"📁 可执行文件位置: {os.path.abspath(exe_path)}")
            print(f"📊 文件大小: {os.path.getsize(exe_path) / (1024*1024):.2f} MB")
            return exe_path

        print("❌ 构建失败：未找到生成的可执行文件")
        return None

    except subprocess.CalledProcessError as e:
        print(f"❌ 构建失败: {e}")
        return None


def main():
    """主函数"""
    print("🪟 Windows 平台打包脚本 (PyInstaller 版)")
    print("=" * 50)

    # 检查依赖
    check_requirements()

    exe_path = build_windows()

    if exe_path:
        print("\n🎉 应用程序构建成功！")
        print("📁 可执行文件位置:", os.path.abspath(exe_path))
        print(f"📊 可执行文件大小: {os.path.getsize(exe_path) / (1024*1024):.2f} MB")
        print("\n🎊 打包完成！")
    else:
        print("\n❌ 打包失败，请检查错误信息")
        sys.exit(1)


if __name__ == "__main__":
    main()
