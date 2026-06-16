# 🧠 MindDeckCard — Proje & Görev Yönetim Sistemi

> Üniversite **Proje Yönetimi** dersi ödevi için geliştirilmiş, uçtan uca çalışan
> bir proje yönetim portalı. Yapay zeka destekli dil öğrenme uygulaması
> **MindDeckCard**'ın geliştirme sürecini örnek senaryo olarak kullanır.

**Teknolojiler:** `Python` · `Streamlit` · `SQLite` · `Plotly` · `Pandas`

---

## 🚀 Hızlı Başlangıç

1. Klasörü bir yere çıkartın.
2. **`calistir.bat`** dosyasına çift tıklayın.
   - Gerekli kütüphaneler otomatik yüklenir.
   - Veritabanı otomatik hazırlanır.
   - Tarayıcıda **http://localhost:8501** adresinde açılır.
3. Aşağıdaki test kullanıcılarından biriyle giriş yapın.

> Tarayıcı kendiliğinden açılmazsa adres çubuğuna `http://localhost:8501` yazın.

---

## 🔑 Test Kullanıcıları

| Rol | Kullanıcı Adı | Şifre | Ad Soyad |
|-----|---------------|-------|----------|
| 👑 Yönetici | `admin` | `1234` | Selenay Tuna |
| 💻 Çalışan | `yazilimci1` | `1234` | Ahmet Yıldız |
| 🎨 Çalışan | `tasarimci1` | `1234` | Ayşe Demir |
| 📊 Çalışan | `analist1` | `1234` | Elif Kaya |
| 🧪 Çalışan | `test1` | `1234` | Burak Şahin |
| 📱 Çalışan | `donanim1` | `1234` | Selin Aksoy |

> **Yönetici** tüm modülleri görür ve düzenleyebilir (görev/bütçe/risk/toplantı ekleme).
> **Çalışan** kendine atanan görevleri görür ve durumlarını günceller.

---

## 📦 Modüller

| Modül | İçerik |
|-------|--------|
| 📊 **Dashboard** | Özet metrik kartları, durum dağılımı, faz ilerlemesi, bütçe karşılaştırması, kilometre taşları |
| 🗂️ **Görev Panosu (Kanban)** | 4 kolonlu (Yapılacak · Devam Ediyor · İncelemede · Tamamlandı) pano + durum güncelleme |
| 📋 **Görev Listesi** | Filtreleme, ilerleme çubukları, yeni görev ekleme |
| 👥 **Ekip Yönetimi** | Ekip üye kartları, iş yükü ve departman dağılımı grafikleri |
| 💰 **Bütçe Takibi** | Planlanan/Harcanan/Kalan analizi, kategori grafikleri, gider ekleme |
| ⚠️ **Risk Kaydı** | İnteraktif risk matrisi (Olasılık × Etki), skorlama, azaltma planları |
| 📅 **Gantt Şeması** | Zaman çizelgesi + "Bugün" çizgisi, faz ilerleme kartları |
| 🗓️ **Toplantılar** | Toplantı notları, kararlar, katılımcılar; yeni kayıt ekleme |
| 📑 **Raporlar** | Proje özet raporu + CSV dışa aktarım (görev/bütçe/risk) |

### ✨ Ek Özellikler
- 🌙 **Koyu Tema (Dark Mode):** Sağ üstteki butonla tüm arayüz ve grafikler anında koyu temaya geçer.
- 🟢 **Canlı veri göstergesi** ve rol bazlı yetkilendirme.
- 📈 Tüm grafikler **Plotly** ile interaktif (zoom, hover, indirme).

---

## 🗂️ Proje Yapısı

```
MindDeckCard/
├── app.py             # Ana uygulama — 9 modül + dark mode
├── build_db.py        # Veritabanı kurulum + gerçekçi örnek veri
├── proje_yonetim.db   # SQLite veritabanı (dolu)
├── calistir.bat       # Windows başlatıcı
└── OKUBENI.txt        # Kısa kullanım notu
```

### Veritabanı Tabloları
`kullanicilar` · `projeler` · `fazlar` · `gorevler` · `butce_kalemleri`
· `riskler` · `kilometre_taslari` · `toplantilar`

---

## 🧩 Örnek Senaryo

Sistem, **MindDeckCard** (AI destekli İngilizce kelime/dil öğrenme uygulaması)
geliştirme projesiyle doldurulmuştur:

- **4 Faz:** Planlama & Analiz → Tasarım & Prototip → Geliştirme → Test & Lansman
- **15 görev**, farklı durum ve önceliklerde
- **6 kişilik ekip** (yazılım, tasarım, analiz, test)
- **6 bütçe kalemi** (₺850.000 toplam bütçe)
- **6 risk** kaydı ve azaltma planı
- **5 kilometre taşı** ve **4 toplantı** kaydı

> Açtığınızda her modül dolu gelir — boş ekran yoktur.

---

## ❓ Sık Sorulanlar

**Python yüklü değil diyor.**
[python.org](https://www.python.org) adresinden Python 3.10+ kurun, kurulumda
*"Add Python to PATH"* kutusunu işaretleyin.

**Veritabanını sıfırlamak istiyorum.**
`proje_yonetim.db` dosyasını silip `calistir.bat`'ı tekrar çalıştırın;
örnek verilerle yeniden oluşturulur.

**Tema seçimi kayıtlı kalıyor mu?**
Oturum boyunca korunur; uygulamayı yeniden başlatınca açık temadan başlar.

---

*MindDeckCard Proje Yönetim Sistemi — Python · Streamlit · SQLite · Plotly · Pandas*
