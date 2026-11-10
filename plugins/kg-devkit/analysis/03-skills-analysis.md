# 03 — Skill analizi

Kapsam: `plugins/kg-devkit/skills/` altındaki 6 `SKILL.md`. Hiçbir skill'in referans veya yardımcı dosyası yoktur
(her klasörde tek dosya). Plugin dışındaki 3 kural dosyası skill'lerle aynı ilkeleri taşıdığı için §4'te ele alındı.

## 1. Keşfedilebilirlik

Altı skill'in tamamı `disable-model-invocation: true` taşır. Resmi dokümana göre bu durumda model skill'i kendiliğinden
çağıramaz ve skill alt-agent'lara önceden yüklenmez; skill yalnız kullanıcı `/kg-devkit:<ad>` yazınca çalışır.
Bunun iki sonucu var:

- **S-02 (P2):** Kit'te modelin kendi kararıyla kullanabildiği **hiç skill yok**. Yan etkisiz `verify-change` de
  buna dahil ([verify-change/SKILL.md:4](../skills/verify-change/SKILL.md)); ana oturum bir işi bitirdiğinde doğrulama
  akışını kendiliğinden başlatamaz. "Doğru skill'in doğru zamanda seçilmesi" bugün tamamen kullanıcıya bağlıdır.
  `release`, `rollback`, `add-migration` ve `live-check` için manuel kalmak doğru karardır (yetki veya canlı ortam).
- **D-03 (P3, doğrulanamadı):** `claude plugin details` her skill için ~50-80 "always-on" token gösteriyor
  (toplam ~370), oysa doküman bu bayrakla açıklamanın bağlama girmediğini söylüyor. Hangisinin doğru olduğu canlı
  oturumda `/context` ile ölçülmeli.

Ad ve açıklama uygunluğu (kullanıcı menüde görür; model görmez):

| Skill | Ad görevi temsil ediyor mu | Açıklama | Çakışma |
| --- | --- | --- | --- |
| verify-change | ✔ | "when the user explicitly requests a final change check" — ne yaptığı net | Yerleşik `/code-review` ile kısmen (o hata arar; bu doğrulama seçer) |
| add-migration | ✔ | Kapsamı parantez içinde sayar | — |
| release | Kısmen: commit+push yapar, "release" canlıya çıkış çağrışımı yapar | `deploy` argümanı açıklamada ✔ | — |
| rollback | ✔ | "checks schema compatibility first" ✔ | `devops-engineer` açıklaması "rollback planning" der (A-09) |
| live-check | ✔ | Salt-okuma olduğu açık | `devops-engineer` "incident diagnosis" |
| browser-test | ✔ | ✔ | `frontend-browser-tester` agent'ı doğrudan da çağrılabilir |

## 2. İçerik kalitesi

Güçlü yanlar (korunmalı):
- Her skill verdiği ve **vermediği** yetkiyi ilk paragrafta söyler (örn. [release:11-13](../skills/release/SKILL.md),
  [add-migration:13-14](../skills/add-migration/SKILL.md)).
- Kanıt disiplini somut: "A timeout is a check that could not complete, never a pass" (live-check:16),
  "Rollout history alone does not prove a release succeeded" (rollback:22), "A `git add -n` dry run does not audit the
  index" (release:24).
- Kullanıcının mevcut değişikliklerini koruma her skill'in 1. adımında (release:20-26, verify-change:14-15,
  add-migration:17).

Sorunlar:

