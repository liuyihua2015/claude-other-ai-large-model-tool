#!/bin/bash

# Claude CLI 全局初始化脚本

CONFIG_DIR="$HOME/.claude-cli"
CONFIG_FILE="$CONFIG_DIR/config.json"
ENV_FILE="$CONFIG_DIR/env.sh"
SWITCH_SCRIPT="$CONFIG_DIR/claude-switch.sh"

# 创建目录
mkdir -p "$CONFIG_DIR"

# 生成默认配置文件
cat > "$CONFIG_FILE" <<'EOF'
{
  "active": "kimi-k2",
  "models": {
    "claude": {
      "ANTHROPIC_AUTH_TOKEN": "sk-xxxxxx",
      "ANTHROPIC_BASE_URL": "https://api.anthropic.com"
    },
    "kimi-k2": {
      "ANTHROPIC_AUTH_TOKEN": "sk-chAkGfUay4ktuCi3ytHuRcMgaEdEwfg4qhwATo5taLAxPkuQ",
      "ANTHROPIC_BASE_URL": "https://api.moonshot.cn/anthropic"
    },
    "gpt-4": {
      "OPENAI_API_KEY": "sk-zzzzzz",
      "OPENAI_BASE_URL": "https://api.openai.com/v1"
    }
  }
}
EOF

echo "✅ 配置文件生成完成：$CONFIG_FILE"

# 生成 env.sh 文件
cat > "$ENV_FILE" <<'EOF'
#!/bin/bash
CONFIG_FILE="$HOME/.claude-cli/config.json"
ACTIVE_MODEL=$(jq -r '.active' $CONFIG_FILE)
MODEL_VARS=$(jq -r ".models[\"$ACTIVE_MODEL\"] | to_entries[] | \"export \(.key)=\(.value)\"" $CONFIG_FILE)
eval "$MODEL_VARS"
EOF

echo "✅ 环境变量加载脚本生成完成：$ENV_FILE"

# 生成切换脚本
cat > "$SWITCH_SCRIPT" <<'EOF'
#!/bin/bash
CONFIG_FILE="$HOME/.claude-cli/config.json"
if [ -z "$1" ]; then
  echo "Usage: $0 <model-name>"
  exit 1
fi
jq ".active=\"$1\"" $CONFIG_FILE > $CONFIG_FILE.tmp && mv $CONFIG_FILE.tmp $CONFIG_FILE
echo "Switched to model: $1"
EOF

chmod +x "$SWITCH_SCRIPT"
echo "✅ 模型切换脚本生成完成：$SWITCH_SCRIPT"


SHELL_RC="$HOME/.zshrc"
if [ -n "$BASH_VERSION" ]; then
  SHELL_RC="$HOME/.bashrc"
fi

# 添加自动加载语句，如果不存在则追加
grep -qxF 'if [ -f "$HOME/.claude-cli/env.sh" ]; then source "$HOME/.claude-cli/env.sh"; fi' $SHELL_RC || \
echo 'if [ -f "$HOME/.claude-cli/env.sh" ]; then source "$HOME/.claude-cli/env.sh"; fi' >> $SHELL_RC

echo "✅ 终端启动时将自动加载当前 active 模型环境变量"

echo "使用方法："
echo "1. source ~/.claude-cli/env.sh  # 加载当前 active 模型的环境变量"
echo "2. ~/.claude-cli/claude-switch.sh <model-name>  # 切换模型"