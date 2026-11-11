#!/usr/bin/env python3
"""Plugin kancalarını sınar: python3 scripts/test_guard_infra.py

1. guard-infra karar fonksiyonu: ASK listesindeki her komut onaya düşmeli, PASS listesindekiler düşmemeli.
2. Uçtan uca: betik stdin'den JSON alır; karar biçimi, bozuk girdi, ortam değişkenleri, süre sınırı.
3. agent_run_log: yalnız meta veri yazar, bozuk girdide sessiz kalır.
Hiçbir komutu ÇALIŞTIRMAZ; komut metinleri yalnız kancaya verilir.
"""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import time

sys.dont_write_bytecode = True  # plugin dizininde __pycache__ oluşmasın
HOOKS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "plugins", "kg-devkit", "hooks")
GUARD = os.path.join(HOOKS, "guard-infra.py")
RUNLOG = os.path.join(HOOKS, "agent_run_log.py")
OUTCOME = os.path.join(HOOKS, "require_outcome.py")
spec = importlib.util.spec_from_file_location("guard_infra", GUARD)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

ASK = [
    'kubectl apply -f x.yaml',
    'kubectl -n prod delete pod a',
    'kubectl --context c --namespace n rollout restart deploy/x',
    'kubectl scale deploy/x --replicas=2',
    'kubectl get secret db -o yaml',
    "kubectl get secrets -n n -o jsonpath='{.data}'",
    'helm upgrade app ./chart',
    'terraform apply -auto-approve',
    "cd x && kubectl patch deploy/a -p '{}'",
    'kubectl replace -f x.yaml',
    'kubectl create deployment a --image=b',
    'kubectl edit deploy/a',
    'kubectl drain node1',
    'kubectl cordon node1',
    'kubectl uncordon node1',
    'kubectl taint nodes n k=v:NoSchedule',
    'kubectl annotate pod a k=v',
    'kubectl label pod a k=v',
    'kubectl set image deploy/a c=img:2',
    'kubectl rollout undo deploy/a',
    'kubectl rollout pause deploy/a',
    'kubectl rollout resume deploy/a',
    'oc delete pod a',
    'oc get secret a -o json',
    "kubectl get secret a --output=go-template='{{.data}}'",
    'helm install app ./chart',
    'helm uninstall app',
    'helm rollback app 1',
    'tofu apply',
    'terraform destroy',
    'terraform import a.b id',
    'terraform state rm a.b',
    'kubectl exec pod -- sh',
    'kubectl port-forward svc/x 8080:80',
    'kubectl config use-context prod',
    'kubectl run x --image=y',
    'docker compose up -d',
    'docker-compose down',
    'docker compose restart api',
    'docker push registry/app:1',
    'docker rm x',
    'docker system prune -f',
    'docker volume rm v',
    'docker stack deploy -c f.yml s',
    'dotnet ef database update',
    'dotnet ef database drop --force',
    'doctl kubernetes cluster delete x',
    'gcloud compute instances delete x',
    'az vm delete -n x -g g',
    'aws ec2 terminate-instances --instance-ids i-1',
    'aws s3 rm s3://b --recursive',
    'oci compute instance terminate --instance-id x',
    'kubectl cp pod:/x ./x',
    'kubectl expose deploy/a --port=80',
    'docker compose rm -f api',
    'docker compose stop api',
    'docker compose start api',
    'docker compose kill api',
    'docker compose run api sh',
    'docker compose exec api sh',
    'docker rmi img:1',
    'docker kill x',
    'docker stop x',
    'docker restart x',
    'docker service update --image i s',
    'docker swarm leave',
    'docker swarm init',
    'docker network rm n',
    'docker image prune -a',
    'docker container rm c',
    'docker service rm s',
    'docker service scale s=2',
    'docker service create img',
    'docker stack rm s',
    'helm delete app',
    'terraform state mv a.b a.c',
    'kubectl config set-context x',
    'kubectl config delete-context x',
    # fiilden önce bayrak, satır devamı, alt komut biçimi, komut ikamesi
    'kubectl --context prod \\\n  -n app delete pod a',
    'helm --namespace prod upgrade app ./chart',
    'helm -n prod uninstall app',
    'terraform -chdir=infra apply',
    'terraform -chdir=infra destroy',
    'docker --context prod compose up -d',
    'docker -H ssh://prod compose down',
    'docker -H ssh://prod rm x',
    'docker --context prod rm -f x',
    'docker container stop x',
    'docker image push a',
    'docker buildx build --push -t a .',
    'dotnet-ef database update',
    'terraform state push x',
    'terraform taint a.b',
    'terraform workspace delete x',
    'kubectl debug pod/x -it --image=busybox',
    'kubectl attach pod/x',
    'kubectl autoscale deploy/x --max=5',
    'kubectl certificate approve x',
    'kubectl auth reconcile -f rbac.yaml',
    'oc rollout latest dc/x',
    'echo "$(kubectl delete pod a)"',
    'x=`kubectl delete pod a`',
    "ssh prod 'systemctl status app; kubectl delete pod a'",
    # secret okuma ve bulut fiilleri
    'kubectl get -o yaml secret db',
    'kubectl get secret db -o custom-columns=X:.data',
    "kubectl get secret db -o template --template='{{.data}}'",
    'aws secretsmanager get-secret-value --secret-id x',
    'aws ssm get-parameter --with-decryption --name x',
    'gcloud secrets versions access latest --secret x',
    'az keyvault secret show --name x --vault-name v',
    'aws ec2 stop-instances --instance-ids i-1',
    'aws s3 sync . s3://b --delete',
    'aws cloudformation deploy --stack-name x',
    'aws ecr batch-delete-image --repository-name r',
    'aws route53 change-resource-record-sets --hosted-zone-id z',
    'aws lambda invoke --function-name x out',
    'gcloud app deploy',
    'gcloud functions deploy f',
    'gcloud compute instances stop x',
    'gcloud sql instances patch x',
    'gcloud projects add-iam-policy-binding p',
    'gcloud container clusters get-credentials prod',
    'az vm stop -n x -g g',
    'az vm deallocate -n x',
    'az webapp deploy',
    'az storage blob upload -f x',
    'doctl registry garbage-collection start',
    'oci compute instance action --action STOP',
    'vault kv get secret/x',
    'sops -d secrets.yaml',
    # migration ve dağıtım araçları
    'npx prisma migrate deploy',
    'npx prisma migrate reset',
    'alembic upgrade head',
    'python manage.py migrate',
    'rails db:migrate',
    'flyway migrate',
    'helmfile apply',
    'pulumi up',
    'terragrunt apply',
    'argocd app sync x',
    'flux reconcile kustomization x',
    'ansible-playbook site.yml',
    # git
    'git push --force origin main',
    'git reset --hard HEAD~1',
    'git clean -fdx',
    # sarmalayıcılar ve bilinçli olarak sorulanlar
    'kubectl apply --dry-run=server -f x',
    'docker compose up -d   # local dev',
    'gcloud run deploy svc --image x',
    'gcloud config set project prod',
    "bash -c 'kubectl delete pod a'",
    'sudo kubectl delete pod a',
    'kubectl get pods | xargs kubectl delete pod',
    'KUBECONFIG=prod kubectl delete pod a',
    # git
    'git add .env',
    'git add k8s/secret.yaml',
    'git add config/secrets.json certs/tls.key',
    # kancanın koruduğu her araç/fiil için en az bir örnek
    'liquibase update',
    'npx knex migrate:latest',
    'npx sequelize-cli db:migrate',
    'npx typeorm migration:run',
    'skaffold run',
    'podman rm x',
    'nerdctl compose up -d',
    'terraform untaint a.b',
    'oc adm drain node1',
    'vault write secret/x v=1',
    'vault delete secret/x',
    'sops exec-env secrets.yaml env',
    'git push --mirror origin',
    'git push origin +main',
]
PASS = [
    'kubectl get pods -n prod',
    'kubectl rollout status deploy/x',
    'kubectl rollout history deploy/x',
    'kubectl logs deploy/x',
    'kubectl describe pod a',
    'kubectl top pods',
    'helm list',
    'helm status app',
    'oc get pods',
    'kubectl get secrets',
    'tofu plan',
    'kubectl config get-contexts',
    'kubectl config current-context',
    'docker ps',
    'docker logs x',
    'docker images',
    'docker compose ps',
    'docker compose logs api',
    'dotnet ef migrations list',
    'dotnet ef dbcontext info',
    'doctl account get',
    'gcloud compute instances list',
    'az group list',
    'aws s3 ls',
    'aws ec2 describe-instances',
    'aws sts get-caller-identity',
    'terraform plan',
    'ls -la',
    # git
    'git push --force-with-lease origin feat',
    'git clean -nfd',
    'git push -u origin feat',
    'git reset --soft HEAD~1',
    # tırnaklı metin, bayrak değeri, --help, dry-run, salt-okuma
    "grep -r 'kubectl apply' docs/",
    "echo 'run kubectl delete pod a manually'",
    "git commit -m 'docs: kubectl apply steps'",
    "git log --grep='helm upgrade'",
    "rg 'terraform apply' .",
    "cat docs/runbook.md | grep 'docker compose up'",
    'kubectl get pods -n prod -l run=api',
    'kubectl get pods -n label',
    'kubectl get pods -n set',
    'kubectl describe pod create-job-x',
    'kubectl get deploy -o yaml > apply.yaml',
    'kubectl auth can-i delete pods',
    'kubectl delete --help',
    'kubectl apply --dry-run=client -f x',
    'kubectl diff -f x',
    'helm upgrade --help',
    'helm upgrade app ./chart --dry-run',
    'helm template .',
    'terraform apply -help',
    'dotnet ef database update --help',
    'aws cloudformation describe-stacks --stack-name update-x',
    'aws ecr describe-images --repository-name create-thing',
    'aws s3 cp s3://bucket/file ./file',
    'aws logs tail /aws/lambda/delete-user',
    'gcloud run services describe svc',
    'gcloud run services list',
    'gcloud compute instances describe run-vm',
    'az resource list --tag update=yes',
    'doctl registry repository list-tags r',
    'kubectl get secret db -o name',
    'kubectl describe secret db',
    "ssh prod 'systemctl status app'",
    'docker build -t a .',
    'npx prisma generate',
    'alembic history',
    'ansible-playbook site.yml --check',
    # git
    'git add .env.example',
    'git add src/a.ts',
    'git add -A',
    'git add deploy/id_rsa.pub',
]
# Bilinçli kör noktalar (belgelenmiş sınır): kanca bunları GÖREMEZ. Biri yakalanmaya başlarsa listeden çıkarıp ASK'a taşı.
KNOWN_BLIND = ['k delete pod a', 'KUBECTL=kubectl; $KUBECTL delete pod a', './deploy.sh prod', 'make deploy', 'npm run deploy', "psql -h prod -c 'delete from users'", 'scp x prod:/etc/app', 'rsync -a --delete . prod:/srv', 'cat .env', 'python3 -c "import subprocess; subprocess.run([\'kubectl\',\'delete\',\'pod\',\'a\'])"']


