#!/usr/bin/env bash
# codex/ çıktısını kullanıcı düzeyinde Codex dizinlerine sembolik bağla.
#   agent'lar -> ~/.codex/agents/<ad>.toml     skill'ler -> ~/.agents/skills/<ad>/
# Var olan, bu repoya işaret etmeyen bir dosya/dizine dokunmaz (atlar ve söyler).
# Kaldırma: ./scripts/install-codex.sh --uninstall
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
AGENTS_DIR="$HOME/.codex/agents"
SKILLS_DIR="$HOME/.agents/skills"
mode="${1:-install}"

link() { # $1 kaynak, $2 hedef
  if [ "$mode" = "--uninstall" ]; then
    if [ -L "$2" ] && [ "$(readlink "$2")" = "$1" ]; then rm "$2"; echo "kaldırıldı: $2"; fi
    return
  fi
  if [ -L "$2" ] && [ "$(readlink "$2")" = "$1" ]; then echo "güncel: $2"; return; fi
  if [ -e "$2" ] || [ -L "$2" ]; then echo "ATLANDI (var): $2"; return; fi
  ln -s "$1" "$2"; echo "bağlandı: $2"
}

[ "$mode" = "--uninstall" ] || mkdir -p "$AGENTS_DIR" "$SKILLS_DIR"
for f in "$ROOT"/codex/agents/*.toml; do link "$f" "$AGENTS_DIR/$(basename "$f")"; done
for d in "$ROOT"/codex/skills/*/; do d="${d%/}"; link "$d" "$SKILLS_DIR/$(basename "$d")"; done
