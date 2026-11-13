import sqlite3
import hashlib

DB_NAME = "hucre_takip.db"

def baglanti_al():
    return sqlite3.connect(DB_NAME)

def sifre_hashle(sifre):
    return hashlib.sha256(sifre.encode("utf-8")).hexdigest()

def tablolari_olustur():
    with baglanti_al() as conn:
        cursor = conn.cursor()
        
        # 1. Kullanıcılar Tablosu
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS kullanicilar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ad TEXT NOT NULL,
                soyad TEXT NOT NULL,
                kullanici_adi TEXT UNIQUE NOT NULL,
                sifre TEXT NOT NULL,
                rol TEXT DEFAULT 'arastirmaci',
                onay_durumu INTEGER DEFAULT 0,
                aktif_mi INTEGER DEFAULT 1
            )
        """)
        
        # 2. Parametre Tabloları (FR-24, 25, 26, 27)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hucre_hatlari (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ad TEXT UNIQUE NOT NULL,
                aktif_mi INTEGER DEFAULT 1
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS besiyerleri (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ad TEXT UNIQUE NOT NULL,
                aktif_mi INTEGER DEFAULT 1
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS kimyasallar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ad TEXT UNIQUE NOT NULL,
                aktif_mi INTEGER DEFAULT 1
            )
        """)

        # 3. Deneyler Tablosu (FR-05 - FR-21, IK-06, IK-07)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS deneyler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kullanici_id INTEGER NOT NULL,
                deney_adi TEXT NOT NULL,
                renk TEXT NOT NULL,
                baslangic_tarihi TEXT NOT NULL,
                bitis_tarihi TEXT NOT NULL,
                hucre_hatti TEXT NOT NULL,
                besiyeri TEXT NOT NULL,
                kimyasallar TEXT NOT NULL,
                durum TEXT DEFAULT 'Aktif',
                notlar TEXT DEFAULT '',
                FOREIGN KEY (kullanici_id) REFERENCES kullanicilar (id)
            )
        """)
        
        try:
            cursor.execute("ALTER TABLE deneyler ADD COLUMN notlar TEXT DEFAULT ''")
        except sqlite3.OperationalError:
            pass

        # 4. Hücre Takvimi Tablosu (FR-19, Sequence 2)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS hucre_takvimi (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                deney_id INTEGER NOT NULL,
                tarih TEXT NOT NULL,
                islem_adi TEXT NOT NULL,
                ikon TEXT DEFAULT '🔴',
                aciklama TEXT,
                aktif_mi INTEGER DEFAULT 1,
                FOREIGN KEY (deney_id) REFERENCES deneyler (id)
            )
        """)

        # 5. Yapılacaklar Listesi Tablosu (FR-20, FR-22, IK-11)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS yapilacaklar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kullanici_id INTEGER NOT NULL,
                deney_id INTEGER,
                gorev TEXT NOT NULL,
                FOREIGN KEY (kullanici_id) REFERENCES kullanicilar (id)
            )
        """)
        
        # Varsayılan Yönetici
        cursor.execute("SELECT * FROM kullanicilar WHERE kullanici_adi = 'admin'")
        if not cursor.fetchone():
            yonetici_sifre = sifre_hashle("admin1234")
            cursor.execute("""
                INSERT INTO kullanicilar (ad, soyad, kullanici_adi, sifre, rol, onay_durumu, aktif_mi)
                VALUES ('Yönetici', 'Sistem', 'admin', ?, 'yonetici', 1, 1)
            """, (yonetici_sifre,))
            
        conn.commit()

# --- KULLANICI & PROFİL İŞLEMLERİ ---
def kullanici_kayit(ad, soyad, kullanici_adi, sifre):
    if len(sifre) < 8:
        return False, "Şifre en az 8 karakter olmalıdır!"
    with baglanti_al() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO kullanicilar (ad, soyad, kullanici_adi, sifre, rol, onay_durumu, aktif_mi)
                VALUES (?, ?, ?, ?, 'arastirmaci', 0, 1)
            """, (ad, soyad, kullanici_adi, sifre_hashle(sifre)))
            conn.commit()
            return True, "Kayıt talebiniz alındı! Yönetici onayından sonra giriş yapabilirsiniz."
        except sqlite3.IntegrityError:
            return False, "Bu kullanıcı adı zaten kullanılmaktadır!"

