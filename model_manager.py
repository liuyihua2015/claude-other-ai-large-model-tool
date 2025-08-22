import sys, os, json, subprocess, requests
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow,
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QListWidget,
    QLineEdit,
    QLabel,
    QMessageBox,
    QTextEdit,
    QMenu,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QProgressBar,
    QFrame,
    QGroupBox,
    QRadioButton,
)
from PyQt6.QtGui import QClipboard, QIcon, QAction, QColor, QFont
from PyQt6.QtCore import QThread, pyqtSignal, QTimer, Qt

# 导入更新检查器
from update_checker import UpdateManager

CONFIG_DIR = Path.home() / ".claude-cli"
CONFIG_FILE = CONFIG_DIR / "config.json"
ENV_FILE = CONFIG_DIR / "env.sh"

DEFAULT_CONFIG = {
    "active": "kimi-k2",
    "models": {
        "kimi-k2": {
            "ANTHROPIC_AUTH_TOKEN": "sk-yyyyyy",
            "ANTHROPIC_BASE_URL": "https://api.moonshot.cn/anthropic",
        }
    },
}

os.makedirs(CONFIG_DIR, exist_ok=True)


# --- 配置文件读写 ---
def load_config():
    if not CONFIG_FILE.exists():
        with open(CONFIG_FILE, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)


def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


# --- 更新 env.sh ---
def update_env_file(active_model, model_data):
    lines = [f'export {k}="{v}"' for k, v in model_data.items()]
    content = "\n".join(lines)
    echo_lines = [
        'echo "✅ 已加载 ANTHROPIC 环境变量:"',
    ]
    for k in model_data.keys():
        echo_lines.append(f'echo "{k}=${k}"')
    content = content + "\n\n" + "\n".join(echo_lines) + "\n"
    with open(ENV_FILE, "w") as f:
        f.write(content)
    print(f"✅ 已更新环境变量文件: {ENV_FILE}")


