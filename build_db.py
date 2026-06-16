# -*- coding: utf-8 -*-
"""
Proje Yönetim Sistemi - Veritabanı kurulum ve örnek veri scripti.
Çalıştırıldığında proje_yonetim.db dosyasını sıfırdan oluşturur ve
gerçekçi, içi dolu örnek verilerle doldurur.
"""
import sqlite3
import hashlib
import os
from datetime import datetime, timedelta

DB = "proje_yonetim.db"

def h(s):
    return hashlib.sha256(s.encode()).hexdigest()

if os.path.exists(DB):
    os.remove(DB)

con = sqlite3.connect(DB)
c = con.cursor()

# ---------------------------------------------------------------- TABLOLAR
c.executescript("""
CREATE TABLE kullanicilar (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kullanici_adi TEXT UNIQUE NOT NULL,
    sifre_hash TEXT NOT NULL,
    ad_soyad TEXT NOT NULL,
    rol TEXT NOT NULL CHECK(rol IN ('Yönetici','Çalışan')),
    unvan TEXT,
    departman TEXT,
    saatlik_ucret REAL DEFAULT 0,
    eposta TEXT,
    avatar TEXT
);

CREATE TABLE projeler (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ad TEXT NOT NULL,
    aciklama TEXT,
    baslangic TEXT,
    bitis TEXT,
    butce REAL DEFAULT 0,
    durum TEXT DEFAULT 'Aktif'
);

CREATE TABLE fazlar (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    proje_id INTEGER,
    ad TEXT NOT NULL,
    baslangic TEXT,
    bitis TEXT,
    sira INTEGER DEFAULT 0,
    FOREIGN KEY(proje_id) REFERENCES projeler(id)
);

CREATE TABLE gorevler (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    proje_id INTEGER,
    faz_id INTEGER,
    baslik TEXT NOT NULL,
    aciklama TEXT,
    durum TEXT NOT NULL DEFAULT 'Yapılacak'
        CHECK(durum IN ('Yapılacak','Devam Ediyor','İncelemede','Tamamlandı')),
    oncelik TEXT DEFAULT 'Orta' CHECK(oncelik IN ('Düşük','Orta','Yüksek','Kritik')),
    atanan_id INTEGER,
    tahmini_saat REAL DEFAULT 0,
    harcanan_saat REAL DEFAULT 0,
    ilerleme INTEGER DEFAULT 0,
    baslangic TEXT,
    bitis TEXT,
    olusturma_tar TEXT NOT NULL,
    FOREIGN KEY(atanan_id) REFERENCES kullanicilar(id),
    FOREIGN KEY(faz_id) REFERENCES fazlar(id)
);

CREATE TABLE butce_kalemleri (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    proje_id INTEGER,
    kategori TEXT NOT NULL,
    aciklama TEXT,
    planlanan REAL DEFAULT 0,
    harcanan REAL DEFAULT 0,
    tarih TEXT
);

CREATE TABLE riskler (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    proje_id INTEGER,
    baslik TEXT NOT NULL,
    aciklama TEXT,
    olasilik INTEGER DEFAULT 3,
    etki INTEGER DEFAULT 3,
    durum TEXT DEFAULT 'Açık' CHECK(durum IN ('Açık','İzleniyor','Kapandı')),
    sahibi_id INTEGER,
    onlem TEXT
);

CREATE TABLE kilometre_taslari (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    proje_id INTEGER,
    ad TEXT NOT NULL,
    tarih TEXT,
    durum TEXT DEFAULT 'Beklemede' CHECK(durum IN ('Beklemede','Tamamlandı','Gecikti')),
    aciklama TEXT
);

CREATE TABLE toplantilar (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    proje_id INTEGER,
    baslik TEXT NOT NULL,
    tarih TEXT,
    notlar TEXT,
    katilimcilar TEXT
);
""")

# ---------------------------------------------------------------- KULLANICILAR
kullanicilar = [
    ("admin","1234","Selenay Tuna","Yönetici","Proje Müdürü","Yönetim",450,"selenay@minddeckcard.com","ST"),
    ("yazilimci1","1234","Ahmet Yıldız","Çalışan","Kıdemli Yazılımcı","Yazılım",350,"ahmet@minddeckcard.com","AY"),
    ("tasarimci1","1234","Ayşe Demir","Çalışan","UI/UX Tasarımcı","Tasarım",300,"ayse@minddeckcard.com","AD"),
    ("analist1","1234","Elif Kaya","Çalışan","İş Analisti","Analiz",280,"elif@minddeckcard.com","EK"),
    ("test1","1234","Burak Şahin","Çalışan","Test Mühendisi","Kalite",260,"burak@minddeckcard.com","BŞ"),
    ("donanim1","1234","Selin Aksoy","Çalışan","Mobil Geliştirici","Yazılım",380,"selin@minddeckcard.com","SA"),
]
for k in kullanicilar:
    c.execute("""INSERT INTO kullanicilar
        (kullanici_adi,sifre_hash,ad_soyad,rol,unvan,departman,saatlik_ucret,eposta,avatar)
        VALUES (?,?,?,?,?,?,?,?,?)""",
        (k[0],h(k[1]),k[2],k[3],k[4],k[5],k[6],k[7],k[8]))

