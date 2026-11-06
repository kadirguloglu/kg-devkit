#!/usr/bin/env python3
"""PreToolUse (Bash) kancası: canlı ortamı değiştiren veya secret okuyan altyapı komutlarını kullanıcı onayına düşürür.

Karar her zaman "ask"tir (bloklamaz); agent metnindeki "açık onay olmadan yok" kuralının ikinci kilidi.
Kaba bir regex eşlemesidir: zararsız bir komut ara sıra onaya düşebilir, tersi (kaçırma) olabildiğince az tutulur.
Yalnız standart kütüphane.
"""
import json
import re
import sys

VERBS = r"(apply|delete|scale|replace|patch|create|edit|drain|cordon|uncordon|taint|annotate|label|set|rollout\s+(restart|undo|pause|resume))"
RULES = [
    (re.compile(rf"\b(kubectl|oc)\b[^|;&\n]*?\s{VERBS}\b"), "kubectl/oc ile canlı kaynak değişikliği"),
    (re.compile(r"\b(kubectl|oc)\b[^|;&\n]*\bget\s+secrets?\b[^|;&\n]*(-o|--output)[ =]?(yaml|json|jsonpath|go-template)"), "secret içeriği okuma"),
    (re.compile(r"\bhelm\s+(install|upgrade|uninstall|delete|rollback)\b"), "helm ile canlı değişiklik"),
    (re.compile(r"\b(terraform|tofu)\s+(apply|destroy|import|state\s+(rm|mv))\b"), "terraform/tofu ile altyapı değişikliği"),
]


def check(command: str):
    for pattern, reason in RULES:
        if pattern.search(command):
            return reason
    return None


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        return
    command = (data.get("tool_input") or {}).get("command") or ""
    reason = check(command)
    if reason:
        print(json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "ask",
                "permissionDecisionReason": f"kg-devkit: {reason}. Bu işlem için açık onay gerekir.",
            }
        }, ensure_ascii=False))


if __name__ == "__main__":
    main()