def kullanici_giris(kullanici_adi, sifre):
    with baglanti_al() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, ad, soyad, kullanici_adi, rol, onay_durumu, aktif_mi 
            FROM kullanicilar 
            WHERE kullanici_adi = ? AND sifre = ?
        """, (kullanici_adi, sifre_hashle(sifre)))
        kullanici = cursor.fetchone()
        
        if not kullanici:
            return False, "Kullanıcı adı veya şifre hatalı!", None
        if kullanici[5] == 0:
            return False, "Hesabınız henüz yönetici tarafından onaylanmamıştır.", None
        if kullanici[6] == 0:
            return False, "Hesabınız askıya alınmıştır.", None
            
        return True, "Giriş başarılı!", {
            "id": kullanici[0], "ad": kullanici[1], "soyad": kullanici[2],
            "kullanici_adi": kullanici[3], "rol": kullanici[4]
        }

def profil_guncelle(kullanici_id, yeni_ad, yeni_soyad, yeni_sifre=None):
    # FR-03, FR-04: Profil bilgilerini güncelleme
    with baglanti_al() as conn:
        cursor = conn.cursor()
        if yeni_sifre:
            if len(yeni_sifre) < 8:
                return False, "Yeni şifre en az 8 karakter olmalıdır! (IK-02)"
            cursor.execute("""
                UPDATE kullanicilar SET ad = ?, soyad = ?, sifre = ? WHERE id = ?
            """, (yeni_ad, yeni_soyad, sifre_hashle(yeni_sifre), kullanici_id))
        else:
            cursor.execute("""
                UPDATE kullanicilar SET ad = ?, soyad = ? WHERE id = ?
            """, (yeni_ad, yeni_soyad, kullanici_id))
        conn.commit()
        return True, "Profil bilgileriniz başarıyla güncellendi!"

def onay_bekleyen_kullanicilari_getir():
    with baglanti_al() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, ad, soyad, kullanici_adi FROM kullanicilar WHERE onay_durumu = 0 AND rol != 'yonetici'")
        return cursor.fetchall()

def tum_arastirmacilari_getir():
    with baglanti_al() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, ad, soyad, kullanici_adi, onay_durumu, aktif_mi FROM kullanicilar WHERE rol != 'yonetici'")
        return cursor.fetchall()

def kullanici_onayla(kullanici_id):
    with baglanti_al() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE kullanicilar SET onay_durumu = 1 WHERE id = ?", (kullanici_id,))
        conn.commit()

def kullanici_durum_degistir(kullanici_id, aktif_mi):
    with baglanti_al() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE kullanicilar SET aktif_mi = ? WHERE id = ?", (aktif_mi, kullanici_id))
        conn.commit()

# --- YÖNETİCİ KÜTÜPHANESİ İŞLEMLERİ (FR-24, 25, 26, 27, IK-13) ---
def kutuphane_veri_ekle(tablo, ad):
    with baglanti_al() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(f"INSERT INTO {tablo} (ad, aktif_mi) VALUES (?, 1)", (ad,))
            conn.commit()
            return True, f"'{ad}' başarıyla eklendi."
        except sqlite3.IntegrityError:
            cursor.execute(f"UPDATE {tablo} SET aktif_mi = 1 WHERE ad = ?", (ad,))
            conn.commit()
            return True, f"'{ad}' tekrar aktifleştirildi."

def kutuphane_veri_guncelle(tablo, veri_id, yeni_ad):
    with baglanti_al() as conn:
        cursor = conn.cursor()
        cursor.execute(f"UPDATE {tablo} SET ad = ? WHERE id = ?", (yeni_ad, veri_id))
        conn.commit()

def kutuphane_veri_sil(tablo, veri_id):
    # IK-13: Kalıcı silme yapılmaz, arşivlenir
    with baglanti_al() as conn:
        cursor = conn.cursor()
        cursor.execute(f"UPDATE {tablo} SET aktif_mi = 0 WHERE id = ?", (veri_id,))
        conn.commit()

def kutuphane_listele(tablo):
    with baglanti_al() as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT id, ad FROM {tablo} WHERE aktif_mi = 1 ORDER BY ad ASC")
        return cursor.fetchall()

# --- DENEY YÖNETİMİ İŞLEMLERİ ---
def deney_ekle(kullanici_id, deney_adi, renk, baslangic, bitis, hucre_hatti, besiyeri, kimyasallar_listesi):
    if baslangic >= bitis:
        return False, "Deney başlangıç tarihi, bitiş tarihinden önce olmalıdır! (IK-04)"
    
    with baglanti_al() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id FROM deneyler 
            WHERE kullanici_id = ? AND durum = 'Aktif' AND renk = ?
        """, (kullanici_id, renk))
        if cursor.fetchone():
            return False, "Bu renk zaten başka bir aktif deneyinizde kullanılıyor! Lütfen farklı bir renk seçin. (IK-15)"

        kimyasallar_str = ", ".join(kimyasallar_listesi)
        cursor.execute("""
            INSERT INTO deneyler (kullanici_id, deney_adi, renk, baslangic_tarihi, bitis_tarihi, hucre_hatti, besiyeri, kimyasallar, durum, notlar)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Aktif', '')
        """, (kullanici_id, deney_adi, renk, str(baslangic), str(bitis), hucre_hatti, besiyeri, kimyasallar_str))
        conn.commit()
        return True, "Deney başarıyla oluşturuldu!"

