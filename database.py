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
        
        # Eski veritabanında notlar sütunu yoksa otomatik ekle
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

        # 5. Yapılacaklar Listesi Tablosu (FR-20, FR-22
