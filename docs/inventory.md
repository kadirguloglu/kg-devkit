# Envanter: hukuk-buro-yonetim → kg-devkit (Faz 1)

Kaynak: `hukuk-buro-yonetim/.claude/`. Sayılar o dosyadaki bağımlılık işaretleyicileridir
(AGENTS.md atfı / dokümana atıf / `dev.sh` / `§` / tenant-büro terimi). Yüksek sayı = daha çok yeniden yazım.

## Durum

| Dosya | Bağımlılık | Karar | Faz |
| --- | --- | --- | --- |
| agent frontend-developer | A1 D0 S0 §0 T0; `../rules/*` linkleri | Taşındı (profil okur) | 2 ✅ |
| agent frontend-browser-tester | A1 S1 T1; kimlik bilgisi, URL, `frontend/src/**`, router yolları | Taşındı (<profile> yer tutucuları) | 2 ✅ |
| skill browser-test | bağımsız; `agent:` ile yukarıdakine bağlı | Taşındı | 2 ✅ |
| agent backend-developer | A1 S2 T1 | Genelleştir | 3 |
| agent backend-test-developer | A1 D1 S1 T2 | Genelleştir | 3 |
| agent frontend-test-developer | A1 S2 | Genelleştir | 3 |
| agent database-reviewer | A1 D1 §3 T5 | Genelleştir (tenant kısmı opsiyonel bölüm) | 3 |
| agent engineering-software-architect | A2 D2 §1 T6 | Genelleştir | 3 |
| agent devops-engineer / devops-operator | A1 D1 S2 / A1 | Genelleştir; DigitalOcean'a özgü kısım profile | 3 |
| skill verify-change | A2 D1 T2 | Genelleştir (bitirme kapısı profilden) | 3 |
| skill add-migration | A2 D1 S5 §3 T3 | Genelleştir (EF/komut profilden) | 3 |
| skill release / rollback / live-check | A2 D2 S4 / A1 S1 / A1 S1 | Genelleştir; ortama özgü adımlar profile | 3 |
| agent tenant-security-reviewer | T10 | Projede kalır; sonra "multi-tenant" adayı | — |
| agent office-scope-advisor | T8, "büro" alan kavramı | Projede kalır | — |
| rules/* (7 dosya) | §-numaralı teknik belge atıfı | Projede kalır (plugin rule taşımaz) | — |

## Açık kararlar

- Kit dili: şimdilik İngilizce yazıldı, rapor dili profilden gelir. Türkçe istenirse tek seferlik çeviri.
- `.codex/` ve `.agents/` kopyaları: kit yalnız Claude tarafını taşıyor; Codex kopyaları ayrı karar (Faz 3 sonrası).
- Genel rule'lar için `~/.claude/rules/` symlink'i: Faz 3'te, hangi kuralların gerçekten genel olduğu netleşince.
- AGENTS.md'deki "agent'tan agent başlatma yok" gibi kısıtlar: kit agent'larında sabit bırakıldı, profil gerekirse ezer.
