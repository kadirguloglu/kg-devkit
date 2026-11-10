#!/usr/bin/env python3
"""guard-infra v1 (mevcut) ile önerilen v2'yi aynı senaryolarda karşılaştırır. Hiçbir komutu ÇALIŞTIRMAZ; yalnız
kancaların karar fonksiyonuna metin verir.

Kullanım (repo kökünden):
    python3 plugins/kg-devkit/analysis/proposals/tests/test_guard_probe.py            # özet + v2 için assert
    python3 plugins/kg-devkit/analysis/proposals/tests/test_guard_probe.py --table    # satır satır tablo
Çıkış kodu: v2 beklentilerden saparsa 1. v1 sapmaları yalnız raporlanır (mevcut davranışın kanıtı).
"""
import ast
import importlib.util
import os
import sys
import time

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", "..", ".."))


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


v1 = load(os.path.join(ROOT, "plugins", "kg-devkit", "hooks", "guard-infra.py"), "guard_v1")
v2 = load(os.path.join(HERE, "..", "hooks", "guard_infra_v2.py"), "guard_v2")

# Mevcut resmi test listeleri (scripts/test_guard_infra.py) çalıştırılmadan AST ile okunur.
legacy = {}
tree = ast.parse(open(os.path.join(ROOT, "scripts", "test_guard_infra.py"), encoding="utf-8").read())
for node in tree.body:
    if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", None) in ("ASK", "PASS"):
        legacy[node.targets[0].id] = ast.literal_eval(node.value)