def run(script, payload, args=(), env=None):
    e = dict(os.environ)
    e.pop("KG_GUARD_DISABLE", None)
    e.pop("KG_GUARD_LOCAL_COMPOSE", None)
    e.pop("KG_AGENT_LOG", None)
    e.pop("KG_REQUIRE_OUTCOME", None)
    e.update(env or {})
    data = payload if isinstance(payload, bytes) else json.dumps(payload).encode()
    return subprocess.run([sys.executable, "-B", script, *args], input=data, capture_output=True, env=e, timeout=30)


def decision(payload, env=None):
    p = run(GUARD, payload, env=env)
    assert p.returncode == 0 and p.stderr == b"", (payload, p.returncode, p.stderr)
    return json.loads(p.stdout)["hookSpecificOutput"] if p.stdout.strip() else None


def cmd(text, **extra):
    return {"tool_name": "Bash", "tool_input": {"command": text}, **extra}


def test_rules():
    bad = [c for c in ASK if not mod.check(c)] + [c for c in PASS if mod.check(c)]
    seen = [c for c in KNOWN_BLIND if mod.check(c)]
    assert not bad, "Beklenmeyen sonuç:\n" + "\n".join(bad)
    assert not seen, "Kör nokta artık yakalanıyor; ASK listesine taşı:\n" + "\n".join(seen)
    assert len(set(ASK) & set(PASS)) == 0


