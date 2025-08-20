# Claude Model Manager 打包指南

## 概述

本文档提供了将 Claude Model Manager 打包为 Windows (.exe) 和 macOS (.dmg) 平台独立应用程序的完整指南。

## 系统要求

### Windows 打包要求

- Windows 10/11 操作系统
- Python 3.8 或更高版本
- 管理员权限（用于安装程序）

### macOS 打包要求

- macOS 10.14 或更高版本
- Python 3.8 或更高版本
- Xcode Command Line Tools
- Homebrew（推荐）

## 快速开始

### 1. 安装依赖

#### Windows

```bash
pip install PyInstaller PyQt6
```

#### macOS

```bash
pip install py2app PyQt6
brew install create-dmg  # 可选，用于创建美观的 DMG
```

### 2. 运行打包脚本

#### Windows 打包

```bash
python package_windows.py
```

#### macOS 打包

```bash
python package_macos.py
```

## 详细打包流程

### Windows 平台 (.exe)

#### 基本打包

1. 运行 `package_windows.py` 脚本
2. 脚本会自动检查并安装必要依赖
3. 使用 PyInstaller 创建单文件可执行程序
4. 生成 `ClaudeModelManager.exe` 文件

#### 高级选项

- **创建安装程序**: 脚本会询问是否创建 NSIS 安装程序
- **自定义图标**: 将图标文件放在 `assets/icon.ico`
- **桌面快捷方式**: 自动创建桌面快捷方式

#### 输出文件

- `dist/ClaudeModelManager.exe` - 主可执行文件
- `ClaudeModelManager_Setup.exe` - 安装程序（可选）

### macOS 平台 (.dmg)

#### 基本打包

1. 运行 `package_macos.py` 脚本
2. 脚本会自动检查并安装必要依赖
3. 使用 py2app 创建 macOS 应用程序包
4. 创建 `.dmg` 磁盘映像

#### 高级选项

- **代码签名**: 支持 Apple Developer 证书签名
- **应用公证**: 支持 Apple 公证流程
- **自定义图标**: 将图标文件放在 `assets/icon.icns`
- **美观 DMG**: 使用 create-dmg 创建专业外观的安装器

#### 输出文件

- `dist/model_manager.app` - macOS 应用程序
- `ClaudeModelManager.dmg` - 磁盘映像文件

## 文件结构

```
claude-tool/
├── package_windows.py      # Windows 打包脚本
├── package_macos.py        # macOS 打包脚本
├── package_all.py          # 统一打包脚本（可选）
├── assets/                 # 资源文件目录
│   ├── icon.ico           # Windows 图标
│   ├── icon.icns          # macOS 图标
│   └── dmg-background.png # DMG 背景图
├── dist/                  # 打包输出目录
├── build/                 # 构建临时目录
└── examples/              # 示例配置文件
```

## 自定义配置

### 图标文件

- **Windows**: 创建 `assets/icon.ico` (256x256 像素)
- **macOS**: 创建 `assets/icon.icns` (1024x1024 像素)

### 应用程序信息

修改打包脚本中的以下参数：

#### Windows (package_windows.py)

```python
"--name=ClaudeModelManager"  # 可执行文件名
```

#### macOS (package_macos.py)

```python
'CFBundleName': 'Claude Model Manager'
'CFBundleVersion': '1.0.0'
```

## 故障排除

### 常见问题

#### Windows

1. **PyInstaller 安装失败**

   ```bash
   pip install --upgrade pip
   pip install pyinstaller
   ```

2. **缺少 winshell/pywin32**

   ```bash
   pip install winshell pywin32
   ```

3. **NSIS 未找到**
   - 下载并安装 NSIS: https://nsis.sourceforge.io/Download

#### macOS

1. **py2app 安装失败**

   ```bash
   pip install --upgrade pip
   pip install py2app
   ```

2. **create-dmg 未找到**

   ```bash
   brew install create-dmg
   ```

3. **代码签名失败**
   - 确保已安装有效的 Apple Developer 证书
   - 在 Xcode 中配置开发者账户

### 调试模式

#### Windows

```bash
# 移除 --windowed 参数以显示控制台输出
pyinstaller --onefile --name=ClaudeModelManager model_manager.py
```

#### macOS

```bash
# 在终端运行以查看错误信息
./dist/model_manager.app/Contents/MacOS/model_manager
```

## 发布准备

### 版本管理

1. 更新版本号
2. 更新 CHANGELOG.md
3. 创建 Git 标签
4. 上传到 GitHub Releases

### 文件验证

- 测试在干净系统上的安装
- 验证所有功能正常工作
- 检查文件权限和签名

## 自动化构建

### GitHub Actions

可以配置 GitHub Actions 自动构建：

```yaml
# .github/workflows/build.yml
name: Build Applications

on:
  push:
    tags:
      - "v*"

jobs:
  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build Windows
        run: python package_windows.py

  build-macos:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build macOS
        run: python package_macos.py
```

## 支持

如有问题，请：

1. 检查本指南的故障排除部分
2. 查看 GitHub Issues
3. 提交新的 Issue 包含错误信息

## 许可证

本项目采用 MIT 许可证，详见 LICENSE 文件。
