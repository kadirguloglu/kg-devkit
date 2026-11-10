---
name: test-discipline
description: Rules for writing, changing or running tests - focused selection, real fixtures over mocks, never weakening assertions, exact reporting. Loads when test files are read or edited.
user-invocable: false
paths:
  - "**/tests/**"
  - "**/test/**"
  - "**/*.test.*"
  - "**/*.spec.*"
  - "**/*Tests.cs"
  - "**/*_test.go"
  - "**/test_*.py"
---

<!-- ÖNERİ (I-02). Kaynak: ../../../../../../rules/kg-test-discipline.md (gövde aynen taşınır).
     Neden: plugin `rules/` taşıyamaz; bugün kurallar yalnız repoyu klonlayıp install-claude-rules.sh çalıştıranlarda
     yüklenir (README.md:50-51). Skill frontmatter'ındaki `paths` aynı yol-kapsamlı yüklemeyi plugin içinde sağlar.
     DOĞRULANMALI: `paths` alanının plugin skill'lerinde beklenen şekilde tetiklendiği canlıda sınanmadı.
     Geçiş: kural dosyası Codex ve mevcut symlink kullanıcıları için bir sürüm boyunca korunur. -->

# Test discipline (kg-devkit)

Generic rules; the repo's own test rules and `Project profile` commands take precedence.

… (rules/kg-test-discipline.md satır 15-28 aynen) …
