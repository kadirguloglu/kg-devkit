# Project profile şablonu

Her projenin `AGENTS.md` (veya `CLAUDE.md`) dosyasına `## Project profile` başlığıyla eklenir.
kg-devkit agent ve skill'leri önce bu bölümü okur; yoksa `package.json`/README'den çıkarım yapar ve raporda söyler.
Yalnız ilgili alanları doldur, kullanılmayanı sil.

```markdown
## Project profile

- Layers / dirs: backend=`backend/`, frontend=`frontend/` (bağımlılık yönü: ...)
- Commands: start=`...`, status=`...`, lint/typecheck/build=`...`, focused tests=`...`, full tests only when: ...
- Dev app: url=`http://localhost:5173`, test login=`user@example.com` / `<dev şifresi>` (yalnız localhost)
- Router / navigation files: `frontend/src/app/router/...`, `.../navigation.ts`
- Rule docs: frontend=`...`, backend=`...`, tests=`...`; technical doc=`docs/...` (hangi bölüm ne için)
- Conventions: tenancy / soft delete / audit / hata (Result) kuralları, para ve tarih kuralları, kimlik yeniden kullanımı, sunucu-otoriter hesaplamalar, başarısız yazma temizliği
- Scope mechanisms: mevcut büro/müşteri ayarı, özellik bayrağı ve lookup mekanizmalarının adları + belgeleri; kapsam sorusunun metni
  (scope-advisor okur; tenant'sız projede yazma, agent durur)
- Security review: tenancy/yetki modeli ve güvenlik kural belgesi (tenant-security-reviewer okur)
- Persistence: ORM=`...`, migration komutu=`...`, migrations dizini=`...`, üretilen migration artefaktları (ör. EF Core: designer/snapshot),
  global filtre bypass API'leri (ör. EF Core `IgnoreQueryFilters`), adlandırma, izin zinciri, API tip üretimi komutu
- API contract: şema/OpenAPI konumu, istemci tipi üretim komutu, versiyonlama ve kullanımdan kaldırma politikası, eski/harici istemciler
  (api-contract-reviewer okur)
- Dependencies: paket yöneticileri ve lockfile konumları, izinli lisanslar, güvenlik taraması komutu, sabitleme/güncelleme politikası, özel registry
  (dependency-supply-chain-reviewer okur)
- Performance: gecikme/boyut bütçeleri, sıcak endpoint ve ekranlar, beklenen veri hacmi, mevcut önbellek mekanizması
  (performance-reviewer okur)
- Observability: log/metrik/trace kütüphaneleri ve kuralları, korelasyon/tenant kimliği, log'a girmeyecek veriler, sağlık endpoint'leri
  (observability-reviewer okur)
- Finish gate: hangi değişiklik hangi bağımsız kontrolü/reviewer'ı zorunlu kılar (tek kaynak); reviewer geçti ifadesi
- Release: changelog dosyası + sürüm kuralı (özellik=minor, düzeltme=patch), commit stili (dil, önek),
  gizli dosya listesi (commit'e girmeyecek), deploy komutu, sağlık URL'leri ve beklenen kodlar
- Production: cluster context=`...`, namespace=`...`, bulut CLI kimlik komutu, status/deploy/rollback komutları, iş yükü adları,
  registry repoları, topoloji sınırları (replika, güncelleme stratejisi, depolama), runbook=`...`, secret konumları
- Report language: Türkçe
- Hard limits: commit/push yetkisi, branch politikası, yasak komutlar (db reset, force-push, ...)
```