A, P = True, False
EXTENDED = [
    # --- H-01: fiilden önce bayrak / satır devamı / alt komut biçimi ---
    ("H-01", A, "kubectl --context prod \\\n  -n app delete pod a"),
    ("H-01", A, "helm --namespace prod upgrade app ./chart"),
    ("H-01", A, "helm -n prod uninstall app"),
    ("H-01", A, "terraform -chdir=infra apply"),
    ("H-01", A, "terraform -chdir=infra destroy"),
    ("H-01", A, "docker --context prod compose up -d"),
    ("H-01", A, "docker -H ssh://prod compose down"),
    ("H-01", A, "docker -H ssh://prod rm x"),
    ("H-01", A, "docker --context prod rm -f x"),
    ("H-01", A, "docker container stop x"),
    ("H-01", A, "docker image push a"),
    ("H-01", A, "docker buildx build --push -t a ."),
    ("H-01", A, "dotnet-ef database update"),
    ("H-01", A, "terraform state push x"),
    ("H-01", A, "terraform taint a.b"),
    ("H-01", A, "terraform workspace delete x"),
    ("H-01", A, "kubectl debug pod/x -it --image=busybox"),
    ("H-01", A, "kubectl attach pod/x"),
    ("H-01", A, "kubectl autoscale deploy/x --max=5"),
    ("H-01", A, "kubectl certificate approve x"),
    ("H-01", A, "kubectl auth reconcile -f rbac.yaml"),
    ("H-01", A, "oc rollout latest dc/x"),
    ("H-01", A, 'echo "$(kubectl delete pod a)"'),
    ("H-01", A, "x=`kubectl delete pod a`"),
    ("H-01", A, "ssh prod 'systemctl status app; kubectl delete pod a'"),
    # --- H-02: secret okuma ve eksik bulut fiilleri ---
    ("H-02", A, "kubectl get -o yaml secret db"),
    ("H-02", A, "kubectl get secret db -o custom-columns=X:.data"),
    ("H-02", A, "kubectl get secret db -o template --template='{{.data}}'"),
    ("H-02", A, "aws secretsmanager get-secret-value --secret-id x"),
    ("H-02", A, "aws ssm get-parameter --with-decryption --name x"),
    ("H-02", A, "gcloud secrets versions access latest --secret x"),
    ("H-02", A, "az keyvault secret show --name x --vault-name v"),
    ("H-02", A, "aws ec2 stop-instances --instance-ids i-1"),
    ("H-02", A, "aws s3 sync . s3://b --delete"),
    ("H-02", A, "aws cloudformation deploy --stack-name x"),
    ("H-02", A, "aws ecr batch-delete-image --repository-name r"),
    ("H-02", A, "aws route53 change-resource-record-sets --hosted-zone-id z"),
    ("H-02", A, "aws lambda invoke --function-name x out"),
    ("H-02", A, "gcloud app deploy"),
    ("H-02", A, "gcloud functions deploy f"),
    ("H-02", A, "gcloud compute instances stop x"),
    ("H-02", A, "gcloud sql instances patch x"),
    ("H-02", A, "gcloud projects add-iam-policy-binding p"),
    ("H-02", A, "gcloud container clusters get-credentials prod"),
    ("H-02", A, "az vm stop -n x -g g"),
    ("H-02", A, "az vm deallocate -n x"),
    ("H-02", A, "az webapp deploy"),
    ("H-02", A, "az storage blob upload -f x"),
    ("H-02", A, "doctl registry garbage-collection start"),
    ("H-02", A, "oci compute instance action --action STOP"),
    ("H-02", A, "vault kv get secret/x"),
    ("H-02", A, "sops -d secrets.yaml"),
    # --- H-07: yığından bağımsız migration ve dağıtım araçları ---
    ("H-07", A, "npx prisma migrate deploy"),
    ("H-07", A, "npx prisma migrate reset"),
    ("H-07", A, "alembic upgrade head"),
    ("H-07", A, "python manage.py migrate"),
    ("H-07", A, "rails db:migrate"),
    ("H-07", A, "flyway migrate"),
    ("H-07", A, "helmfile apply"),
    ("H-07", A, "pulumi up"),
    ("H-07", A, "terragrunt apply"),
    ("H-07", A, "argocd app sync x"),
    ("H-07", A, "flux reconcile kustomization x"),
    ("H-07", A, "ansible-playbook site.yml"),
    # --- R-git: kullanıcının değişikliklerini ezebilen git komutları (yeni kural grubu) ---
    ("R-git", A, "git push --force origin main"),
    ("R-git", A, "git reset --hard HEAD~1"),
    ("R-git", A, "git clean -fdx"),
    ("R-git", P, "git push --force-with-lease origin feat"),
    ("R-git", P, "git clean -nfd"),
    ("R-git", P, "git push -u origin feat"),
    ("R-git", P, "git reset --soft HEAD~1"),
    # --- H-03: yanlış pozitifler (onaya düşmemeli) ---
    ("H-03", P, "grep -r 'kubectl apply' docs/"),
    ("H-03", P, "echo 'run kubectl delete pod a manually'"),
    ("H-03", P, "git commit -m 'docs: kubectl apply steps'"),
    ("H-03", P, "git log --grep='helm upgrade'"),
    ("H-03", P, "rg 'terraform apply' ."),
    ("H-03", P, "cat docs/runbook.md | grep 'docker compose up'"),
    ("H-03", P, "kubectl get pods -n prod -l run=api"),
    ("H-03", P, "kubectl get pods -n label"),
    ("H-03", P, "kubectl get pods -n set"),
    ("H-03", P, "kubectl describe pod create-job-x"),
    ("H-03", P, "kubectl get deploy -o yaml > apply.yaml"),
    ("H-03", P, "kubectl auth can-i delete pods"),
    ("H-03", P, "kubectl delete --help"),
    ("H-03", P, "kubectl apply --dry-run=client -f x"),
    ("H-03", P, "kubectl diff -f x"),
    ("H-03", P, "helm upgrade --help"),
    ("H-03", P, "helm upgrade app ./chart --dry-run"),
    ("H-03", P, "helm template ."),
    ("H-03", P, "terraform apply -help"),
    ("H-03", P, "dotnet ef database update --help"),
    ("H-03", P, "aws cloudformation describe-stacks --stack-name update-x"),
    ("H-03", P, "aws ecr describe-images --repository-name create-thing"),
    ("H-03", P, "aws s3 cp s3://bucket/file ./file"),
    ("H-03", P, "aws logs tail /aws/lambda/delete-user"),
    ("H-03", P, "gcloud run services describe svc"),
    ("H-03", P, "gcloud run services list"),
    ("H-03", P, "gcloud compute instances describe run-vm"),
    ("H-03", P, "az resource list --tag update=yes"),
    ("H-03", P, "doctl registry repository list-tags r"),
    ("H-03", P, "kubectl get secret db -o name"),
    ("H-03", P, "kubectl describe secret db"),
    ("H-03", P, "ssh prod 'systemctl status app'"),
    ("H-03", P, "docker build -t a ."),
    ("H-03", P, "npx prisma generate"),
    ("H-03", P, "alembic history"),
    ("H-03", P, "ansible-playbook site.yml --check"),
    # v2'de de bilinçli olarak onaya düşenler (dry-run=server API'ye gider; yerel/uzak compose ayırt edilemez)
    ("keep", A, "kubectl apply --dry-run=server -f x"),
    ("keep", A, "docker compose up -d   # local dev"),
    ("keep", A, "gcloud run deploy svc --image x"),
    ("keep", A, "gcloud config set project prod"),
    ("keep", A, "bash -c 'kubectl delete pod a'"),
    ("keep", A, "sudo kubectl delete pod a"),
    ("keep", A, "kubectl get pods | xargs kubectl delete pod"),
    ("keep", A, "KUBECONFIG=prod kubectl delete pod a"),
]
# Her iki sürümün de bilinçli olarak GÖREMEDİĞİ biçimler (belgelenmiş sınır; assert edilmez, yalnız listelenir)
KNOWN_BLIND = [
    "k delete pod a", "KUBECTL=kubectl; $KUBECTL delete pod a", "./deploy.sh prod", "make deploy", "npm run deploy",
    "psql -h prod -c 'delete from users'", "scp x prod:/etc/app", "rsync -a --delete . prod:/srv", "cat .env",
    "python3 -c \"import subprocess; subprocess.run(['kubectl','delete','pod','a'])\"",
]


