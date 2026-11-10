#!/usr/bin/env python3
"""PreToolUse (Bash) kancası: canlı ortamı değiştiren, secret okuyan veya kullanıcının çalışmasını silebilen komutları
kullanıcı onayına düşürür.

Karar her zaman "ask"tir (bloklamaz); agent metnindeki "açık onay olmadan yok" kuralının ikinci kilidi. Etkileşimsiz
çalışmada (`claude -p`, `dontAsk`) Claude Code "ask" kararını ret olarak uygular: komut çalışmaz.

Komut `shlex` ile belirteçlere ayrılır: tırnak içindeki metin (grep/echo/commit mesajı) komut sayılmaz, satır devamı
birleştirilir, fiilden önceki global bayraklar atlanır, `bash -c`/`ssh`/`eval`/`sudo`/`xargs` sarmalayıcılarının ve
`$(...)`/backtick ikamelerinin içine girilir. `--help` ve `--dry-run=client` sorulmaz. Ayrıştırılamayan komutta
(dengesiz tırnak) kaba bir regex'e düşülür ve şüphede sorulur.

Kural grupları:
  k8s      kubectl/oc değiştirici fiiller, exec/cp/port-forward/debug, secret içeriği okuma
  helm     install/upgrade/uninstall/delete/rollback
  iac      terraform/tofu apply/destroy/import/taint/state rm|mv|push/workspace delete
  docker   docker/podman/nerdctl ve compose: kalıcı/paylaşılan kaynak değişikliği, push
  cloud    aws/gcloud/az/doctl/oci: oluşturma/değiştirme/silme/durdurma/dağıtım ve secret/kimlik okuma
  secrets  vault, sops
  migrate  dotnet ef, prisma, alembic, django, rails, flyway, liquibase, knex, sequelize, typeorm
  deploytools  helmfile, pulumi, skaffold, terragrunt, argocd, flux, ansible-playbook
  git      push --force, reset --hard, clean -f, secret görünümlü dosyayı `git add`

Ortam değişkenleri (isteğe bağlı):
  KG_GUARD_DISABLE=git,migrate,deploytools   adı verilen kural gruplarını kapatır (yalnız bu üçü kapatılabilir)
  KG_GUARD_LOCAL_COMPOSE=allow               uzak hedef (-H/--context/DOCKER_HOST) yoksa docker compose sorulmaz

Sınırlar (bilinçli): yalnız Bash aracının komut metnine bakar; kabuk kısayolu/fonksiyon (`k delete ...`), değişkenle
çağrı (`$KUBECTL ...`), betik/Makefile içinde çağrılan komutlar (`./deploy.sh`, `make deploy`), `psql`, `scp`/`rsync`
ve MCP/başka araçlar görünmez. Bulut CLI fiil kümeleri sezgiseldir; tanınmayan fiil geçer (aws hariç: orada
salt-okuma olarak tanınmayan işlem sorulur). Python yoksa veya girdi çözümlenemezse sessizce geçer (fail-open).
Yalnız standart kütüphane. Testler: python3 scripts/test_guard_infra.py
"""
import json
import os
import re
import shlex
import sys

MAX_LEN = 20000  # yalnız regex yedeği için: ayrıştırma hatasında ilk MAX_LEN karakter taranır
SEPARATORS = set(";|&()")
SHELLS = {"bash", "sh", "zsh", "dash", "ksh", "fish"}
PREFIX = {"sudo", "doas", "env", "time", "nohup", "nice", "command", "builtin", "exec", "watch", "timeout",
          "xargs", "microk8s", "k3s", "minikube", "stdbuf", "ionice"}
PREFIX_VALUE_FLAGS = {"-u", "-g", "-n", "-I", "-P", "-L", "-s", "-k", "--user", "--group", "--signal", "--kill-after"}

K8S_VALUE_FLAGS = {"-n", "--namespace", "--context", "--kubeconfig", "-s", "--server", "--cluster", "--user",
                   "--as", "--as-group", "--token", "--request-timeout", "-v", "--v", "--cache-dir",
                   "--certificate-authority", "--client-certificate", "--client-key", "--tls-server-name"}
