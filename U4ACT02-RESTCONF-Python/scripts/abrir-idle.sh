#!/bin/zsh
# Abre IDLE usando el entorno virtual del proyecto (que tiene instalado "requests").
# Uso: ./abrir-idle.sh "lab 2.5.py"
cd "$(dirname "$0")"
../.venv/bin/python -m idlelib "$@"
