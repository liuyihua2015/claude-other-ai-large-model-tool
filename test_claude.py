#!/usr/bin/env python3
"""测试 ClaudeManager 功能"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from model_manager import ClaudeManager
import asyncio

def test_claude_manager():
    print("=== 测试 Claude Manager ===\n")
    
    # 创建 ClaudeManager 实例
    manager = ClaudeManager()
    
    # 测试安装状态检测
    print("1. 检查 Claude CLI 安装状态...")
    is_installed = manager.is_installed()
    print(f"   已安装: {is_installed}")
    
    if is_installed:
        version = manager.get_installed_version()
        print(f"   当前版本: {version}")
    
    # 测试获取最新版本
    print("\n2. 检查最新版本...")
    latest_version = manager.get_latest_version()
    print(f"   最新版本: {latest_version}")
    
    # 测试下载 URL 生成
    print("\n3. 测试下载 URL 生成...")
    if latest_version:
        download_url = manager.get_download_url(latest_version)
        print(f"   下载 URL: {download_url}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_claude_manager()