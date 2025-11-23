#!/bin/bash

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_PATH="$PROJECT_DIR/venv/bin/activate"

if [ -f "$PROJECT_DIR/deploy.sh" ]; then
    cat > "$HOME/run" << EOF
#!/bin/bash
cd $PROJECT_DIR
chmod +x deploy.sh
./deploy.sh
EOF
    chmod +x "$HOME/run"
    echo "✓ ~/run"
fi

if [ -f "$VENV_PATH" ]; then
    cat > "$HOME/go" << EOF
#!/bin/bash
. $VENV_PATH
cd $PROJECT_DIR
EOF
    chmod +x "$HOME/go"
    echo "✓ ~/go"
fi

echo "Готово!"
