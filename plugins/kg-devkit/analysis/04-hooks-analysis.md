# 04 — Hook analizi

Kapsam: plugin'in tek kancası. Bu rapordaki "ölçüm" ifadeleri bu analiz sırasında çalıştırılan komutların çıktısıdır;
kanca gerçek bir Claude Code oturumunda tetiklenerek **gözlemlenmedi** (karar fonksiyonu ve betik doğrudan çağrıldı).

## 1. Envanter

| Alan | Değer |
| --- | --- |
| Hook | `guard-infra` — [hooks/guard-infra.py](../hooks/guard-infra.py), kayıt [hooks/hooks.json](../hooks/hooks.json) |
| Event | `PreToolUse` |
| Matcher | `Bash` (tam ad eşleşmesi; her Bash çağrısında süreç başlatılır) |
| İşlem | Komut metnini 8 regex ile tarar; eşleşirse `permissionDecision: "ask"` + gerekçe döndürür; aksi halde çıktısız çıkar |
| Girdi | stdin JSON; yalnız `tool_input.command` okunur (satır 42). `agent_type`, `permission_mode`, `cwd` kullanılmaz |
| Çıktı | stdout JSON `hookSpecificOutput{hookEventName, permissionDecision, permissionDecisionReason}`; çıkış kodu 0 |
| Timeout | Belirtilmemiş → dokümana göre komut kancalarında varsayılan **600 sn** |
| Hata yönetimi | Bozuk JSON → sessiz çıkış (satır 38-41). JSON geçerli ama nesne değilse → **yakalanmamış istisna, çıkış 1** (H-05). Dokümana göre 0/2 dışı çıkış bloklamaz → fiilen fail-open |
| Risk | Güvenlik: kaçırılan biçimler (H-01, H-02). Performans: süreç başına ~23-27 ms; patolojik girdide saniyeler (H-05). Platform: `python3` yoksa etkisiz (H-06) |

Plugin dışı: `.claude/hooks/kit-review-gate.py` (`Stop`, yalnız bu repo) kapsam dışıdır; tek ilgili not
[M-01](10-improvement-roadmap.md)'dedir.

## 2. Davranış

