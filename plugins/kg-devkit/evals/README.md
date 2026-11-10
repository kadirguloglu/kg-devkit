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
