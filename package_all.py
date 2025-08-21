#!/usr/bin/env python3
"""
统一打包脚本 - 支持 Windows 和 macOS 平台
自动检测当前系统并执行相应的打包流程
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def print_banner():
    """打印欢迎横幅"""
    print("=" * 60)
    print("🚀 Claude Model Manager 统一打包工具")
    print("=" * 60)
    print(f"操作系统: {platform.system()} {platform.release()}")
    print(f"Python版本: {sys.version}")
    print("=" * 60)


def detect_platform():
    """检测当前操作系统"""
    system = platform.system()
    if system == "Windows":
        return "windows"
    elif system == "Darwin":
        return "macos"
    else:
        return "linux"


def check_python_version():
    """检查Python版本是否满足要求"""
    if sys.version_info < (3, 8):
        print("❌ Python 版本过低，需要 3.8 或更高版本")
        sys.exit(1)
    print("✅ Python 版本检查通过")


def install_dependencies():
    """安装通用依赖"""
    print("\n📦 安装依赖包...")

    dependencies = ["PyQt6"]

    # 根据平台添加特定依赖
    current_platform = detect_platform()
    if current_platform == "windows":
        dependencies.extend(["pyinstaller", "winshell", "pywin32"])
    elif current_platform == "macos":
        dependencies.extend(["pyinstaller"])

    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep} 已安装")
        except ImportError:
            print(f"📥 正在安装 {dep}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])


def run_platform_specific_script():
    """运行平台特定的打包脚本"""
    current_platform = detect_platform()

    if current_platform == "windows":
        script = "package_windows_pyinstaller.py"
    elif current_platform == "macos":
        script = "package_macos_pyinstaller.py"
    else:
        print("❌ 不支持的平台:", platform.system())
        print("目前支持: Windows 和 macOS")
        sys.exit(1)

    if not os.path.exists(script):
        print(f"❌ 找不到打包脚本: {script}")
        sys.exit(1)

    print(f"\n🎯 运行 {current_platform} 平台打包脚本...")
    try:
        subprocess.check_call([sys.executable, script])
    except subprocess.CalledProcessError as e:
        print(f"❌ 打包失败: {e}")
        sys.exit(1)


def create_assets_directory():
    """创建资源目录"""
    assets_dir = Path("assets")
    assets_dir.mkdir(exist_ok=True)

    # 创建占位图标文件说明
    icon_readme = assets_dir / "README.md"
    if not icon_readme.exists():
        with open(icon_readme, "w") as f:
            f.write(
                """# 图标文件说明

## Windows 图标
- 文件名: icon.ico
- 尺寸: 256x256 像素
- 格式: ICO

## macOS 图标
- 文件名: icon.icns
- 尺寸: 1024x1024 像素
- 格式: ICNS

## 创建方法
1. 准备 1024x1024 PNG 文件
2. 使用在线转换工具或专业软件转换格式
3. 将文件放入此目录

## 在线工具推荐
- Windows: https://convertico.com/
- macOS: https://iconverticons.com/online/
"""
            )


def show_help():
    """显示帮助信息"""
    help_text = """
使用方法:
    python package_all.py [选项]

选项:
    --help, -h      显示此帮助信息
    --check         检查系统环境和依赖
    --install       仅安装依赖，不打包
    --clean         清理构建文件

示例:
    python package_all.py          # 自动检测平台并打包
    python package_all.py --check  # 检查环境
    python package_all.py --clean  # 清理构建文件
"""
    print(help_text)


def check_environment():
    """检查系统环境"""
    print("\n🔍 系统环境检查:")

    # 检查Python版本
    check_python_version()

    # 检查平台
    current_platform = detect_platform()
    print(f"✅ 平台: {current_platform}")

    # 检查依赖
    print("\n📋 依赖检查:")
    dependencies = {
        "windows": ["PyQt6", "PyInstaller"],
        "macos": ["PyQt6", "py2app"],
        "linux": ["PyQt6"],
    }

    platform_deps = dependencies.get(current_platform, [])
    for dep in platform_deps:
        try:
            __import__(dep)
            print(f"✅ {dep}")
        except ImportError:
            print(f"❌ {dep} - 需要安装")

    # 检查可选工具
    print("\n🔧 可选工具检查:")
    if current_platform == "windows":
        try:
            subprocess.run(["where", "makensis"], capture_output=True, check=True)
            print("✅ NSIS (安装程序创建工具)")
        except:
            print("⚠️  NSIS 未安装 - 无法创建安装程序")

    elif current_platform == "macos":
        try:
            subprocess.run(["which", "create-dmg"], capture_output=True, check=True)
            print("✅ create-dmg (美观DMG创建工具)")
        except:
            print("⚠️  create-dmg 未安装 - 将使用基本DMG创建")


def clean_build_files():
    """清理构建文件"""
    print("\n🧹 清理构建文件...")

    dirs_to_clean = ["build", "dist", "__pycache__", "*.egg-info"]
    files_to_clean = ["*.spec", "*.pyc", "*.pyo"]

    cleaned = 0

    # 清理目录
    for pattern in dirs_to_clean:
        import glob

        for path in glob.glob(pattern):
            if os.path.isdir(path):
                shutil.rmtree(path)
                print(f"✅ 已删除目录: {path}")
                cleaned += 1

    # 清理文件
    for pattern in files_to_clean:
        import glob

        for path in glob.glob(pattern):
            if os.path.isfile(path):
                os.remove(path)
                print(f"✅ 已删除文件: {path}")
                cleaned += 1

    if cleaned == 0:
        print("✅ 无需清理")
    else:
        print(f"✅ 共清理 {cleaned} 个文件/目录")


def main():
    """主函数"""
    print_banner()

    # 处理命令行参数
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ["--help", "-h"]:
            show_help()
            return
        elif arg == "--check":
            check_environment()
            return
        elif arg == "--install":
            install_dependencies()
            return
        elif arg == "--clean":
            clean_build_files()
            return

    # 默认行为：检查环境并打包
    check_environment()
    create_assets_directory()
    install_dependencies()
    run_platform_specific_script()

    print("\n" + "=" * 60)
    print("🎉 打包完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