# --- GUI 主窗口 ---
class ModelManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Claude / Kimi-K2 模型管理")
        self.resize(600, 700)
        self.config = load_config()
        self.current_model = None
        self.update_manager = UpdateManager(self)
        self.init_ui()
        self.init_menu()
        self.update_manager.start_auto_check()

    def init_menu(self):
        # 获取菜单栏
        menu_bar = self.menuBar()

        # macOS 默认应用菜单 - 使用标准名称确保系统识别
        app_menu = menu_bar.addMenu("Claude Model Manager")

        # 关于应用 - 使用标准About名称
        about_action = QAction("关于", self)
        about_action.setMenuRole(QAction.MenuRole.AboutRole)
        about_action.triggered.connect(self.show_about_dialog)
        app_menu.addAction(about_action)

        # 添加分隔符
        app_menu.addSeparator()

        # 检查更新 - 添加到应用菜单
        check_update_action = QAction("检查更新", self)
        check_update_action.triggered.connect(self.check_for_updates_manual)
        app_menu.addAction(check_update_action)

        # 更新设置 - 添加到应用菜单
        update_settings_action = QAction("更新设置", self)
        update_settings_action.triggered.connect(self.show_update_settings)
        app_menu.addAction(update_settings_action)

    def show_about_dialog(self):
        from version import get_current_version

        msg = QMessageBox(self)
        msg.setWindowTitle("About Claude Model Manager")
        current_version = get_current_version()
        msg.setText(
            f"Claude CLI 模型管理工具\n版本: {current_version}\n© 2025 Claude CLI Tools"
        )
        icon = QIcon("assets/icon.icns")
        msg.setIconPixmap(icon.pixmap(128, 128))
        msg.exec()

    def check_for_updates_manual(self):
        """手动触发更新检查"""
        self.update_manager.check_for_updates(manual=True)

    def show_update_settings(self):
        """显示更新设置对话框"""
        self.update_manager.show_update_settings()

    def init_ui(self):
        central = QWidget()
        layout = QVBoxLayout()
        central.setLayout(layout)
        self.setCentralWidget(central)

        # 官方文档内容文本
        self.doc_text = (
            "步骤 1：安装 Claude Code\n\n"
            "NPM 安装\n"
            "如果您已安装 Node.js 18 或更新版本：\n"
            "npm install -g @anthropic-ai/claude-code\n\n"
            "原生安装\n"
            "或者，尝试我们新的原生安装，现在处于测试版。\n\n"
            "macOS、Linux、WSL：\n"
            "curl -fsSL claude.ai/install.sh | bash\n"
            "Windows PowerShell：\n"
            "irm https://claude.ai/install.ps1 | iex\n\n"
            "步骤 2：开始您的第一个会话\n"
            "在任何项目目录中打开终端并启动 Claude Code：\n"
            "cd /path/to/your/project\n"
            "claude\n"
            "您将在新的交互式会话中看到 Claude Code 提示符：\n"
            "✻ 欢迎使用 Claude Code！\n\n"
            "官方地址: https://docs.anthropic.com/zh-CN/docs/claude-code/quickstart"
        )

        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)

        # 顶部目录路径和打开按钮
        dir_layout = QHBoxLayout()
        config_directory = str(CONFIG_DIR)
        dir_label = QLabel(f"Claude配置目录: {config_directory}")
        open_btn = QPushButton("打开目录")
        doc_btn = QPushButton("官方文档与安装步骤")
        manual_btn = QPushButton("Claude Code 命令说明书")

        def open_directory():
            if sys.platform.startswith("win"):
                subprocess.run(["explorer", config_directory])
            elif sys.platform == "darwin":
                subprocess.run(["open", config_directory])
            else:
                subprocess.run(["xdg-open", config_directory])

        open_btn.clicked.connect(open_directory)
        dir_layout.addWidget(dir_label)
        dir_layout.addWidget(open_btn)
        dir_layout.addWidget(doc_btn)
        dir_layout.addWidget(manual_btn)
        layout.addLayout(dir_layout)

        def show_doc_dialog():
            dialog = QDialog(self)
            dialog.setWindowTitle("官方文档与安装步骤")
            dialog.setMinimumWidth(500)
            vbox = QVBoxLayout(dialog)
            doc_view = QTextEdit()
            doc_view.setReadOnly(True)
            doc_view.setPlainText(self.doc_text)
            doc_view.setMinimumHeight(400)
            vbox.addWidget(doc_view)
            button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
            button_box.accepted.connect(dialog.accept)
            vbox.addWidget(button_box)
            dialog.exec()

        doc_btn.clicked.connect(show_doc_dialog)

        def show_manual_dialog():
            info_text = (
                "/add-dir 添加新的工作目录\n"
                "/agents 管理代理配置\n"
                "/bashes 列出并管理后台bash shell\n"
                "/bug 提交关于Claude Code的反馈\n"
                "/clear 清除对话历史并释放上下文\n"
                "/compact 清除对话历史但在上下文中保留摘要。可选：/compact [摘要指令]\n"
                "/config 打开配置面板\n"
                "/cost 显示当前会话的总成本和持续时间\n"
                "/doctor 诊断并验证您的Claude Code安装和设置\n"
                "/exit 退出REPL\n"
                "/export 将当前对话导出到文件或剪贴板\n"
                "/help 显示帮助和可用命令\n"
                "/hooks 管理工具事件的钩子配置\n"
                "/ide 管理IDE集成并显示状态\n"
                "/init 使用代码库文档初始化新的CLAUDE.md文件\n"
                "/install-github-app 为仓库设置Claude GitHub Actions\n"
                "/login 使用您的Anthropic账户登录\n"
                "/logout 从您的Anthropic账户登出\n"
                "/mcp 管理MCP服务器\n"
                "/memory 编辑Claude内存文件\n"
                "/migrate-installer 从全局npm安装迁移到本地安装\n"
                "/model 设置Claude Code的AI模型\n"
                "/output-style 直接设置输出样式或从选择菜单中设置\n"
                "/output-style:new 创建自定义输出样式\n"
                "/permissions 管理允许和拒绝工具权限规则\n"
                "/pr-comments 获取GitHub拉取请求的评论\n"
                "/release-notes 查看发布说明\n"
                "/resume 恢复对话\n"
                "/review 审查拉取请求\n"
                "/security-review 完成当前分支上待处理更改的安全审查\n"
                "/status 显示Claude Code状态，包括版本、模型、账户、API连接和工具状态\n"
                "/statusline 设置Claude Code的状态行UI\n"
                "/terminal-setup 安装Shift+Enter键绑定用于换行\n"
                "/upgrade 升级到Max以获得更高的速率限制和更多的Opus\n"
                "/vim 在Vim和普通编辑模式之间切换\n"
            )
            dialog = QDialog(self)
            dialog.setWindowTitle("Claude Code 命令说明书")
            dialog.setMinimumWidth(500)
            vbox = QVBoxLayout(dialog)
            text_view = QTextEdit()
            text_view.setReadOnly(True)
            text_view.setPlainText(info_text)
            text_view.setMinimumHeight(400)
            vbox.addWidget(text_view)
            button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
            button_box.accepted.connect(dialog.accept)
            vbox.addWidget(button_box)
            dialog.exec()

        manual_btn.clicked.connect(show_manual_dialog)

        # 模型列表
        self.model_list = QListWidget()
        self.model_list.itemClicked.connect(self.show_model_details)
        layout.addWidget(QLabel("模型列表:"))
        layout.addWidget(self.model_list)

        # 模型详情只读
        self.detail_text = QTextEdit()
        self.detail_text.setReadOnly(True)
        layout.addWidget(QLabel("模型详情（只读）:"))
        layout.addWidget(self.detail_text)

        # 操作按钮
        btn_layout = QHBoxLayout()
        select_btn = QPushButton("设为 Active 模型")
        select_btn.clicked.connect(self.select_model)
        del_btn = QPushButton("删除选中模型")
        del_btn.clicked.connect(self.delete_model)
        edit_btn = QPushButton("修改")
        edit_btn.clicked.connect(self.edit_model_dialog)
        btn_layout.addWidget(select_btn)
        btn_layout.addWidget(del_btn)
        btn_layout.addWidget(edit_btn)
        layout.addLayout(btn_layout)

        # 添加新模型按钮
        add_btn = QPushButton("添加模型")
        add_btn.clicked.connect(self.add_model)
        layout.addWidget(add_btn)

        # 初始化和复制刷新命令
        bottom_layout = QHBoxLayout()
        init_btn = QPushButton("初始化全局配置")
        init_btn.clicked.connect(self.init_config)
        copy_btn = QPushButton("复制刷新终端命令")
        copy_btn.clicked.connect(self.copy_refresh_command)
        bottom_layout.addWidget(init_btn)
        bottom_layout.addWidget(copy_btn)
        layout.addLayout(bottom_layout)

        self.refresh_model_list()

    def refresh_model_list(self):
        self.model_list.clear()
        for name in self.config["models"]:
            active_mark = " (Active)" if name == self.config.get("active") else ""
            self.model_list.addItem(name + active_mark)
        self.detail_text.clear()
        self.current_model = None

    def show_model_details(self, item):
        name = item.text().replace(" (Active)", "")
        self.current_model = name
        model = self.config["models"].get(name, {})
        detail = f"模型名称: {name}\n"
        for k, v in model.items():
            detail += f"{k}: {v}\n"
        self.detail_text.setText(detail)

    def edit_model_dialog(self):
        if not self.current_model:
            QMessageBox.warning(self, "错误", "请选择要修改的模型")
            return
        name = self.current_model
        model = self.config["models"].get(name, {})
        dialog = QDialog(self)
        dialog.setWindowTitle(f"编辑模型: {name}")
        dialog.setFixedWidth(self.width())
        form = QFormLayout(dialog)
        # 不允许编辑模型名称
        name_label = QLabel(name)
        form.addRow("模型名称:", name_label)
        token_edit = QLineEdit(model.get("ANTHROPIC_AUTH_TOKEN", ""))
        url_edit = QLineEdit(model.get("ANTHROPIC_BASE_URL", ""))
        min_width = 380
        token_edit.setMinimumWidth(min_width)
        url_edit.setMinimumWidth(min_width)
        form.addRow("ANTHROPIC_AUTH_TOKEN:", token_edit)
        form.addRow("ANTHROPIC_BASE_URL:", url_edit)

        # 按钮：取消、确定修改、修改并切换当前模型
        button_box = QDialogButtonBox()
        btn_cancel = QPushButton("取消")
        btn_ok = QPushButton("确定修改")
        btn_ok_switch = QPushButton("修改并切换当前模型")
        button_box.addButton(btn_cancel, QDialogButtonBox.ButtonRole.RejectRole)
        button_box.addButton(btn_ok, QDialogButtonBox.ButtonRole.AcceptRole)
        button_box.addButton(btn_ok_switch, QDialogButtonBox.ButtonRole.ActionRole)
        form.addRow(button_box)

        def do_save_model_changes(set_active=False):
            token = token_edit.text().strip()
            url = url_edit.text().strip()
            if not token or not url:
                QMessageBox.warning(
                    dialog,
                    "错误",
                    "ANTHROPIC_AUTH_TOKEN 和 ANTHROPIC_BASE_URL 不能为空",
                )
                return
            self.config["models"][name] = {
                "ANTHROPIC_AUTH_TOKEN": token,
                "ANTHROPIC_BASE_URL": url,
            }
            if set_active:
                self.config["active"] = name
            save_config(self.config)
            # 更新 env.sh
            active = self.config["active"]
            update_env_file(active, self.config["models"][active])
            self.refresh_model_list()
            if set_active:
                self.auto_source_terminal()
                QMessageBox.information(
                    self,
                    "提示",
                    f"模型 {name} 修改成功，并已切换为当前模型并刷新 env.sh",
                )
            else:
                QMessageBox.information(
                    self,
                    "提示",
                    f"模型 {name} 修改成功并刷新 env.sh",
                )
            dialog.accept()

        btn_cancel.clicked.connect(dialog.reject)
        btn_ok.clicked.connect(lambda: do_save_model_changes(False))
        btn_ok_switch.clicked.connect(lambda: do_save_model_changes(True))
        dialog.exec()

    def select_model(self):
        item = self.model_list.currentItem()
        if item:
            name = item.text().replace(" (Active)", "")
            self.config["active"] = name
            save_config(self.config)
            # 更新 env.sh
            update_env_file(name, self.config["models"][name])
            self.refresh_model_list()
            # 自动在新终端执行 source（跨平台支持）
            self.auto_source_terminal()
            QMessageBox.information(
                self, "提示", f"已切换到模型: {name} 并在新终端刷新环境变量"
            )

    def delete_model(self):
        item = self.model_list.currentItem()
        if item:
            name = item.text().replace(" (Active)", "")
            reply = QMessageBox.question(
                self,
                "确认删除",
                f"确定要删除模型 '{name}' 吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                if name in self.config["models"]:
                    del self.config["models"][name]
                    if self.config.get("active") == name:
                        self.config["active"] = next(iter(self.config["models"]), None)
                        # 更新 env.sh
                        if self.config.get("active"):
                            update_env_file(
                                self.config["active"],
                                self.config["models"][self.config["active"]],
                            )
                    save_config(self.config)
                    self.refresh_model_list()
                    QMessageBox.information(self, "提示", f"已删除模型: {name}")

    def add_model(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("添加新模型")
        dialog.setFixedWidth(self.width())
        form = QFormLayout(dialog)
        name_edit = QLineEdit()
        token_edit = QLineEdit()
        url_edit = QLineEdit()
        # Set minimum width for inputs to ensure sufficient space for API keys and URLs
        min_width = 380
        name_edit.setMinimumWidth(min_width)
        token_edit.setMinimumWidth(min_width)
        url_edit.setMinimumWidth(min_width)
        form.addRow("模型名称:", name_edit)
        form.addRow("ANTHROPIC_AUTH_TOKEN:", token_edit)
        form.addRow("ANTHROPIC_BASE_URL:", url_edit)
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        form.addRow(button_box)

        def on_accept():
            name = name_edit.text().strip()
            token = token_edit.text().strip()
            base_url = url_edit.text().strip()
            if not name or not token or not base_url:
                QMessageBox.warning(
                    dialog,
                    "错误",
                    "模型名称、ANTHROPIC_AUTH_TOKEN 和 ANTHROPIC_BASE_URL 不能为空",
                )
                return
            self.config["models"][name] = {
                "ANTHROPIC_AUTH_TOKEN": token,
                "ANTHROPIC_BASE_URL": base_url,
            }
            save_config(self.config)
            self.refresh_model_list()
            QMessageBox.information(self, "提示", f"模型 {name} 添加成功")
            dialog.accept()

        button_box.accepted.connect(on_accept)
        button_box.rejected.connect(dialog.reject)
        dialog.exec()

    def init_config(self):
        self.config = DEFAULT_CONFIG
        save_config(self.config)
        # 更新 env.sh
        active = self.config["active"]
        update_env_file(active, self.config["models"][active])
        self.refresh_model_list()
        # 自动写入 shell 配置文件，确保每次新终端自动加载
        shell_configs = [Path.home() / ".zshrc", Path.home() / ".bashrc"]
        source_line = f"source {ENV_FILE}\n"
        for shell_config in shell_configs:
            try:
                if shell_config.exists():
                    content = shell_config.read_text()
                else:
                    content = ""
                if source_line not in content:
                    with open(shell_config, "a") as f:
                        f.write("\n# Auto-load Claude Model Manager env\n")
                        f.write(source_line)
            except Exception as e:
                print(f"无法写入 {shell_config}: {e}")
        QMessageBox.information(self, "提示", "已初始化全局配置并刷新 env.sh")

    def copy_refresh_command(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(f"source {ENV_FILE}")
        QMessageBox.information(
            self, "提示", "已复制刷新终端命令到剪贴板:\n" + f"source {ENV_FILE}"
        )

    def auto_source_terminal(self):
        """自动在新终端中执行source命令（跨平台支持）"""
        env_file = str(ENV_FILE)

        try:
            if sys.platform == "darwin":
                # macOS: 智能检测iTerm或Terminal并执行source
                self._macos_auto_source(env_file)
                subprocess.run("env | grep ANTHROPIC", shell=True, check=False)

            elif sys.platform.startswith("win"):
                # Windows: 使用PowerShell打开新窗口并执行source
                # 注意：Windows使用Git Bash或WSL时需要不同的处理方式
                ps_script = f"""
$env_file = "{env_file}"
if (Test-Path "$env:USERPROFILE\\scoop\\apps\\git\\current\\bin\\bash.exe") {{
    # Git Bash via Scoop
    Start-Process "$env:USERPROFILE\\scoop\\apps\\git\\current\\bin\\bash.exe" -ArgumentList "-c", "source $env_file && echo 'Environment refreshed' && sleep 3"
}} elseif (Test-Path "$env:ProgramFiles\\Git\\bin\\bash.exe") {{
    # Git Bash
    Start-Process "$env:ProgramFiles\\Git\\bin\\bash.exe" -ArgumentList "-c", "source $env_file && echo 'Environment refreshed' && sleep 3"
}} elseif (Test-Path "$env:SystemRoot\\System32\\wsl.exe") {{
    # WSL
    Start-Process "$env:SystemRoot\\System32\\wsl.exe" -ArgumentList "bash", "-c", "source {env_file} && echo 'Environment refreshed' && sleep 3"
}} else {{
    # 普通cmd
    Start-Process "cmd.exe" -ArgumentList "/k", "echo Please manually run: source {env_file}"
}}
"""
                subprocess.run(["powershell", "-Command", ps_script], check=True)

            elif sys.platform.startswith("linux"):
                # Linux: 根据桌面环境选择终端
                terminals = [
                    [
                        "gnome-terminal",
                        "--",
                        "bash",
                        "-c",
                        f"source {env_file}; echo 'Environment refreshed'; read -p 'Press Enter to close...'",
                    ],
                    [
                        "konsole",
                        "-e",
                        "bash",
                        "-c",
                        f"source {env_file}; echo 'Environment refreshed'; read -p 'Press Enter to close...'",
                    ],
                    [
                        "xterm",
                        "-e",
                        "bash",
                        "-c",
                        f"source {env_file}; echo 'Environment refreshed'; read -p 'Press Enter to close...'",
                    ],
                    [
                        "xfce4-terminal",
                        "-e",
                        "bash",
                        "-c",
                        f"source {env_file}; echo 'Environment refreshed'; read -p 'Press Enter to close...'",
                    ],
                ]

                for terminal_cmd in terminals:
                    try:
                        subprocess.run(terminal_cmd, check=True)
                        break
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        continue
                else:
                    # 如果没有找到支持的终端，使用x-terminal-emulator（Debian/Ubuntu默认）
                    try:
                        subprocess.run(
                            [
                                "x-terminal-emulator",
                                "-e",
                                "bash",
                                "-c",
                                f"source {env_file}; echo 'Environment refreshed'; read -p 'Press Enter to close...'",
                            ],
                            check=True,
                        )
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        # 最后尝试使用默认的shell
                        subprocess.run(
                            [
                                "xterm",
                                "-e",
                                "bash",
                                "-c",
                                f"source {env_file}; echo 'Environment refreshed'; read -p 'Press Enter to close...'",
                            ],
                            check=False,
                        )

        except subprocess.CalledProcessError as e:
            print(f"自动刷新终端失败: {e}")
            # 静默失败，不显示错误对话框，因为这不是核心功能

    def _macos_auto_source(self, env_file):
        """macOS专用：智能检测iTerm或Terminal并执行source"""
        try:
            # 首先尝试iTerm
            iterm_script = f"""
tell application "iTerm"
    if it is running then
        create window with default profile
        tell current window
            tell current session
                write text "source {env_file}"
            end tell
        end tell
    else
        create window with default profile
        tell current window
            tell current session
                write text "source {env_file}"
            end tell
        end tell
    end if
    activate
end tell
"""
            subprocess.run(["osascript", "-e", iterm_script], check=True)
        except subprocess.CalledProcessError:
            # iTerm失败，尝试Terminal
            try:
                terminal_script = f"""
tell application "Terminal"
    if it is running then
        do script "source {env_file}"
    else
        do script "source {env_file}"
    end if
    activate
end tell
"""
                subprocess.run(["osascript", "-e", terminal_script], check=True)
            except subprocess.CalledProcessError as e:
                print(f"macOS终端自动source失败: {e}")
                # 最后尝试使用open命令
                try:
                    subprocess.run(["open", "-a", "Terminal", env_file], check=False)
                except:
                    pass

    # Claude CLI 管理区域和相关功能已移除，改为仅显示官方文档和安装步骤


if __name__ == "__main__":

    app = QApplication(sys.argv)
    # app.setApplicationName("Claude Model Manager")
    # app.setApplicationVersion("1.0.0")
    # app.setOrganizationName("Claude CLI Tools")
    # app.setWindowIcon(QIcon("assets/icon.icns"))

    window = ModelManager()
    window.show()
    sys.exit(app.exec())
