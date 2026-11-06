# Prompt: projenin `## Project profile` bölümünü üret (soru-cevap)

kg-devkit agent ve skill'leri çalıştıkları reponun `AGENTS.md` dosyasındaki `## Project profile` bölümünü okur
([şablon](../project-profile-template.md), [gereksinimler](../agent-requirements.md)). Aşağıdaki prompt'u yeni
projenin kök dizininde Claude Code veya Codex'e ver (kg-devkit reposunu açman gerekmez): repodan çıkarabildiğini çıkarır, **yalnız bulamadığı veya emin olmadığı alanları** sana
sorar, sonra bölümü yazar.

````markdown
Görev: Bu reponun AGENTS.md dosyasına (yoksa oluştur; CLAUDE.md varsa yalnız oku) `## Project profile` bölümünü ekle veya
güncelle. Şablon aşağıda (## 0). Bölüm dışındaki içeriği değiştirme. Bunu SORU-CEVAP olarak yürüt: önce repodan çıkar,
cevabı bulunanı sorma, kalanı kullanıcıya sor. Dil: Türkçe. Bu prompt kendi içinde eksiksizdir: kg-devkit reposundaki dosyalara ihtiyaç duymaz.

## 0. Şablon (alan listesi; kullanılmayan alanı silerek doldur)
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

## 1. Keşif (yalnız oku; komut çalıştırma, canlı sisteme bağlanma)
Mevcut `## Project profile` varsa önce onu oku; dolu ve repoyla tutarlı alanı yeniden sorma, çelişen/eskiyeni işaretle.
Her alan için değeri ve dayanak dosyayı (yol:satır) çıkar:
- Layers / dirs: backend/frontend/test dizinleri, bağımlılık yönü
- Commands: start, status, lint/typecheck/build, odaklı test, tam test (package.json, Makefile, CI, README)
- Dev app: yerel URL ve test girişi (yalnız repoda belgelenmiş localhost hesabı; şifre/anahtar uydurma)
- Router / navigation files
- Rule docs ve teknik doküman: docs/ altında frontend, backend, test kural belgeleri ve hangi bölümün ne için olduğu
- Conventions: tenancy, soft delete, audit, hata/Result stili, para ve tarih, kimlik yeniden kullanımı, sunucu-otoriter hesaplamalar, başarısız yazma temizliği
- Scope mechanisms: müşteri/büro ayarı, özellik bayrağı, lookup mekanizmaları + belgeleri + kapsam sorusunun metni. Tek müşterili projede alanı hiç yazma (`scope-advisor` `NOT-APPLICABLE` döner)
- Security review: tenancy/yetki modeli ve güvenlik kural belgesi
- Persistence: ORM, migration komutu ve dizini, üretilen migration artefaktları (ör. EF Core: designer/snapshot), global filtre bypass API'leri ve ham SQL, adlandırma, izin zinciri, API tip üretimi komutu
- API contract: şema/OpenAPI konumu, istemci tipi üretim komutu, versiyonlama/kullanımdan kaldırma politikası, eski veya harici istemciler
- Dependencies: paket yöneticileri, lockfile konumları, izinli lisanslar, güvenlik taraması komutu, sabitleme/güncelleme politikası, özel registry
- Performance: gecikme/boyut bütçeleri, sıcak endpoint/ekranlar, veri hacmi, önbellek (yalnız belgelenmişse)
- Observability: log/metrik/trace kütüphaneleri ve kuralları, korelasyon/tenant kimliği, log'a girmeyecek veriler, sağlık endpoint'leri
- Finish gate: hangi değişiklik hangi bağımsız kontrolü/reviewer'ı gerektirir; reviewer geçti ifadesi (yalnız mevcut belgelerden)
- Release: changelog + sürüm kuralı, commit stili, commit'e girmeyecek gizli dosyalar (.gitignore'dan), deploy komutu, sağlık URL'leri ve beklenen kodlar
- Production: orkestratör/hedef (Kubernetes: context+namespace; değilse host/proje/stack), bulut CLI kimlik komutu, status/deploy/rollback komutları,
  iş yükü adları, registry repoları, topoloji sınırları ve güncelleme stratejisi, runbook, secret KONUMLARI
- Report language ve Hard limits: yasak komutlar, branch politikası, ek kısıtlar

## 2. Eşleştirme: cevaplı / cevapsız
Keşiften sonra alanları üç gruba ayır ve kullanıcıya KISA bir tablo olarak göster (alan | durum | değer/dayanak):
1. **Bulundu:** dayanak dosya var, çelişki yok. Sorma; yalnız tabloda göster.
2. **Belirsiz:** birden fazla aday veya çelişen kaynak. Aday(lar)ı seçenek diye sun, kullanıcı seçsin.
3. **Bulunamadı:** repoda dayanak yok. Sor.
Her zaman kullanıcıya sorulacaklar (çıkarım yazılmaz): Production hedefi, Release deploy komutu, Hard limits, Finish gate
(belgede yoksa), Dev app test girişi (belgelenmemişse). Tek müşterili olduğu anlaşıldıysa tenant alanlarını sorma.

## 3. Soru-cevap
- Soruları gruplar halinde ve en çok 4 soruyla sor (AskUserQuestion varsa onu kullan: cevaplanabilir seçenekler + "Diğer").
  Her soruda neyi aradığını, nerede baktığını ve varsa önerini söyle.
- Kullanıcı "bilmiyorum/geç" derse alanı `BELİRTİLMEMİŞ` yaz; ısrar etme, uydurma.
- Aynı cevabı iki kez isteme; önceki cevaplardan türeyen alanı (ör. tek müşterili → tenant alanları yok) sormadan ele.
- Cevapları yazmadan önce özetle ve onay al; onaydan sonra bölümü yaz.

## 4. Yazma kuralları
- Yalnız ilgili alanları yaz, kullanılmayanı sil. Her alan tek satır/kısa madde; uzun açıklama için belgeye link.
- Secret, şifre, token, bağlantı dizesi, özel anahtar ASLA yazma; yalnız dosya yolunu/adını yaz.
- Production'ı agent'ın açıkça kullanabileceği biçimde yaz (Kubernetes: context+namespace; "geçerli context"e güvenme).
- `Hard limits` yalnız ek kısıt koyar; agent'ların commit/push yapmama kuralını gevşetemez, bunu tekrar yazma.
  `release` skill'i yalnız kullanıcı `/release` çağırınca commit+push yapar; profile "onaysız" ifadesi koyma.
- Plugin kancası `guard-infra` canlıyı değiştiren komutları onaya düşürür; profilde bu komutlar "onaysız çalıştırılabilir" yazılmaz.

## 5. Doğrulama ve teslim
- Yazdığın her yolun repoda var olduğunu, her komutun package.json/Makefile/CI'da geçtiğini kontrol et (çalıştırma).
- Tek müşterili projede Scope mechanisms ve tenant alanlarının yazılmadığını doğrula.
- Raporla: doldurulan alanlar, `BELİRTİLMEMİŞ` kalanlar, kullanıcıdan alınan cevaplar, açık noktalar.
- Commit ve push yapma; yalnız istenirse yap.
````
