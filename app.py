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

import streamlit as st
import database as db

st.set_page_config(
    page_title="Hücre Kültürü Takip Sistemi",
    page_icon="🔬",
    layout="wide"
)

# Tabloları oluştur
db.tablolari_olustur()

# Oturum yönetimi
if "giris_yapildi" not in st.session_state:
    st.session_state["giris_yapildi"] = False
    st.session_state["aktif_kullanici"] = None

st.title("🔬 Hücre Kültürü Takip Sistemi")

# GİRİŞ YAPILMIŞ EKRAN
if st.session_state["giris_yapildi"]:
    kullanici = st.session_state["aktif_kullanici"]
    st.sidebar.write(f"👤 Aktif Kullanıcı: **{kullanici['ad']} {kullanici['soyad']}**")
    st.sidebar.caption(f"Rol: {kullanici['rol'].capitalize()}")
    
    if st.sidebar.button("Çıkış Yap"):
        st.session_state["giris_yapildi"] = False
        st.session_state["aktif_kullanici"] = None
        st.rerun()

    # Yönetici Ekranı (FR-23)
    if kullanici["rol"] == "yonetici":
        st.header("⚙️ Yönetici Paneli")
        st.subheader("Onay Bekleyen Araştırmacılar")
        
        bekleyenler = db.onay_bekleyen_kullanicilari_getir()
        if not bekleyenler:
            st.info("Onay bekleyen yeni araştırmacı kaydı bulunmamaktadır.")
        else:
            for k_id, ad, soyad, k_adi in bekleyenler:
                col1, col2, col3 = st.columns([3, 2, 2])
                with col1:
                    st.write(f"**{ad} {soyad}** (@{k_adi})")
                with col2:
                    if st.button("Onayla", key=f"onay_{k_id}"):
                        db.kullanici_onayla(k_id)
                        st.success(f"{ad} {soyad} onaylandı!")
                        st.rerun()
                with col3:
                    if st.button("Reddet / Pasife Al", key=f"pasif_{k_id}"):
                        db.kullanici_durum_degistir(k_id, 0)
                        st.warning(f"{ad} {soyad} askıya alındı.")
                        st.rerun()

    # Araştırmacı Ekranı
    else:
        st.header(f"Hoş geldiniz, {kullanici['ad']} {kullanici['soyad']}")
        st.info("Laboratuvar deney yönetimi ve Hücre Takvimi modülleri buraya entegre edilecek.")

# GİRİŞ YAPILMAMIŞ EKRAN
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