def test_end_to_end():
    out = decision(cmd("kubectl delete pod a"))
    assert out["hookEventName"] == "PreToolUse" and out["permissionDecision"] == "ask"
    assert out["permissionDecisionReason"].startswith("kg-devkit: ")
    assert decision(cmd("ls -la")) is None
    # agent adı gerekçeye eklenir; komut metni ve içindeki değerler geri yazılmaz
    out = decision(cmd("TOKEN=abc123 helm -n prod upgrade a ./c", agent_type="kg-devkit:devops-engineer"))
    assert "kg-devkit:devops-engineer" in out["permissionDecisionReason"] and "abc123" not in json.dumps(out)
    # kg-devkit agent'ı içinden commit/push sorulur; ana oturumda ve başka plugin'in agent'ında sorulmaz
    for text in ("git commit -m x", "git -C repo push origin feat", "cd app && git merge main", "git tag v1"):
        assert decision(cmd(text, agent_type="kg-devkit:backend-developer")), text
        assert decision(cmd(text)) is None, text
        assert decision(cmd(text, agent_type="other:helper")) is None, text
    for text in ("git status --short", "git diff --cached", "git log --oneline", "git commit --help"):
        assert decision(cmd(text, agent_type="kg-devkit:devops-engineer")) is None, text
    assert decision(cmd("git commit -m x", agent_type="kg-devkit:backend-developer"), {"KG_GUARD_DISABLE": "git"}) is None
    # bozuk veya beklenmeyen girdi: sessiz, çıkış 0 (fail-open)
    for raw in (b"", b"not json", b"[1,2]", b'{"tool_input":"x"}', b'{"tool_input":{"command":["kubectl","delete"]}}', b"null"):
        p = run(GUARD, raw)
        assert (p.returncode, p.stdout, p.stderr) == (0, b"", b""), (raw, p)
    # dengesiz tırnak: ayrıştırılamaz, şüphede sor
    assert decision(cmd('echo "unbalanced; kubectl delete pod a'))["permissionDecision"] == "ask"
    assert decision(cmd('echo "unbalanced text')) is None
    # idempotent
    assert run(GUARD, cmd("terraform destroy")).stdout == run(GUARD, cmd("terraform destroy")).stdout


