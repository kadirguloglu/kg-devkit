#!/usr/bin/env python3
"""guard-infra kancasının regex kurallarını sınar: python3 scripts/test_guard_infra.py"""
import importlib.util
import os
import sys

sys.dont_write_bytecode = True  # plugin dizininde __pycache__ oluşmasın
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
    "kubectl replace -f x.yaml",
    "kubectl create deployment a --image=b",
    "kubectl edit deploy/a",
    "kubectl drain node1",
    "kubectl cordon node1",
    "kubectl uncordon node1",
    "kubectl taint nodes n k=v:NoSchedule",
    "kubectl annotate pod a k=v",
    "kubectl label pod a k=v",
    "kubectl set image deploy/a c=img:2",
    "kubectl rollout undo deploy/a",
    "kubectl rollout pause deploy/a",
    "kubectl rollout resume deploy/a",
    "oc delete pod a",
    "oc get secret a -o json",
    "kubectl get secret a --output=go-template='{{.data}}'",
    "helm install app ./chart",
    "helm uninstall app",
    "helm rollback app 1",
    "tofu apply",
    "terraform destroy",
    "terraform import a.b id",
    "terraform state rm a.b",
    "kubectl exec pod -- sh",
    "kubectl port-forward svc/x 8080:80",
    "kubectl config use-context prod",
    "kubectl run x --image=y",
    "docker compose up -d",
    "docker-compose down",
    "docker compose restart api",
    "docker push registry/app:1",
    "docker rm x",
    "docker system prune -f",
    "docker volume rm v",
    "docker stack deploy -c f.yml s",
    "dotnet ef database update",
    "dotnet ef database drop --force",
    "doctl kubernetes cluster delete x",
    "gcloud compute instances delete x",
    "az vm delete -n x -g g",
    "aws ec2 terminate-instances --instance-ids i-1",
    "aws s3 rm s3://b --recursive",
]
PASS = [
    "kubectl get pods -n prod",
    "kubectl rollout status deploy/x",
    "kubectl rollout history deploy/x",
    "kubectl logs deploy/x",
    "kubectl describe pod a",
    "kubectl top pods",
    "helm list",
    "helm status app",
    "oc get pods",
    "kubectl get secrets",
    "tofu plan",
    "kubectl config get-contexts",
    "kubectl config current-context",
    "docker ps",
    "docker logs x",
    "docker images",
    "docker compose ps",
    "docker compose logs api",
    "dotnet ef migrations list",
    "dotnet ef dbcontext info",
    "doctl account get",
    "gcloud compute instances list",
    "az group list",
    "aws s3 ls",
    "aws ec2 describe-instances",
    "aws sts get-caller-identity",
    "terraform plan",
    "ls -la",
]
bad = [c for c in ASK if not mod.check(c)] + [c for c in PASS if mod.check(c)]
if bad:
    sys.exit("Beklenmeyen sonuç:\n" + "\n".join(bad))
print(f"guard-infra: {len(ASK) + len(PASS)} örnek geçti")