### H-01 (P0, koşullu) — Yaygın komut biçimleri kancayı atlıyor
Regex'ler fiilin araç adından hemen sonra geldiğini (helm, terraform, docker) veya aynı satırda olduğunu (kubectl,
bulut CLI: `[^|;&\n]*?`) varsayar ([guard-infra.py:19-26](../hooks/guard-infra.py)). Ölçüm
([test_guard_probe.py](proposals/tests/test_guard_probe.py), grup H-01: 25 senaryodan 3'ü onaya düştü):

| Komut | Mevcut karar | Neden |
| --- | --- | --- |
| `kubectl --context prod \`⏎`  -n app delete pod a` | geçer | `\n` karakter sınıfının dışında |
| `helm -n prod uninstall app`, `helm --namespace prod upgrade …` | geçer | fiil `helm`'den hemen sonra değil |
| `terraform -chdir=infra apply` / `destroy` | geçer | aynı |
| `docker --context prod compose up -d`, `docker -H ssh://prod rm x` | geçer | aynı |
| `docker container stop x`, `docker image push a` | geçer | alt komut biçimi listede yok |
| `dotnet-ef database update` | geçer | yalnız `dotnet ef` |
| `kubectl debug`, `attach`, `autoscale`, `certificate approve` | geçer | fiil listesinde yok |

Bu özellikle önemlidir çünkü kit'in kendi talimatları bağlam ve namespace'in **her çağrıda açıkça** yazılmasını ister
(`live-check:19-20`, `devops-engineer:22-23`, `kg-ops-safety:19`); uzun komutlar satır devamıyla yazılmaya yatkındır.
*Koşul:* varsayılan izin modunda izin listesinde olmayan Bash komutları zaten sorulur; kanca asıl olarak kullanıcı
`Bash(kubectl *)` gibi izin kuralları eklediğinde veya daha serbest bir modda çalıştığında tek deterministik engeldir.

### H-02 (P1) — Secret okuma ve bulut fiilleri eksik
Grup H-02: 27 senaryodan 0'ı onaya düştü.
- `kubectl get -o yaml secret db` (bayrak kaynaktan önce), `-o custom-columns=…`, `-o template` → geçer (satır 20 sıra ve
  biçim varsayar).
- `aws secretsmanager get-secret-value`, `aws ssm get-parameter --with-decryption`,
  `gcloud secrets versions access`, `az keyvault secret show`, `vault kv get`, `sops -d` → geçer. Betiğin kendi
  belge dizgisi "secret okuyan altyapı komutları" der (satır 2).
- `CLOUD_VERBS` (satır 17) `stop`, `start`, `deallocate`, `deploy`, `patch`, `sync`, `invoke`, `upload`, `change-*`,
  `add-*` içermez: `aws ec2 stop-instances`, `gcloud app deploy`, `az vm deallocate`, `aws s3 sync … --delete`,
  `aws route53 change-resource-record-sets` → geçer.

### H-03 (P1) — Yanlış pozitifler onay yorgunluğu üretir
Grup H-03: onaya düşmemesi gereken 36 senaryodan 24'ü düştü.
- Tırnak içindeki metin komut sayılır: `grep -r 'kubectl apply' docs/`, `git commit -m 'docs: kubectl apply steps'`,
  `echo '…kubectl delete…'`.
- Bayrak değerleri fiil sanılır: `kubectl get pods -n prod -l run=api`, `kubectl get deploy -o yaml > apply.yaml`,
  `aws cloudformation describe-stacks --stack-name update-x`, `az resource list --tag update=yes`.
- `gcloud run services describe svc`: `run` fiil listesinde olduğu için Cloud Run'ın **her** salt-okuma komutu sorulur;
  bu, `live-check`'in "read-only inspection is free" ilkesiyle çelişir.
- `--help`, `--dry-run=client`, `helm upgrade --dry-run`, `kubectl auth can-i delete …` sorulur.
- Yerel geliştirme: `docker compose up/down/exec/run`, `docker stop/rm` hedef ayrımı olmadan her zaman sorulur.

Sık ve anlamsız onaylar kullanıcıyı "evet"e alıştırır; gerçek riskli komutun onayı da aynı refleksle geçer.

### H-04 (P1, doğrulanamadı) — `ask` kararının etkileşimsiz bağlamlardaki davranışı
Doküman `ask`'in varsayılan ve auto modda kullanıcıya sorduğunu söyler; `bypassPermissions`, `dontAsk` ve arka planda
çalışan alt-agent için davranış **belirtilmemiştir**. `browser-test` skill'i `context: fork` kullanır
([browser-test/SKILL.md:7-8](../skills/browser-test/SKILL.md)); doküman özetine göre fork'lar varsayılan olarak arka
planda çalışır. Agent'ın "servisleri başlat" adımı (`frontend-browser-tester.md:35`) tipik olarak `docker compose up`
olur ve satır 23 kuralına takılır. Onay istemi arka planda gösterilemiyorsa test başlamadan durur.
**Yapılacak:** canlı deney ([11](11-test-strategy.md) HT-9/HT-10). Sonuca göre: `browser-test`'e `background: false`
eklenir **veya** yerel compose için `KG_GUARD_LOCAL_COMPOSE=allow` belgelenir.

### H-07 (P2) — "Projeden bağımsız" iddiası ile kural kapsamı uyumsuz
Migration uygulama yalnız EF Core için tanınır (satır 25). Prisma, Alembic, Django, Rails, Flyway, Knex; ayrıca
`helmfile`, `pulumi`, `terragrunt`, `argocd`, `flux`, `ansible-playbook` hiç kapsanmaz (grup H-07: 0/12).
`docs/inventory.md:3` kit'in .NET kökenini açıklar; README ise "project-agnostic" der.

### Diğer davranış soruları
| Soru | Cevap |
| --- | --- |
| Doğru olayda mı? | Evet; `PreToolUse` + `ask` bu amaç için dokümandaki doğru kalıp. Üst düzey `decision` yerine `hookSpecificOutput` kullanılıyor ✔ |
| Gereğinden sık mı tetikleniyor? | Her Bash çağrısında bir Python süreci (ölçüm: medyan 22,9 ms, p95 32,0 ms; 40 çalıştırma, Python 3.13, Linux). Etkisi ihmal edilebilir. Dokümandaki `if` alanı (`"Bash(kubectl *)"`) süreci azaltabilirdi ama tek desen aldığı ve sarmalayıcıları (`sudo`, `bash -c`) kaçıracağı için **önerilmez** |
| Aynı işi yapan başka hook? | Yok |
| Alt-agent'larda çalışıyor mu? | Dokümana göre plugin kancaları alt-agent araç çağrılarında da çalışır ✔ (canlıda gözlemlenmedi) |
| Kritik akışı engelliyor mu? | Bloklamaz; yalnız sorar. H-04'teki olası istisna dışında yok |

## 3. Güvenlik

| Konu | Değerlendirme |
| --- | --- |
| Komut enjeksiyonu | Yok: betik komut metnini yalnız regex'e verir; kabuk, `eval`, alt süreç çalıştırmaz. `hooks.json` komutunda yol tırnaklı (`"${CLAUDE_PLUGIN_ROOT}/…"`) ✔ |
| Hassas veri loglama | Yok: stdout'a yalnız sabit gerekçe yazılır; komut metni geri yazılmaz ✔. İstisna durumunda traceback stderr'e gider; komut içeriği içermez |
| Ortam değişkenleri | Hiçbiri okunmaz ✔ |
| Dosya/sistem yetkisi | Yalnız stdin okur; dosya yazmaz ✔. Betik ana modül olarak çalıştığı için `__pycache__` üretmez (çalıştırma sonrası `git status` temiz); test betiği ayrıca `dont_write_bytecode` ayarlar ✔ |
| Onay yönetimi | `ask` kullanıcıya gerekçe gösterir ✔. Hangi agent'ın çalıştırdığı gösterilmez (A-04); prototip `agent_type` ekler |
| Güven sınırı | SECURITY.md:12-13 kancayı "ikinci kilit, güvenlik sınırı değil" olarak doğru konumlar; ancak kapsamı `kubectl/helm/terraform` diye yazar, README:52-54 ise docker ve bulut CLI'larını da sayar (**D-01**, P3) |
| Bilinçli kör noktalar | Takma ad (`k delete`), değişken (`$KUBECTL`), betik/Makefile (`./deploy.sh`, `make deploy`), `psql`, `scp/rsync`, MCP araçları. Belgelenmiş (satır 8-9) ✔; `release deploy` profilin deploy komutunu (çoğunlukla sarmalayıcı) çalıştırdığı için kanca o yolu **hiç görmez** |

### I-04 (P2) — Kullanıcının çalışmasını silebilen git komutları yalnız metinle korunuyor
`git reset --hard`, `git clean -fdx`, `git push --force` için hiçbir deterministik engel yok; koruma skill ve agent
metinlerindeki "no force-push", "never claim or delete the user's changes" cümlelerinden ibaret. Aynı kancaya küçük bir
kural grubu eklemek yeni bileşen gerektirmez (prototipte `R-git`, `KG_GUARD_DISABLE=git` ile kapatılabilir).

## 4. Dayanıklılık

### H-05 (P2) — Girdi doğrulama, zaman aşımı ve regex karmaşıklığı
| Senaryo | Ölçülen sonuç |
| --- | --- |
| `not json`, boş stdin | çıkış 0, çıktı yok ✔ |
| `[1,2]` | `AttributeError` traceback, **çıkış 1** (satır 42) |
| `{"tool_input":"…"}` | `AttributeError`, çıkış 1 |
| `{"tool_input":{"command":["kubectl","delete"]}}` | `TypeError`, çıkış 1 (satır 32) |
| `"kubectl x "` × 4.000 (40 KB, ayırıcısız) | **2.992 ms** |
| `"kubectl x "` × 10.000 (100 KB) | **20.842 ms** |
| 300 satırlık heredoc (her satırda `kubectl`) | 1,1 ms (yeni satır taramayı böler) |

Karesel büyüme, satır 19 ve 26'daki `\b(araç)\b[^|;&\n]*?\s(fiil)` kalıbının her araç adı için satır sonuna kadar
taramasından gelir. Gerçekçi komutlarda görülmesi olası değildir (tek satırda binlerce araç adı gerekir), ancak
`timeout` alanı olmadığı için üst sınır 600 sn'dir. Çıkış 1 dokümana göre bloklamaz; yani davranış fail-open kalır,
yalnız hata gürültüsü üretir.
**Çözüm:** `hooks.json`'a `"timeout": 5`; betikte `isinstance` kontrolleri; doğrusal zamanlı ayrıştırıcı
(prototip: 1 MB girdide 417 ms).

### H-06 (P2) — `python3` bağımlılığı ve sessiz devre dışı kalma
`hooks.json:9` `python3` çağırır. Windows'ta yorumlayıcı çoğunlukla `python` adıyla bulunur; doküman komut kancalarının
Windows'ta Git Bash yoksa PowerShell ile çalıştığını söyler ve `python3`/`python` konusunda yönlendirme vermez.
Yorumlayıcı yoksa kanca hata koduyla döner ve işlem devam eder: koruma **kullanıcıya haber verilmeden** yoktur.
README bunu belgeler (satır 5, 55) fakat çalışma anında bir işaret yoktur.
**Çözüm:** `python3 … || python …` yedeği ([hooks.proposed.json](proposals/hooks/hooks.proposed.json)); Windows'ta
sınanmadı. İsteğe bağlı: `SessionStart` kancasıyla "guard etkin değil" tek satır uyarı (P3; yalnız yorumlayıcı
bulunamazsa çıktı üretir).

| Diğer dayanıklılık soruları | Cevap |
| --- | --- |
| Idempotent mi? | Evet; durumsuz, aynı girdi aynı çıktı ✔ |
| İptal/timeout | Betikte yok; H-05 ile ele alınır |
| Çıkış kodu kullanımı | Karar JSON + çıkış 0 ile verilir ✔ (çıkış 2 kullanılmaz; "ask" için doğru) |
| macOS/Linux | Yalnız stdlib; fark beklenmez (macOS'ta çalıştırılmadı) |
| Windows | H-06; sınanmadı |
| Codex | Kanca yok; `rollback:45-46` bunu açıkça yazar ✔ |

## 5. Önerilen yeniden yazım (özet)

[proposals/hooks/guard_infra_v2.py](proposals/hooks/guard_infra_v2.py): `shlex` ile belirteçleme, satır devamı
birleştirme, fiilden önceki bayrakları atlama, `bash -c`/`ssh`/`sudo`/`xargs`/`$(…)` içine girme, `--help` ve
`--dry-run=client` muafiyeti, bulut CLI'larında yalnız konumsal argümanlarda fiil arama, secret okuma, yığından bağımsız
migration ve dağıtım araçları, git kural grubu, savunmacı girdi doğrulama, ayrıştırma hatasında regex yedeği
(belirsiz durumda **sor**).

Karşılaştırma (aynı betik, `python3 …/test_guard_probe.py`):

| Senaryo grubu | Örnek | Mevcut doğru | Prototip doğru |
| --- | ---: | ---: | ---: |
| Resmi liste (`scripts/test_guard_infra.py`) | 106 | 106 | 106 |
| H-01 biçim kaçakları | 25 | 3 | 25 |
| H-02 secret / bulut fiilleri | 27 | 0 | 27 |
| H-07 migration / dağıtım araçları | 12 | 0 | 12 |
| R-git | 7 | 4 | 7 |
| H-03 yanlış pozitifler | 36 | 12 | 36 |
| Bilinçli olarak sorulmaya devam edenler | 8 | 7 | 8 |
| Süreç başlatma (medyan / p95) | — | 22,9 / 32,0 ms | 26,9 / 37,4 ms |

Sınırlar: senaryoları bu analiz yazdı (bağımsız değil); prototip gerçek oturumda kanca olarak çalıştırılmadı; bulut CLI
fiil kümeleri sezgiseldir ve bilinmeyen fiili geçirir (`aws` hariç: orada bilinmeyen işlem sorulur). Takma ad, değişken,
betik ve MCP kör noktaları aynen kalır. Kural sayısı arttığı için bakım yükü de artar; her yeni kural test listesine
örnek eklemeyi gerektirir (mevcut `kit-doc-sync` kontrolü bunu zaten ister).

## 6. Kancanın çalıştığını kanıtlayacak testler
Senaryo listesi [11-test-strategy.md](11-test-strategy.md) §2'dedir (HT-1 … HT-12).