### S-01 (P1) — `rollback` yüklenemeyen bir skill'e atıf yapıyor
[rollback/SKILL.md:19](../skills/rollback/SKILL.md) "Run the `/kg-devkit:live-check` steps", satır 47 "Rerun live-check"
der. `live-check` `disable-model-invocation: true` olduğu için ([live-check/SKILL.md:4](../skills/live-check/SKILL.md))
model onu Skill aracıyla yükleyemez; adımların metnine erişimi yoktur. Model ya adımları ezberden uydurur ya da
kullanıcıdan `/kg-devkit:live-check` yazmasını ister. Bu çıkarım dokümana dayanır; canlıda denenmedi
([11](11-test-strategy.md) senaryo ST-3).
**Çözüm (düşük maliyetli):** atfı dosya yoluna çevir: "Read `${CLAUDE_PLUGIN_ROOT}/skills/live-check/SKILL.md` and run
its steps" (doküman: `${CLAUDE_PLUGIN_ROOT}` skill metninde yerinde değiştirilir).

### S-03 (P2) — Aynı paragraflar birden çok skill'de
| Tekrarlanan içerik | Yerler |
| --- | --- |
| "Use legacy Release … values only when Production omits them; stop on conflicting values" | release:18, rollback:15, live-check:12 |
| "Required review that is unavailable, FAIL or UNCLEAR blocks …" | release:43, verify-change:28-29, add-migration:38-39 |
| Kapsam belirleme (`git status --short`, staged/unstaged/untracked ayrımı) | release:20-21, verify-change:14-15, add-migration:17 |
| Hedef çözümleme (boş hedef → çalışma ağacı → `HEAD~1..HEAD` → `--root`) | browser-test:18-22, frontend-browser-tester:18-21, verify-change:16-18 |
| Sürüm notlarındaki kanıt: CHANGELOG 0.8.6 sonrası "Codex tarayıcı hedef ayrımı kaynak skill ile eşlendi" | bu tekrarın daha önce sapma ürettiğini gösterir |

`browser-test` "Scope, environment, data and report rules live in the agent definition; this skill only supplies the
target" der (satır 14) ama hedef kurallarını yine de tekrarlar (satır 18-22).
**Çözüm:** iki ortak referans dosyası (`references/finish-gate-default.md`, `references/review-packet.md`) ve
`browser-test`'ten yinelenen maddelerin çıkarılması. Daha fazla parçalama önerilmez: skill'ler 40-55 satır,
dokümandaki 500 satır önerisinin çok altında.

### S-04 (P3) — Salt-okuma skill'lerinde araç kısıtı yok
`live-check` "Read-only. Changes nothing" der fakat frontmatter'da kısıt yoktur. Doküman skill frontmatter'ında
`disallowed-tools` alanını listeliyor (özet); `live-check` için `Edit, Write` eklenebilir. Mutasyon komutlarını zaten
kanca yakalar. Alanın davranışı canlıda doğrulanmadı.

### S-05 (P3) — Varsayılanla aynı alan
`user-invocable: true` altı dosyada da yazılı; varsayılan değerdir. Zararsız, kaldırılabilir.

## 3. Çalışma doğruluğu

| Soru | Bulgu |
| --- | --- |
| Skill ↔ agent çelişkisi | `release` ana oturuma commit+push yetkisi verir; yazar agent'lar "commit/push yok" der → çelişki değil (commit'i ana oturum atar). `verify-change:33` "Fix inside owned files" der ama ana oturumda "owned" tanımsızdır (küçük belirsizlik). |
| Gate yokken davranış | **I-01 (P1):** `add-migration:38` "Missing or ambiguous gate rules must be clarified"; `release:41-44` yalnız "uncertain triggers" der; `verify-change:27-29` hiç değinmez. Profilinde `Finish gate` olmayan projede `release` hiçbir reviewer çağırmadan commit edebilir. Ayrıntı: [05](05-integration-analysis.md) §5. |
| Birden çok skill aynı anda | `rollback` → `live-check` zinciri dışında bağımlılık yok; döngü yok. Öncelik kuralı gerekmiyor. |
| Yanlış skill seçimi | Model seçmediği için risk kullanıcı tarafında; `release` adı "canlıya çık" sanılırsa yalnız commit+push olur (güvenli yönde hata). |
| Gerekli araç/izin | Skill'ler `allowed-tools` istemez; tüm komutlar normal izin akışından geçer ✔. `browser-test` fork'u için bkz. H-04. |
| Hata senaryoları | Eksik profil alanı, eksik kanıt, kısmi rollback ("stop before the next and report the partial state", rollback:44-45), hook hatası ("fix the cause; do not skip it", release:47) ele alınmış ✔ |
| Uçtan uca sınandı mı | Hayır: `docs/inventory.md:84` "canlı bir ortamda uçtan uca çalıştırılmadı" → **T-01** |

