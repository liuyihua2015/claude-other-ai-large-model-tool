"""
Update checker for Claude Model Manager
Uses GitHub API to check for new releases based on Git tags
"""

import json
import requests
from PyQt6.QtCore import QObject, pyqtSignal, QThread, QTimer, Qt, QUrl
from PyQt6.QtWidgets import (
    QMessageBox,
    QDialog,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QCheckBox,
    QProgressDialog,
)
from PyQt6.QtGui import QDesktopServices
import time
from pathlib import Path
from version import get_current_version, compare_versions, parse_version


class UpdateChecker(QObject):
    """Background update checker using GitHub API"""

    update_available = pyqtSignal(
        str, str, str
    )  # current_version, latest_version, release_url
    no_update = pyqtSignal()
    error_occurred = pyqtSignal(str)

    def __init__(self, owner="liuyihua2015", repo="claude-other-ai-large-model-tool"):
        super().__init__()
        self.owner = owner
        self.repo = repo
        self.api_url = f"https://api.github.com/repos/{owner}/{repo}/tags"
        self.current_version = get_current_version()

    def check_for_updates(self):
        """Check GitHub for latest tag/release"""
        try:
            headers = {
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "Claude-Model-Manager",
            }

            response = requests.get(self.api_url, headers=headers, timeout=10)
            response.raise_for_status()

            tags = response.json()
            if not tags:
                self.no_update.emit()
                return

            # Get the latest tag
            latest_tag = tags[0]
            latest_version = latest_tag["name"]

            # Compare versions
            comparison = compare_versions(self.current_version, latest_version)

            if comparison < 0:
                # Update available
                release_url = f"https://github.com/{self.owner}/{self.repo}/releases/tag/{latest_version}"
                self.update_available.emit(
                    self.current_version, latest_version, release_url
                )
            else:
                self.no_update.emit()

        except requests.exceptions.Timeout:
            self.error_occurred.emit("连接超时，请检查网络连接")
        except requests.exceptions.RequestException as e:
            self.error_occurred.emit(f"网络错误: {str(e)}")
        except Exception as e:
            self.error_occurred.emit(f"检查更新时出错: {str(e)}")


class UpdateCheckThread(QThread):
    """Thread for checking updates without blocking UI"""

    def __init__(self, update_checker):
        super().__init__()
        self.update_checker = update_checker

    def run(self):
        self.update_checker.check_for_updates()


class UpdateDialog(QDialog):
    """Dialog to show update information"""

    def __init__(
        self, parent=None, current_version=None, latest_version=None, release_url=None
    ):
        super().__init__(parent)
        self.release_url = release_url
        self.setWindowTitle("发现新版本")
        self.setModal(True)
        self.resize(400, 200)

        layout = QVBoxLayout(self)

        # Update info
        info_label = QLabel(
            f"发现新版本可用！\n\n"
            f"当前版本: {current_version}\n"
            f"最新版本: {latest_version}\n\n"
            f"是否前往 GitHub 下载更新？"
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # Buttons
        download_btn = QPushButton("前往下载")
        download_btn.clicked.connect(self.open_download)
        skip_btn = QPushButton("稍后提醒")
        skip_btn.clicked.connect(self.reject)

        layout.addWidget(download_btn)
        layout.addWidget(skip_btn)

    def open_download(self):
        """Open the release URL in browser"""
        if self.release_url:
            QDesktopServices.openUrl(QUrl(self.release_url))
        self.accept()


class UpdateSettingsDialog(QDialog):
    """Settings dialog for update preferences"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("更新设置")
        self.setModal(True)
        self.resize(300, 150)

        layout = QVBoxLayout(self)

        # Check on startup
        self.startup_check = QCheckBox("启动时检查更新")
        self.startup_check.setChecked(self.get_startup_check_setting())
        layout.addWidget(self.startup_check)

        # Check now button
        check_now_btn = QPushButton("立即检查更新")
        check_now_btn.clicked.connect(self.check_now)
        layout.addWidget(check_now_btn)

        # Close button
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)

    def get_startup_check_setting(self):
        """Get startup check setting from config"""
        config_path = Path.home() / ".claude-cli" / "update_config.json"
        if config_path.exists():
            try:
                with open(config_path, "r") as f:
                    config = json.load(f)
                    return config.get("check_on_startup", True)
            except:
                pass
        return True

    def save_startup_check_setting(self, value):
        """Save startup check setting to config"""
        config_path = Path.home() / ".claude-cli" / "update_config.json"
        config_path.parent.mkdir(parents=True, exist_ok=True)

        config = {}
        if config_path.exists():
            try:
                with open(config_path, "r") as f:
                    config = json.load(f)
            except:
                pass

        config["check_on_startup"] = value

        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)

    def check_now(self):
        """Trigger immediate update check"""
        if self.parent():
            self.parent().check_for_updates_manual()
        self.accept()

    def accept(self):
        """Save settings when dialog is closed"""
        self.save_startup_check_setting(self.startup_check.isChecked())
        super().accept()


class UpdateManager(QObject):
    """Main update manager that coordinates checking and UI"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.update_checker = UpdateChecker()
        self.update_thread = None
        self.update_timer = QTimer()
        self.update_timer.setInterval(24 * 60 * 60 * 1000)  # 24 hours

        # Connect signals
        self.update_checker.update_available.connect(self.on_update_available)
        self.update_checker.no_update.connect(self.on_no_update)
        self.update_checker.error_occurred.connect(self.on_error)

        self.update_timer.timeout.connect(self.check_for_updates)

    def start_auto_check(self):
        """Start automatic update checking"""
        if self.should_check_on_startup():
            self.check_for_updates()
        self.update_timer.start()

    def stop_auto_check(self):
        """Stop automatic update checking"""
        self.update_timer.stop()

    def check_for_updates(self, manual=False):
        """Check for updates (manual or automatic)"""
        if self.update_thread and self.update_thread.isRunning():
            return

        self.update_thread = UpdateCheckThread(self.update_checker)

        if manual:
            # Show checking message for manual checks
            if self.parent:
                self.progress = QProgressDialog(
                    "正在检查更新...", None, 0, 0, self.parent
                )
                self.progress.setWindowModality(Qt.WindowModality.WindowModal)
                self.progress.setAutoClose(True)
                self.progress.show()

                self.update_thread.finished.connect(self.progress.close)

        self.update_thread.start()

    def on_update_available(self, current_version, latest_version, release_url):
        """Handle update available notification"""
        if self.parent:
            dialog = UpdateDialog(
                self.parent, current_version, latest_version, release_url
            )
            dialog.exec()

    def on_no_update(self):
        """Handle no update available"""
        if self.parent and hasattr(self.parent, "manual_check_triggered"):
            QMessageBox.information(
                self.parent,
                "检查更新",
                f"当前版本 {get_current_version()} 已是最新版本。",
            )

    def on_error(self, error_msg):
        """Handle update check errors"""
        if self.parent and hasattr(self.parent, "manual_check_triggered"):
            QMessageBox.warning(
                self.parent, "检查更新失败", f"无法检查更新：\n{error_msg}"
            )

    def should_check_on_startup(self):
        """Check if we should check on startup"""
        config_path = Path.home() / ".claude-cli" / "update_config.json"
        if config_path.exists():
            try:
                with open(config_path, "r") as f:
                    config = json.load(f)
                    return config.get("check_on_startup", True)
            except:
                pass
        return True

    def show_update_settings(self):
        """Show update settings dialog"""
        if self.parent:
            dialog = UpdateSettingsDialog(self.parent)
            dialog.exec()