K8S_VERBS = {"apply", "delete", "scale", "replace", "patch", "create", "edit", "drain", "cordon", "uncordon",
             "taint", "annotate", "label", "set", "run", "expose", "exec", "cp", "port-forward", "debug",
             "attach", "proxy", "autoscale", "new-app", "new-project", "start-build", "import-image"}
K8S_TWO = {"rollout": {"restart", "undo", "pause", "resume", "latest", "cancel", "retry"},
           "config": {"use-context", "set-context", "delete-context", "set-cluster", "delete-cluster",
                      "set-credentials", "delete-user", "set", "unset", "rename-context"},
           "certificate": {"approve", "deny"}, "auth": {"reconcile"}}
SECRET_OUTPUT = ("yaml", "json", "jsonpath", "go-template", "template", "custom-columns")

HELM_VALUE_FLAGS = {"-n", "--namespace", "--kube-context", "--kubeconfig", "--kube-apiserver", "--kube-token",
                    "--kube-as-user", "--registry-config", "--repository-config", "--repository-cache"}
HELM_VERBS = {"install", "upgrade", "uninstall", "delete", "rollback"}
TF_VERBS = {"apply", "destroy", "import", "taint", "untaint"}
TF_TWO = {"state": {"rm", "mv", "push"}, "workspace": {"delete"}}

DOCKER_VALUE_FLAGS = {"-c", "--context", "-H", "--host", "--config", "-l", "--log-level", "--tlscacert",
                      "--tlscert", "--tlskey"}
COMPOSE_VALUE_FLAGS = {"-f", "--file", "-p", "--project-name", "--profile", "--env-file", "--project-directory",
                       "--parallel", "--ansi", "--progress"}
COMPOSE_VERBS = {"up", "down", "rm", "restart", "stop", "start", "kill", "run", "exec"}
DOCKER_VERBS = {"push", "rm", "rmi", "stop", "kill", "restart", "prune"}
DOCKER_TWO = {"system": {"prune"}, "volume": {"rm", "prune"}, "network": {"rm", "prune"},
              "image": {"rm", "prune", "push"}, "container": {"rm", "prune", "stop", "kill", "restart"},
              "builder": {"prune"}, "service": {"update", "rm", "scale", "create", "rollback"},
              "stack": {"deploy", "rm"}, "swarm": {"leave", "init"}}

AWS_VALUE_FLAGS = {"--profile", "--region", "--output", "--endpoint-url", "--query", "--color", "--ca-bundle",
                   "--cli-read-timeout", "--cli-connect-timeout", "--cli-binary-format"}
AWS_READ_PREFIX = ("describe", "list", "get", "ls", "head", "wait", "help", "filter", "tail", "lookup", "search",
                   "show", "view", "validate", "check", "estimate", "preview", "decode", "presign", "simulate",
                   "scan", "query", "select", "batch-get")
AWS_SECRET_OPS = {"get-secret-value", "batch-get-secret-value", "get-login-password", "get-authorization-token",
                  "get-password-data", "get-session-token"}

CLOUD_BOOL_FLAGS = {"--quiet", "-q", "--yes", "-y", "--force", "-f", "--debug", "--verbose", "--no-wait",
                    "--async", "--only-show-errors", "--no-user-output-enabled", "--help", "-h"}
CLOUD_READ = {"list", "describe", "show", "get", "read", "info", "tail", "help", "version", "ls", "cat", "du",
              "logs", "check", "validate", "diff", "export", "wait", "exists", "query", "search", "browse"}
CLOUD_SECRET = {"access", "get-credentials", "get-access-token", "print-access-token", "print-identity-token",
                "get-login-password", "print-refresh-token"}
CLOUD_MUTATE = {"delete", "destroy", "terminate", "remove", "create", "update", "resize", "rebuild", "reboot",
                "restart", "scale", "power-off", "power-on", "rm", "put", "run", "modify", "attach", "detach",
                "stop", "start", "deallocate", "deploy", "patch", "reset", "set", "unset", "import", "ssh", "scp",
                "execute", "rollback", "promote", "failover", "restore", "move", "mv", "cp", "rsync", "apply",
                "replace", "enable", "disable", "submit", "activate", "revoke", "upload", "save", "action",
                "purge", "rotate", "redeploy", "swap", "add", "invoke", "call", "bulk-upload", "bulk-delete",
                "connect", "expose", "migrate", "upgrade", "resume", "suspend", "cancel", "abandon", "recreate"}

