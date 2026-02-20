import streamlit as st
from datetime import date
import pandas as pd
import gspread
import json
import os

# --- GOOGLE SHEETS BAĞLANTISI ---
try:
    if os.path.exists('kpss_kimlik.json'):
        # Bilgisayarda çalışırken (Senin bilgisayarın)
        gc = gspread.service_account(filename='kpss_kimlik.json')
    else:
        # İnternette (Telefondan girilen web sitesi) çalışırken
        kimlik_dict = json.loads(st.secrets["google_sifrem"])
        gc = gspread.service_account_from_dict(kimlik_dict)
        
    sh = gc.open('KPSS_Veritabani')
    ws_takip = sh.worksheet('Takip')
    ws_yanlis = sh.worksheet('Yanlis_Defteri')
except Exception as e:
    st.error(f"Google Bağlantı Hatası! Detay: {e}")
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
        gy_dersler = ["Türkçe", "Matematik", "Geometri"]
        for d in gy_dersler:
            toplam_konu = len(dersler[d])
            biten_konu = len(df_takip[(df_takip['Ders'] == d) & ((df_takip['Soru_Bankasi'] == "Evet") | (df_takip['Soru_Bankasi'] == True))]) if not df_takip.empty else 0
            yuzde = biten_konu / toplam_konu if toplam_konu > 0 else 0
            st.write(f"**{d}** - *{biten_konu} / {toplam_konu} Konu Bitti*")
            st.progress(yuzde)
            
    with col2:
        st.markdown("#### 🌍 Genel Kültür")
        gk_dersler = ["Tarih", "Coğrafya", "Vatandaşlık"]
        for d in gk_dersler:
            toplam_konu = len(dersler[d])
            biten_konu = len(df_takip[(df_takip['Ders'] == d) & ((df_takip['Soru_Bankasi'] == "Evet") | (df_takip['Soru_Bankasi'] == True))]) if not df_takip.empty else 0
            yuzde = biten_konu / toplam_konu if toplam_konu > 0 else 0
            st.write(f"**{d}** - *{biten_konu} / {toplam_konu} Konu Bitti*")
            st.progress(yuzde)

# --- MODÜL 2: ÇALIŞMA TAKİBİ ---
elif menu == "Çalışma Takibi & Notlar":
    df_takip = verileri_yukle(ws_takip, ["Ders", "Konu", "Pegem_Video", "Konu_Kitabi", "Soru_Bankasi", "Kisisel_Not"])
    
    st.title("📅 Konu Takip Sistemi (Bulut)")
    secilen_ders = st.selectbox("Çalıştığın Dersi Seç:", list(dersler.keys()), key="takip_ders")
    secilen_konu = st.selectbox("Konuyu Seç:", dersler[secilen_ders], key="takip_konu")
    
    st.markdown(f"### 📌 {secilen_ders} - {secilen_konu}")
    
    col1, col2 = st.columns(2)
    with col1:
        video_izlendi = st.checkbox("📺 Pegem Canlı Ders/Video İzlendi")
        konu_calisildi = st.checkbox("📖 Konu Anlatım Kitabından Okundu")
        soru_cozuldu = st.checkbox("📝 Soru Bankası Testleri Bitti")
    
    with col2:
        alinan_not = st.text_area("Bu konuyla ilgili kendi notların:", placeholder="Örn: Bu konudan çok soru kaçırdım...")
    
    if st.button("☁️ Buluta Kaydet"):
        yeni_satir = [
            secilen_ders, secilen_konu, 
            "Evet" if video_izlendi else "Hayır", 
            "Evet" if konu_calisildi else "Hayır", 
            "Evet" if soru_cozuldu else "Hayır", 
            alinan_not
        ]
        ws_takip.append_row(yeni_satir)
        st.success("Google E-Tablolara başarıyla kaydedildi!")
        st.rerun()

    st.divider()
    st.subheader("📚 Kaydedilen Çalışmalarım")
    st.dataframe(df_takip.iloc[::-1], use_container_width=True)

# --- MODÜL 3: YANLIŞ DEFTERİ ---
elif menu == "Yanlış Defteri":
    df_yanlis = verileri_yukle(ws_yanlis, ["Ders", "Konu", "Kaynak", "Hata_Sebebi", "Soru_Ozeti", "Dogru_Cozum"])
    
    st.title("📝 Yanlış Defteri (Bulut)")
    
    col1, col2 = st.columns(2)
    with col1:
        y_ders = st.selectbox("Hata Yapılan Ders:", list(dersler.keys()), key="yanlis_ders")
        y_konu = st.selectbox("Hata Yapılan Konu:", dersler[y_ders], key="yanlis_konu")
        y_kaynak = st.text_input("Hangi Kaynak?")
        
    with col2:
        y_sebep = st.selectbox("Hata Sebebi Nedir?", [
            "Bilgi Eksikliği", "Dikkat Hatası", "İşlem Hatası", "İki Şık Arasında Kaldım", "Süreyi Yetiştiremedim"
        ])
        
    y_soru = st.text_area("Sorunun Metni veya Kısa Özeti:")
    y_dogru = st.text_area("✨ Doğru Çözüm / Öğrenilen Bilgi:")
    
    if st.button("☁️ Yanlışı Buluta Kaydet"):
        if y_soru == "" or y_dogru == "":
            st.warning("Lütfen soru özetini ve çözümünü gir!")
        else:
            yeni_satir = [y_ders, y_konu, y_kaynak, y_sebep, y_soru, y_dogru]
            ws_yanlis.append_row(yeni_satir)
            st.success("Yanlış defterine eklendi! Google Drive'dan da görebilirsin.")
            st.rerun()
            
    st.divider()
    st.subheader("🔍 Kayıtlı Yanlışlarım")
    st.dataframe(df_yanlis.iloc[::-1], use_container_width=True)