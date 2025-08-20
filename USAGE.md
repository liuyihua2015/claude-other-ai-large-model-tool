# Claude CLI 模型管理工具 - 使用指南

## 🚀 快速开始

### 方法 1：使用安装脚本（推荐）

```bash
# 克隆项目
git clone git@github.com:liuyihua2015/claude-other-ai-large-model-tool.git
cd claude-other-ai-large-model-tool

# 运行安装脚本
python3 setup.py
```

### 方法 2：手动安装

```bash
# 克隆项目
git clone git@github.com:liuyihua2015/claude-other-ai-large-model-tool.git
cd claude-other-ai-large-model-tool

# 安装依赖（macOS/Linux）
python3 -m pip install --user PyQt6

# 或者使用虚拟环境
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows
pip install PyQt6

# 运行程序
python model_manager.py
```

## 📋 界面操作指南

### 主界面布局

```
┌─────────────────────────────────────────────────────────┐
│ Claude配置目录: /Users/用户名/.claude-cli/    [打开目录] │
├─────────────────────────────────────────────────────────┤
│ 模型列表:                                               │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ kimi-k2 (Active)                                    │ │
│ │ claude-sonnet                                       │ │
│ │ custom-model                                        │ │
│ └─────────────────────────────────────────────────────┘ │
│ 模型详情（可编辑）:                                     │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ 模型名称: kimi-k2 (Active)                          │ │
│ │ ANTHROPIC_AUTH_TOKEN: sk-xxxxxxxx                   │ │
│ │ ANTHROPIC_BASE_URL: https://api.moonshot.cn/...     │ │
│ └─────────────────────────────────────────────────────┘ │
│ [设为Active模型] [删除选中模型] [保存修改]              │
│ [添加模型]                                              │
│ [初始化全局配置] [复制刷新终端命令]                     │
└─────────────────────────────────────────────────────────┘
```

### 操作流程

#### 1. 首次使用

1. 启动程序后，会自动创建默认配置
2. 点击"初始化全局配置"重置为默认设置
3. 默认包含一个 kimi-k2 模型配置

#### 2. 添加新模型

1. 点击"添加模型"按钮
2. 填写表单：
   - **模型名称**：如 `claude-sonnet`、`gpt-4` 等
   - **ANTHROPIC_AUTH_TOKEN**：你的 API 密钥
   - **BASE_URL**：API 接口地址
3. 点击"确定"保存

#### 3. 切换模型

1. 在左侧列表中选择要使用的模型
2. 点击"设为 Active 模型"
3. 程序会自动：
   - 更新环境变量文件
   - 在新终端中刷新环境变量
   - 标记该模型为激活状态

#### 4. 编辑模型

1. 选择要编辑的模型
2. 在右侧文本框中直接修改
3. 点击"保存修改"按钮
4. 可以修改模型名称、API 密钥、URL 等

#### 5. 删除模型

1. 选择要删除的模型
2. 点击"删除选中模型"
3. 确认删除操作
4. 如果删除的是当前激活模型，会自动选择下一个可用模型

## 🔧 配置示例

### Kimi-K2 配置

```json
{
  "kimi-k2": {
    "ANTHROPIC_AUTH_TOKEN": "sk-your-kimi-key-here",
    "ANTHROPIC_BASE_URL": "https://api.moonshot.cn/anthropic"
  }
}
```

### Claude 官方配置

```json
{
  "claude-sonnet": {
    "ANTHROPIC_AUTH_TOKEN": "sk-your-claude-key-here",
    "ANTHROPIC_BASE_URL": "https://api.anthropic.com"
  }
}
```

### 自定义 API 配置

```json
{
  "custom-api": {
    "ANTHROPIC_AUTH_TOKEN": "sk-your-custom-key",
    "ANTHROPIC_BASE_URL": "https://your-api.com/anthropic"
  }
}
```

## 🖥️ 终端集成

### 手动刷新环境变量

```bash
# macOS/Linux
source ~/.claude-cli/env.sh

# Windows (Git Bash)
source ~/.claude-cli/env.sh

# Windows (PowerShell)
. ~/.claude-cli/env.sh
```

### 在脚本中使用

```bash
#!/bin/bash
source ~/.claude-cli/env.sh
# 现在可以使用配置的环境变量
echo $ANTHROPIC_AUTH_TOKEN
echo $ANTHROPIC_BASE_URL
```

## 🐛 常见问题

### Q: 程序无法启动

**A:** 检查 Python 版本和 PyQt6 安装

```bash
python3 --version
python3 -c "import PyQt6; print('PyQt6 installed')"
```

### Q: 配置文件在哪里？

**A:** 配置文件位于：

- macOS/Linux: `~/.claude-cli/config.json`
- Windows: `C:\Users\用户名\.claude-cli\config.json`

### Q: 如何备份配置？

**A:** 备份配置文件：

```bash
cp ~/.claude-cli/config.json ~/claude-config-backup.json
```

### Q: 如何恢复默认配置？

**A:** 删除配置文件后重启程序：

```bash
rm ~/.claude-cli/config.json
python model_manager.py
```

### Q: 终端没有自动刷新

**A:** 手动执行：

```bash
source ~/.claude-cli/env.sh
```

## 📱 快捷操作

### 键盘快捷键

- **Enter**: 在列表中选择模型后按 Enter 可设为激活
- **Delete**: 在列表中选择模型后按 Delete 可删除
- **Ctrl+C**: 复制当前选中的模型配置

### 右键菜单

- 在模型列表上右键可以快速访问常用操作

## 🔄 更新程序

### 更新到新版本

```bash
git pull origin main
python3 setup.py
```

## 📞 技术支持

如有问题，请：

1. 检查本使用指南
2. 查看 README.md 中的故障排除部分
3. 在 GitHub 提交 Issue
