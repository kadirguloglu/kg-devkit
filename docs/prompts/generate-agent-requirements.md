# Prompt: agent gereksinim dokümanı üret

Bir agent koleksiyonunu inceleyip [agent-requirements.md](../agent-requirements.md) benzeri bir doküman üretmek için
aşağıdaki prompt'u Claude Code veya Codex'e ver. Agent eklediğinde/değiştirdiğinde dokümanı güncel tutmak için de kullanılır.

````markdown
Görev: Bu repodaki agent'ları inceleyip her birinin çalışması için gereken şeyleri tek bir Markdown dosyasında topla.
Çıktı dosyası: docs/agent-requirements.md. Dil: Türkçe. Başka dosyaya dokunma.

## 1. Keşif (önce oku, sonra yaz)
- Agent tanım dosyalarını bul (ör. plugins/*/agents/*.md, .claude/agents/*.md, codex/agents/*.toml) ve hepsini baştan sona oku.
  Kaynak ile üretilmiş çıktı varsa (ör. Claude .md → Codex .toml) yalnız kaynağı esas al, üretilmiş olanı elle değiştirme.
- Proje profili şablonunu (ör. docs/project-profile-template.md) ve tasarım notlarını (docs/inventory.md vb.) oku.
- Her agent için şunları çıkar:
  1. Tür, araçlar ve model (`tools:` ve `model:` alanları; salt-okuma mı, dosya yazar mı, Bash kullanır mı, özel araç/eklenti gerekir mi)
  2. Okuduğu proje profili alanları (şablondaki alan adlarıyla eşle)
  3. Projede bulunması gerekenler (dizin, komut, çalışan uygulama, ana oturumun vermesi gereken kanıt vb.)
  4. Profil yoksa veya koşul sağlanmıyorsa davranışı (çıkarım yapar / durur / sorar / özel bir sonuç döner)
  5. Gizli varsayımlar (belirli stack, çok kiracılılık, Kubernetes, belirli tarayıcı, dil/log kalıbı)
  6. Onay ve güvenlik sınırları (hangi işlem açık kullanıcı onayı ister, hangileri yasak; profildeki `Hard limits` okunuyor mu)
- Agent dışındaki koruma katmanlarını da çıkar: plugin kancaları (ör. plugins/*/hooks/hooks.json ve betikleri), izin kuralı örnekleri.
  Hangi istemcide (Claude/Codex) geçerli olduklarını ve agent ayrımı yapıp yapmadıklarını not et.
- Claude kaynağı ile Codex çıktısı arasındaki farkları not et (araç adı, ad öneki, kanca yokluğu, model alanı).
- Bir iddiayı yalnız agent dosyasında (veya kanca/betikte) birebir dayanağı varsa yaz; "yetki şu alandan gelir" gibi çıkarımlar yapma.
- Metinde yazmayan bir şeyi uydurma. Bir bilgiyi dosyada bulamazsan "belirtilmemiş" yaz.

## 2. Doküman yapısı
1. Giriş: 2-3 cümle; alan adlarının hangi şablona ait olduğunu ve profil yoksa genel davranışı söyle.
2. **Özet tablo:** satır = agent; sütunlar = Tür/araçlar | Profil alanları | Projede olması gereken | Profil yoksa/uygulanamazsa.
3. **Ortak kurallar:** tüm agent'lara uyan kurallar (loglama satırları (rapor diline göre), rapor dili, profil önce okunur, alt agent başlatmama,
   reviewer çıktı formatı (+ profilin geçme ifadesi), commit/push yetkisi). Yalnız gerçekten hepsinde geçenleri yaz.
4. **Varsayımlar ve ortama bağlılık** (orkestratör, tarayıcı, çok kiracılılık, model katmanları, kancalar/ikinci kilitler, Claude–Codex farkları): Konu | Hangi agent | Ne varsayıyor | Uymuyorsa ne olur. Her satır için agent
   dosyasından dayanak göster.
5. **Yeni projeye başlarken kontrol listesi:** 4-6 madde, uygulanabilir ve kısa.

## 3. Kurallar
- Tablo hücreleri kısa olsun; uzun açıklamayı tablo dışına al.
- Agent adlarını, alan adlarını ve komutları `kod` biçiminde yaz.
- Aynı bilgiyi iki yerde tekrar etme; ortak olanı "Ortak kurallar"a koy.
- Agent dosyalarıyla çelişen bir şey bulursan dokümanı değil çelişkiyi raporla.

## 4. Doğrulama ve teslim
- Tablodaki agent sayısı, repodaki gerçek agent sayısıyla eşleşmeli; eksik veya fazla varsa düzelt.
- Profil alan adlarının hepsi şablonda gerçekten var mı kontrol et.
- Dokümandaki her satırı agent dosyasıyla karşılaştır: tabloda yazan "okur" alanı agent metninde gerçekten geçiyor mu? Geçmiyorsa satırı düzelt.
- Kancalar için varsa testlerini çalıştır (ör. python3 scripts/test_guard_infra.py).
- Varsa üretim betiğini/CI kontrolünü çalıştır (ör. python3 scripts/build-codex.py --check) ve sonucu bildir.
- README'den yeni dosyaya bir link ekle.
- Sürüm otomatik artıyorsa (ör. bump-version iş akışı) doküman değişikliğinin merge mesajında `[minor]`/`[major]` gerekip gerekmediğini söyle.
- Sonunda şunları söyle: kaç agent incelendi, hangi varsayımlar "belirtilmemiş" kaldı, hangi çelişkiler bulundu.
- Commit ve push yapma; yalnız istenirse yap.
````