def main():
    table = "--table" in sys.argv
    bad_v2, miss_v1 = [], []
    for want, cmds in ((A, legacy["ASK"]), (P, legacy["PASS"])):
        for c in cmds:
            if bool(v2.check(c)) != want:
                bad_v2.append(("legacy", want, c))
    groups = {}
    for gid, want, c in EXTENDED:
        r1, r2 = bool(v1.check(c)), bool(v2.check(c))
        g = groups.setdefault(gid, [0, 0, 0])
        g[0] += 1
        g[1] += r1 == want
        g[2] += r2 == want
        if r2 != want:
            bad_v2.append((gid, want, c))
        if r1 != want:
            miss_v1.append((gid, want, c))
        if table:
            f = lambda b: "ASK " if b else "pass"
            print(f"{gid:6} beklenen={f(want)} v1={f(r1)}{'' if r1 == want else ' !'} v2={f(r2)}{'' if r2 == want else ' !'} | {c!r}")
    print(f"resmi liste (scripts/test_guard_infra.py): {len(legacy['ASK']) + len(legacy['PASS'])} örnek; v2 sapma: "
          f"{sum(1 for b in bad_v2 if b[0] == 'legacy')}")
    print("grup    örnek  v1-doğru  v2-doğru")
    for gid, (n, a, b) in groups.items():
        print(f"{gid:7} {n:5} {a:9} {b:9}")
    n = len(EXTENDED)
    print(f"toplam  {n:5} {n - len(miss_v1):9} {n - len([b for b in bad_v2 if b[0] != 'legacy']):9}")
    print("bilinen kör noktalar (v1/v2 ASK?):")
    for c in KNOWN_BLIND:
        print(f"  v1={bool(v1.check(c))!s:5} v2={bool(v2.check(c))!s:5} | {c}")
    for label, unit in (("kubectl x ", 4000), ("aws x ", 4000)):
        c = label * unit
        t = time.perf_counter(); v1.check(c); d1 = (time.perf_counter() - t) * 1000
        t = time.perf_counter(); v2.check(c); d2 = (time.perf_counter() - t) * 1000
        print(f"süre  {label!r}x{unit} ({len(c)} bayt): v1={d1:.0f} ms  v2={d2:.0f} ms")
    if bad_v2:
        sys.exit("v2 beklenmeyen sonuç:\n" + "\n".join(f"  [{g}] beklenen={'ASK' if w else 'pass'} | {c!r}" for g, w, c in bad_v2))
    print("v2: tüm beklentiler karşılandı")


if __name__ == "__main__":
    main()