def deney_tarih_guncelle(deney_id, yeni_baslangic, yeni_bitis):
    # FR-08, IK-04: Tarih düzenleme
    if yeni_baslangic >= yeni_bitis:
        return False, "Başlangıç tarihi bitiş tarihinden önce olmalıdır! (IK-04)"
    with baglanti_al() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE deneyler SET baslangic_tarihi = ?, bitis_tarihi = ? WHERE id = ?
        """, (str(yeni_baslangic), str(yeni_bitis), deney_id))
        conn.commit()
        return True, "Deney tarihleri güncellendi!"

def aktif_deneyleri_getir(kullanici_id):
    with baglanti_al() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, deney_adi, renk, baslangic_tarihi, bitis_tarihi, hucre_hatti, besiyeri, kimyasallar, notlar 
            FROM deneyler 
            WHERE kullanici_id = ? AND durum = 'Aktif'
            ORDER BY id DESC
        """, (kullanici_id,))
        return cursor.fetchall()

def deney_son_islem_getir(deney_id):
    # FR-14: Aktif deneylerde yapılan en son işlemi getirme
    with baglanti_al() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT tarih, islem_adi, ikon, aciklama 
            FROM hucre_takvimi 
            WHERE deney_id = ? AND aktif_mi = 1 
            ORDER BY tarih DESC, id DESC LIMIT 1
        """, (deney_id,))
        return cursor.fetchone()

def gecmis_deneyleri_getir(kullanici_id, arama_metni=""):
    # FR-15, FR-16, IK-05, IK-16: Geçmiş deneyleri listeleme ve deney adıyla arama
    with baglanti_al() as conn:
        cursor = conn.cursor()
        if arama_metni.strip():
            cursor.execute("""
                SELECT id, deney_adi, renk, baslangic_tarihi, bitis_tarihi, hucre_hatti, besiyeri, kimyasallar, durum, notlar 
                FROM deneyler 
                WHERE kullanici_id = ? AND durum != 'Aktif' AND deney_adi LIKE ?
                ORDER BY id DESC
            """, (kullanici_id, f"%{arama_metni.strip()}%"))
        else:
            cursor.execute("""
                SELECT id, deney_adi, renk, baslangic_tarihi, bitis_tarihi, hucre_hatti, besiyeri, kimyasallar, durum, notlar 
                FROM deney
