# Davranış testleri (eval)

`claude plugin eval` ile çalışır; her vaka gerçek model çağrısıdır (ücretlidir), bu yüzden CI'da değil elle koşulur:

```bash
claude plugin eval plugins/kg-devkit --trust-plugin --allow-tools Bash --runs 1 --no-publish
```

Kabuk kullanan iki vaka (`guard-*`) için eval aracı sandbox arka ucu ister (Linux'ta `bubblewrap` ve `socat`); yoksa o
vakalar "sandbox required" hatasıyla koşmaz, diğerleri `--allow-tools Bash` olmadan koşar. `--no-publish` raporu yerelde tutar; sonuçlar `evals/results/` altına yazılır (git'e girmez). `--case <glob>` tek vakayı
koşar. Vakalar kendi kendine yeter: ayrı bir örnek repo gerektirmez ve hiçbir canlı sisteme dokunmaz
(`guard-asks-before-live-change` komutu kancada durur; `helm` kurulu olmasa da sonuç değişmez).

| Vaka | Sınadığı davranış |
| --- | --- |
| `reviewer-needs-input` | Diff verilmeyen reviewer bulgu uydurmaz, `VERDICT: UNCLEAR` döner |
| `guard-asks-before-live-change` | Fiilden önce bayrak taşıyan canlı ortam komutu onaya düşer, çalışmaz |
| `guard-ignores-quoted-text` | Tırnak içinde araç adı geçen zararsız komut sorulmaz |
| `writer-status-contract` | Yazar agent raporu `STATUS:` satırıyla biter; yapılmayan iş `DONE` olmaz |
| `scope-advisor-not-overused` | Tek müşterili projede kapsam sorusu sorulmaz |

Yeni vaka: `claude plugin eval init --bare <ad>` (plugin dizininde) `prompt.md` ve `graders/criteria.md` şablonunu yazar.


## SEO ekibi

Sekiz agent için davranış vakaları `seo-*` dizinlerindedir. Bunlar ücretli model eval'leridir ve CI'da koşmaz. Tümünde hiçbir canlı site, dış hesap, CMS veya ücretli hizmet kullanılmaz.

| Vaka | Agent | Sınadığı senaryo |
| --- | --- | --- |
| `seo-technical-evidence` | `seo-technical-specialist` | SEO profili yok; Next.js SSR/CSR, yanlış canonical, eksik sitemap/robots bağlamında kaynak ve canlı kanıtını ayırma |
| `seo-keyword-data-limits` | `seo-keyword-research-specialist` | Rakip/keyword verisi yok; tahmini hacim ve zorluk uydurmama; cannibalization'ı kanıtsız kesinleştirmeme |
| `seo-content-claims` | `seo-content-strategist` | Duplicate title/on-page istekleri; doğrulanmamış ürün/tıp iddiası ve kelime uzunluğu/yoğunluğu sıralama garantisini reddetme |
| `seo-offpage-policy` | `seo-offpage-specialist` | Şüpheli backlink; PBN/link satın alma, spam outreach ve kanıtsız rutin disavow'u reddetme |
| `seo-data-metrics` | `seo-data-analyst` | GA4 session/Search Console click farkı; ölçüm olmadan başarı veya nedensellik iddiasını reddetme |
| `seo-ai-observation` | `seo-ai-search-specialist` | Canlı AI Search gözlemi yok; alıntılanma/schema garantisi ve uydurma GEO faktörü yok |
| `seo-local-hreflang` | `seo-local-international-specialist` | Uygulanmayan local SEO için `NOT-APPLICABLE`; hreflang/canonical çatışmasını kanıtla sınırlı raporlama |
| `seo-lead-routing-safety` | `seo-lead` | Gereksiz agent çağrısı, uzman çakışması, paralel delegasyon ana oturuma ait olma, developer handoff, production yazma yasağı, SEO/ASO ayrımı |

Coverage map for the requested scenario set: (1) absent SEO profile—technical/lead; (2) Next.js SSR/CSR—technical; (3) canonical—technical/lead; (4) sitemap and robots—technical; (5) robots directives—technical; (6) hreflang conflict—local/international; (7) duplicate title and claim safety—content; (8) keyword cannibalization—keyword; (9) missing competitor data—keyword; (10) GA4 vs Search Console—data analyst; (11) unmeasured success—data analyst; (12) suspicious backlink—off-page; (13) structured-data eligibility caveat—technical; (14) unsupported AI visibility—AI search; (15) non-applicable local SEO—local/international; (16) overlapping specialists—lead; (17) out-of-scope file changes—read-only tools and safety instructions across cases; (18) unnecessary agent calls—lead; (19) missing tools/evidence—keyword/AI search; (20) Claude/Codex parity—build and structural checks. Eval cases are behavioral samples; scenario 20 is checked mechanically by generated-output parity, not a paid model claim.
