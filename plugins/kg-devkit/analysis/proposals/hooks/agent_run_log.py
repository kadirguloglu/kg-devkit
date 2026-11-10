#!/usr/bin/env python3
"""ÖNERİ (uygulanmadı): SubagentStart/SubagentStop kancası — agent çalıştırmalarını JSONL olarak kaydeder.

Amaç: agent gövdelerindeki "çalışmaya başladım / çalışmam tamamlandı" satırlarının (A-06) yerine sıfır token
maliyetli, deterministik kayıt ve 07-performance-optimization.md'deki metriklerin (delegasyon sayısı, süre,
hüküm dağılımı) ham verisi. Prompt, komut, dosya içeriği veya rapor metni YAZMAZ; yalnız aşağıdaki alanlar.
Kullanım: agent_run_log.py <veri_dizini>   (hooks.json içinde ${CLAUDE_PLUGIN_DATA} verilir)
Fail-open: her hata sessizce yutulur, çıktı üretmez, çıkış kodu 0.
"""
import json
import os
import re
import sys
import time

KEEP = ("hook_event_name", "session_id", "agent_id", "agent_type", "permission_mode")


def main():
    try:
        data = json.load(sys.stdin)
        if not isinstance(data, dict) or len(sys.argv) < 2 or not sys.argv[1] or "${" in sys.argv[1]:
            return
        row = {"ts": round(time.time(), 3)}
        row.update({k: data[k] for k in KEEP if isinstance(data.get(k), str)})
        last = data.get("last_assistant_message")  # varsa yalnız hüküm/durum satırı çıkarılır, metin saklanmaz
        if isinstance(last, str):
            m = re.search(r"\b(VERDICT|STATUS):\s*([A-Z-]+)", last)
            row["outcome"] = f"{m.group(1)}:{m.group(2)}" if m else "none"
        os.makedirs(sys.argv[1], exist_ok=True)
        with open(os.path.join(sys.argv[1], "agent-runs.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    except Exception:
        return


if __name__ == "__main__":
    main()
