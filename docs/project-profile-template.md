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
- Conventions: tenancy / soft delete / audit / hata (Result) kuralları, para ve tarih kuralları
- Persistence: migration komutu=`...`, migrations dizini=`...`, adlandırma, izin zinciri, API tip üretimi komutu
- Finish gate: hangi değişiklik hangi bağımsız kontrolü/reviewer'ı zorunlu kılar (tek kaynak); reviewer geçti ifadesi
- Release: changelog dosyası + sürüm kuralı (özellik=minor, düzeltme=patch), commit stili (dil, önek),
  gizli dosya listesi (commit'e girmeyecek), deploy komutu, sağlık URL'leri ve beklenen kodlar
- Production: cluster context=`...`, namespace=`...`, status/deploy komutları, iş yükü adları,
  registry repoları, topoloji sınırları (replika, güncelleme stratejisi, depolama), runbook=`...`, secret konumları
- Report language: Türkçe
- Hard limits: commit/push yetkisi, branch politikası, yasak komutlar (db reset, force-push, ...)
```
