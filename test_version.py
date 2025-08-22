#!/usr/bin/env python3
"""
测试脚本：验证macOS应用包的版本信息
"""
import os
import plistlib
import sys
import subprocess
from pathlib import Path

def test_app_version():
    """测试应用包的版本信息"""
    app_path = Path("dist/Claude Model Manager.app")
    
    if not app_path.exists():
        print("❌ 未找到应用包，请先运行打包脚本")
        return False
    
    # 读取Info.plist文件
    plist_path = app_path / "Contents" / "Info.plist"
    
    if not plist_path.exists():
        print("❌ 未找到Info.plist文件")
        return False
    
    try:
        with open(plist_path, 'rb') as f:
            plist = plistlib.load(f)
        
        print("📋 应用包信息:")
        print(f"   CFBundleShortVersionString: {plist.get('CFBundleShortVersionString', '未设置')}")
        print(f"   CFBundleVersion: {plist.get('CFBundleVersion', '未设置')}")
        print(f"   CFBundleIdentifier: {plist.get('CFBundleIdentifier', '未设置')}")
        print(f"   CFBundleName: {plist.get('CFBundleName', '未设置')}")
        
        # 验证版本不是0.0.0
        version = plist.get('CFBundleShortVersionString', '0.0.0')
        if version == '0.0.0' or version == '1.0.0':
            print(f"⚠️  版本可能不正确: {version}")
            return False
        else:
            print(f"✅ 版本设置正确: {version}")
            return True
            
    except Exception as e:
        print(f"❌ 读取Info.plist失败: {e}")
        return False

if __name__ == "__main__":
    test_app_version()