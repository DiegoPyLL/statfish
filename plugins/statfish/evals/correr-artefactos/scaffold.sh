#!/usr/bin/env bash
# Copia la plantilla de modelo del plugin (un modelo mínimo y válido) a ./corrida.
set -euo pipefail
mkdir -p corrida
RAIZ="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/../.." && pwd)}"
cp "$RAIZ/plantillas/modelo.toml" corrida/modelo.toml
