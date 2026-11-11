# Güvenlik politikası / Security policy

## Güvenlik açığı bildirme / Reporting a vulnerability
Açığı herkese açık issue olarak **açma**. GitHub'da bu reponun **Security → Report a vulnerability** (özel güvenlik
danışmanlığı) bölümünü kullan. Do not open a public issue; use **Security → Report a vulnerability** (private advisory).

## Güven modeli / Trust model
- **Plugin kodu ve talimatları güvenilir sayılır.** `plugins/kg-devkit/agents`, `skills`, `hooks` ve `rules/` plugin'i kuran
  herkesin Claude Code/Codex oturumunda çalışır. Bu yüzden bu yollardaki her değişiklik `CODEOWNERS` ile sahibinin
  incelemesinden geçer.
- **Agent'lar çalıştıkları reponun `AGENTS.md` dosyasını okur ve uyar.** Güvenmediğin bir repoda kit'i kullanma.
- **`hooks/guard-infra.py` bir ikinci kilittir, güvenlik sınırı değildir.** Canlı ortamı değiştiren veya secret okuyan
  `kubectl`/`oc`/`helm`/`terraform`/`docker`/bulut CLI/migration/dağıtım aracı komutlarını ve `git push --force`,
  `git reset --hard`, `git clean -f` ile secret görünümlü dosyanın stage'lenmesini onaya düşürür (komut metnini
  belirteçlere ayırarak); her komutu yakalamayı garanti etmez. Takma ad, değişken, betik ve MCP çağrıları görünmez.
- **`hooks/agent_run_log.py` yalnız meta veri yazar** (olay, oturum ve agent kimliği/türü, izin modu, zaman, `VERDICT`/`STATUS` değeri); prompt, komut veya
  rapor metni kaydetmez. Dosya yerelde, plugin veri dizininde kalır; `KG_AGENT_LOG=off` ile kapatılır.
- **`hooks/require_outcome.py` yalnız sonuç satırının varlığını zorlar** (`VERDICT:`/`STATUS:`); hükmün doğruluğunu
  kanıtlamaz. Bir reviewer'ın `PASS` demesi incelemenin yeterli olduğu anlamına gelmez.
- **Yazma yetkisi** yalnız repo sahibi ve belirlenen collaborator'dadır. Dışarıdan katkı fork + PR iledir.

## Katkı vermeden önce / Before contributing
PR'lar `plugins/`, `.claude/`, `.github/`, `scripts/` altını değiştiriyorsa özellikle satır satır incelenir.
Agent talimatlarına gizli komut, dış URL'e veri gönderme veya yetki genişletme eklemeyin.
