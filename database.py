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
        
        # 2. Parametre Tabloları (Yönetici Kütüphanesi - FR-24, 25, 26, 27)
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

        # 3. Deneyler Tablosu (FR-05 - FR-14, IK-04, IK-08, IK-15, IK-16)
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

# --- KULLANICI İŞLEMLERİ ---
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

def onay_bekleyen_kullanicilari_getir():
    with baglanti_al() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, ad, soyad, kullanici_adi FROM kullanicilar WHERE onay_durumu = 0 AND rol != 'yonetici'")
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

# --- YÖNETİCİ KÜTÜPHANESİ İŞLEMLERİ (Soft Delete Destekli - IK-13) ---
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

def kutuphane_veri_sil(tablo, veri_id):
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
        return False, "Deney başlangıç tarihi, bitiş tarihinden önce olmalıdır!"
    
    with baglanti_al() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id FROM deneyler 
            WHERE kullanici_id = ? AND durum = 'Aktif' AND renk = ?
        """, (kullanici_id, renk))
        if cursor.fetchone():
            return False, "Bu renk zaten başka bir aktif deneyinizde kullanılıyor! Lütfen farklı bir renk seçin."

        kimyasallar_str = ", ".join(kimyasallar_listesi)
        cursor.execute("""
            INSERT INTO deneyler (kullanici_id, deney_adi, renk, baslangic_tarihi, bitis_tarihi, hucre_hatti, besiyeri, kimyasallar, durum)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Aktif')
        """, (kullanici_id, deney_adi, renk, str(baslangic), str(bitis), hucre_hatti, besiyeri, kimyasallar_str))
        conn.commit()
        return True, "Deney başarıyla oluşturuldu!"

def aktif_deneyleri_getir(kullanici_id):
    with baglanti_al() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, deney_adi, renk, baslangic_tarihi, bitis_tarihi, hucre_hatti, besiyeri, kimyasallar 
            FROM deneyler 
            WHERE kullanici_id = ? AND durum = 'Aktif'
            ORDER BY id DESC
        """, (kullanici_id,))
        return cursor.fetchall()
