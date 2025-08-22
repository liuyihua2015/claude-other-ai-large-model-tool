# 发布流程指南

## 快速开始

使用自动版本更新脚本，无需手动修改版本号：

### 1. 更新版本号
```bash
# 补丁版本 (1.0.0 → 1.0.1)
python bump_version.py patch

# 次版本 (1.0.0 → 1.1.0)
python bump_version.py minor

# 主版本 (1.0.0 → 2.0.0)
python bump_version.py major

# 指定版本号
python bump_version.py set --version 1.2.3
```

### 2. 创建Git标签（可选）
```bash
# 获取当前版本号
VERSION=$(python -c "from version import get_current_version; print(get_current_version())")

# 创建标签
git tag -a v$VERSION -m "Release version $VERSION"
git push origin v$VERSION
```

### 3. 构建发布包

#### macOS
```bash
# 安装打包工具
pip install py2app

# 构建应用
python setup.py py2app
```

#### Windows
```bash
# 运行Windows打包脚本
python package_windows.py
```

## 版本号规则

遵循语义化版本（SemVer）：

- **主版本** (major): 不兼容的API变更
- **次版本** (minor): 向后兼容的功能添加
- **补丁版本** (patch): 向后兼容的bug修复

## 文件更新说明

运行 `bump_version.py` 会自动更新以下文件：

- ✅ `version.py` - 应用版本号
- ✅ `setup.py` - macOS打包配置
- ✅ `package_windows.py` - Windows打包配置

## 发布检查清单

- [ ] 代码测试通过
- [ ] 更新版本号
- [ ] 创建Git标签
- [ ] 构建所有平台包
- [ ] 上传到GitHub Release
- [ ] 更新发布说明

## 示例发布流程

```bash
# 1. 功能开发完成后
python bump_version.py patch  # 或 minor/major

# 2. 提交代码
git add .
git commit -m "Release version $(python -c 'from version import get_current_version; print(get_current_version())')"

# 3. 打标签并推送
VERSION=$(python -c "from version import get_current_version; print(get_current_version())")
git tag v$VERSION
git push origin main --tags

# 4. 构建发布包
# macOS
python setup.py py2app
# Windows
python package_windows.py
```

## 注意事项

1. 版本号使用语义化版本规范
2. 每次发布前确保运行测试
3. 创建标签时使用`v`前缀（如`v1.0.1`）
4. 发布包文件名包含版本号便于识别