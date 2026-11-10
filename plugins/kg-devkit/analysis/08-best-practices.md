# 08 — Resmi doküman ve en iyi uygulamalarla karşılaştırma

## 1. Kaynaklar ve doğrulama düzeyi

10 Kasım 2026'da okunan resmi sayfalar (`code.claude.com/docs/en/…`): `plugins-reference`, `plugins/loading`, `hooks`,
`sub-agents`, `skills`, `plugin-marketplaces`, `memory`. Yerel CLI: Claude Code **2.1.322** (`claude --version`); CI
2.1.304'e sabit (`.github/workflows/check.yml:31`).

Sayfalar bir alt-agent aracılığıyla alındı. Aşağıda **[D]** = sayfadan birebir alıntıyla doğrulandı,
**[Ö]** = sayfanın model özeti (birebir metin görülmedi; uygulamadan önce sayfada teyit edilmeli),
**[Y]** = yerel CLI çıktısıyla doğrulandı, **[—]** = dokümanda belirtilmemiş.

**İncelenmeyenler:** başka açık kaynak plugin'ler veya "rakip" kit'ler incelenmedi; bu raporda onlarla karşılaştırma
yoktur. Karşılaştırma yalnız resmi dokümanla yapılmıştır.

## 2. Plugin yapısı ve dağıtım

| Konu | Doküman | kg-devkit | Değerlendirme |
| --- | --- | --- | --- |
| Bileşen dizinleri | `skills/`, `commands/`, `agents/`, `hooks/hooks.json`, `.mcp.json`, `settings.json`, `bin/`, `monitors/` … **[D]** | `agents/`, `skills/`, `hooks/` | Uyumlu ✔ |
| Plugin kural (`rules/`) taşıyabilir mi | Bileşen listesinde yok; plugin kökündeki `CLAUDE.md` yüklenmez, "talimatları skill'e koy" **[D]** | Kurallar symlink ile ayrı kurulur | Kit'in tespiti doğru; dokümanın önerdiği yol skill → **I-02** |
| `plugin.json` alanları | `name` zorunlu; `license`, `repository`, `homepage`, `keywords`, `userConfig`, `dependencies` … **[D]** | 4 alan | **M-02** (P3): `license`, `repository`, `keywords` eklenebilir |
| Sürüm çözümleme | Manifest sürümü sabitse kullanıcılar sürüm dizgisi değişene kadar önbellekteki kopyada kalır **[D]** | Her `main` push'unda otomatik artış | Doğru kalıp ✔. Yan etki: birleştirme ile bump commit'i arasındaki kısa pencerede `main` eski sürümü taşır |
| Önbelleğe kopyalama | "Claude Code copies the plugin into cache/… Files outside the plugin directory aren't copied" **[D]** | `plugins/kg-devkit/analysis/` plugin dizininin içinde | **M-01**: bu raporlar plugin'i kuran herkese kopyalanır |
| `${CLAUDE_PLUGIN_ROOT}` | Kanca komutlarında ve skill/agent Markdown'unda yerinde değiştirilir; Bash ortam değişkeni değildir **[D]** | Yalnız `hooks.json`'da | Skill'ler arası atıf ve referans dosyaları için kullanılabilir → S-01 çözümü |
| `${CLAUDE_PLUGIN_DATA}` | Güncellemeler arası kalıcı veri dizini **[D]** | Kullanılmıyor | Kayıt kancası için uygun yer |
| Doğrulama | — | `claude plugin validate` CI'da | ✔ **[Y]**: geçti, tek uyarı ikon |
| Token projeksiyonu | — | Kullanılmıyor | `claude plugin details` **[Y]**; CI'da eşik olarak izlenebilir (P3) |
| Eval | `experimental.evals` manifest anahtarı **[D]**; `claude plugin eval` **[Y]** | Yok | **T-01** |

## 3. Alt-agent'lar

