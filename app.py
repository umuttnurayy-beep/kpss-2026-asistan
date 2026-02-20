import streamlit as st
from datetime import date
import pandas as pd
import gspread
import json
import os

# --- GOOGLE SHEETS BAĞLANTISI ---
@st.cache_resource
def get_gspread_client():
    try:
        # 1. Bilgisayarda yerel dosya varsa onu kullan
        if os.path.exists('kpss_kimlik.json'):
            return gspread.service_account(filename='kpss_kimlik.json')
        
        # 2. İnternette (Secrets) üzerinden bağlan
        elif "google_sifrem" in st.secrets:
            # Secrets içindeki veriyi al
            creds_data = st.secrets["google_sifrem"]
            
            # Eğer veri string ise (tırnaklar içinde) sözlüğe çevir
            if isinstance(creds_data, str):
                creds_dict = json.loads(creds_data, strict=False)
            else:
                # Eğer Streamlit veriyi otomatik dict yaptıysa direkt kullan
                creds_dict = dict(creds_data)
                
            return gspread.service_account_from_dict(creds_dict)
        else:
            return None
    except Exception as e:
        st.error(f"Bağlantı Kurulamadı: {e}")
        return None

# Bağlantıyı Başlat
gc = get_gspread_client()

if gc:
    try:
        # Tablo isminin tam olarak 'KPSS_Veritabani' olduğundan emin ol
        sh = gc.open('KPSS_Veritabani')
        ws_takip = sh.worksheet('Takip')
        ws_yanlis = sh.worksheet('Yanlis_Defteri')
    except Exception as e:
        st.error(f"E-Tablo sayfalarına erişilemedi (İsimleri kontrol et!): {e}")
        st.stop()
else:
    st.warning("Kimlik bilgileri bekleniyor... Lütfen Secrets ayarlarını kontrol edin.")
    st.stop()

def verileri_yukle(worksheet, kolonlar):
    data = worksheet.get_all_records()
    if data:
        return pd.DataFrame(data)
    else:
        return pd.DataFrame(columns=kolonlar)

# --- Sayfa Ayarları ---
st.set_page_config(page_title="KPSS 2026 Asistanı", layout="wide")

# KPSS Müfredat Listesi
dersler = {
    "Türkçe": ["Sözcükte Anlam", "Cümlede Anlam", "Paragraf (Anlatım Biçimleri, Düşünceyi Geliştirme Yolları)", "Paragraf (Yapı, Ana Düşünce, Yardımcı Düşünce)", "Dil Bilgisi (Ses Bilgisi, Yazım Kuralları, Noktalama)", "Dil Bilgisi (Sözcük Türleri)", "Dil Bilgisi (Cümle Ögeleri, Çatı, Türleri)", "Anlatım Bozuklukları", "Sözel Mantık"],
    "Matematik": ["Temel Kavramlar", "Sayı Basamakları ve Çözümleme", "Bölme ve Bölünebilme", "Asal Çarpanlara Ayırma, EBOB - EKOK", "Rasyonel ve Ondalıklı Sayılar", "Basit Eşitsizlikler", "Mutlak Değer", "Üslü Sayılar", "Köklü Sayılar", "Çarpanlara Ayırma", "Birinci Dereceden Denklemler", "Oran - Orantı", "Problemler (Sayı, Kesir, Yaş, İşçi, Hareket, Yüzde vb.)", "Kümeler ve Kartezyen Çarpım", "Fonksiyonlar ve İşlem", "Modüler Aritmetik", "Permütasyon, Kombinasyon, Olasılık", "Sayısal Mantık ve Grafik Yorumlama"],
    "Geometri": ["Doğruda ve Üçgende Açılar", "Açı - Kenar Bağıntıları", "Özel Üçgenler", "Üçgende Açıortay, Kenarortay ve Benzerlik", "Üçgende Alan", "Çokgenler ve Dörtgenler", "Çember ve Daire", "Analitik Geometri", "Katı Cisimler"],
    "Tarih": ["İslamiyet Öncesi Türk Tarihi", "İlk Türk-İslam Devletleri", "Osmanlı Devleti (Kuruluş ve Yükselme)", "Osmanlı Kültür ve Uygarlığı", "17. Yüzyılda Osmanlı (Duraklama)", "18. Yüzyılda Osmanlı (Gerileme)", "19. ve 20. Yüzyıl Başlarında Osmanlı (Dağılma)", "Milli Mücadele Hazırlık Dönemi", "Milli Mücadele Cepheler ve Antlaşmalar", "Atatürk Dönemi İç Politika ve İnkılaplar", "Atatürk İlkeleri", "Atatürk Dönemi Türk Dış Politikası", "Çağdaş Türk ve Dünya Tarihi"],
    "Coğrafya": ["Türkiye'nin Coğrafi Konumu", "Türkiye'nin Yer Şekilleri ve Fiziki Özellikleri", "Türkiye'nin İklimi ve Bitki Örtüsü", "Türkiye'de Nüfus ve Yerleşme", "Türkiye'de Tarım", "Türkiye'de Hayvancılık ve Ormancılık", "Türkiye'de Madenler ve Enerji Kaynakları", "Türkiye'de Sanayi ve Endüstri", "Türkiye'de Ulaşım, Ticaret ve Turizm", "Bölgesel Kalkınma Projeleri"],
    "Vatandaşlık": ["Temel Hukuk Kavramları", "Devlet Biçimleri ve Demokrasi", "Anayasa Tarihi", "1982 Anayasası Temel Hükümleri", "Temel Hak ve Hürriyetler", "Yasama (TBMM)", "Yürütme (Cumhurbaşkanı)", "Yargı", "İdare Hukuku", "Güncel ve Kültürel Bilgiler"]
}

