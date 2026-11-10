# Öneri örnekleri (uygulanmadı)

Bu klasördeki her dosya **taslaktır**; plugin tarafından yüklenmez (Claude Code yalnız plugin kökündeki `agents/`,
`skills/`, `hooks/hooks.json` yollarını okur) ve mevcut hiçbir dosyanın yerine geçmemiştir. Gerekçeler için ilgili
bulgu ID'sine bakın: [10-improvement-roadmap.md](../10-improvement-roadmap.md).

| Dosya | İlgili bulgu | Doğrulama durumu |
| --- | --- | --- |
| [hooks/guard_infra_v2.py](hooks/guard_infra_v2.py) | H-01, H-02, H-03, H-05, H-07, I-04 | Karar fonksiyonu sınandı: resmi 106 örnek + 115 ek senaryo ([tests/test_guard_probe.py](tests/test_guard_probe.py)). Claude Code içinde canlı kanca olarak **çalıştırılmadı**. |
| [hooks/hooks.proposed.json](hooks/hooks.proposed.json) | H-05, H-06, A-06 | Sözdizimi geçerli JSON; çalışma zamanında sınanmadı. |
| [hooks/agent_run_log.py](hooks/agent_run_log.py) | A-06, T-01 (ölçüm) | Elle verilen JSON ile sınandı; `SubagentStart/Stop` girdi alanları resmi dokümandan alındı, canlıda doğrulanmadı. |
| [agents/database-reviewer.proposed.md](agents/database-reviewer.proposed.md) | A-01, A-05, A-06 | Yalnız metin; davranış ölçülmedi. |
| [agents/scope-advisor.proposed.md](agents/scope-advisor.proposed.md) | A-02 | Yalnız metin (ön madde + değişen bölümler). |
| [skills/verify-change/SKILL.proposed.md](skills/verify-change/SKILL.proposed.md) | S-02, I-01 | Yalnız metin. |
| [skills/test-discipline/SKILL.proposed.md](skills/test-discipline/SKILL.proposed.md) | I-02 | `paths` alanının skill'lerde desteklendiği dokümandan özet olarak alındı; **doğrulanmalı**. |
| [references/finish-gate-default.md](references/finish-gate-default.md) | I-01 | Yalnız metin. |
| [references/review-packet.md](references/review-packet.md) | A-01, A-03 | Yalnız metin. |
| [tests/test_guard_probe.py](tests/test_guard_probe.py) | H-01..H-07 | Çalıştırıldı (çıkış 0). |
