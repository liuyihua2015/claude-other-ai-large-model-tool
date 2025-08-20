# Claude CLI 模型管理工具

一个基于 PyQt6 的图形化 Claude/Kimi-K2 模型管理工具，用于管理多个 AI 模型的配置和环境变量。

## 🚀 功能特性

- **多模型管理**：支持添加、编辑、删除多个 Claude/Kimi-K2 模型配置
- **一键切换**：快速切换当前激活的模型
- **环境变量自动更新**：切换模型后自动更新环境变量文件
- **跨平台支持**：支持 macOS、Windows 和 Linux
- **终端自动刷新**：切换模型后自动在新终端中刷新环境变量
- **配置持久化**：所有配置保存在本地 JSON 文件中
- **图形化界面**：直观的 PyQt6 图形界面

## 📋 系统要求

- Python 3.6+
- PyQt6
- 支持的操作系统：macOS、Windows、Linux

## 🔧 安装

### 1. 克隆项目

```bash
git clone git@github.com:liuyihua2015/claude-other-ai-large-model-tool.git
cd claude-other-ai-large-model-tool
```

### 2. 安装依赖

```bash
pip install PyQt6
```

### 3. 运行程序

```bash
python model_manager.py
```

## 🎯 使用方法

### 启动程序

运行 `model_manager.py` 文件即可启动图形界面：

```bash
python model_manager.py
```

### 添加新模型

1. 点击"添加模型"按钮
2. 填写模型名称、ANTHROPIC_AUTH_TOKEN 和 BASE_URL
3. 点击"确定"保存

### 切换模型

1. 在模型列表中选择要使用的模型
2. 点击"设为 Active 模型"按钮
3. 程序会自动更新环境变量并在新终端中刷新

### 编辑模型

1. 在模型列表中选择要编辑的模型
2. 在右侧文本框中修改模型详情
3. 点击"保存修改"按钮

### 删除模型

1. 在模型列表中选择要删除的模型
2. 点击"删除选中模型"按钮
3. 确认删除操作

## 📁 配置文件

程序会在用户主目录下创建 `.claude-cli` 文件夹，包含以下文件：

- `config.json`：存储所有模型配置
- `env.sh`：当前激活模型的环境变量文件

### 配置目录位置

- **macOS/Linux**: `~/.claude-cli/`
- **Windows**: `C:\Users\[用户名]\.claude-cli\`

## 🔐 环境变量

程序会自动生成包含以下环境变量的 `env.sh` 文件：

```bash
export ANTHROPIC_AUTH_TOKEN="your-api-key"
export ANTHROPIC_BASE_URL="https://api.moonshot.cn/anthropic"
```

### 手动刷新环境变量

在终端中运行：

```bash
source ~/.claude-cli/env.sh
```

## 🖥️ 跨平台终端支持

### macOS

- 自动检测并使用 iTerm 或 Terminal
- 支持 AppleScript 自动化

### Windows

- 支持 Git Bash、WSL 和 PowerShell
- 自动检测 Git 安装路径

### Linux

- 支持 GNOME Terminal、Konsole、xterm、xfce4-terminal
- 自动检测可用的终端模拟器

## 🛠️ 开发

### 项目结构

```
claude-other-ai-large-model-tool/
├── model_manager.py    # 主程序文件
├── README.md          # 项目文档
└── ...                # 其他项目文件
```

### 技术栈

- **GUI 框架**: PyQt6
- **配置管理**: JSON
- **跨平台支持**: Python 标准库 + 平台特定命令

## 🐛 故障排除

### 常见问题

1. **PyQt6 未安装**

   ```bash
   pip install PyQt6
   ```

2. **权限问题**

   - 确保有权限写入用户主目录
   - 检查 `.claude-cli` 目录权限

3. **终端无法自动刷新**

   - 手动运行 `source ~/.claude-cli/env.sh`
   - 检查终端类型是否受支持

4. **配置文件损坏**
   - 删除 `~/.claude-cli/config.json`
   - 重新启动程序会自动创建默认配置

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 📞 联系

如有问题，请在 GitHub 上提交 Issue。
