# Prompt: projenin `## Project profile` bölümünü üret (soru-cevap)

kg-devkit agent ve skill'leri çalıştıkları reponun `AGENTS.md` dosyasındaki `## Project profile` bölümünü okur
([şablon](../project-profile-template.md), [gereksinimler](../agent-requirements.md)). Aşağıdaki prompt'u yeni
projenin kök dizininde Claude Code veya Codex'e ver (kg-devkit reposunu açman gerekmez). Önce projeyi araştırır, ardından
ilgili her alanı sana sorar. Bulduğu bilgiyi doğrulatır, bulamadığı bilgiyi senden ister ve cevaplarına göre bölümü yazar.

````markdown
Görev: Bu reponun AGENTS.md dosyasına (yoksa oluştur; CLAUDE.md varsa yalnız oku, yalnız `@AGENTS.md` satırı eksikse bölüm 4'e göre ekletmeyi öner) `## Project profile` bölümünü ekle veya
güncelle. Şablon aşağıda (## 0). Bölüm dışındaki içeriği değiştirme. Önce ilgili soruların yanıtlarını projede ara.
Ardından bulgu olup olmamasına bakmadan ilgili her alanı kullanıcıya sor. Dil: Türkçe. Bu prompt kendi içinde eksiksizdir: kg-devkit reposundaki dosyalara ihtiyaç duymaz.

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
- ASO (isteğe bağlı): uygulama adı ve mağaza bağlantıları, hedef platformlar, ülkeler ve diller, hedef kullanıcı, marka dili,
  doğrulanmış özellikler, analitik olayları, veri dönemi ve mevcut mağaza varlıkları veya kanıt dosyalarının yolları
  (ASO agent'ları okur; kapsam ve kanıt çağrı sırasında da verilebilir)
- SEO (isteğe bağlı): website URL/domain, iş türü ve framework; birincil/hedef ülkeler ve diller; hedef kitle; önemli landing page'ler; rakipler; organik dönüşüm hedefleri; Analytics/Search Console erişilebilirliği; CMS; sitemap konumu; SEO kısıtları; baseline raporlama dönemi
- Finish gate: hangi değişiklik hangi bağımsız kontrolü/reviewer'ı zorunlu kılar (tek kaynak); reviewer geçti ifadesi
  (yazılmazsa kit'in varsayılan gate tablosu kullanılır)
- Release: changelog dosyası + sürüm kuralı (özellik=minor, düzeltme=patch), commit stili (dil, önek),
  gizli dosya listesi (commit'e girmeyecek)
- Production: cluster context=`...`, namespace=`...`, bulut CLI kimlik komutu, status/deploy/rollback komutları, iş yükü adları,
  sağlık URL'leri ve beklenen kodlar, registry repoları, topoloji sınırları (replika, güncelleme stratejisi, depolama), runbook=`...`, secret konumları
- Report language: Türkçe
- Hard limits: commit/push yetkisi, branch politikası, yasak komutlar (db reset, force-push, ...)
```

## 1. Keşif (yalnız oku; komut çalıştırma, canlı sisteme bağlanma)
Mevcut `## Project profile` varsa önce onu oku ve alanlarını repodaki kaynaklarla karşılaştır. Dolu ve tutarlı alanları da
doğrulatmak için soru listesine al. Çelişen veya eski görünen değerleri işaretle.
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
- İsteğe bağlı `ASO` alanı için uygulama adını, mağaza bağlantılarını, platform/ülke/dil kapsamını, hedef kullanıcıyı, marka dilini,
  doğrulanmış özellikleri, analitik olaylarını, veri dönemini ve varlık veya kanıt dosyalarının yollarını ara. Ürün belgelerini,
  mağaza taslaklarını ve mevcut raporları kullan.
- Finish gate: hangi değişiklik hangi bağımsız kontrolü/reviewer'ı gerektirir; reviewer geçti ifadesi (yalnız mevcut belgelerden)
- Release: changelog + sürüm kuralı, commit stili, commit'e girmeyecek gizli dosyalar (.gitignore ve belgelenmiş dosya listesinden; zaten izlenen/stage edilmiş dosyalar da kapsamdadır)
- Production: orkestratör/hedef (Kubernetes: context+namespace; değilse host/proje/stack), bulut CLI kimlik komutu, status/deploy/rollback komutları,
  sağlık URL'leri ve beklenen kodlar, iş yükü adları, registry repoları, topoloji sınırları ve güncelleme stratejisi, runbook, secret KONUMLARI.
  Rollback runbook'unda başarılı release kanıtı, image digest → kaynak commit/revision eşlemesi ve uygulanan şemayı salt-okunur doğrulama yöntemi var mı?
  Eski Release deploy/sağlık değerleri Production'da eksikse kullanılabilir; çelişen değerleri kullanıcıya netleştir, yeni yazımda Production'ı kullan.
- SEO (isteğe bağlı): site/domain, iş türü/framework, hedef ülke/diller/kitle, önemli sayfalar, rakipler, organik dönüşüm hedefleri, Analytics/Search Console, CMS, sitemap, kısıtlar ve baseline dönemi; yalnız belgeli değerleri çıkar, eksikleri zorunlu sayma
- Report language ve Hard limits: yasak komutlar, branch politikası, ek kısıtlar

## 2. Eşleştirme: cevaplı / cevapsız
Keşiften sonra ilgili alanları kısa bir tabloda göster (alan | durum | değer/dayanak). Her durum için soru sor.

1. **Bulundu.** Değeri ve `yol:satır` dayanağını paylaş. Güncel ve doğru olduğunu doğrulat veya düzeltmesini iste.
2. **Belirsiz.** Aday değerleri ve dayanaklarını paylaş. Hangisinin geçerli olduğunu sor.
3. **Bulunamadı.** Baktığın dosyaları kısaca belirt ve değeri kullanıcıdan iste.

`Production` hedefi ve deploy komutunu, `Hard limits` ve `Finish gate` alanlarını doğrudan kullanıcıya sor.
`Dev app` kapsamı varsa test girişini de sor. Kullanıcı `Finish gate` istemezse alanı yazma. Kit'in varsayılan gate tablosu kullanılır.
Kiracı modelini doğrulat. Kullanıcı tek müşterili olduğunu doğrularsa kiracıya özgü alanları atla.
App Store veya Google Play kapsamı varsa isteğe bağlı `ASO` alanını da aynı şekilde sor.

## 3. Soru-cevap
- Soruları gruplar halinde ve en çok 4 soruyla sor (AskUserQuestion varsa onu kullan: cevaplanabilir seçenekler + "Diğer").
  Her soruda neyi aradığını, nerede baktığını ve varsa önerini söyle. Gizli değerler için yalnız dosya yolunu belirt.
- Kullanıcı "bilmiyorum/geç" derse alanı `BELİRTİLMEMİŞ` yaz; ısrar etme, uydurma.
- İsteğe bağlı `ASO` alanını mevcut ve ilgili bilgilerle doldur. Bilgi yoksa alanı atla. Girdiler çağrı sırasında da verilebilir.
- Kullanıcının bu oturumda yanıtladığı soruyu tekrarlama. Önceki yanıtlar bir alanı kapsam dışı bırakıyorsa o alanı atla.
- Profil taslağında kullanıcının doğruladığı veya düzelttiği değerleri esas al. Bölümü yazmadan önce taslağı özetle ve onay al.

## 4. Yazma kuralları
- Yalnız ilgili alanları yaz, kullanılmayanı sil. Her alan tek satır/kısa madde; uzun açıklama için belgeye link.
- Secret, şifre, token, bağlantı dizesi, özel anahtar ASLA yazma; yalnız dosya yolunu/adını yaz.
- Production'ı agent'ın açıkça kullanabileceği biçimde yaz (Kubernetes: context+namespace; "geçerli context"e güvenme).
- `Hard limits` yalnız ek kısıt koyar; agent'ların commit/push yapmama kuralını gevşetemez, bunu tekrar yazma.
  `release` skill'i yalnız kullanıcı `/release` çağırınca commit+push yapar; profile "onaysız" ifadesi koyma.
- Plugin kancası `guard-infra` canlıyı değiştiren, secret okuyan, migration/dağıtım aracı çalıştıran ve `git push --force`/`reset --hard`/`clean -f`/secret dosyası `git add` komutlarını, ayrıca bir kit agent'ının içinden gelen `git commit`/`push`/`merge`/`rebase`/`tag`/`cherry-pick`/`revert` komutlarını onaya düşürür (ana oturumun commit'i etkilenmez); profilde bu komutlar "onaysız çalıştırılabilir" yazılmaz.
- Hem `AGENTS.md` hem `CLAUDE.md` varsa ve profil `AGENTS.md` içindeyse, `CLAUDE.md`'de `@AGENTS.md` satırı yoksa kullanıcıdan onay al ve yalnız bu satırı ekle;
  aksi halde ana oturum profili görmez. Profil skill'lerdeki sınırları kaldıramaz, yalnız ekler.

## 5. Doğrulama ve teslim
- Yazdığın her yolun repoda var olduğunu, her komutun package.json/Makefile/CI'da geçtiğini kontrol et (çalıştırma).
- Tek müşterili projede Scope mechanisms ve tenant alanlarının yazılmadığını doğrula.
- Raporla: doldurulan alanlar, `BELİRTİLMEMİŞ` kalanlar, kullanıcıdan alınan cevaplar, açık noktalar.
- Commit ve push yapma; yalnız istenirse yap.
````