MIGRATE_RULES = [  # (komut adı, ardışık belirteç dizileri)
    ("prisma", [("migrate", "deploy"), ("migrate", "reset"), ("db", "push"), ("migrate", "resolve")]),
    ("alembic", [("upgrade",), ("downgrade",), ("stamp",)]),
    ("flyway", [("migrate",), ("clean",), ("undo",), ("repair",)]),
    ("liquibase", [("update",), ("rollback",), ("drop-all",), ("dropAll",)]),
]
DEPLOY_TOOLS = {
    "helmfile": {"apply", "sync", "destroy", "delete"},
    "pulumi": {"up", "destroy", "refresh", "import", "cancel"},
    "skaffold": {"run", "deploy", "delete", "dev"},
    "terragrunt": {"apply", "destroy", "import"},
}

SECRET_FILE = re.compile(r"^(\.env(\..+)?|.*\.(pem|pfx|p12|key|kubeconfig)|id_(rsa|ed25519|ecdsa|dsa)|.*secrets?\.(ya?ml|json|env)|credentials(\.json)?)$")
SECRET_FILE_OK = re.compile(r"(example|sample|template|dist|\.pub$)")

LONG_TOKEN = re.compile(r"(\S{4096})\S+")
LEGACY = re.compile(  # ayrıştırma başarısız olursa kaba, doğrusal zamanlı yedek
    r"\b(kubectl|oc|helm|terraform|tofu|terragrunt|doctl|gcloud|az|oci|aws|docker|docker-compose|dotnet|pulumi)\b"
    r".{0,400}?\b(apply|delete|destroy|scale|replace|patch|create|edit|drain|exec|rollout|install|upgrade|uninstall"
    r"|rollback|import|up|down|rm|rmi|push|stop|kill|restart|prune|update|drop|terminate|deploy|secret)", re.S)


def _disabled():
    return {x.strip() for x in os.environ.get("KG_GUARD_DISABLE", "").split(",") if x.strip()}


def _positionals(args, value_flags=(), bool_flags=None):
    """Bayrakları (ve bilinen bayrakların değerlerini) atlayıp konumsal belirteçleri döndürür.

    bool_flags verilirse: bilinmeyen `--bayrak` (eşittirsiz) kendisinden sonraki belirteci değer olarak yutar.
    """
    out, i = [], 0
    while i < len(args):
        a = args[i]
        if a == "--":
            out.extend(args[i + 1:])
            break
        if a.startswith("-") and len(a) > 1:
            if "=" in a:
                pass
            elif a in value_flags:
                i += 1
            elif bool_flags is not None and a not in bool_flags and a.startswith("--"):
                i += 1
        else:
            out.append(a)
        i += 1
    return out


def _has(args, *flags):
    return any(a == f or a.startswith(f + "=") for a in args for f in flags)


def _is_help(args):
    return any(a in ("--help", "-h", "-help") for a in args)


def _flag_value(args, *names):
    """-o yaml | -o=yaml | -oyaml | --output yaml | --output=yaml biçimlerinin değerini verir."""
    for i, a in enumerate(args):
        for n in names:
            if a == n and i + 1 < len(args):
                return args[i + 1]
            if a.startswith(n + "="):
                return a[len(n) + 1:]
            if not n.startswith("--") and a.startswith(n) and len(a) > len(n):
                return a[len(n):]
    return None