# --- Sol Menü ---
st.sidebar.title("📌 Menü")
menu = st.sidebar.radio("Modül Seçiniz:", ("Ana Sayfa (Dashboard)", "Çalışma Takibi & Notlar", "Yanlış Defteri"))

# --- MODÜL 1: ANA SAYFA ---
if menu == "Ana Sayfa (Dashboard)":
    st.title("🎯 KPSS 2026 Lisans - Bulut Asistanı ☁️")
    bugun = date.today()
    sinav_tarihi = date(2026, 9, 6)
    kalan_gun = (sinav_tarihi - bugun).days
    st.markdown(f"### ⏳ Sınava Kalan Süre: **{kalan_gun} Gün**")
    st.progress(max(0.0, min(1.0, 1.0 - (kalan_gun / 195)))) 
    st.divider()
    
    st.subheader("📊 Ders İlerleme Durumu")
    df_takip = verileri_yukle(ws_takip, ["Ders", "Konu", "Pegem_Video", "Konu_Kitabi", "Soru_Bankasi", "Kisisel_Not"])
    if not df_takip.empty:
        df_takip = df_takip.drop_duplicates(subset=['Ders', 'Konu'], keep='last')
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 🧠 Genel Yetenek")
        for d in ["Türkçe", "Matematik", "Geometri"]:
            toplam = len(dersler[d])
            biten = len(df_takip[(df_takip['Ders'] == d) & (df_takip['Soru_Bankasi'].isin(["Evet", True]))]) if not df_takip.empty else 0
            st.write(f"**{d}** - *{biten}/{toplam}*")
            st.progress(biten/toplam if toplam > 0 else 0)
    with col2:
        st.markdown("#### 🌍 Genel Kültür")
        for d in ["Tarih", "Coğrafya", "Vatandaşlık"]:
            toplam = len(dersler[d])
            biten = len(df_takip[(df_takip['Ders'] == d) & (df_takip['Soru_Bankasi'].isin(["Evet", True]))]) if not df_takip.empty else 0
            st.write(f"**{d}** - *{biten}/{toplam}*")
            st.progress(biten/toplam if toplam > 0 else 0)

# --- MODÜL 2: ÇALIŞMA TAKİBİ ---
elif menu == "Çalışma Takibi & Notlar":
    st.title("📅 Konu Takip Sistemi")
    sec_ders = st.selectbox("Ders:", list(dersler.keys()))
    sec_konu = st.selectbox("Konu:", dersler[sec_ders])
    v = st.checkbox("📺 Video")
    k = st.checkbox("📖 Kitap")
    s = st.checkbox("📝 Soru Bankası")
    n = st.text_area("Notlar:")
    if st.button("💾 Kaydet"):
        ws_takip.append_row([sec_ders, sec_konu, "Evet" if v else "Hayır", "Evet" if k else "Hayır", "Evet" if s else "Hayır", n])
        st.success("Kaydedildi!")
        st.rerun()
    df_t = verileri_yukle(ws_takip, [])
    st.dataframe(df_t.iloc[::-1])

# --- MODÜL 3: YANLIŞ DEFTERİ ---
elif menu == "Yanlış Defteri":
    st.title("📝 Yanlış Defteri")
    y_d = st.selectbox("Ders:", list(dersler.keys()), key="y1")
    y_k = st.selectbox("Konu:", dersler[y_d], key="y2")
    y_s = st.text_area("Soru Özeti:")
    y_c = st.text_area("Doğru Çözüm:")
    if st.button("❌ Yanlışı Kaydet"):
        ws_yanlis.append_row([y_d, y_k, "", "", y_s, y_c])
        st.success("Eklendi!")
        st.rerun()
    df_y = verileri_yukle(ws_yanlis, [])
    st.dataframe(df_y.iloc[::-1])
