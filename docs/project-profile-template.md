# Project profile şablonu

Her projenin `AGENTS.md` (veya `CLAUDE.md`) dosyasına `## Project profile` başlığıyla eklenir.
kg-devkit agent'ları önce bu bölümü okur; yoksa `package.json`/README'den çıkarım yapar ve raporda söyler.
Yalnız ilgili alanları doldur, kullanılmayanı sil.

```markdown
## Project profile

- Layers / dirs: backend=`backend/`, frontend=`frontend/` (bağımlılık yönü: ...)
- Commands: start=`./dev.sh start`, status=`./dev.sh status`, lint/typecheck/build=`pnpm run ...`,
  focused tests=`...`, full tests only when: ...
- Dev app: url=`http://localhost:5173`, test login=`user@example.com` / `<dev şifresi>` (yalnız localhost)
- Router / navigation files: `frontend/src/app/router/...`, `.../navigation.ts`
- Rule docs: frontend=`.claude/rules/frontend.md`, backend=`...`; technical doc=`docs/...` (hangi bölüm ne için)
- Finish gate: hangi değişiklik hangi bağımsız kontrolü/reviewer'ı zorunlu kılar (tek kaynak)
- Report language: Türkçe
- Hard limits: commit/push yetkisi, branch politikası, yasak komutlar (db reset, force-push, ...)
```