def r_kubectl(args, env):
    if _is_help(args):
        return None
    pos = _positionals(args, K8S_VALUE_FLAGS)
    if pos and pos[0] == "kubectl":  # microk8s kubectl / minikube kubectl --
        pos = pos[1:]
    if pos and pos[0] == "adm":
        pos = pos[1:]
        if pos and pos[0] in {"policy", "upgrade", "taint", "drain", "cordon", "uncordon", "prune", "migrate"}:
            return "kubectl/oc adm ile küme değişikliği"
    if not pos:
        return None
    verb = pos[0]
    if verb == "get":
        out = _flag_value(args, "-o", "--output") or ""
        res = [p for p in pos[1:] if re.match(r"^(.*,)?secrets?([/,.]|$)", p)]
        if res and out.startswith(SECRET_OUTPUT):
            return "secret içeriği okuma"
        return None
    dry = _flag_value(args, "--dry-run")
    if verb in K8S_VERBS or (verb in K8S_TWO and len(pos) > 1 and pos[1] in K8S_TWO[verb]):
        if dry == "client" and verb not in {"exec", "cp", "port-forward", "debug", "attach", "proxy"}:
            return None
        return "kubectl/oc ile canlı kaynak değişikliği veya tünel/exec"
    return None


def r_helm(args, env):
    if _is_help(args) or _has(args, "--dry-run"):
        return None
    pos = _positionals(args, HELM_VALUE_FLAGS)
    if pos and pos[0] in HELM_VERBS:
        return "helm ile canlı değişiklik"
    return None


def r_terraform(args, env):
    if _is_help(args):
        return None
    pos = _positionals(args)
    if pos and pos[0] == "run-all":
        pos = pos[1:]
    if pos and (pos[0] in TF_VERBS or (pos[0] in TF_TWO and len(pos) > 1 and pos[1] in TF_TWO[pos[0]])):
        return "terraform/tofu ile altyapı değişikliği"
    return None


def r_compose(args, env, remote=False):
    if _is_help(args):
        return None
    pos = _positionals(args, COMPOSE_VALUE_FLAGS)
    if pos and pos[0] in COMPOSE_VERBS:
        remote = remote or "DOCKER_HOST" in env or "DOCKER_CONTEXT" in env
        if not remote and os.environ.get("KG_GUARD_LOCAL_COMPOSE") == "allow":
            return None
        return "docker compose ile servis değişikliği"
    return None


def r_docker(args, env):
    if _is_help(args):
        return None
    remote = _has(args, "-H", "--host", "--context", "-c")
    pos = _positionals(args, DOCKER_VALUE_FLAGS)
    if not pos:
        return None
    if pos[0] == "compose":
        idx = args.index("compose")
        return r_compose(args[idx + 1:], env, remote)
    if pos[0] in DOCKER_VERBS or (pos[0] in DOCKER_TWO and len(pos) > 1 and pos[1] in DOCKER_TWO[pos[0]]):
        return "docker ile kalıcı/paylaşılan kaynak değişikliği"
    if pos[0] in {"buildx", "build"} and _has(args, "--push"):
        return "docker ile imaj gönderme"
    return None


def r_dotnet(args, env, is_ef=False):
    if _is_help(args):
        return None
    pos = _positionals(args)
    if not is_ef:
        if pos[:1] != ["ef"]:
            return None
        pos = pos[1:]
    if pos[:1] == ["database"] and len(pos) > 1 and pos[1] in {"update", "drop"}:
        return "veritabanına migration uygulama/silme"
    return None


def r_aws(args, env):
    if _is_help(args):
        return None
    pos = _positionals(args, AWS_VALUE_FLAGS, CLOUD_BOOL_FLAGS)
    if len(pos) < 2 or pos[0] in {"help", "configure", "sso", "sts"}:
        if pos[:2] == ["sts", "get-session-token"]:
            return "bulut CLI ile kimlik bilgisi/secret okuma"
        return None
    op = pos[1]
    if op in AWS_SECRET_OPS or (op.startswith("get-parameter") and _has(args, "--with-decryption")):
        return "bulut CLI ile kimlik bilgisi/secret okuma"
    if pos[0] == "s3" and op == "cp" and not pos[-1].startswith("s3://"):
        return None  # indirme
    if op.startswith(AWS_READ_PREFIX):
        return None
    return "bulut CLI ile kaynak oluşturma/değiştirme/silme"


