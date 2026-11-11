#!/usr/bin/env python3
"""SubagentStop kancası: kg-devkit agent'ı raporunu sözleşmedeki sonuç satırı olmadan bitirirse bir kez geri çevirir.

Reviewer'lar `VERDICT: PASS|FAIL|UNCLEAR`, yazar agent'lar ve tarayıcı testçisi `STATUS: DONE|PARTIAL|BLOCKED` satırıyla
biter (references/review-packet.md). Satır yoksa agent'a tek cümlelik hatırlatma döner ve agent raporu tamamlar.
Döngü olmaz: Claude Code ikinci durmada `stop_hook_active: true` gönderir, o zaman kanca karışmaz. Satırın DEĞERİNİ
denetlemez (yanlış PASS'i yakalamaz); yalnız varlığını zorlar. Danışman agent'lara (architect, scope-advisor) karışmaz.

Kapatma: KG_REQUIRE_OUTCOME=off. Fail-open: her hata sessizce yutulur, çıkış kodu 0. Yalnız standart kütüphane.
"""
import json
import os
import re
import sys

VERDICT = re.compile(r"\bVERDICT:\s*\**\s*(PASS|FAIL|UNCLEAR)\b")
STATUS = re.compile(r"\bSTATUS:\s*\**\s*(DONE|PARTIAL|BLOCKED)\b")
WRITERS = {"backend-developer", "backend-test-developer", "frontend-developer", "frontend-test-developer",
           "frontend-browser-tester", "devops-engineer", "devops-operator"}


def missing(agent_type, message):
    """Eksik satır için hatırlatma metni; eksik yoksa veya agent kapsam dışıysa None."""
    if not isinstance(agent_type, str) or not agent_type.startswith("kg-devkit:") or not isinstance(message, str):
        return None
    name = agent_type.split(":", 1)[1]
    if name.endswith("-reviewer") and not VERDICT.search(message):
        return ("Your report has no verdict line. Repeat the report and end it with exactly one of: "
                "`VERDICT: PASS`, `VERDICT: FAIL` or `VERDICT: UNCLEAR` (with what is missing).")
    if name in WRITERS and not STATUS.search(message):
        return ("Your report has no status line. Repeat the report and end it with `STATUS: DONE`, `STATUS: PARTIAL` or "
                "`STATUS: BLOCKED` as your definition describes; DONE only if every required check ran and passed.")
    return None


def main():
    try:
        if os.environ.get("KG_REQUIRE_OUTCOME", "").lower() == "off":
            return
        data = json.load(sys.stdin)
        if not isinstance(data, dict) or data.get("stop_hook_active"):
            return
        reason = missing(data.get("agent_type"), data.get("last_assistant_message"))
    except Exception:
        return
    if reason:
        print(json.dumps({"decision": "block", "reason": "kg-devkit: " + reason}))


if __name__ == "__main__":
    main()
