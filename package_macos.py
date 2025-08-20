#!/usr/bin/env python3
"""
macOS 平台打包脚本 - 生成 .dmg 磁盘映像
使用 py2app 创建 macOS 应用程序包并打包成 .dmg
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

# 检查是否在 macOS 系统上运行
if sys.platform != "darwin":
    print("⚠️  警告：此脚本专为 macOS 平台设计")
    print("   当前系统不是 macOS，继续执行可能会导致问题")
    response = input("是否继续？(y/N): ")
    if response.lower() not in ["y", "yes"]:
        sys.exit(1)


def check_requirements():
    """检查必要的依赖是否已安装"""
    print("🔍 检查依赖...")

    # 检查 py2app
    try:
        import py2app

        print("✅ py2app 已安装")
    except ImportError:
        print("❌ py2app 未安装，正在安装...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "py2app"])

    # 检查 PyQt6
    try:
        import PyQt6

        print("✅ PyQt6 已安装")
    except ImportError:
        print("❌ PyQt6 未安装，正在安装...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "PyQt6"])

    # 检查 create-dmg
    try:
        subprocess.run(["create-dmg", "--version"], check=True, capture_output=True)
        print("✅ create-dmg 已安装")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ create-dmg 未安装")
        print("   安装方法: brew install create-dmg")
        print("   或者使用内置的 hdiutil 创建 DMG")


def create_setup_py():
    """创建 py2app 的 setup.py 文件"""
    setup_content = '''
"""
macOS 应用程序打包配置
使用 py2app 创建 macOS 应用程序包
"""

from setuptools import setup

APP = ['model_manager.py']
DATA_FILES = [
    ('examples', ['examples/config.json']),
]
OPTIONS = {
    'argv_emulation': False,
    'iconfile': 'assets/icon.icns',  # macOS 图标文件
    'plist': {
        'CFBundleName': 'Claude Model Manager',
        'CFBundleDisplayName': 'Claude Model Manager',
        'CFBundleGetInfoString': "Claude CLI 模型管理工具",
        'CFBundleIdentifier': "com.claude-cli.model-manager",
        'CFBundleVersion': "1.0.0",
        'CFBundleShortVersionString': "1.0.0",
        'NSHumanReadableCopyright': u"Copyright © 2024, Claude CLI Tools, All Rights Reserved",
        'NSHighResolutionCapable': True,
        'LSUIElement': False,  # 显示在 Dock 中
        'NSPrincipalClass': 'NSApplication',
        'LSApplicationCategoryType': 'public.app-category.utilities',
        'NSApplicationAppleMenu': True,
        'NSApplicationSupportsAutomaticTermination': True,
        'NSAppTransportSecurity': True,
    },
    'packages': ['PyQt6'],
    'includes': ['PyQt6.QtCore', 'PyQt6.QtGui', 'PyQt6.QtWidgets', "jaraco.text"],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
'''

    with open("setup.py", "w") as f:
        f.write(setup_content)
    print("✅ 已创建 setup.py 配置文件")


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


def build_app():
    """使用 py2app 构建 macOS 应用程序"""
    print("🚀 开始构建 macOS 应用程序...")

    # 清理之前的构建
    safe_rmtree("build")
    safe_rmtree("dist")

    # 创建 setup.py
    create_setup_py()

    # 构建命令
    cmd = [sys.executable, "setup.py", "py2app"]

    try:
        subprocess.check_call(cmd)
        print("✅ 应用程序构建完成！")

        # 获取生成的应用程序路径
        app_path = os.path.join("dist", "Claude Model Manager.app")
        if os.path.exists(app_path):
            print(f"📁 应用程序位置: {os.path.abspath(app_path)}")

            # 计算应用程序大小
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(app_path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    if os.path.exists(fp):
                        total_size += os.path.getsize(fp)

            print(f"📊 应用程序大小: {total_size / (1024*1024):.2f} MB")

            return app_path
        else:
            # 检查其他可能的名称
            possible_names = ["model_manager.app", "Claude Model Manager.app"]
            for name in possible_names:
                test_path = os.path.join("dist", name)
                if os.path.exists(test_path):
                    print(f"📁 应用程序位置: {os.path.abspath(test_path)}")

                    # 计算应用程序大小
                    total_size = 0
                    for dirpath, dirnames, filenames in os.walk(test_path):
                        for f in filenames:
                            fp = os.path.join(dirpath, f)
                            if os.path.exists(fp):
                                total_size += os.path.getsize(fp)

                    print(f"📊 应用程序大小: {total_size / (1024*1024):.2f} MB")
                    return test_path

            print("❌ 构建失败：未找到生成的应用程序")
            return None

    except subprocess.CalledProcessError as e:
        print(f"❌ 构建失败: {e}")
        return None


def debug_app_run(app_path):
    """调试运行打包后的 .app 并输出日志"""
    print("\n🐞 开始调试运行应用程序...")
    exe_path = os.path.join(
        app_path, "Contents", "MacOS", os.path.splitext(os.path.basename(app_path))[0]
    )
    if not os.path.exists(exe_path):
        print(f"❌ 未找到可执行文件: {exe_path}")
        return
    try:
        result = subprocess.run([exe_path], capture_output=True, text=True)
        print("📜 应用运行输出:")
        print(result.stdout)
        if result.stderr:
            print("⚠️ 应用错误输出:")
            print(result.stderr)

        # 保存到日志文件
        with open("app_debug.log", "w", encoding="utf-8") as log_file:
            log_file.write("=== 应用运行输出 ===\n")
            log_file.write(result.stdout)
            if result.stderr:
                log_file.write("\n=== 应用错误输出 ===\n")
                log_file.write(result.stderr)
        print("📝 已将日志保存到 app_debug.log")
    except Exception as e:
        print(f"❌ 调试运行失败: {e}")


def create_dmg(app_path):
    """创建 .dmg 磁盘映像"""
    print("\n📦 开始创建 .dmg 磁盘映像...")

    # 清理之前的 DMG
    dmg_path = "dist/ClaudeModelManager.dmg"
    if os.path.exists(dmg_path):
        os.remove(dmg_path)

    # 检查是否安装了 create-dmg
    try:
        subprocess.run(["create-dmg", "--version"], check=True, capture_output=True)
        use_create_dmg = True
    except (subprocess.CalledProcessError, FileNotFoundError):
        use_create_dmg = False

    if use_create_dmg:
        # 使用 create-dmg 创建更美观的 DMG
        create_dmg_with_create_dmg(app_path, dmg_path)
    else:
        # 使用内置的 hdiutil 创建基本 DMG
        create_dmg_with_hdiutil(app_path, dmg_path)


def create_dmg_with_create_dmg(app_path, dmg_path):
    """使用 create-dmg 创建美观的 DMG"""
    print("🎨 使用 create-dmg 创建美观的磁盘映像...")

    # 创建临时目录
    temp_dir = "temp_dmg"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)

    # 复制应用程序到临时目录
    shutil.copytree(app_path, os.path.join(temp_dir, "Claude Model Manager.app"))

    # create-dmg 命令
    cmd = [
        "create-dmg",
        "--volname",
        "Claude Model Manager",
        "--volicon",
        "assets/icon.icns" if os.path.exists("assets/icon.icns") else "",
        "--background",
        (
            "assets/dmg-background.png"
            if os.path.exists("assets/dmg-background.png")
            else ""
        ),
        "--window-pos",
        "200",
        "120",
        "--window-size",
        "800",
        "400",
        "--icon-size",
        "100",
        "--icon",
        "Claude Model Manager.app",
        "200",
        "190",
        "--hide-extension",
        "Claude Model Manager.app",
        "--app-drop-link",
        "600",
        "185",
        dmg_path,
        temp_dir,
    ]

    # 移除不存在的参数
    cmd = [arg for arg in cmd if arg != ""]

    try:
        subprocess.check_call(cmd)
        print("✅ DMG 创建完成！")
        print(f"📁 DMG 文件位置: {os.path.abspath(dmg_path)}")

        # 清理临时目录
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

    except subprocess.CalledProcessError as e:
        print(f"❌ create-dmg 创建失败: {e}")
        print("   尝试使用 hdiutil 创建基本 DMG...")
        create_dmg_with_hdiutil(app_path, dmg_path)


def create_dmg_with_hdiutil(app_path, dmg_path):
    """使用 hdiutil 创建基本 DMG"""
    print("📁 使用 hdiutil 创建基本磁盘映像...")

    # 创建临时目录
    temp_dir = "temp_dmg"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)

    # 复制应用程序到临时目录
    shutil.copytree(app_path, os.path.join(temp_dir, "Claude Model Manager.app"))

    # 创建 Applications 别名
    applications_link = os.path.join(temp_dir, "Applications")
    if not os.path.exists(applications_link):
        subprocess.run(["ln", "-s", "/Applications", applications_link])

    # 计算所需大小
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(temp_dir):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.exists(fp):
                total_size += os.path.getsize(fp)

    # 添加额外空间
    dmg_size = max(total_size * 1.5, 100 * 1024 * 1024)  # 至少 100MB

    try:
        # 创建 DMG
        subprocess.check_call(
            [
                "hdiutil",
                "create",
                "-srcfolder",
                temp_dir,
                "-volname",
                "Claude Model Manager",
                "-format",
                "UDZO",
                "-size",
                f"{int(dmg_size / 1024 / 1024)}m",
                dmg_path,
            ]
        )

        print("✅ DMG 创建完成！")
        print(f"📁 DMG 文件位置: {os.path.abspath(dmg_path)}")

        # 清理临时目录
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

    except subprocess.CalledProcessError as e:
        print(f"❌ hdiutil 创建失败: {e}")


def create_app_icon():
    """创建 macOS 应用程序图标（如果缺少）"""
    icon_path = "assets/icon.icns"
    if not os.path.exists(icon_path):
        print("⚠️  未找到 macOS 图标文件 assets/icon.icns")
        print("   建议创建 1024x1024 的 ICNS 图标文件")

        # 创建简单的图标目录结构（可选）
        os.makedirs("assets", exist_ok=True)

        # 提示用户创建图标
        print("   可以使用在线工具将 PNG 转换为 ICNS")
        print("   或使用 macOS 的 iconutil 工具创建")


def codesign_app(app_path):
    """代码签名应用程序（可选）"""
    print("\n🔐 是否对应用程序进行代码签名？")
    print("   这需要有效的 Apple Developer 证书")

    response = input("是否进行代码签名？(y/N): ")
    if response.lower() not in ["y", "yes"]:
        return

    # 检查是否有签名证书
    try:
        result = subprocess.run(
            ["security", "find-identity", "-v", "-p", "codesigning"],
            capture_output=True,
            text=True,
        )
        if "0 valid identities found" in result.stdout:
            print("❌ 未找到有效的代码签名证书")
            print("   请在 Xcode 中配置开发者证书")
            return

        print("🔍 找到以下签名证书:")
        print(result.stdout)
        identity = input("请输入要使用的证书标识符: ").strip()

        if identity:
            # 签名应用程序
            subprocess.check_call(
                ["codesign", "--force", "--deep", "--sign", identity, app_path]
            )
            print("✅ 应用程序签名完成")

    except subprocess.CalledProcessError as e:
        print(f"❌ 签名失败: {e}")


def notarize_app(app_path):
    """公证应用程序（可选，需要 Apple Developer 账户）"""
    print("\n🍎 是否对应用程序进行公证？")
    print("   这需要 Apple Developer 账户和 App Store Connect API 密钥")

    response = input("是否进行公证？(y/N): ")
    if response.lower() not in ["y", "yes"]:
        return

    print("⚠️  公证功能需要手动配置")
    print("   请参考 Apple 文档进行公证设置")
    print(
        "   https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution"
    )


def main():
    """主函数"""
    print("🍎 macOS 平台打包脚本")
    print("=" * 50)

    # 检查依赖
    check_requirements()

    # 检查图标
    create_app_icon()

    # 构建应用程序
    app_path = build_app()

    if app_path:
        print("\n🎉 应用程序构建成功！")
        print("📁 应用程序位置:", os.path.abspath(app_path))

        debug_app_run(app_path)

        # 代码签名（可选）
        # codesign_app(app_path)

        # # 公证（可选）
        # notarize_app(app_path)

        # 创建 DMG
        create_dmg(app_path)

        print("\n🎊 打包完成！")
        print("📦 DMG 文件: ClaudeModelManager.dmg")

    else:
        print("\n❌ 打包失败，请检查错误信息")
        sys.exit(1)


if __name__ == "__main__":
    main()
