import streamlit as st

# Sayfa Yapılandırması
st.set_page_config(
    page_title="Hücre Kültürü Takip Sistemi",
        page_icon="🔬",
            layout="wide"
            )

            st.title("🔬 Hücre Kültürü Takip Sistemi")
     ⁴       st.write("Sisteme hoş geldiniz! Giriş veya Kayıt sekmesini seçerek devam edin.")

            # Giriş / Kayıt Menüsü
            menu = ["Giriş Yap", "Kayıt Ol"]
            secim = st.sidebar.selectbox("İşlem Seçiniz", menu)

            if secim == "Giriş Yap":
                st.subheader("Kullanıcı Girişi")
                    kullanici_adi = st.text_input("Kullanıcı Adı")
                        sifre = st.text_input("Şifre", type="password")
                            if st.button("Giriş Yap"):
                                    st.info("Giriş kontrolü backend bağlantısı sonrası aktifleşecek.")

                                    elif secim == "Kayıt Ol":
                                        st.subheader("Yeni Araştırmacı Kaydı")
                                            ad = st.text_input("Ad")
                                                soyad = st.text_input("Soyad")
                                                    yeni_kullanici = st.text_input("Benzersiz Kullanıcı Adı")
                                                        yeni_sifre = st.text_input("Şifre (En az 8 karakter)", type="password")
                                                            if st.button("Kayıt Talebi Gönder"):
                                                                    if len(yeni_sifre) < 8:
                                                                                st.error("Şifre en az 8 karakter olmalıdır!")
                                                                                        else:
                                                                                                    st.success("Kaydınız alındı! Yönetici onayından sonra giriş yapabilirsiniz.")