| Konu | Doküman | kg-devkit | Değerlendirme |
| --- | --- | --- | --- |
| Seçim | Görev tanımı + `description`; "use proactively" gibi ifadeler önerilir **[Ö]** | Açıklamalar kapsam ve "not for" içerir; tetik zamanı ve girdi içermez | A-01, A-02 |
| Alt-agent ne görür | Kendi sistem prompt'u + temel ortam bilgisi; ana konuşmayı görmez **[D]**; `CLAUDE.md` hiyerarşisini yükler (Explore/Plan hariç) **[Ö]** | "First read the Project profile …" ×15 | A-05 (ölçülmeli) |
| İç içe başlatma | Alt-agent 3 katmana kadar başlatabilir; engellemek için `Agent`'ı `tools`'a koyma **[Ö]** | Hiçbir `tools` listesinde `Agent` yok + metin kuralı | Yapısal olarak doğru ✔ |
| Plugin agent'larında yok sayılan alanlar | `hooks`, `mcpServers`, `permissionMode`, `initialPrompt` **[D]** | Hiçbiri kullanılmıyor | ✔. Sonuç: agent'a özel kanca yazılamaz; agent bazlı davranış için plugin kancasında `agent_type` kullanılmalı |
| `model` | `sonnet`/`opus`/`haiku`/`inherit`/tam kimlik; atlanırsa oturum modeli sırası **[D]** | 15/15 açıkça belirtilmiş | ✔ (maliyet öngörülebilir) |
| `maxTurns`, `effort` | Destekleniyor **[D]** | Kullanılmıyor | A-08, A-10 |
| `skills` (ön yükleme) | Listelenen skill'in tam içeriği enjekte edilir **[D]**; `disable-model-invocation` skill'ler ön yüklenmez **[Ö]** | Kullanılmıyor | Ortak içerik için aday; ancak her çağrıda tam içerik maliyeti getirir → referans dosyası tercih edildi |
| Listelenen araç yoksa | Hiçbir giriş çözülmezse agent çoğunlukla başlamaz **[D]** | Tarayıcı testçisi yerleşik araçları da listeler | Chrome bağlı değilken başlar ama test yapamaz (A-08) |
| En az yetki | — | Reviewer'lar `Read, Grep, Glob` | Güçlü yan ✔ |

## 4. Skill'ler

| Konu | Doküman | kg-devkit | Değerlendirme |
| --- | --- | --- | --- |
| `disable-model-invocation: true` | Model çağıramaz; açıklama bağlamda tutulmaz; alt-agent'a ön yüklenmez **[Ö]** | 6/6 | Yetkili skill'ler için doğru; `verify-change` için gereksiz kısıt (S-02). `plugin details` çıktısı açıklamaları "always-on" sayıyor **[Y]** → D-03 |
| Açıklama bütçesi | `description`+`when_to_use` listede 1.536 karakterde kesilir; toplam bütçe bağlam penceresinin %1'i **[Ö]** | En uzun 249 karakter | ✔ |
| Boyut | SKILL.md < 500 satır; ayrıntıyı destek dosyalarına taşı **[Ö]** | 24-54 satır; destek dosyası yok | ✔; aşırı bölme gereksiz |
| `context: fork` + `agent` | Skill içeriği fork'lanan agent'ın prompt'u olur; konuşma geçmişini görmez; varsayılan arka plan, `background: false` bekler **[Ö]** | `browser-test` | H-04: arka plan + `ask` etkileşimi belirsiz |
| `paths` (skill) | Frontmatter alanı olarak listelenir **[Ö]** | Kullanılmıyor | I-02 için aday; canlıda doğrula (E-4) |
| `disallowed-tools` (skill) | Listelenir **[Ö]** | Kullanılmıyor | S-04 |
| Dinamik bağlam (`` !`cmd` ``) | Skill gövdesinde komut çıktısı yerine konur **[D]** | Kullanılmıyor | `verify-change`/`release` 1. adımındaki `git status`/`git diff --stat` için kullanılabilir (bir araç turu kazandırır). Yan etki: komut skill yüklenirken çalışır; Codex çıktısında karşılığı yok → `build-codex.py` uyarlaması gerekir. **Önerilmez** (kazanç küçük, parite maliyeti var) |
| `commands/` | Skill'lerle birleşti; eski dosyalar çalışır **[D]** | `commands/` yok | ✔ |
| Ad alanı | `/plugin-adı:skill-adı` **[D]** | README:38 aynı | ✔ |

## 5. Kancalar