def test_env_switches():
    assert decision(cmd("git reset --hard")) and decision(cmd("git reset --hard"), {"KG_GUARD_DISABLE": "git"}) is None
    assert decision(cmd("alembic upgrade head"), {"KG_GUARD_DISABLE": "git, migrate"}) is None
    assert decision(cmd("pulumi up"), {"KG_GUARD_DISABLE": "deploytools"}) is None
    assert decision(cmd("kubectl delete pod a"), {"KG_GUARD_DISABLE": "k8s,git,migrate,deploytools"})  # çekirdek gruplar kapatılamaz
    allow = {"KG_GUARD_LOCAL_COMPOSE": "allow"}
    assert decision(cmd("docker compose up -d"), allow) is None
    assert decision(cmd("docker --context prod compose up -d"), allow)
    assert decision(cmd("DOCKER_HOST=ssh://prod docker compose up -d"), allow)
    assert decision(cmd("docker push registry/app:1"), allow)


def test_time_bound():
    for text in ("kubectl x " * 10000, "aws x " * 10000, "docker compose x " * 5000, "a" * 500000, "'" + "kubectl apply " * 20000):
        start = time.perf_counter()
        mod.check(text)
        assert time.perf_counter() - start < 2, f"yavaş: {text[:20]!r} x {len(text)} bayt"


def test_run_log():
    with tempfile.TemporaryDirectory() as tmp:
        base = {"session_id": "s1", "agent_id": "a1", "agent_type": "kg-devkit:database-reviewer", "prompt": "GIZLI-PROMPT"}
        run(RUNLOG, {**base, "hook_event_name": "SubagentStart"}, [tmp])
        run(RUNLOG, {**base, "hook_event_name": "SubagentStop", "permission_mode": "default",
                     "last_assistant_message": "bulgu GIZLI-RAPOR\nVERDICT: UNCLEAR sonra düzeltildi\n**VERDICT: PASS**"}, [tmp])
        run(RUNLOG, {**base, "agent_id": "a2", "agent_type": "kg-devkit:backend-developer", "hook_event_name": "SubagentStop",
                     "last_assistant_message": "STATUS: PARTIAL\nCHANGED: x"}, [tmp])
        for raw in (b"", b"[]", b"not json"):
            p = run(RUNLOG, raw, [tmp])
            assert (p.returncode, p.stdout, p.stderr) == (0, b"", b"")
        assert run(RUNLOG, {**base, "hook_event_name": "SubagentStop"}, [tmp], {"KG_AGENT_LOG": "off"}).returncode == 0
        assert run(RUNLOG, base, ["${CLAUDE_PLUGIN_DATA}"]).returncode == 0  # çözülmemiş değişken: yazma
        text = open(os.path.join(tmp, "agent-runs.jsonl"), encoding="utf-8").read()
        rows = [json.loads(line) for line in text.splitlines()]
        assert len(rows) == 3 and "GIZLI" not in text
        # aynı agent iki kez durursa (sonuç satırı hatırlatması) özet tek çalışma sayar ve son sonucu alır
        run(RUNLOG, {**base, "hook_event_name": "SubagentStop", "last_assistant_message": "VERDICT: FAIL"}, [tmp])
        out = subprocess.run([sys.executable, "-B", RUNLOG, "--summary", tmp], capture_output=True, text=True).stdout
        line = next(row for row in out.splitlines() if "database-reviewer" in row)
        assert " 1 " in line and "VERDICT:FAIL" in line and "VERDICT:PASS" not in line, line
        assert rows[1]["outcome"] == "VERDICT:PASS" and rows[2]["outcome"] == "STATUS:PARTIAL" and "outcome" not in rows[0]
        assert set(rows[1]) <= {"ts", "hook_event_name", "session_id", "agent_id", "agent_type", "permission_mode", "outcome"}
        p = subprocess.run([sys.executable, "-B", RUNLOG, "--summary", tmp], capture_output=True)
        assert p.returncode == 0 and b"kg-devkit:database-reviewer" in p.stdout
    assert not os.path.exists("${CLAUDE_PLUGIN_DATA}")


