# Prompt: projenin `## Project profile` bölümünü üret

kg-devkit agent'ları çalıştıkları reponun `AGENTS.md` dosyasındaki `## Project profile` bölümünü okur
([şablon](../project-profile-template.md), [agent gereksinimleri](../agent-requirements.md)). Aşağıdaki prompt'u yeni
projede Claude Code veya Codex'e vererek bu bölümü repodan çıkarttır.

````markdown
Görev: Bu reponun AGENTS.md dosyasına (yoksa oluştur; CLAUDE.md varsa ona da bakma, yalnız oku) `## Project profile`
bölümünü ekle veya güncelle. Şablon: docs/project-profile-template.md (kg-devkit) ya da aşağıdaki alan listesi.
Dil: Türkçe. Bölüm dışındaki mevcut içeriği değiştirme.

## 1. Keşif (yalnız oku, çalıştırma)
Şunları repodan çıkar; her değerin yanında dayanak dosyayı (yol:satır) not al:
- Layers/dirs: backend/frontend/test dizinleri, bağımlılık yönü (solution/package yapısından)
- Commands: start, status, lint/typecheck/build, odaklı test, tam test (package.json scripts, Makefile, CI workflow'ları, README)
- Dev app: yerel URL ve test girişi. Şifre/anahtar uydurma; repoda belgelenmiş localhost test hesabı yoksa
  "BELİRTİLMEMİŞ - kullanıcıya sor" yaz
- Router / navigation files: frontend yönlendirme ve menü dosyaları
- Rule docs / teknik doküman: docs/ altında frontend, backend, test kural belgeleri ve hangi bölümün ne için olduğu
- Conventions: tenancy, soft delete, audit, hata/Result stili, para ve tarih kuralları (kodda ve belgelerde ara)
- Scope mechanisms: müşteri/büro ayarı, özellik bayrağı, lookup mekanizmalarının adları ve belgeleri.
  Proje tek müşterili ise alanı hiç yazma (scope-advisor bu durumda NOT-APPLICABLE döner)
- Security review: tenancy/yetki modeli ve güvenlik kural belgesi
- Persistence: ORM, migration komutu, migrations dizini, adlandırma, API tip üretimi komutu
- Finish gate: hangi değişiklik türü hangi bağımsız kontrolü/reviewer'ı gerektirir (varsa mevcut belgelerden; yoksa önerme, sor)
- Release: changelog dosyası, sürüm kuralı, commit stili, commit'e girmeyecek gizli dosyalar (.gitignore'dan), deploy komutu, sağlık URL'leri
- Production: orkestratör/hedef (Kubernetes ise context+namespace; değilse host/proje/stack), status ve deploy komutları,
  iş yükü adları, registry, topoloji sınırları, runbook, secret KONUMLARI
- Report language ve Hard limits (commit/push yetkisi, branch politikası, yasak komutlar)

## 2. Yazma kuralları
- Yalnız ilgili alanları yaz, kullanılmayanı sil. Kanıtı olmayan değeri uydurma; bulunamayanı `BELİRTİLMEMİŞ` olarak işaretle
  ve sonda toplu listele.
- Secret, şifre, token, bağlantı dizesi, özel anahtar ASLA yazma; yalnız bunların dosya yolunu/adını yaz.
- Production, Release ve Hard limits alanlarında emin olmadığın hiçbir şeyi çıkarım olarak yazma; kullanıcıya sor.
  Canlı sistem komutu çalıştırma, canlı ortama bağlanma.
- Her alan tek satır veya kısa madde olsun; uzun açıklama için ilgili belgeye link ver.

## 3. Doğrulama ve teslim
- Yazdığın her yolun repoda var olduğunu, her komutun package.json/Makefile/CI'da geçtiğini kontrol et
  (komutları çalıştırma, yalnız varlıklarını doğrula).
- Çok kiracılı değilse Scope mechanisms ve tenant alanlarının yazılmadığını doğrula.
- Sonunda raporla: doldurulan alanlar, `BELİRTİLMEMİŞ` kalanlar, kullanıcıya sorulması gereken noktalar
  (Dev app girişi, Production, Hard limits, Finish gate).
- Commit ve push yapma; yalnız istenirse yap.
````
