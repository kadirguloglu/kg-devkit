#!/usr/bin/env python3
"""guard-infra kancasının regex kurallarını sınar: python3 scripts/test_guard_infra.py"""
import importlib.util
import os
import sys

path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "plugins", "kg-devkit", "hooks", "guard-infra.py")
spec = importlib.util.spec_from_file_location("guard_infra", path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

ASK = [
    "kubectl apply -f x.yaml",
    "kubectl -n prod delete pod a",
    "kubectl --context c --namespace n rollout restart deploy/x",
    "kubectl scale deploy/x --replicas=2",
    "kubectl get secret db -o yaml",
    "kubectl get secrets -n n -o jsonpath='{.data}'",
    "helm upgrade app ./chart",
    "terraform apply -auto-approve",
    "cd x && kubectl patch deploy/a -p '{}'",
]
PASS = [
    "kubectl get pods -n prod",
    "kubectl rollout status deploy/x",
    "kubectl rollout history deploy/x",
    "kubectl logs deploy/x",
    "kubectl describe pod a",
    "kubectl top pods",
    "helm list",
    "terraform plan",
    "ls -la",
]
bad = [c for c in ASK if not mod.check(c)] + [c for c in PASS if mod.check(c)]
if bad:
    sys.exit("Beklenmeyen sonuç:\n" + "\n".join(bad))
print(f"guard-infra: {len(ASK) + len(PASS)} örnek geçti")