# ---------------------------------------------------------------- PROJE
bugun = datetime.now()
def gun(offset):
    return (bugun + timedelta(days=offset)).strftime("%Y-%m-%d")

c.execute("""INSERT INTO projeler (ad,aciklama,baslangic,bitis,butce,durum)
    VALUES (?,?,?,?,?,?)""",
    ("MindDeckCard – AI Destekli Dil Öğrenme Uygulaması",
     "Yapay zeka destekli İngilizce kelime ve dil öğrenme mobil uygulaması. "
     "Kelime kartları, gramer, dinleme, okuma ve aralıklı tekrar (spaced "
     "repetition) modüllerinin tasarım, geliştirme, test ve lansman süreci.",
     gun(-40), gun(50), 850000, "Aktif"))
proje_id = c.lastrowid

# ---------------------------------------------------------------- FAZLAR
fazlar = [
    ("1. Planlama & Analiz", -40, -25, 1),
    ("2. Tasarım & Prototip", -24, -5, 2),
    ("3. Geliştirme", -4, 25, 3),
    ("4. Test & Lansman", 26, 50, 4),
]
faz_ids = []
for ad,b,bt,s in fazlar:
    c.execute("INSERT INTO fazlar (proje_id,ad,baslangic,bitis,sira) VALUES (?,?,?,?,?)",
              (proje_id,ad,gun(b),gun(bt),s))
    faz_ids.append(c.lastrowid)

