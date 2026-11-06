#!/usr/bin/env python3
"""PreToolUse (Bash) kancası: canlı ortamı değiştiren veya secret okuyan altyapı komutlarını kullanıcı onayına düşürür.

Karar her zaman "ask"tir (bloklamaz); agent metnindeki "açık onay olmadan yok" kuralının ikinci kilidi.
Kaba bir regex eşlemesidir: zararsız bir komut ara sıra onaya düşebilir, tersi (kaçırma) olabildiğince az tutulur.

Kapsam: kubectl/oc, helm, terraform/tofu, docker ve docker compose, `dotnet ef database update|drop`, doctl/gcloud/az/oci/aws.
Sınırlar (bilinçli): yalnız Bash aracının komut metnine bakar; kabuk kısayolu/fonksiyon (`k delete ...`), betik içinde
çağrılan komutlar ve MCP/başka araçlar görünmez. Python yoksa veya girdi çözümlenemezse sessizce geçer (fail-open).
Yalnız standart kütüphane.
"""
import json
import re
import sys

K8S_VERBS = r"(apply|delete|scale|replace|patch|create|edit|drain|cordon|uncordon|taint|annotate|label|set|run|expose|exec|cp|port-forward|rollout\s+(restart|undo|pause|resume)|config\s+(use-context|set-context|delete-context))"
CLOUD_VERBS = r"(delete|destroy|terminate|remove|create|update|resize|rebuild|reboot|restart|scale|power-off|rm|put|run|modify|attach|detach)[\w-]*"
RULES = [
    (re.compile(rf"\b(kubectl|oc)\b[^|;&\n]*?\s{K8S_VERBS}\b"), "kubectl/oc ile canlı kaynak değişikliği veya tünel/exec"),
    (re.compile(r"\b(kubectl|oc)\b[^|;&\n]*\bget\s+secrets?\b[^|;&\n]*(-o|--output)[ =]?(yaml|json|jsonpath|go-template)"), "secret içeriği okuma"),
    (re.compile(r"\bhelm\s+(install|upgrade|uninstall|delete|rollback)\b"), "helm ile canlı değişiklik"),
    (re.compile(r"\b(terraform|tofu)\s+(apply|destroy|import|state\s+(rm|mv))\b"), "terraform/tofu ile altyapı değişikliği"),
    (re.compile(r"\bdocker(?:-compose|\s+compose)\b[^|;&\n]*?\s(up|down|rm|restart|stop|start|kill|run|exec)\b"), "docker compose ile servis değişikliği"),
    (re.compile(r"\bdocker\s+(push|rm|rmi|stop|kill|restart|prune|system\s+prune|(volume|network|image|container)\s+(rm|prune)|service\s+(update|rm|scale|create)|stack\s+(deploy|rm)|swarm\s+(leave|init))\b"), "docker ile kalıcı/paylaşılan kaynak değişikliği"),
    (re.compile(r"\bdotnet\s+ef\s+database\s+(update|drop)\b"), "veritabanına migration uygulama/silme"),
    (re.compile(rf"\b(doctl|gcloud|az|oci|aws)\b[^|;&\n]*?\s{CLOUD_VERBS}\b"), "bulut CLI ile kaynak oluşturma/değiştirme/silme"),
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