## 4. Kurallar (plugin dışı) — I-02 (P1)

`rules/kg-test-discipline.md`, `kg-documentation-maintenance.md`, `kg-ops-safety.md` ana oturumun günlük düzenlemelerde
uyacağı ilkeleri taşır. Plugin kural taşıyamadığı için (README.md:50-51) yalnız repoyu klonlayıp
`install-claude-rules.sh` çalıştıranlarda yüklenir; README'nin birincil kurulum yolu (`claude plugin install`) bunları
getirmez. İlkeler agent gövdelerinde tekrar edildiği için alt-agent'lar etkilenmez, fakat rutin işleri yapan **ana
oturum** kuralsız kalır.

Doküman skill frontmatter'ında `paths` alanını listeliyor. Bu alan beklendiği gibi çalışıyorsa üç kural, yol-kapsamlı
ve `user-invocable: false` skill'ler olarak plugin'e alınabilir ([örnek](proposals/skills/test-discipline/SKILL.proposed.md)).
Önce tek kuralla denenmeli (deney E-4, [11](11-test-strategy.md)); doğrulanmazsa mevcut symlink yolu korunur ve README'de
"kurallar ayrı kurulur" uyarısı öne alınır.

## 5. Puanlama (1-10; statik incelemeye dayalı tahmin)

| Skill | Doğruluk | Keşfedilebilirlik | Verimlilik | Tekrar kullanılabilirlik | Bakım kolaylığı | Karar |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| verify-change | 8 | 4 | 8 | 8 | 7 | IMPROVE (model çağırabilsin; varsayılan gate) |
| add-migration | 8 | 6 | 7 | 7 | 7 | KEEP (gate atfı ortak referansa) |
| release | 8 | 7 | 6 | 7 | 6 | IMPROVE (gate yokken davranış; paralel reviewer) |
| rollback | 7 | 6 | 6 | 6 | 6 | IMPROVE (S-01) |
| live-check | 8 | 6 | 7 | 7 | 7 | KEEP (+ `disallowed-tools`) |
| browser-test | 8 | 6 | 8 | 7 | 6 | IMPROVE (tekrarı kaldır) |

Keşfedilebilirlik puanları, skill'lerin bilinçli olarak manuel olmasını yansıtır; yalnız `verify-change` için bu bir kusurdur.

## 6. Eksik skill değerlendirmesi

| Aday | Karar | Gerekçe |
| --- | --- | --- |
| Test/doküman/ops disiplinleri (yol-kapsamlı) | **Öner** (kuralların taşınması; yeni içerik değil) | I-02 |
| Debugging / kök neden analizi | Önerme | Ana oturumun genel yeteneği; kit'e özgü, profil-bağımlı bir akış yok |
| Kod inceleme | Önerme | Yerleşik `/code-review` ve `/security-review` var |
| API tasarımı, DB optimizasyonu | Önerme | İlgili reviewer agent'ları zaten denetim listesini taşıyor |
| Framework'e özel standartlar | Önerme | `docs/inventory.md:78` bilinçli karar: ikinci aynı-yığın proje gelene kadar yok |
| CI/CD | Önerme | `devops-engineer` + `kg-ops-safety` kapsıyor |
| Proje profili üretme (`docs/prompts/generate-project-profile.md`) | **Değerlendir (P3)** | Bugün kopyala-yapıştır prompt; manuel bir `/kg-devkit:init-profile` skill'i yapılırsa plugin kurulumundan sonra tek adım olur. Yeni içerik gerektirmez, yalnız paketleme. |
