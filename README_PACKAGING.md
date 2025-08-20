# 快速打包指南

## 一键打包

### 最简单的方法

```bash
python package_all.py
```

### 分步操作

#### 1. 检查环境

```bash
python package_all.py --check
```

#### 2. 安装依赖

```bash
python package_all.py --install
```

#### 3. 清理构建文件

```bash
python package_all.py --clean
```

## 平台特定打包

### Windows (.exe)

```bash
python package_windows.py
```

### macOS (.dmg)

```bash
python package_macos.py
```

## 输出文件

### Windows

- `dist/ClaudeModelManager.exe` - 可执行文件
- `ClaudeModelManager_Setup.exe` - 安装程序（可选）

### macOS

- `dist/model_manager.app` - 应用程序
- `ClaudeModelManager.dmg` - 磁盘映像

## 需要帮助？

查看完整文档: [PACKAGING_GUIDE.md](PACKAGING_GUIDE.md)
