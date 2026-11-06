# Güvenlik politikası / Security policy

## Güvenlik açığı bildirme / Reporting a vulnerability
Açığı herkese açık issue olarak **açma**. GitHub'da bu reponun **Security → Report a vulnerability** (özel güvenlik
danışmanlığı) bölümünü kullan. Do not open a public issue; use **Security → Report a vulnerability** (private advisory).

## Güven modeli / Trust model
- **Plugin kodu ve talimatları güvenilir sayılır.** `plugins/kg-devkit/agents`, `skills`, `hooks` ve `rules/` plugin'i kuran
  herkesin Claude Code/Codex oturumunda çalışır. Bu yüzden bu yollardaki her değişiklik `CODEOWNERS` ile sahibinin
  incelemesinden geçer.
- **Agent'lar çalıştıkları reponun `AGENTS.md` dosyasını okur ve uyar.** Güvenmediğin bir repoda kit'i kullanma.
- **`hooks/guard-infra.py` bir ikinci kilittir, güvenlik sınırı değildir.** Canlı ortamı değiştiren `kubectl`/`helm`/
  `terraform` komutlarını onaya düşürür (regex tabanlı); her komutu yakalamayı garanti etmez.
- **Yazma yetkisi** yalnız repo sahibi ve belirlenen collaborator'dadır. Dışarıdan katkı fork + PR iledir.

## Katkı vermeden önce / Before contributing
PR'lar `plugins/`, `.claude/`, `.github/`, `scripts/` altını değiştiriyorsa özellikle satır satır incelenir.
Agent talimatlarına gizli komut, dış URL'e veri gönderme veya yetki genişletme eklemeyin.
