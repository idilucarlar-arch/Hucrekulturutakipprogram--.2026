import streamlit as st
import database as db
from datetime import date, timedelta

st.set_page_config(
    page_title="Hücre Kültürü Takip Sistemi",
    page_icon="🔬",
    layout="wide"
)

# Tabloları hazırla
db.tablolari_olustur()

# Oturum yönetimi
if "giris_yapildi" not in st.session_state:
    st.session_state["giris_yapildi"] = False
    st.session_state["aktif_kullanici"] = None

st.title("🔬 Hücre Kültürü Takip Sistemi")

# GİRİŞ YAPILMIŞ DURUM
if st.session_state["giris_yapildi"]:
    kullanici = st.session_state["aktif_kullanici"]
    st.sidebar.write(f"👤 Aktif Kullanıcı: **{kullanici['ad']} {kullanici['soyad']}**")
    st.sidebar.caption(f"Rol: {kullanici['rol'].capitalize()}")
    
    if st.sidebar.button("Çıkış Yap"):
        st.session_state["giris_yapildi"] = False
        st.session_state["aktif_kullanici"] = None
        st.rerun()

    # --- YÖNETİCİ ARAYÜZÜ (FR-23, FR-24, FR-25, FR-26) ---
    if kullanici["rol"] == "yonetici":
        st.header("⚙️ Yönetici Kontrol Paneli")
        sekme1, sekme2 = st.tabs(["Onay Bekleyenler", "Laboratuvar Kütüphanesi"])

        with sekme1:
            st.subheader("Onay Bekleyen Araştırmacılar")
            bekleyenler = db.onay_bekleyen_kullanicilari_getir()
            if not bekleyenler:
                st.info("Onay bekleyen araştırmacı bulunmamaktadır.")
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
                        if st.button("Reddet", key=f"red_{k_id}"):
                            db.kullanici_durum_degistir(k_id, 0)
                            st.rerun()

        with sekme2:
            st.subheader("Parametre Kütüphanesi Tanımlama")
            tablo_secim = st.selectbox(
                "Yöneteceğiniz Parametreyi Seçin", 
                ["Hücre Hatları", "Besiyerleri", "Kimyasallar"]
            )
            tablo_map = {
                "Hücre Hatları": "hucre_hatlari",
                "Besiyerleri": "besiyerleri",
                "Kimyasallar": "kimyasallar"
            }
            secilen_tablo = tablo_map[tablo_secim]

            yeni_oge = st.text_input(f"Yeni {tablo_secim[:-1]} Adı Girin")
            if st.button(f"{tablo_secim[:-1]} Ekle"):
                if yeni_oge.strip():
                    basari, mesaj = db.kutuphane_veri_ekle(secilen_tablo, yeni_oge.strip())
                    st.success(mesaj)
                    st.rerun()
                else:
                    st.warning("Lütfen bir isim yazın.")

            st.write("---")
            st.write(f"**Mevcut Onaylı {tablo_secim} Listesi:**")
            ogeler = db.kutuphane_listele(secilen_tablo)
            if not ogeler:
                st.info(f"Henüz kayıtlı {tablo_secim.lower()} bulunmamaktadır.")
            else:
                for oge_id, oge_ad in ogeler:
                    c1, c2 = st.columns([5, 1])
                    c1.write(f"• {oge_ad}")
                    if c2.button("Sil", key=f"del_{secilen_tablo}_{oge_id}"):
                        db.kutuphane_veri_sil(secilen_tablo, oge_id)
                        st.rerun()

    # --- ARAŞTIRMACI ARAYÜZÜ (FR-05 - FR-14) ---
    else:
        st.header(f"Hoş geldiniz, {kullanici['ad']} {kullanici['soyad']}")
        menu_arastirmaci = st.sidebar.radio("Menü", ["Aktif Deneylerim", "Yeni Deney Oluştur"])

        if menu_arastirmaci == "Yeni Deney Oluştur":
            st.subheader("🧪 Yeni Laboratuvar Deneyi Başlat")
            
            # Kütüphaneden parametreleri çek
            hucre_listesi = [ad for _, ad in db.kutuphane_listele("hucre_hatlari")]
            besiyeri_listesi = [ad for _, ad in db.kutuphane_listele("besiyerleri")]
            kimyasal_listesi = [ad for _, ad in db.kutuphane_listele("kimyasallar")]

            if not hucre_listesi or not besiyeri_listesi or not kimyasal_listesi:
                st.warning("⚠️ Yönetici henüz kütüphaneye hücre hattı, besiyeri veya kimyasal eklememiş. Deney oluşturabilmek için önce yöneticinin bunları tanımlaması gerekir.")
            else:
                col1, col2 = st.columns(2)
                with col1:
                    deney_adi = st.text_input("Deney Adı (Zorunlu)")
                    renk = st.color_picker("Deney Kimlik Rengi (IK-15)", "#2E86AB")
                    secilen_hucre = st.selectbox("Hücre Hattı Seçin", hucre_listesi)
                with col2:
                    baslangic = st.date_input("Planlanan Başlangıç Tarihi", date.today())
                    bitis = st.date_input("Tahmini Bitiş Tarihi", date.today() + timedelta(days=7))
                    secilen_besiyeri = st.selectbox("Besiyeri Reçetesi Seçin", besiyeri_listesi)

                secilen_kimyasallar = st.multiselect("Kullanılacak Onaylı Solüsyon ve Kimyasallar", kimyasal_listesi)

                if st.button("Deneyi Başlat"):
                    if not deney_adi.strip():
                        st.error("IK-09: Araştırmacı yeni deney oluştururken deneyine isim vermek zorundadır!")
                    elif not secilen_kimyasallar:
                        st.warning("Lütfen en az bir kimyasal / solüsyon seçin.")
                    else:
                        basari, mesaj = db.deney_ekle(
                            kullanici["id"], deney_adi.strip(), renk,
                            baslangic, bitis, secilen_hucre, secilen_besiyeri, secilen_kimyasallar
                        )
                        if basari:
                            st.success(mesaj)
                        else:
                            st.error(mesaj)

        elif menu_arastirmaci == "Aktif Deneylerim":
            st.subheader("📋 Yürütülen Aktif Deneyler (FR-14)")
            deneyler = db.aktif_deneyleri_getir(kullanici["id"])
            
            if not deneyler:
                st.info("Şu anda devam eden aktif bir deneyiniz bulunmamaktadır. Sol menüden 'Yeni Deney Oluştur' diyerek başlayabilirsiniz.")
            else:
                for d_id, ad, renk, bas, bit, hatti, besi, kimya in deneyler:
                    with st.container():
                        st.markdown(
                            f"""
                            <div style="border-left: 6px solid {renk}; padding: 10px 15px; background-color: rgba(255, 255, 255, 0.05); border-radius: 4px; margin-bottom: 12px;">
                                <h4 style="margin: 0; color: {renk};">🔬 {ad}</h4>
                                <p style="margin: 5px 0 0 0; font-size: 0.9em;">
                                    <b>Tarih:</b> {bas} ➔ {bit} | <b>Hücre Hattı:</b> {hatti} | <b>Besiyeri:</b> {besi}
                                </p>
                                <p style="margin: 3px 0 0 0; font-size: 0.85em; opacity: 0.8;">
                                    <b>Kimyasallar:</b> {kimya}
                                </p>
                            </div>
                            """, 
                            unsafe_allow_html=True
                        )

# GİRİŞ YAPILMAMIŞ DURUM
else:
    menu = ["Giriş Yap", "Kayıt Ol"]
    secim = st.sidebar.selectbox("İşlem Seçiniz", menu, key="ana_giris_menusu")

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