# ---------------------------------------------------------------- GÖREVLER
# (faz_idx, baslik, aciklama, durum, oncelik, atanan_id, tahmini, harcanan, ilerleme, b_off, bt_off)
gorevler = [
    (0,"Gereksinim analizi","Hedef kitle ve öğrenme modülleri gereksinim dokümanı.","Tamamlandı","Yüksek",4,40,42,100,-40,-34),
    (0,"Rakip uygulama analizi","Duolingo, Anki, Memrise pazar ve özellik analizi.","Tamamlandı","Orta",4,24,20,100,-38,-30),
    (0,"Proje planı & WBS","İş kırılım yapısı ve zaman çizelgesi oluşturma.","Tamamlandı","Kritik",1,32,30,100,-33,-25),
    (1,"UI/UX tasarımı","Kelime kartı ve ana ekran arayüz tasarımı (Figma).","Tamamlandı","Yüksek",3,60,58,100,-24,-14),
    (1,"Veritabanı şeması","Firebase kelime/kullanıcı/ilerleme şema tasarımı.","Tamamlandı","Kritik",2,80,85,100,-22,-8),
    (1,"Kelime kartı prototipi","Etkileşimli kart ve aralıklı tekrar prototipi.","Devam Ediyor","Yüksek",3,50,32,65,-20,-2),
    (2,"Aralıklı tekrar motoru","Spaced repetition algoritması (SM-2) geliştirme.","Devam Ediyor","Kritik",2,120,70,55,-4,20),
    (2,"AI içerik üretimi","Gemini ile örnek cümle/çeviri üretim entegrasyonu.","Devam Ediyor","Yüksek",2,90,40,40,-2,18),
    (2,"Gramer modülü","Gramer dersleri ve test ekranı geliştirme.","İncelemede","Yüksek",2,70,65,80,0,15),
    (2,"Dinleme modülü","Ses tabanlı dinleme alıştırmaları (Tip1/2/3).","Yapılacak","Orta",2,60,0,0,5,22),
    (2,"Okuma & ödev sistemi","Okuma pasajları ve günlük ödev görevleri.","Yapılacak","Düşük",3,80,0,0,10,25),
    (3,"Performans & hata testleri","Yükleme süresi, çökme ve regresyon testleri.","Yapılacak","Yüksek",5,50,0,0,26,38),
    (3,"Mağaza yayın hazırlığı","App Store / Play Store uyumluluk ve onay süreci.","Yapılacak","Kritik",1,40,0,0,30,45),
    (3,"Beta kullanıcı testleri","Kapalı beta geri bildirim turu.","Yapılacak","Orta",5,36,0,0,35,46),
    (3,"Lansman & pazarlama","Uygulama lansmanı ve tanıtım kampanyası.","Yapılacak","Orta",1,30,0,0,46,50),
]
for f,ba,ac,du,on,at,th,ha,il,bo,bto in gorevler:
    c.execute("""INSERT INTO gorevler
        (proje_id,faz_id,baslik,aciklama,durum,oncelik,atanan_id,tahmini_saat,
         harcanan_saat,ilerleme,baslangic,bitis,olusturma_tar)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (proje_id,faz_ids[f],ba,ac,du,on,at,th,ha,il,gun(bo),gun(bto),
         gun(bo)+" 09:00"))

# ---------------------------------------------------------------- BÜTÇE
butce = [
    ("Personel","Yazılım & tasarım ekibi maaş",300000,182000,gun(-30)),
    ("Sunucu & Altyapı","Firebase, bulut depolama, CDN",120000,72000,gun(-20)),
    ("AI / API","Gemini API ve yapay zeka servisleri",90000,55000,gun(-25)),
    ("Yazılım Lisans","Geliştirme araçları & lisanslar",60000,48000,gun(-25)),
    ("Pazarlama","Lansman, reklam, içerik üretimi",100000,15000,gun(-10)),
    ("Mağaza & Operasyon","App Store/Play ücretleri, ofis",80000,38000,gun(-15)),
]
for kat,ac,pl,ha,t in butce:
    c.execute("""INSERT INTO butce_kalemleri (proje_id,kategori,aciklama,planlanan,harcanan,tarih)
        VALUES (?,?,?,?,?,?)""",(proje_id,kat,ac,pl,ha,t))

# ---------------------------------------------------------------- RİSKLER
riskler = [
    ("AI API maliyet aşımı","Gemini API kullanımı tahminin üzerinde artabilir.",4,4,"İzleniyor",6,"İstek önbellekleme ve token limiti optimizasyonu."),
    ("Mağaza onay reddi","App Store/Play onay sürecinde gecikme riski.",3,5,"Açık",1,"Erken uyumluluk kontrolü ve test yayını."),
    ("Aralıklı tekrar gecikmesi","SM-2 algoritma entegrasyonu beklenenden karmaşık.",3,4,"İzleniyor",2,"Ek geliştirici kaynağı ve sprint planı."),
    ("Bütçe aşımı","Sunucu ve AI maliyetleri tahminin üzerinde.",3,4,"Açık",1,"Haftalık bütçe gözden geçirme toplantısı."),
    ("Anahtar personel kaybı","Kıdemli yazılımcı bağımlılığı yüksek.",2,4,"İzleniyor",1,"Bilgi paylaşımı ve dokümantasyon."),
    ("Tasarım revizyonu","Beta geri bildirimi büyük UI değişikliği isteyebilir.",2,3,"Kapandı",3,"Erken prototip onayı alındı."),
]
for ba,ac,ol,et,du,sa,on in riskler:
    c.execute("""INSERT INTO riskler (proje_id,baslik,aciklama,olasilik,etki,durum,sahibi_id,onlem)
        VALUES (?,?,?,?,?,?,?,?)""",(proje_id,ba,ac,ol,et,du,sa,on))

# ---------------------------------------------------------------- KİLOMETRE TAŞLARI
ktaslari = [
    ("Proje Onayı & Kickoff",-40,"Tamamlandı","Proje resmi başlangıcı."),
    ("Tasarım Onayı (Design Freeze)",-5,"Tamamlandı","UI/UX tasarımı ve veri şeması kilitlendi."),
    ("İlk Çalışan Sürüm (MVP)",12,"Beklemede","Temel kelime kartı modülü ile MVP teslimi."),
    ("Kapalı Beta Yayını",45,"Beklemede","Test kullanıcılarına beta dağıtımı."),
    ("Mağaza Lansmanı",50,"Beklemede","App Store & Play Store resmi çıkış."),
]
for ad,t,du,ac in ktaslari:
    c.execute("""INSERT INTO kilometre_taslari (proje_id,ad,tarih,durum,aciklama)
        VALUES (?,?,?,?,?)""",(proje_id,ad,gun(t),du,ac))

# ---------------------------------------------------------------- TOPLANTILAR
toplantilar = [
    ("Haftalık Sprint Planlama",-7,"Sprint 6 görevleri planlandı. Aralıklı tekrar motoru önceliklendirildi.","Selenay, Ahmet, Ayşe, Selin"),
    ("Bütçe Gözden Geçirme",-5,"Sunucu ve AI giderleri gözden geçirildi, %15 tasarruf hedefi.","Selenay, Selin"),
    ("Tasarım İnceleme",-3,"Kelime kartı UI prototipi onaylandı, küçük revizyonlar istendi.","Selenay, Ayşe, Elif"),
    ("Risk Değerlendirme",-1,"AI API maliyeti ana risk olarak güncellendi.","Selenay, Selin, Ahmet"),
]
for ba,t,no,ka in toplantilar:
    c.execute("""INSERT INTO toplantilar (proje_id,baslik,tarih,notlar,katilimcilar)
        VALUES (?,?,?,?,?)""",(proje_id,ba,gun(t),no,ka))

con.commit()
con.close()
print("Veritabani olusturuldu:", DB)
