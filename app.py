import streamlit as st
import database as db
from datetime import date, datetime, timedelta

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
if "secili_deney_id" not in st.session_state:
    st.session_state["secili_deney_id"] = None
if "aktif_menu" not in st.session_state:
    st.session_state["aktif_menu"] = "Aktif Deneylerim"

st.title("🔬 Hücre Kültürü Takip Sistemi")

# GİRİŞ YAPILMIŞ DURUM
if st.session_state["giris_yapildi"]:
    kullanici = st.session_state["aktif_kullanici"]
    st.sidebar.write(f"👤 **{kullanici['ad']} {kullanici['soyad']}**")
    st.sidebar.caption(f"Kullanıcı Adı: @{kullanici['kullanici_adi']} | Rol: {kullanici['rol'].capitalize()}")
    
    if st.sidebar.button("Çıkış Yap"):
        st.session_state["giris_yapildi"] = False
        st.session_state["aktif_kullanici"] = None
        st.session_state["secili_deney_id"] = None
        st.rerun()

    # --- YÖNETİCİ ARAYÜZÜ (FR-23, 24, 25, 26, 27) ---
    if kullanici["rol"] == "yonetici":
        st.header("⚙️ Yönetici Kontrol Paneli")
        sekme1, sekme2, sekme3 = st.tabs([
            "Onay Bekleyenler", 
            "Tüm Araştırmacı Hesapları", 
            "Laboratuvar Kütüphanesi"
        ])

        with sekme1:
            st.subheader("Onay Bekleyen Araştırmacılar (FR-23, IK-03)")
            bekleyenler = db.onay_bekleyen_kullanicilari_getir()
            if not bekleyenler:
                st.info("Onay bekleyen yeni araştırmacı bulunmamaktadır.")
            else:
                for k_id, ad, soyad, k_adi in bekleyenler:
                    col1, col2, col3 = st.columns([3, 2, 2])
                    col1.write(f"**{ad} {soyad}** (@{k_adi})")
                    if col2.button("Onayla", key=f"onay_{k_id}"):
                        db.kullanici_onayla(k_id)
                        st.success(f"{ad} {soyad} onaylandı!")
                        st.rerun()
                    if col3.button("Pasife Al", key=f"red_{k_id}"):
                        db.kullanici_durum_degistir(k_id, 0)
                        st.rerun()

        with sekme2:
            st.subheader("Kayıtlı Araştırmacı Hesap Yönetimi (FR-23)")
            tum_kullanicilar = db.tum_arastirmacilari_getir()
            if not tum_kullanicilar:
                st.info("Henüz kayıtlı araştırmacı bulunmuyor.")
            else:
                for k_id, ad, soyad, k_adi, onay, aktif in tum_kullanicilar:
                    c1, c2, c3 = st.columns([4, 2, 2])
                    durum_etiket = "🟢 Aktif" if aktif == 1 else "🔴 Pasif"
                    onay_etiket = "Onaylı" if onay == 1 else "Onay Bekliyor"
                    c1.write(f"**{ad} {soyad}** (@{k_adi}) — {onay_etiket} | {durum_etiket}")
                    if aktif == 1:
                        if c2.button("Hesabı Pasife Al", key=f"pasif_{k_id}"):
                            db.kullanici_durum_degistir(k_id, 0)
                            st.rerun()
                    else:
                        if c2.button("Hesabı Aktifleştir", key=f"aktif_{k_id}"):
                            db.kullanici_durum_degistir(k_id, 1)
                            st.rerun()

        with sekme3:
            st.subheader("Parametre Kütüphanesi (FR-24, FR-25, FR-26, IK-12, IK-13)")
            tablo_secim = st.selectbox(
                "Yöneteceğiniz Kütüphaneyi Seçin", 
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
                    c1, c2, c3 = st.columns([3, 2, 1])
                    yeni_isim = c1.text_input("Düzenle", value=oge_ad, key=f"edit_{secilen_tablo}_{oge_id}", label_visibility="collapsed")
                    if c2.button("Güncelle", key=f"upd_{secilen_tablo}_{oge_id}"):
                        if yeni_isim.strip():
                            db.kutuphane_veri_guncelle(secilen_tablo, oge_id, yeni_isim.strip())
                            st.success("Güncellendi!")
                            st.rerun()
                    if c3.button("Arşivle/Sil", key=f"del_{secilen_tablo}_{oge_id}"):
                        db.kutuphane_veri_sil(secilen_tablo, oge_id)
                        st.rerun()

    # --- ARAŞTIRMACI ARAYÜZÜ ---
    else:
        menu_secenekleri = [
            "Aktif Deneylerim", 
            "Yeni Deney Oluştur", 
            "Genel Takvim", 
            "Geçmiş Deneylerim (Arşiv)", 
            "Yapılacaklar Listesi", 
            "Profilim"
        ]
        menu_arastirmaci = st.sidebar.radio("Menü", menu_secenekleri)

        if menu_arastirmaci != "Aktif Deneylerim":
            st.session_state["secili_deney_id"] = None

        # 1. YENİ DENEY OLUŞTUR (FR-05 - FR-12)
        if menu_arastirmaci == "Yeni Deney Oluştur":
            st.subheader("🧪 Yeni Laboratuvar Deneyi Başlat")
            
            hucre_listesi = [ad for _, ad in db.kutuphane_listele("hucre_hatlari")]
            besiyeri_listesi = [ad for _, ad in db.kutuphane_listele("besiyerleri")]
            kimyasal_listesi = [ad for _, ad in db.kutuphane_listele("kimyasallar")]

            if not hucre_listesi or not besiyeri_listesi or not kimyasal_listesi:
                st.warning("⚠️ Yönetici henüz kütüphaneye hücre hattı, besiyeri veya kimyasal eklememiş.")
            else:
                col1, col2 = st.columns(2)
                with col1:
                    deney_adi = st.text_input("Deney Adı (Zorunlu - IK-09)")
                    renk = st.color_picker("Deney Kimlik Rengi (IK-15)", "#2E86AB")
                    secilen_hucre = st.selectbox("Hücre Hattı Seçin (FR-09)", hucre_listesi)
                with col2:
                    baslangic = st.date_input("Planlanan Başlangıç Tarihi", date.today())
                    bitis = st.date_input("Tahmini Bitiş Tarihi", date.today() + timedelta(days=7))
                    secilen_besiyeri = st.selectbox("Besiyeri Reçetesi Seçin (FR-10)", besiyeri_listesi)

                secilen_kimyasallar = st.multiselect("Kullanılacak Onaylı Solüsyon ve Kimyasallar (FR-11)", kimyasal_listesi)

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

        # 2. AKTİF DENEYLERİM VE DENEY DETAY EKRANI (FR-14, FR-17, FR-18, FR-19, FR-21)
        elif menu_arastirmaci == "Aktif Deneylerim":
            if st.session_state["secili_deney_id"] is not None:
                deney = db.deney_detay_getir(st.session_state["secili_deney_id"], kullanici["id"])
                if not deney:
                    st.session_state["secili_deney_id"] = None
                    st.rerun()
                else:
                    d_id, ad, renk, bas, bit, hatti, besi, kimya, durum, mevcut_not = deney
                    
                    if st.button("⬅️ Aktif Deneyler Listesine Dön"):
                        st.session_state["secili_deney_id"] = None
                        st.rerun()

                    st.markdown(f"<h2 style='color:{renk};'>🔬 {ad}</h2>", unsafe_allow_html=True)
                    
                    tab_bilgi, tab_takvim, tab_notlar, tab_gorev = st.tabs([
                        "📄 Deney Bilgileri", 
                        "📅 Hücre Takvimi", 
                        "📝 Deney Notları", 
                        "✅ Deney Görevleri"
                    ])

                    # SEKME 1: Deney Genel Bilgileri, Tarih Düzenleme & Sonlandırma
                    with tab_bilgi:
                        st.subheader("Deney Genel Bilgileri")
                        c1, c2 = st.columns(2)
                        with c1:
                            st.write(f"**Hücre Hattı:** {hatti}")
                            st.write(f"**Besiyeri:** {besi}")
                            st.write(f"**Kimyasallar:** {kimya}")
                            st.write(f"**Durum:** {durum}")
                        with c2:
                            st.write("**Tarihleri Düzenle (FR-08, IK-04):**")
                            mevcut_bas = datetime.strptime(bas, "%Y-%m-%d").date()
                            mevcut_bit = datetime.strptime(bit, "%Y-%m-%d").date()
                            yeni_bas = st.date_input("Başlangıç Tarihi", mevcut_bas, key="upd_bas")
                            yeni_bit = st.date_input("Tahmini Bitiş Tarihi", mevcut_bit, key="upd_bit")
                            if st.button("Tarihleri Güncelle"):
                                basari, mesaj = db.deney_tarih_guncelle(d_id, yeni_bas, yeni_bit)
                                if basari:
                                    st.success(mesaj)
                                    st.rerun()
                                else:
                                    st.error(mesaj)

                        st.write("---")
                        st.subheader("🏁 Deneyi Sonlandır (FR-13, IK-16)")
                        sonuc_secim = st.radio(
                            "Deney Sonucu Seçin:", 
                            ["Başarıyla Tamamlandı", "Başarısız"], 
                            horizontal=True
                        )
                        if st.button("Deneyi Sonlandır ve Arşive Gönder"):
                            db.deney_sonlandir(d_id, sonuc_secim)
                            st.success(f"Deney '{sonuc_secim}' olarak sonlandırıldı ve geçmiş deneyler arşivine taşındı!")
                            st.session_state["secili_deney_id"] = None
                            st.rerun()

                    # SEKME 2: Hücre Takvimi (FR-19, Sequence 2)
                    with tab_takvim:
                        st.subheader("📅 Özel Hücre Takvimi İşlemleri")
                        with st.expander("➕ Takvime Yeni Laboratuvar İşlemi Ekle", expanded=True):
                            t_col1, t_col2, t_col3 = st.columns([2, 2, 1])
                            with t_col1:
                                islem_tarihi = st.date_input("İşlem Günü Seçin", date.today(), key="takvim_gun")
                            with t_col2:
                                islem_turu = st.selectbox(
                                    "İşlem Türü", 
                                    ["Hücre Çözdürme", "Besiyeri Değişimi", "Pasajlama", "İnkübasyon Kontrolü", "Hücre Sayımı", "Diğer"]
                                )
                            with t_col3:
                                ikon_secim = st.selectbox(
                                    "İkon Seç", 
                                    ["Boş Bırak (Otomatik 🔴)", "🟢", "🔵", "🟡", "🟣", "🧪", "🔬"]
                                )
                            
                            islem_aciklama = st.text_input("İşlem Notu / Açıklama")
                            if st.button("Takvime Kaydet"):
                                kaydedilecek_ikon = "🔴" if "Boş Bırak" in ikon_secim else ikon_secim
                                db.takvim_islem_ekle(d_id, islem_tarihi, islem_turu, kaydedilecek_ikon, islem_aciklama)
                                st.success("İşlem hücre takvimine kaydedildi!")
                                st.rerun()

                        st.write("### Kayıtlı Takvim Adımları")
                        takvim_kayitlari = db.takvim_islemleri_getir(d_id)
                        if not takvim_kayitlari:
                            st.info("Bu deneye ait hücre takviminde henüz kayıtlı bir işlem bulunmuyor.")
                        else:
                            for t_id, t_tarih, t_islem, t_ikon, t_aciklama in takvim_kayitlari:
                                tk1, tk2 = st.columns([6, 1])
                                tk1.markdown(f"**{t_ikon} {t_tarih}** — **{t_islem}**: {t_aciklama}")
                                if tk2.button("Sil", key=f"tsil_{t_id}"):
                                    db.takvim_islem_sil(t_id)
                                    st.rerun()

                    # SEKME 3: Deney Notları (FR-21, IK-06, IK-07)
                    with tab_notlar:
                        st.subheader("📝 Deney Bulguları ve Notlar (Maks. 5000 Karakter)")
                        yeni_not_icerik = st.text_area(
                            "Elde edilen bulguları, analiz verilerini ve sonuçları buraya işleyin (IK-06):",
                            value=mevcut_not if mevcut_not else "",
                            height=250,
                            max_chars=5000
                        )
                        st.caption(f"Karakter Sayısı: {len(yeni_not_icerik)} / 5000")
                        if st.button("Notları Kaydet"):
                            basari, mesaj = db.deney_notu_guncelle(d_id, yeni_not_icerik)
                            if basari:
                                st.success(mesaj)
                                st.rerun()
                            else:
                                st.error(mesaj)

                    # SEKME 4: Deneye Özel Yapılacaklar (FR-20, FR-22, IK-11)
                    with tab_gorev:
                        st.subheader("✅ Deney Yapılacaklar Listesi")
                        yeni_gorev = st.text_input("Yeni Görev Yazın", key="deney_gorev_input")
                        if st.button("Ekle", key="deney_gorev_ekle_btn"):
                            if yeni_gorev.strip():
                                db.gorev_ekle(kullanici["id"], d_id, yeni_gorev.strip())
                                st.success("Görev eklendi!")
                                st.rerun()

                        gorevler = db.gorevleri_getir(kullanici["id"], d_id)
                        if not gorevler:
                            st.info("Bu deney için bekleyen görev bulunmamaktadır.")
                        else:
                            st.write("Görevi tamamladığınızda kutucuğu işaretleyin (IK-11 uyarınca otomatik silinir):")
                            for g_id, g_metin in gorevler:
                                if st.checkbox(g_metin, key=f"dgorev_{g_id}"):
                                    db.gorev_tamamla_ve_sil(g_id)
                                    st.rerun()

            # Aktif Deneyler Listesi (FR-14: Son yapılan işlemle birlikte)
            else:
                st.subheader("📋 Yürütülen Aktif Deneyler (FR-14)")
                deneyler = db.aktif_deneyleri_getir(kullanici["id"])
                
                if not deneyler:
                    st.info("Şu anda devam eden aktif bir deneyiniz bulunmamaktadır. Sol menüden 'Yeni Deney Oluştur' diyerek başlayabilirsiniz.")
                else:
                    for d_id, ad, renk, bas, bit, hatti, besi, kimya, _ in deneyler:
                        son_islem = db.deney_son_islem_getir(d_id)
                        son_islem_metni = f"{son_islem[2]} {son_islem[0]} - {son_islem[1]} ({son_islem[3]})" if son_islem else "Henüz işlem kaydedilmedi."
                        
                        col_kart, col_btn = st.columns([5, 1])
                        with col_kart:
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
                                    <p style="margin: 5px 0 0 0; font-size: 0.85em; color: #a8dadc;">
                                        <b>En Son İşlem:</b> {son_islem_metni}
                                    </p>
                                </div>
                                """, 
                                unsafe_allow_html=True
                            )
                        with col_btn:
                            st.write("")
                            st.write("")
                            if st.button("Detay / Aç", key=f"detay_{d_id}"):
                                st.session_state["secili_deney_id"] = d_id
                                st.rerun()

        # 3. GENEL TAKVİM (IK-14 ve Sınıf Diyagramı)
        elif menu_arastirmaci == "Genel Takvim":
            st.subheader("🗓️ Genel Laboratuvar Takvimi (IK-14)")
            st.caption("Aktif olan tüm deneylerinizdeki önemli tarihler ve adımlar burada deney renkleriyle topluca görüntülenir. Detaylı bilgi girişi için ilgili deneyin kendi Hücre Takvimine gidiniz.")
            
            aktif_deneyler = db.aktif_deneyleri_getir(kullanici["id"])
            if aktif_deneyler:
                st.write("**Aktif Deney Renk Anahtarı:**")
                cols = st.columns(min(len(aktif_deneyler), 4))
                for idx, (d_id, ad, renk, bas, bit, _, _, _, _) in enumerate(aktif_deneyler):
                    with cols[idx % 4]:
                        st.markdown(f"<span style='color:{renk}; font-weight:bold;'>⬤ {ad}</span><br><small>{bas} ➔ {bit}</small>", unsafe_allow_html=True)

            st.write("---")
            olaylar = db.genel_takvim_olaylarini_getir(kullanici["id"])
            if not olaylar:
                st.info("Aktif deneylerinize ait takvimlerde henüz işaretlenmiş bir adım bulunmamaktadır.")
            else:
                for tarih, d_adi, d_renk, islem_adi, ikon, d_id in olaylar:
                    st.markdown(
                        f"""
                        <div style="border-left: 5px solid {d_renk}; padding: 8px 12px; margin-bottom: 8px; background-color: rgba(255,255,255,0.03);">
                            <b>{tarih}</b> | <span style="color:{d_renk}; font-weight:bold;">{d_adi}</span> — {ikon} {islem_adi}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

        # 4. GEÇMİŞ DENEYLERİM / ARŞİV VE ARAMA (FR-15, FR-16, IK-05, IK-16)
        elif menu_arastirmaci == "Geç