def r_cloud(args, env):
    if _is_help(args):
        return None
    pos = _positionals(args, (), CLOUD_BOOL_FLAGS)
    if "keyvault" in pos and "secret" in pos and any(p in {"show", "download", "backup"} for p in pos):
        return "bulut CLI ile kimlik bilgisi/secret okuma"
    for p in pos[1:] if pos[:1] == ["run"] else pos:  # `gcloud run ...` grubunda `run` fiil değildir
        head = p.split("-", 1)[0]
        if p in CLOUD_SECRET:
            return "bulut CLI ile kimlik bilgisi/secret okuma veya kimlik bağlamı değişikliği"
        if p in CLOUD_MUTATE or (head in CLOUD_MUTATE and "-" in p):
            return "bulut CLI ile kaynak oluşturma/değiştirme/silme"
        if p in CLOUD_READ or (head in CLOUD_READ and "-" in p):
            return None
    return None


def r_git(args, env):
    pos = _positionals(args, {"-C", "-c", "--git-dir", "--work-tree"})
    if not pos:
        return None
    if pos[0] == "push" and (_has(args, "--force", "-f", "--mirror") or any(p.startswith("+") for p in pos[1:])):
        return "git force-push (uzak geçmişi ezer)"
    if pos[0] == "reset" and _has(args, "--hard"):
        return "git reset --hard (commit'lenmemiş değişiklikleri siler)"
    if pos[0] == "add":
        for p in pos[1:]:
            base = os.path.basename(p.rstrip("/")).lower()
            if SECRET_FILE.search(base) and not SECRET_FILE_OK.search(base):
                return "secret görünümlü dosyayı stage'leme (" + base + ")"
    if pos[0] == "clean" and any(re.match(r"^-[a-zA-Z]*f", a) for a in args) and not any(re.match(r"^-[a-zA-Z]*n", a) or a == "--dry-run" for a in args):
        return "git clean (izlenmeyen dosyaları siler)"
    return None


def r_secret_tools(name, args):
    if name == "vault" and len(args) > 1 and (args[0] in {"read", "write", "delete"} or args[:2] in (["kv", "get"], ["kv", "put"], ["kv", "delete"])):
        return "vault ile secret okuma/yazma"
    if name == "sops" and _has(args, "-d", "--decrypt", "decrypt", "exec-env", "exec-file"):
        return "sops ile secret çözme"
    return None


def _contains_seq(tokens, seq):
    n = len(seq)
    return any(tuple(tokens[i:i + n]) == seq for i in range(len(tokens) - n + 1))


