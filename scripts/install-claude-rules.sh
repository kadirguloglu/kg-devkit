#!/usr/bin/env bash
# rules/*.md dosyalarını kullanıcı düzeyinde ~/.claude/rules altına sembolik bağla (plugin kural taşımaz).
# Var olan, bu repoya işaret etmeyen dosyaya dokunmaz. Kaldırma: --uninstall
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$HOME/.claude/rules"
mode="${1:-install}"
[ "$mode" = "--uninstall" ] || mkdir -p "$DEST"
for f in "$ROOT"/rules/*.md; do
  t="$DEST/$(basename "$f")"
  if [ "$mode" = "--uninstall" ]; then
    if [ -L "$t" ] && [ "$(readlink "$t")" = "$f" ]; then rm "$t"; echo "kaldırıldı: $t"; fi
  elif [ -L "$t" ] && [ "$(readlink "$t")" = "$f" ]; then echo "güncel: $t"
  elif [ -e "$t" ] || [ -L "$t" ]; then echo "ATLANDI (var): $t"
  else ln -s "$f" "$t"; echo "bağlandı: $t"; fi
done