def test_require_outcome():
    def blocked(agent, message, env=None, **extra):
        p = run(OUTCOME, {"hook_event_name": "SubagentStop", "agent_type": agent, "last_assistant_message": message, **extra}, env=env)
        assert p.returncode == 0 and p.stderr == b"", p
        return bool(p.stdout.strip()) and json.loads(p.stdout)["decision"] == "block"

    assert blocked("kg-devkit:database-reviewer", "bulgular...")
    assert not blocked("kg-devkit:database-reviewer", "bulgular\nVERDICT: FAIL")
    assert not blocked("kg-devkit:api-contract-reviewer", "x\n**VERDICT: UNCLEAR** eksik: diff")
    assert blocked("kg-devkit:tenant-security-reviewer", "STATUS: DONE")  # reviewer için STATUS yetmez
    assert blocked("kg-devkit:backend-developer", "değişti: a.cs")
    assert not blocked("kg-devkit:backend-developer", "STATUS: PARTIAL\nCHANGED: a.cs")
    assert not blocked("kg-devkit:frontend-browser-tester", "senaryolar...\nSTATUS: BLOCKED")
    assert blocked("kg-devkit:devops-operator", "bitti")
    # danışmanlar, başka plugin'ler ve yerleşik agent'lar kapsam dışı
    for agent in ("kg-devkit:scope-advisor", "kg-devkit:engineering-software-architect", "other:database-reviewer", "Explore", None):
        assert not blocked(agent, "sonuç satırı yok")
    assert not blocked("kg-devkit:database-reviewer", "satır yok", stop_hook_active=True)  # ikinci durma: döngü yok
    assert not blocked("kg-devkit:database-reviewer", "satır yok", env={"KG_REQUIRE_OUTCOME": "off"})
    assert not blocked("kg-devkit:database-reviewer", None)
    for raw in (b"", b"[]", b"not json", b"null"):
        p = run(OUTCOME, raw)
        assert (p.returncode, p.stdout, p.stderr) == (0, b"", b"")
    # yazar agent listesi agent dosyalarıyla eşit kalmalı
    spec2 = importlib.util.spec_from_file_location("require_outcome", OUTCOME)
    ro = importlib.util.module_from_spec(spec2)
    spec2.loader.exec_module(ro)
    agents_dir = os.path.join(os.path.dirname(HOOKS), "agents")
    writers = set()
    for name in os.listdir(agents_dir):
        text = open(os.path.join(agents_dir, name), encoding="utf-8").read()
        tools = next(line for line in text.splitlines() if line.startswith("tools:"))
        if "Bash" in tools:
            writers.add(name[:-3])
    assert writers == ro.WRITERS, (writers ^ ro.WRITERS)


def test_hooks_json():
    cfg = json.load(open(os.path.join(HOOKS, "hooks.json"), encoding="utf-8"))["hooks"]
    for event, entries in cfg.items():
        for entry in entries:
            for hook in entry["hooks"]:
                assert hook.get("timeout"), f"{event}: timeout yok"
                assert "${CLAUDE_PLUGIN_ROOT}/hooks/" in hook["command"], f"{event}: plugin köküne göre yol değil"


if __name__ == "__main__":
    tests = [test_rules, test_end_to_end, test_env_switches, test_time_bound, test_run_log, test_require_outcome, test_hooks_json]
    for test in tests:
        test()
    print(f"kancalar: {len(ASK)} onay + {len(PASS)} geçiş örneği, {len(KNOWN_BLIND)} bilinen kör nokta, {len(tests)} test geçti")