def check_segment(tokens):
    """Tek bir basit komutun belirteçleri (operatörsüz)."""
    env, i = {}, 0
    while i < len(tokens):
        t = tokens[i]
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", t):
            env[t.split("=", 1)[0]] = 1
            i += 1
            continue
        base = os.path.basename(t).lower()
        if base in PREFIX:
            i += 1
            while i < len(tokens) and tokens[i].startswith("-"):
                i += 2 if tokens[i] in PREFIX_VALUE_FLAGS else 1
            if base == "timeout" and i < len(tokens) and re.match(r"^[0-9.]+[smhd]?$", tokens[i]):
                i += 1
            continue
        break
    if i >= len(tokens):
        return None
    name = os.path.basename(tokens[i]).lower()
    if name.endswith(".exe"):
        name = name[:-4]
    args = tokens[i + 1:]
    off = _disabled()

    if name in SHELLS:
        for j, a in enumerate(args):
            if re.match(r"^-[a-zA-Z]*c$", a) and j + 1 < len(args):
                return check(args[j + 1])
        return None
    if name == "eval":
        return check(" ".join(args))
    if name == "ssh":
        pos = _positionals(args, {"-i", "-p", "-l", "-o", "-F", "-J", "-L", "-R", "-D", "-b", "-c", "-E", "-e", "-m", "-S", "-W", "-w", "-Q", "-B", "-O"})
        return check(" ".join(pos[1:])) if len(pos) > 1 else None
    if name in {"kubectl", "oc"}:
        return r_kubectl(args, env)
    if name == "helm":
        return r_helm(args, env)
    if name in {"terraform", "tofu"}:
        return r_terraform(args, env)
    if name == "docker-compose":
        return r_compose(args, env)
    if name in {"docker", "podman", "nerdctl"}:
        return r_docker(args, env)
    if name == "dotnet":
        return r_dotnet(args, env)
    if name == "dotnet-ef":
        return r_dotnet(args, env, is_ef=True)
    if name == "aws":
        return r_aws(args, env)
    if name in {"gcloud", "az", "doctl", "oci"}:
        return r_cloud(args, env)
    if name in {"vault", "sops"}:
        return r_secret_tools(name, args)
    if name == "git" and "git" not in off:
        return r_git(args, env)
    if "deploytools" not in off:
        if name in DEPLOY_TOOLS and not _is_help(args):
            pos = _positionals(args)
            if name == "terragrunt" and pos[:1] == ["run-all"]:
                pos = pos[1:]
            if pos and pos[0] in DEPLOY_TOOLS[name]:
                return f"{name} ile canlı değişiklik"
        if name == "argocd" and _contains_seq(args, ("app",)) and any(a in {"sync", "rollback", "delete", "set", "patch", "terminate-op"} for a in args):
            return "argocd ile canlı değişiklik"
        if name == "flux" and args[:1] and args[0] in {"reconcile", "suspend", "resume", "delete", "create", "bootstrap"}:
            return "flux ile canlı değişiklik"
        if name == "ansible-playbook" and not _has(args, "--check", "-C", "--syntax-check", "--list-hosts", "--list-tasks", "--help", "-h"):
            return "ansible-playbook ile uzak değişiklik"
    if "migrate" not in off:
        toks = [name] + args
        if name in {"npx", "pnpm", "yarn", "bunx", "poetry", "uv", "pipx", "bundle"}:
            toks = [os.path.basename(a).lower() for a in args if not a.startswith("-") and a not in {"exec", "run", "dlx"}]
        if toks and not _is_help(args):
            for tool, seqs in MIGRATE_RULES:
                if toks[0] == tool and any(_contains_seq(toks[1:], s) for s in seqs):
                    return f"{tool} ile veritabanı şema değişikliği"
            joined = " ".join(toks)
            if re.search(r"(^|\s)(manage\.py|django-admin)\s+(migrate|flush)\b", joined) or \
               re.search(r"^(rails|rake)\s+db:(migrate|rollback|drop|reset|setup|schema:load)", joined) or \
               re.search(r"^knex\s+migrate:(latest|up|down|rollback)", joined) or \
               re.search(r"^(sequelize|sequelize-cli)\s+db:(migrate|drop)", joined) or \
               re.search(r"^typeorm\s+(migration:(run|revert)|schema:(sync|drop))", joined):
                return "ORM aracı ile veritabanı şema değişikliği"
    return None


def check(command):
    if not isinstance(command, str) or not command.strip():
        return None
    text = command.replace("\\\r\n", " ").replace("\\\n", " ").replace("\n", " ; ").replace("`", " ; ")
    text = LONG_TOKEN.sub(r"\1", text)  # shlex tek ve çok uzun belirteçte kareseldir; anlamlı komut sözcüğü bu kadar uzun olmaz
    try:
        lex = shlex.shlex(text, posix=True, punctuation_chars=";|&()")
        lex.whitespace_split = True
        lex.commenters = ""
        tokens = list(lex)
    except ValueError:
        return "ayrıştırılamayan komutta altyapı aracı ve değiştirici fiil" if LEGACY.search(text[:MAX_LEN]) else None
    segment = []
    for t in tokens + [";"]:
        if t and set(t) <= SEPARATORS:
            if segment:
                reason = check_segment(segment)
                if reason:
                    return reason
            segment = []
        else:
            if "$(" in t:  # çift tırnak içindeki komut ikamesi
                reason = check(t.replace("$(", " ; ").replace(")", " ; "))
                if reason:
                    return reason
            segment.append(t)
    return None


def main():
    try:
        data = json.load(sys.stdin)
        if not isinstance(data, dict):
            return
        tool_input = data.get("tool_input")
        command = tool_input.get("command") if isinstance(tool_input, dict) else None
        reason = check(command)
    except Exception:
        return  # fail-open: kanca hatası geliştirme akışını kilitlemez
    if reason:
        who = data.get("agent_type")
        suffix = f" (agent: {who})" if isinstance(who, str) and who else ""
        print(json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": f"kg-devkit: {reason}{suffix}. Bu işlem için açık onay gerekir.",
        }}, ensure_ascii=False))


if __name__ == "__main__":
    main()
