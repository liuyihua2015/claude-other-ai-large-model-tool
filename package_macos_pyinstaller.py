#!/usr/bin/env python3
"""
macOS 平台打包脚本 - 使用 PyInstaller 减少包体积
生成轻量级的 macOS 应用程序包
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


def build_app():
    """使用 PyInstaller 构建 macOS 应用程序"""
    print("🚀 开始构建 macOS 应用程序（使用 PyInstaller）单文件模式 ...")

    # 清理之前的构建
    safe_rmtree("build")
    safe_rmtree("dist")
    safe_rmtree("spec")

    # PyInstaller 命令 - 优化配置以减少体积
    cmd = [
        "pyinstaller",
        "--onefile",  # 打包成单个文件（更小的体积）
        "--windowed",  # 窗口程序（无控制台）
        "--name=Claude Model Manager",  # 应用程序名
        "--icon=assets/icon.icns",  # macOS 图标文件
        "--add-data=examples/config.json:examples",  # 添加配置文件
        "--add-data=assets/icon.icns:assets",  # 添加图标文件
        "--clean",  # 清理临时文件
        "--noconfirm",  # 不确认覆盖
        "--strip",  # 移除调试符号
        "--optimize=2",  # Python 优化级别
        "model_manager.py",  # 主程序文件
    ]

    # 如果没有图标文件，移除图标参数
    if not os.path.exists("assets/icon.icns"):
        cmd = [arg for arg in cmd if not arg.startswith("--icon=")]
        print("⚠️  未找到图标文件 assets/icon.icns，将使用默认图标")

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
            # 检查单个可执行文件
            exe_path = os.path.join("dist", "Claude Model Manager")
            if os.path.exists(exe_path):
                print(f"📁 可执行文件位置: {os.path.abspath(exe_path)}")
                print(f"📊 文件大小: {os.path.getsize(exe_path) / (1024*1024):.2f} MB")
                return exe_path

            print("❌ 构建失败：未找到生成的应用程序")
            return None

    except subprocess.CalledProcessError as e:
        print(f"❌ 构建失败: {e}")
        return None


def build_app_bundle():
    """使用 PyInstaller 构建 macOS .app 包（更完整的应用包）"""
    print("🚀 开始构建 macOS .app 应用程序包...")

    # 清理之前的构建
    safe_rmtree("build")
    safe_rmtree("dist")
    safe_rmtree("spec")

    # PyInstaller 命令 - 创建完整的 .app 包
    cmd = [
        "pyinstaller",
        "model_manager.py",
        "--onedir",
        "--windowed",
        "--name=Claude Model Manager",
        "--icon=assets/icon.icns",
        "--add-data=examples/config.json:examples",
        "--add-data=assets/icon.icns:assets",
        "--osx-bundle-identifier=com.claude-cli.model-manager",
        "--clean",
        "--noconfirm",
        "--strip",
        "--optimize=2",
    ]

    # 如果没有图标文件，移除图标参数
    if not os.path.exists("assets/icon.icns"):
        cmd = [arg for arg in cmd if not arg.startswith("--icon=")]
        print("⚠️  未找到图标文件 assets/icon.icns，将使用默认图标")

    try:
        subprocess.check_call(cmd)
        print("✅ .app 应用程序包构建完成！")

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

        print("❌ 构建失败：未找到生成的应用程序")
        return None

    except subprocess.CalledProcessError as e:
        print(f"❌ 构建失败: {e}")
        return None


def debug_app_run(app_path):
    """调试运行打包后的应用程序"""
    print("\n🐞 开始调试运行应用程序...")

    if app_path.endswith(".app"):
        # 运行 .app 包
        exe_path = os.path.join(app_path, "Contents", "MacOS", "Claude Model Manager")
    else:
        # 运行单个可执行文件
        exe_path = app_path

    if not os.path.exists(exe_path):
        print(f"❌ 未找到可执行文件: {exe_path}")
        return

    try:
        # 设置环境变量以避免 macOS 安全警告
        env = os.environ.copy()
        env["QT_MAC_WANTS_LAYER"] = "1"

        result = subprocess.run(
            [exe_path], capture_output=True, text=True, env=env, timeout=10
        )
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
    except subprocess.TimeoutExpired:
        print("✅ 应用程序启动成功（运行超时，这是正常的）")
    except Exception as e:
        print(f"❌ 调试运行失败: {e}")


def create_dmg(app_path):
    """创建 .dmg 磁盘映像"""
    print("\n📦 开始创建 .dmg 磁盘映像...")

    # 清理之前的 DMG
    dmg_path = "dist/Claude Model Manager.dmg"
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
    app_name = os.path.basename(app_path)
    shutil.copytree(app_path, os.path.join(temp_dir, app_name))

    # 组装 create-dmg 命令参数，避免空字符串导致的错误
    cmd = [
        "create-dmg",
        "--volname",
        "Claude Model Manager",
    ]

    icon_path = "assets/icon.icns"
    if os.path.exists(icon_path):
        cmd.extend(["--volicon", icon_path])

    background_path = "assets/dmg-background.png"
    if os.path.exists(background_path):
        cmd.extend(["--background", background_path])

    cmd.extend(
        [
            "--window-pos",
            "200",
            "120",
            "--window-size",
            "800",
            "400",
            "--icon-size",
            "100",
            "--icon",
            app_name,
            "200",
            "190",
            "--hide-extension",
            app_name,
            "--app-drop-link",
            "600",
            "185",
            dmg_path,
            temp_dir,
        ]
    )

    try:
        subprocess.check_call(cmd)
        print("✅ DMG 创建完成！")
        print(f"📁 DMG 文件位置: {os.path.abspath(dmg_path)}")

        # 清理临时目录
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

        # 注释掉自动打开 DMG 的代码
        # subprocess.run(["open", dmg_path])

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
    app_name = os.path.basename(app_path)
    shutil.copytree(app_path, os.path.join(temp_dir, app_name))

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
    dmg_size = max(total_size * 1.5, 50 * 1024 * 1024)  # 至少 50MB（PyInstaller包更小）

    try:
        # 创建未压缩的临时 DMG
        temp_dmg = dmg_path + ".temp.dmg"
        subprocess.check_call(
            [
                "hdiutil",
                "create",
                "-srcfolder",
                temp_dir,
                "-volname",
                "Claude Model Manager",
                "-format",
                "UDRW",
                "-size",
                f"{int(dmg_size / 1024 / 1024)}m",
                temp_dmg,
            ]
        )
        # 压缩 DMG
        subprocess.check_call(
            [
                "hdiutil",
                "convert",
                temp_dmg,
                "-format",
                "UDZO",
                "-o",
                dmg_path,
            ]
        )
        # 删除临时 DMG
        if os.path.exists(temp_dmg):
            os.remove(temp_dmg)

        print("✅ DMG 创建完成！")
        print(f"📁 DMG 文件位置: {os.path.abspath(dmg_path)}")

        # 清理临时目录
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

    except subprocess.CalledProcessError as e:
        print(f"❌ hdiutil 创建失败: {e}")


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


# def show_size_comparison():
#     """显示与 py2app 的大小对比"""
#     print("\n📊 PyInstaller vs py2app 大小对比:")
#     print("   PyInstaller 通常比 py2app 减少 50-70% 的体积")
#     print("   - py2app 典型大小: 200-400 MB")
#     print("   - PyInstaller 典型大小: 50-150 MB")
#     print("   - 单文件模式: 30-80 MB")


def upx_compress(app_path):
    """使用 UPX 压缩可执行文件"""
    exe_path = os.path.join(app_path, "Contents", "MacOS", "Claude Model Manager")
    if os.path.exists(exe_path):
        print(f"🔧 压缩可执行文件: {exe_path}")
        subprocess.run(["upx", "--best", "--lzma", exe_path])
        print("✅ 压缩完成")
    else:
        print("⚠️ 未找到可执行文件，跳过 UPX 压缩")


def main():
    """主函数"""
    print("🍎 macOS 平台打包脚本 (PyInstaller 版)")
    print("=" * 50)

    # 检查依赖
    check_requirements()

    # 选择构建模式
    print("\n🔧 选择构建模式:")
    print("1. 单文件模式 (--onefile) - 最小体积，单个可执行文件")
    # print("2. 应用包模式 (--onedir) - 完整 .app 包，更好的 macOS 集成")

    # choice = input("请选择 (1/2，默认1): ").strip()
    # if choice == "2":
    #     app_path = build_app_bundle()  # 应用包模式
    # else:
    app_path = build_app()  # 单文件模式

    if app_path:
        print("\n🎉 应用程序构建成功！")
        print("📁 应用程序位置:", os.path.abspath(app_path))

        # 调试运行
        # debug_app_run(app_path)

        # 代码签名（可选）
        # codesign_app(app_path)

        # 公证（可选）
        # notarize_app(app_path)

        # upx压缩
        # upx_compress(app_path)

        # 创建 DMG
        create_dmg(app_path)

        # 创建基本 DMG.
        # create_dmg_with_hdiutil(app_path)

        print("\n🎊 打包完成！")
        print("📦 DMG 文件: Claude Model Manager.dmg")

    else:
        print("\n❌ 打包失败，请检查错误信息")
        sys.exit(1)


if __name__ == "__main__":
    main()
