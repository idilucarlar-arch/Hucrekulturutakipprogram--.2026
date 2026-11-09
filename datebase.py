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
        
        # Kullanıcılar Tablosu (IK-01, IK-02, IK-03, FR-23)
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
        
        # Varsayılan Yönetici Hesabı (Sistem ilk açıldığında giriş yapabilmek için)
        cursor.execute("SELECT * FROM kullanicilar WHERE kullanici_adi = 'admin'")
        if not cursor.fetchone():
            yonetici_sifre = sifre_hashle("admin1234")
            cursor.execute("""
                INSERT INTO kullanicilar (ad, soyad, kullanici_adi, sifre, rol, onay_durumu, aktif_mi)
                VALUES ('Yönetici', 'Sistem', 'admin', ?, 'yonetici', 1, 1)
            """, (yonetici_sifre,))
            
        conn.commit()

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
        
        # IK-03: Yönetici onayı kontrolü
        if kullanici[5] == 0:
            return False, "Hesabınız henüz yönetici tarafından onaylanmamıştır.", None
            
        if kullanici[6] == 0:
            return False, "Hesabınız askıya alınmıştır. Lütfen yöneticiyle iletişime geçin.", None
            
        kullanici_bilgi = {
            "id": kullanici[0],
            "ad": kullanici[1],
            "soyad": kullanici[2],
            "kullanici_adi": kullanici[3],
            "rol": kullanici[4]
        }
        return True, "Giriş başarılı!", kullanici_bilgi
