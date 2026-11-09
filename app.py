import streamlit as st
import database as db
from datetime import date, timedelta

# Sayfa yapılandırması
st.set_page_config(
    page_title="Hücre Kültürü Takip Sistemi",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Minimalist, tweek.so esintili monokrom CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #1A1A1A;
    }
    
    /* Arka plan - temiz kağıt tonu */
    .stApp {
        background-color: #FAFAFA;
    }

    /* Kenar çubuğu sadeleştirme */
    section[data-testid="stSidebar"] {
        background-color: #F4F4F5;
        border-right: 1px solid #E4E4E7;
    }

    /* Başlıklar */
    h1, h2, h3, h4 {
        font-weight: 600 !important;
        letter-spacing: -0.02em !important;
        color: #111827 !important;
    }

    /* Butonlar: Minimal, mat ve keskin */
    .stButton > button {
        background-color: #18181B;
        color: #FFFFFF;
        border: 1px solid #18181B;
        border-radius: 6px;
        font-weight: 500;
        font-size: 0.875rem;
        padding: 6px 14px;
        transition: all 0.15s ease;
    }
    .stButton > button:hover {
        background-color: #27272A;
        border-color: #27272A;
        color: #FFFFFF;
    }
    .stButton > button:active {
        background-color: #09090B;
    }

    /* İkincil / Silme Butonları */
    div[data-testid="stHorizontalBlock"] .stButton > button {
        border-radius: 4px;
    }

    /* Form ve girdi alanları */
    input, select, textarea {
        border-radius: 6px !important;
        border: 1px solid #E4E4E7 !important;
        background-color: #FFFFFF !important;
        color: #18181B !important;
    }
    input:focus {
        border-color: #71717A !important;
        box-shadow: none !important;
    }

    /* Sekmeler (Tabs) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 16px;
        border-bottom: 1px solid #E4E4E7;
    }
    .stTabs [data-baseweb="tab"] {
        font-size: 0.9rem;
        font-weight: 500;
        color: #71717A;
        padding: 8px 4px;
    }
    .stTabs [aria-selected="true"] {
        color: #18181B !important;
        border-bottom-color: #18181B !important;
    }

    /* Minimal Kart Tasarımı */
    .experiment-card {
        background-color: #FFFFFF;
        border: 1px solid #E4E4E7;
        border-radius: 6px;
        padding: 16px 20px;
        margin-bottom: 12px;
        position: relative;
    }
    .experiment-card .title {
        font-size: 1rem;
        font-weight: 600;
        color: #18181B;
        margin-bottom: 6px;
    }
    .experiment-card .meta {
        font-size: 0.825rem;
        color: #52525B;
        line-height: 1.5;
    }
    .experiment-card .tag {
        font-size: 0.75rem;
        color: #71717A;
        margin-top: 6px;
    }
    </style>
""", unsafe_allow_html=True)

# Tabloları hazırla
db.tablolari_olustur()

# Oturum yönetimi
if "giris_yapildi" not in st.session_state:
    st.session_state["giris_yapildi"] = False
    st.session_state["aktif_kullanici"] = None

# Ana Başlık
st.markdown("<h2 style='margin-bottom: 2rem; font-weight: 600;'>Hücre Kültürü Takip Sistemi</h2>", unsafe_allow_html=True)

# -------------------------------------------------------------
# 1. GİRİŞ YAPILMIŞ DURUM
# -------------------------------------------------------------
if st.session_state["giris_yapildi"]:
    kullanici = st.session_state["aktif_kullanici"]
    
    # Kenar Çubuğu
    st.sidebar.markdown(f"**{kullanici['ad']} {kullanici['soyad']}**")
    st.sidebar.caption(f"Yetki Düzeyi: {kullanici['rol'].capitalize()}")
    st.sidebar.markdown("---")
    
    if st.sidebar.button("Oturumu Kapat", use_container_width=True):
        st.session_state["giris_yapildi"] = False
        st.session_state["aktif_kullanici"] = None
        st.rerun()

    # --- YÖNETİCİ ARAYÜZÜ ---
    if kullanici["rol"] == "yonetici":
        st.markdown("### Yönetim Paneli")
        sekme1, sekme2 = st.tabs(["Onay Bekleyenler", "Kütüphane Parametreleri"])

        with sekme1:
            bekleyenler = db.onay_bekleyen_kullanicilari_getir()
            if not bekleyenler:
                st.caption("Onay bekleyen araştırmacı bulunmuyor.")
            else:
                for k_id, ad, soyad, k_adi in bekleyenler:
                    col1, col2, col3 = st.columns([4, 1.2, 1.2])
                    with col1:
                        st.markdown(f"**{ad} {soyad}** `@{k_adi}`")
                    with col2:
                        if st.button("Onayla", key=f"onay_{k_id}", use_container_width=True):
                            db.kullanici_onayla(k_id)
                            st.rerun()
                    with col3:
                        if st.button("Reddet", key=f"red_{k_id}", use_container_width=True):
                            db.kullanici_durum_degistir(k_id, 0)
                            st.rerun()
                    st.divider()

        with sekme2:
            tablo_secim = st.selectbox(
                "Yönetilecek Parametre", 
                ["Hücre Hatları", "Besiyerleri", "Kimyasallar"]
            )
            tablo_map = {
                "Hücre Hatları": "hucre_hatlari",
                "Besiyerleri": "besiyer"
                "Kimyasallar": "kimyyasallar"
