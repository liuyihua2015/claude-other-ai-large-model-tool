#!/usr/bin/env python3
"""
自动版本号更新脚本
用于在发布新版本时自动更新所有相关文件的版本号
"""

import re
import json
from pathlib import Path
import argparse


def parse_version(version_str):
    """解析版本号为元组 (major, minor, patch)"""
    parts = version_str.split('.')
    return tuple(int(part) for part in parts)


def format_version(major, minor, patch):
    """格式化版本号"""
    return f"{major}.{minor}.{patch}"


def bump_version(current_version, bump_type='patch'):
    """根据类型递增版本号"""
    major, minor, patch = parse_version(current_version)
    
    if bump_type == 'major':
        major += 1
        minor = 0
        patch = 0
    elif bump_type == 'minor':
        minor += 1
        patch = 0
    elif bump_type == 'patch':
        patch += 1
    else:
        raise ValueError(f"不支持的版本类型: {bump_type}")
    
    return format_version(major, minor, patch)


def update_version_py(version):
    """更新 version.py 文件"""
    version_file = Path(__file__).parent / "version.py"
    content = version_file.read_text(encoding="utf-8")
    
    # 使用正则表达式更新版本号
    content = re.sub(
        r'__version__ = "[^"]*"',
        f'__version__ = "{version}"',
        content
    )
    
    version_file.write_text(content, encoding="utf-8")
    print(f"✅ 更新 version.py: {version}")


def update_setup_py(version):
    """更新 setup.py 文件"""
    setup_file = Path(__file__).parent / "setup.py"
    if not setup_file.exists():
        return
    
    content = setup_file.read_text(encoding="utf-8")
    
    # 更新版本号
    content = re.sub(
        r"'CFBundleVersion': \"[^\"]*\"",
        f"'CFBundleVersion': \"{version}\"",
        content
    )
    content = re.sub(
        r"'CFBundleShortVersionString': \"[^\"]*\"",
        f"'CFBundleShortVersionString': \"{version}\"",
        content
    )
    
    setup_file.write_text(content, encoding="utf-8")
    print(f"✅ 更新 setup.py: {version}")


def update_package_windows(version):
    """更新 package_windows.py 文件"""
    package_file = Path(__file__).parent / "package_windows.py"
    if not package_file.exists():
        return
    
    content = package_file.read_text(encoding="utf-8")
    
    # 更新版本号
    content = re.sub(
        r'!define APP_VERSION "[^"]*"',
        f'!define APP_VERSION "{version}"',
        content
    )
    
    package_file.write_text(content, encoding="utf-8")
    print(f"✅ 更新 package_windows.py: {version}")


def get_current_version():
    """获取当前版本号"""
    version_file = Path(__file__).parent / "version.py"
    content = version_file.read_text(encoding="utf-8")
    
    match = re.search(r'__version__ = "([^"]*)"', content)
    if match:
        return match.group(1)
    return "1.0.0"


def update_all_versions(new_version):
    """更新所有文件的版本号"""
    print(f"🔄 更新所有版本号到: {new_version}")
    
    update_version_py(new_version)
    update_setup_py(new_version)
    update_package_windows(new_version)
    
    print("🎉 版本号更新完成！")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="自动更新应用版本号")
    parser.add_argument(
        "type", 
        choices=["major", "minor", "patch", "set"],
        help="版本更新类型或设置为指定版本"
    )
    parser.add_argument(
        "--version",
        type=str,
        help="当type为set时，指定具体的版本号"
    )
    
    args = parser.parse_args()
    
    current_version = get_current_version()
    print(f"📋 当前版本: {current_version}")
    
    if args.type == "set":
        if not args.version:
            print("❌ 使用set类型时必须指定--version参数")
            return
        new_version = args.version
    else:
        new_version = bump_version(current_version, args.type)
    
    print(f"🆕 新版本: {new_version}")
    
    confirm = input("确认更新？(y/N): ")
    if confirm.lower() in ["y", "yes"]:
        update_all_versions(new_version)
    else:
        print("❌ 操作已取消")


if __name__ == "__main__":
    main()