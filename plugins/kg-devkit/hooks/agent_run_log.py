#!/usr/bin/env python3
"""SubagentStart/SubagentStop kancası: agent çalıştırmalarını JSONL olarak kaydeder (model bağlamına girmez).

Agent gövdelerindeki eski "çalışmaya başladım / çalışmam tamamlandı" satırlarının yerini alır ve delegasyon sayısı,
süre, hüküm dağılımı gibi metriklerin ham verisidir. Prompt, komut, dosya içeriği veya rapor metni YAZMAZ; yalnız
olay adı, oturum ve agent kimliği/türü, izin modu, zaman ve rapordaki `VERDICT:`/`STATUS:` değeri.

Kullanım: agent_run_log.py <veri_dizini>      (hooks.json içinde ${CLAUDE_PLUGIN_DATA} verilir)
Çıktı:    <veri_dizini>/agent-runs.jsonl       (özet: python3 agent_run_log.py --summary <veri_dizini>)
Kapatma:  KG_AGENT_LOG=off
Fail-open: her hata sessizce yutulur, stdout'a bir şey yazmaz, çıkış kodu 0. Yalnız standart kütüphane.
"""
import json
import os
import re
import sys
import time

KEEP = ("hook_event_name", "session_id", "agent_id", "agent_type", "permission_mode")
OUTCOME = re.compile(r"\b(VERDICT|STATUS):\s*\**\s*([A-Z][A-Z-]+)")
MAX_BYTES = 5 * 1024 * 1024  # dosya bu boyutu aşınca .1 olarak döndürülür


def record(data, directory):
    row = {"ts": round(time.time(), 3)}
    row.update({k: data[k] for k in KEEP if isinstance(data.get(k), str)})
    last = data.get("last_assistant_message")
    if isinstance(last, str):
        found = OUTCOME.findall(last)
        row["outcome"] = ":".join(found[-1]) if found else "none"
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, "agent-runs.jsonl")
    if os.path.exists(path) and os.path.getsize(path) > MAX_BYTES:
        os.replace(path, path + ".1")
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def summary(directory):
    starts, runs = {}, {}
    with open(os.path.join(directory, "agent-runs.jsonl"), encoding="utf-8") as f:
        for line in f:
            try:
                r = json.loads(line)
            except ValueError:
                continue
            key = r.get("agent_id")
            agent = r.get("agent_type", "?")
            if r.get("hook_event_name") == "SubagentStart":
                starts[key] = r.get("ts", 0)
            elif r.get("hook_event_name") == "SubagentStop":
                s = runs.setdefault(agent, {"n": 0, "sec": 0.0, "outcomes": {}})
                s["n"] += 1
                if key in starts:
                    s["sec"] += max(0.0, r.get("ts", 0) - starts.pop(key))
                o = r.get("outcome", "none")
                s["outcomes"][o] = s["outcomes"].get(o, 0) + 1
    print(f"{'agent':45} {'çalışma':>7} {'ort. sn':>8}  sonuçlar")
    for agent, s in sorted(runs.items(), key=lambda kv: -kv[1]["n"]):
        avg = s["sec"] / s["n"] if s["n"] else 0
        print(f"{agent:45} {s['n']:7d} {avg:8.1f}  {s['outcomes']}")


def main():
    if len(sys.argv) == 3 and sys.argv[1] == "--summary":
        summary(sys.argv[2])
        return
    try:
        if os.environ.get("KG_AGENT_LOG", "").lower() == "off":
            return
        data = json.load(sys.stdin)
        if not isinstance(data, dict) or len(sys.argv) < 2 or not sys.argv[1] or "${" in sys.argv[1]:
            return
        record(data, sys.argv[1])
    except Exception:
        return


if __name__ == "__main__":
    main()
