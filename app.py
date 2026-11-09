import streamlit as st
import database as db

st.set_page_config(
    page_title="Hücre Kültürü Takip Sistemi",
    page_icon="🔬",
    layout="wide"
)

# Veritabanı tablolarını ilk açılışta hazırla
db.tablolari_olustur()

# Oturum durumunu (Session State) başlat
if "giris_yapildi" not in st.session_state:
    st.session_state["giris_yapildi"] = False
    st.session_state["aktif_kullanici"] = None

st.title("🔬 Hücre Kültürü Takip Sistemi")

# Giriş Yapılmış Durum
if st.session_state["giris_yapildi"]:
    kullanici = st.session_state["aktif_kullanici"]
    st.sidebar.write(f"👤 Aktif Kullanıcı: **{kullanici['ad']} {kullanici['soyad']}** ({kullanici['rol']})")
    
    if st.sidebar.button("Çıkış Yap"):
        st.session_state["giris_yapildi"] = False
        st.session_state["aktif_kullanici"] = None
        st.rerun()

    st.success(f"Hoş geldiniz, {kullanici['ad']}! Sisteme başarıyla giriş yaptınız.")
    st.info("2. Hafta modülleri: Deney Yönetimi ve Hücre Takvimi bu alana eklenecektir.")

# Giriş Yapılmamış Durum (Kayıt / Giriş Ekranı)
else:
    menu = ["Giriş Yap", "Kayıt Ol"]
    secim = st.sidebar.selectbox("İşlem Seçiniz", menu)

    if secim == "Giriş Yap":
        st.subheader("Kullanıcı Girişi")
        kullanici_adi = st.text_input("Kullanıcı Adı")
        sifre = st.text_input("Şifre", type="password")
        
        if st.button("Giriş Yap"):
            basarili, mesaj, kullanici_bilgi = db.kullanici_giris(kullanici_adi, sifre)
            if basarili:
                st.session_state["giris_yapildi"] = True
                st.session_state["aktif_kullanici"] = kullanici_bilgi
                st.rerun()
            else:
                st.error(mesaj)

    elif secim == "Kayıt Ol":
        st.subheader("Yeni Araştırmacı Kaydı")
        ad = st.text_input("Ad")
        soyad = st.text_input("Soyad")
        yeni_kullanici = st.text_input("Benzersiz Kullanıcı Adı")
        yeni_sifre = st.text_input("Şifre (En az 8 karakter)", type="password")
        
        if st.button("Kayıt Talebi Gönder"):
            if not ad or not soyad or not yeni_kullanici or not yeni_sifre:
                st.warning("Lütfen tüm alanları doldurun.")
            else:
                basarili, mesaj = db.kullanici_kayit(ad, soyad, yeni_kullanici, yeni_sifre)
                if basarili:
                    st.success(mesaj)
                else:
                    st.error(mesaj)