| Konu | Doküman | kg-devkit | Değerlendirme |
| --- | --- | --- | --- |
| `PreToolUse` karar biçimi | `hookSpecificOutput.permissionDecision`: `allow/deny/ask/defer`; üst düzey `decision` kullanımdan kalkmış **[D]** | `ask` + gerekçe | Güncel biçim ✔ |
| Çıkış kodları | 0 = başarı; 2 = blokla; diğer = bloklamayan hata **[D]** | Normalde 0; istisnada 1 | Fail-open davranışı tutarlı; H-05 gürültü |
| Zaman aşımı | Komut kancaları için varsayılan 600 sn; `timeout` saniye **[D]** | Belirtilmemiş | H-05 |
| Girdi alanları | `tool_name`, `tool_input`, `permission_mode`, `cwd`, alt-agent içinde `agent_id`/`agent_type` **[D]** | Yalnız `tool_input.command` | `agent_type` onay mesajına eklenebilir (A-04) |
| Alt-agent'larda | Ayar ve plugin kancaları alt-agent içinde de çalışır **[D]** | Belgelenmiş (`agent-requirements.md:64`) | ✔ |
| `ask` ve izin modları | Varsayılan ve auto modda sorar **[D]**; `bypassPermissions`/`dontAsk` için **[—]** | — | H-04 |
| `allow` ile etkileşim | Kanca ne dönerse dönsün deny/ask kuralları ayrıca değerlendirilir **[D]** | — | Kullanıcının `Bash(kubectl *)` izin kuralı varken kancanın `ask`'i sorar (öncelik `deny > defer > ask > allow`) |
| `if` alanı | İzin kuralı sözdizimiyle süzme (`"Bash(git *)"`) **[D]** | Kullanılmıyor | Değerlendirildi, önerilmedi ([04](04-hooks-analysis.md) §2) |
| `onFailure: "block"` | Komut kancası hata/timeout'ta bloklasın (v2.1.295+) **[D]** | Kullanılmıyor | Fail-closed seçeneği. Kişisel kit için **önerilmez** (Python'suz makinede tüm Bash'i kilitler); kurumsal kullanımda değerlendirilebilir |
| Windows | Git Bash yoksa PowerShell; `python3` konusunda **[—]** | `python3` | H-06 |
| `SubagentStart/Stop` | Var; `SubagentStop` çıkış 2 ile durmayı engeller, `SubagentStart` bağlam ekleyebilir **[Ö]** | Kullanılmıyor | Kayıt (A-06). `SubagentStop` ile "`VERDICT:` satırı yoksa durma" zorlaması mümkün görünüyor; alan adları doğrulanmadan önerilmez (I-03) |
| `async` | Komut kancası alanı **[D]** | — | Kayıt kancası için uygun |

## 6. Bellek ve kurallar

| Konu | Doküman | kg-devkit |
| --- | --- | --- |
| `AGENTS.md` | v2.1.277'den beri doğal okunur; varsayılan olarak yalnız `CLAUDE.md`/`CLAUDE.local.md` yokken. Önerilen: `CLAUDE.md` içinde `@AGENTS.md` **[D]** | Profil "`AGENTS.md` (veya `CLAUDE.md`)" içinde aranır ✔. Her ikisi de varsa ve profil `AGENTS.md`'deyse ana oturum onu görmeyebilir; şablona tek satır not eklenmeli (**D-04**, P3) |
| `~/.claude/rules/*.md` + `paths:` | Kullanıcı düzeyinde desteklenir; desenler oturumun çalışma dizinine göre **[D]** | `install-claude-rules.sh` bunu kullanır ✔ |

## 7. Doğrudan uygulanabilir çıkarımlar

1. Çağıranın gördüğü tek metin `description`'dır → tetik ve girdi oraya (A-01, A-02).
2. Plugin talimat taşıyacaksa skill ile taşır → kurallar için yol-kapsamlı skill denemesi (I-02).
3. Skill'ler arası atıf `${CLAUDE_PLUGIN_ROOT}` yolu ile yapılır (S-01).
4. Plugin agent'ına özel kanca yoktur → agent bazlı davranış plugin kancasında `agent_type` ile (A-04, A-06).
5. `timeout` her komut kancasında açıkça verilir (H-05).
6. Eval ve token projeksiyonu CLI'da hazır → CI'a eklenir (T-01).

## 8. Dokümanla çelişen veya güncelliğini yitirmiş kit ifadeleri

| Yer | İfade | Durum |
| --- | --- | --- |
| `SECURITY.md:12-13` | Kanca "`kubectl`/`helm`/`terraform` komutlarını onaya düşürür" | Eksik: docker, EF, bulut CLI'ları da kapsanıyor (D-01) |
| `live-check/SKILL.md:20-21` | "the plugin's guard hook inspects the literal command text" | Doğru ama satır devamı ve bayrak-önce biçimlerde eşleşmediği belirtilmiyor (H-01) |
| `docs/agent-requirements.md:5` | "Profil yoksa tüm agent'lar … çıkarım yapar" | `devops-operator` ve tarayıcı testçisi durup sorar; tablo satırları doğru, giriş cümlesi genelleme (P3) |
| README:38 | "Aynı adlı proje agent'ı/skill'i plugin'i ezer" | Plugin bileşenleri ad alanlıdır (`kg-devkit:<ad>`); "ezme" davranışı bu analizde doğrulanmadı |
