---
name: verify-change
description: Review the current diff and run the smallest meaningful verification (focused build/tests, docs checks, gate-triggered reviewers) before handing work back. Use when implementation of a change is finished and before saying it is done, or when the user asks for a final check. Never commits, pushes, deploys or resets data.
---

<!-- ÖNERİ. Mevcut dosya: ../../../../skills/verify-change/SKILL.md. Değişenler:
     1) `disable-model-invocation: true` ve varsayılanla aynı olan `user-invocable: true` kaldırıldı (S-02, S-05):
        skill hiçbir yetki vermediği için modelin iş bitiminde kendiliğinden çağırması güvenlidir.
     2) description "ne zaman" koşulunu taşır.
     3) Finish gate yoksa varsayılan tabloya düşer (I-01); reviewer girdisi ortak pakete bağlanır (A-01).
     Adımlar 1, 2, 4, 5 mevcut dosyadaki ile aynıdır. -->

# Change verification

… (mevcut giriş ve adım 1-2 aynen) …

3. Choose the smallest meaningful set of checks:
   - Documentation or agent/skill config only … (aynen)
   - Backend behavior … (aynen)
   - Frontend behavior … (aynen)
   - Reviewers: use the profile's `Finish gate`. If the profile has none, use
     `${CLAUDE_PLUGIN_ROOT}/references/finish-gate-default.md`. Prepare the evidence once as described in
     `${CLAUDE_PLUGIN_ROOT}/references/review-packet.md` and launch all triggered reviewers in one turn.
     A required reviewer that is unavailable, FAIL, UNCLEAR or without a `VERDICT:` line blocks verification.

… (mevcut adım 4-6 aynen) …
