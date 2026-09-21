#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/Template_AGES___Guvidaletti"

echo "Compilando documento com Tectonic..."
tectonic main.tex

cp -p main.pdf "$SCRIPT_DIR/main.pdf"
echo "Compilação concluída com sucesso! Gerado: $SCRIPT_DIR/main.pdf"
