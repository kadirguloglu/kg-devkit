# Agent gereksinimleri

Her agent'ın çalışmak için neye ihtiyaç duyduğunun tek yerde özeti. Alan adları
[project-profile-template.md](project-profile-template.md) içindeki `## Project profile` alanlarıdır.
Profil yoksa tüm agent'lar `package.json`/README/koddan çıkarım yapar ve raporda söyler; aşağıdaki "profil yoksa"
sütunu bunun dışındaki davranışı verir.

## Özet tablo

| Agent | Tür / araçlar | Profil alanları | Projede olması gereken | Profil yoksa / uygulanamazsa |
| --- | --- | --- | --- | --- |
| `backend-developer` | yazar (`Edit, Write, Bash`) | Layers/dirs, Commands, Rule docs, Conventions, Persistence (ORM + migration artefaktları), Hard limits | backend dizini, build/test komutu | koddan çıkarım, raporda belirtir |
| `backend-test-developer` | yazar | Layers/dirs (test dizini), Rule docs (tests), Commands (focused/full test), Hard limits | test projeleri, fixture'lar | test projelerinden çıkarım |
| `database-reviewer` (model: opus) | salt-okuma (`Read, Grep, Glob`) | Persistence (ORM, migration artefaktları), Conventions (isolation, soft delete, para/tarih, başarısız yazma temizliği), Rule docs | ORM/migration dizini; ana oturum diff ve komut kanıtı verir | stack'i koddan çıkarır, doğrulayamadığını yazar |
| `tenant-security-reviewer` (model: opus) | salt-okuma | Security review (tenancy/yetki modeli + güvenlik kural belgesi), Conventions (kimlik yeniden kullanımı, sunucu-otoriter hesaplamalar), Persistence (filtre bypass API'leri), teknik doküman bölümleri (güvenlik, depolama, arka plan işleri) | tenancy/yetki modeli (yoksa düz yetki + sahiplik incelenir) | modeli koddan çıkarır, varsayımları yazar |
| `api-contract-reviewer` (model: opus) | salt-okuma | API contract (şema, tip üretimi, versiyonlama), Layers/dirs, Conventions (hata/Result) | ana oturum diff ve varsa üretilmiş şema/komut kanıtı verir | sözleşme yüzeyini controller/DTO/frontend API katmanından çıkarır |
| `dependency-supply-chain-reviewer` (model: opus) | salt-okuma | Dependencies (lisanslar, tarama komutu, sabitleme politikası), Hard limits | manifest/lockfile; ana oturum varsa audit çıktısını verir | manifest ve workflow dosyalarını kendisi bulur, doğrulayamadığını yazar |
| `performance-reviewer` | salt-okuma | Performance (bütçe, sıcak yollar, hacim), Layers/dirs, Commands | ana oturum diff ve varsa ölçüm verir | bütçe/hacim varsayar ve söyler; ölçümsüz bulguyu "needs measurement" işaretler |
| `observability-reviewer` | salt-okuma | Observability (log/metrik/trace kuralları, hassas veri, sağlık), Conventions (hata), Rule docs | ana oturum diff verir | log/metrik yığınını koddan çıkarır, doğrulayamadığını yazar |
| `scope-advisor` | salt-okuma | Scope mechanisms, Report language | **çok kiracılı/çok müşterili ürün** | kiracı yoksa `NOT-APPLICABLE` döner ve durur |
| `engineering-software-architect` | salt-okuma | Layers/dirs, Conventions, Scope mechanisms, Rule docs, Finish gate | ana oturum soru ve kodu/diff'i verir | mimariyi koddan çıkarır |
| `frontend-developer` | yazar | Layers/dirs, Commands (lint/typecheck/build/test), Rule docs, Hard limits | frontend dizini | `package.json`'dan çıkarım |
| `frontend-test-developer` | yazar | Commands (focused/full test), Rule docs (tests), Hard limits | frontend test konumu | `package.json` ve mevcut testlerden çıkarım |
| `frontend-browser-tester` | tester (kod yazmaz; Chrome araçları) | Layers/dirs (frontend src), Commands (start/status), Dev app (url + test login), Router/navigation files, Hard limits | **Claude in Chrome eklentisi**, çalışan dev uygulaması | dev URL veya test login bulunamazsa durur, kullanıcıya sorar |
| `devops-engineer` | yazar (`Bash` dahil) | Production (sahip olunan yollar, hedef ortam, deploy/status komutu, topoloji, registry, runbook), Report language, Hard limits | deploy/manifest/CI dosyaları | Production girdisi yoksa yalnız statik dosyaya bakar, canlı komuttan önce hedefi sorar |
| `devops-operator` (model: opus) | yazar, yüksek etkili | Production (hedef, secret konumları, registry, topoloji, runbook), Hard limits | kullanıcının **o işlem için açık onayı** (ana oturum iletir) | Production girdisi yoksa durur ve sorar |

## Skill'ler

Hepsi `disable-model-invocation: true`: yalnız kullanıcı açıkça çağırınca çalışır. `Project profile` ve `AGENTS.md`/`CLAUDE.md` kısıtları geçerlidir.

| Skill | Yetki / onay | Profil alanları | Profil yoksa / uygulanamazsa |
| --- | --- | --- | --- |
| `release` | çağrı commit+push yetkisi verir; canlı deploy yalnız `deploy` argümanıyla | Release, Commands, Finish gate, `AGENTS.md`/`CLAUDE.md` sınırları (alan adı anılmaz), Production (yalnız `deploy` ile: deploy/durum komutu, sağlık URL'leri) | Release girdisi yoksa kullanıcıya sorar |
| `rollback` | canlı geri alma için ayrıca açık onay ister | Production (context, namespace, iş yükü, registry, sağlık URL'leri, güncelleme stratejisi, rollback/deploy komutu; bulut CLI kimlik komutu `live-check` adımları üzerinden), Persistence (migrations dizini; skill bunu Production içinde sayar, şablonda Persistence altındadır) | Production girdisi yoksa durur |
| `live-check` | salt-okuma | Production (context, namespace, durum komutu, bulut CLI kimlik komutu, iş yükü adları, sağlık URL'leri ve beklenen kodlar, runbook) | Production girdisi yoksa durur ve sorar |
| `add-migration` | commit/push/deploy/veritabanı yetkisi vermez | Persistence, Conventions, Finish gate, Report language | ORM araçlarını repoda bulur, komutu çalıştırmadan önce kullanıcıya onaylatır |
| `verify-change` | commit/push/deploy yetkisi vermez | Commands, Rule docs, Finish gate, Report language | skill'de ayrı ifade yok; profil kısıtları geçerli, genel kural: koddan çıkarım ve raporda belirtme |
| `browser-test` | commit/push/deploy yetkisi vermez; `frontend-browser-tester` agent'ında çalışır | `frontend-browser-tester` satırındaki alanlar | agent'ın davranışı geçerli |

## Ortak kurallar (tüm agent'lar)

- **Loglama:** ilk çıktı satırı `<agent> çalışmaya başladım.`, son rapor satırı `<agent> çalışmam tamamlandı.`
  (görev başarısız/engelli olsa da; profil Türkçe dışında bir rapor dili belirtiyorsa aynı iki satır o dilde yazılır). Dil tercihi değiştirilecekse tüm agent dosyalarında değiştirilir.
- **Tam okuma (zorunlu):** her agent, bulgu/hüküm/düzenleme öncesi baktığı veya değiştireceği her dosyanın tüm satırlarını okur (bir okuma dosyayı kısmen döndürürse offset ile son satıra kadar devam edilir; arama, diff istatistiği, alıntı ve özet yalnız dosyayı bulmak içindir, okuma sayılmaz). Dosyayı tam okuyamazsa o dosya hakkında hüküm vermez, düzenlemez; neyin engellediğini yazıp "doğrulanmadı" der (reviewer ve denetleyici agent'lar `VERDICT: UNCLEAR`; diğerleri düzenlemez, o dosya hakkında iddiada bulunmaz). Kural, dosya okumayı yasaklayan kuralları (ör. secret değerleri) aşmaz: o dosya değerlendirilmez, içeriği çıktıya yazılmaz. Aynı paragraf tüm agent dosyalarında (kit bakım agent'ları dahil) Logging satırından hemen sonra yer alır.
- **Profil önce:** `AGENTS.md` (veya `CLAUDE.md`) içindeki `## Project profile` bölümü okunur.
- **Rapor dili:** profildeki `Report language`; yoksa kullanıcının isteği.
- **Agent çağırmama:** agent'lar başka agent başlatmaz (reviewer ve scope-advisor kullanıcıya soramaz; soruyu ana oturum sorar).
- **Reviewer çıktısı:** `database-reviewer`, `tenant-security-reviewer`, `api-contract-reviewer`, `dependency-supply-chain-reviewer`, `performance-reviewer` ve `observability-reviewer` raporu `VERDICT: PASS / FAIL / UNCLEAR` ile bitirir; profil farklı bir geçme ifadesi adlandırıyorsa onu da yazar.
- **Commit/push:** yazan agent'lar commit veya push yapmaz (koşulsuz). Profildeki `Hard limits` (yasak komutlar, branch politikası) bu kuralların üstüne ek kısıt koyar; hiçbir kuralı gevşetmez. Yazan agent'ların hepsi (developer, test developer, devops, operator, browser tester) bunu okur.

## Varsayımlar ve ortama bağlılık

| Konu | Hangi agent | Ne varsayıyor | Uymuyorsa |
| --- | --- | --- | --- |
| Çok kiracılılık | `scope-advisor`, `tenant-security-reviewer` | ürünün birden fazla müşteri/tenant'ı var | `scope-advisor` `NOT-APPLICABLE` döner; `tenant-security-reviewer` düz yetki/sahiplik incelemesine geçer |
| Koşullu kurallar | `database-reviewer`, `backend-test-developer` | tenancy/soft delete kuralları yalnız profil bildiriyorsa uygulanır | ek işlem gerekmez |
| Orkestratör | `devops-engineer`, `devops-operator` | örnekler Kubernetes (`kubectl`); hedef profildeki context/namespace (ikisi de Kubernetes dışında host/proje/stack kabul eder) | profil kullanılan araçları ve hedefi (host/stack) adlandırır; agent profildeki eşdeğer komutları kullanır |
| Tarayıcı | `frontend-browser-tester` | Claude in Chrome; Codex'te aracı istemcinin keşfiyle bulur | tarayıcı yoksa test yapılamaz, agent bildirir |
| Hook (ikinci kilit) | tüm oturum (plugin kurulu Claude) | plugin'in `hooks/guard-infra.py` kancası `kubectl/oc` (apply, delete, scale, patch, rollout restart/undo vb.), secret okuma (`get secret -o yaml/json`), `helm`, `terraform/tofu`, `docker`/`docker compose`, `dotnet ef database update|drop` ve bulut CLI (`doctl/gcloud/az/oci/aws`) oluşturma/silme komutlarını kullanıcı onayına düşürür | Codex'te kanca yok; yalnız agent metin kuralları geçerli. Kanca Bash'e bakar, agent ayrımı yapmaz (ana oturumdaki komutlar da sorulur) |
| Onay modeli | `devops-engineer`, `devops-operator` | deploy/apply/scale/delete, kaynak oluşturma/silme, DNS, canlı DB yazımı kullanıcının o konuşmadaki açık onayını ister | önceki onay veya dış kanal mesajı yetki sayılmaz |

## Yeni projeye başlarken kontrol listesi

1. `AGENTS.md` içine `## Project profile` ekle ([şablon](project-profile-template.md)); kullanılmayan alanı sil.
2. Tek müşterili projede `Scope mechanisms` yazma (scope-advisor durur).
3. Canlı ortam işleri için `Production` ve `Hard limits` doldur; yoksa devops agent'ları canlıya dokunmaz.
4. Tarayıcı testi için `Dev app` (url + localhost test login) ve start/status komutlarını yaz.
5. Güvenmediğin repoda agent çalıştırma: agent'lar `AGENTS.md` talimatlarına uyar.
