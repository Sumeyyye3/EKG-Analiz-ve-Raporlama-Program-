"""
EKG Analiz ve Aritmi İkaz Paneli — Streamlit Web Arayüzü
=========================================================
Bu dosya mevcut hiçbir modülü değiştirmez; yalnızca var olan
  transform_time_voltage, signal_processing, coord_determ, analyzer, ai_report
modüllerini çağırarak çıktıları web sayfasında gösterir.

Çalıştırmak için:
    streamlit run app.py
"""

import os
import tempfile

import streamlit as st
import matplotlib
matplotlib.use("Agg")          # GUI olmayan arka plan; Streamlit için gerekli
import matplotlib.pyplot as plt

# ── Mevcut modüller (hiçbiri değiştirilmedi) ─────────────────────────────────
from transform_time_voltage import read_ecg_data
from signal_processing import cleaning_signals
from coord_determ import detect_r_peaks, detect_ecg_waves, get_valid_peaks
from analyzer import analyze_ecg_metrics
from ai_report import generate_ecg_report

# ── Sayfa ayarları ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="EKG Analiz Paneli",
    page_icon="❤️",
    layout="wide",
)

st.title("❤️ Akıllı EKG Analiz ve Aritmi İkaz Paneli")
st.caption("Mevcut analiz modülleri değiştirilmeden Streamlit arayüzüyle görselleştirilmiştir.")

# ── Kenar çubuğu: Dosya yükleme ve ayarlar ───────────────────────────────────
with st.sidebar:
    st.header("⚙️ Ayarlar")
    uploaded_file = st.file_uploader(
        "EKG Dosyası Yükle (.csv / .txt / .dat)",
        type=["csv", "txt", "dat"],
        help="WFDB (.dat) için aynı isimli .hea dosyasının da yüklenmesi gerekir.",
    )

    hea_file = st.file_uploader(
        ".hea Header Dosyası (.dat için zorunlu)",
        type=["hea"],
        help="Yalnızca .dat dosyası yüklediğinizde gereklidir.",
    )

    sampling_rate = st.number_input(
        "Örnekleme Hızı (Hz)",
        min_value=100,
        max_value=10000,
        value=1000,
        step=50,
        help="Dosyadan otomatik okunabiliyorsa bu değer kullanılmaz.",
    )

    run_ai = st.checkbox(
        "🤖 Gemini AI Raporu Oluştur",
        value=False,
        help="GEMINI_API_KEY ortam değişkeni tanımlı olmalıdır.",
    )

    analyze_btn = st.button("🔍 Analizi Başlat", type="primary", disabled=uploaded_file is None)

# ── Yardımcı: Grafik oluşturma fonksiyonları ─────────────────────────────────
def _plot_filtered(raw_signal, cleaned_signal):
    """Ham ve temizlenmiş sinyali karşılaştıran grafik."""
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(raw_signal.values, label="Ham Sinyal (Raw)", color="gray", alpha=0.6, linewidth=1)
    ax.plot(cleaned_signal.values, label="Temizlenmiş Sinyal (Filtered)", color="#1f77b4", linewidth=1.5)
    ax.set_title("EKG Sinyali Filtreleme Karşılaştırması", fontsize=14, fontweight="bold")
    ax.set_xlabel("Örnek Numarası (Sample)")
    ax.set_ylabel("Genlik (mV)")
    ax.legend(loc="upper right")
    ax.grid(True, linestyle="--", alpha=0.5)
    fig.tight_layout()
    return fig


def _plot_waves(cleaned_signal, rpeaks_info, waves_info):
    """R, P, Q, S, T noktalarını EKG üzerinde gösteren grafik."""
    r_peaks = rpeaks_info["ECG_R_Peaks"]
    p_peaks = get_valid_peaks(waves_info, "ECG_P_Peaks")
    q_peaks = get_valid_peaks(waves_info, "ECG_Q_Peaks")
    s_peaks = get_valid_peaks(waves_info, "ECG_S_Peaks")
    t_peaks = get_valid_peaks(waves_info, "ECG_T_Peaks")

    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(cleaned_signal.values, label="Temiz EKG Sinyali", color="black", alpha=0.7, linewidth=1.2)
    ax.scatter(r_peaks, cleaned_signal.iloc[r_peaks], color="red",    marker="^", s=80,  label="R Tepesi",  zorder=5)
    if p_peaks:
        ax.scatter(p_peaks, cleaned_signal.iloc[p_peaks], color="blue",   marker="o", s=50,  label="P Dalgası", zorder=4)
    if q_peaks:
        ax.scatter(q_peaks, cleaned_signal.iloc[q_peaks], color="purple", marker="v", s=40,  label="Q Dalgası", alpha=0.7)
    if s_peaks:
        ax.scatter(s_peaks, cleaned_signal.iloc[s_peaks], color="orange", marker="v", s=40,  label="S Dalgası", alpha=0.7)
    if t_peaks:
        ax.scatter(t_peaks, cleaned_signal.iloc[t_peaks], color="green",  marker="s", s=50,  label="T Dalgası", zorder=4)

    ax.set_title("EKG Dalga Analizi (R, P, Q, S, T Noktaları)", fontsize=14, fontweight="bold")
    ax.set_xlabel("Örnek Numarası (Sample)")
    ax.set_ylabel("Genlik (mV)")
    ax.legend(loc="upper right")
    ax.grid(True, linestyle="--", alpha=0.5)
    fig.tight_layout()
    return fig


# ── Ana analiz akışı ──────────────────────────────────────────────────────────
if analyze_btn and uploaded_file is not None:

    suffix = os.path.splitext(uploaded_file.name)[1]

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = os.path.join(tmp_dir, uploaded_file.name)
        with open(tmp_path, "wb") as f:
            f.write(uploaded_file.read())

        if suffix == ".dat" and hea_file is not None:
            hea_path = os.path.join(tmp_dir, hea_file.name)
            with open(hea_path, "wb") as f:
                f.write(hea_file.read())

        # ADIM 1: Veri okuma
        with st.spinner("📂 Veri dosyası okunuyor..."):
            try:
                _, voltage = read_ecg_data(tmp_path)
            except Exception as e:
                st.error(f"Dosya okunurken hata: {e}")
                st.stop()

        fs = getattr(voltage, "attrs", {}).get("sampling_rate", sampling_rate)
        st.success(f"✅ Toplam **{len(voltage):,}** örnek yüklendi. Örnekleme hızı: **{fs} Hz**")

        # ADIM 2: Sinyal temizleme
        with st.spinner("🧹 Sinyal gürültüden arındırılıyor..."):
            cleaned_signal = cleaning_signals(ecg_signal=voltage, sampling_rate=fs)

        st.subheader("📊 Adım 1 — Filtrelenmiş Sinyal")
        raw_series = voltage.reset_index(drop=True) if hasattr(voltage, "reset_index") else voltage
        fig1 = _plot_filtered(raw_series, cleaned_signal)
        st.pyplot(fig1)
        plt.close(fig1)

        # ADIM 3: Dalga tespiti
        with st.spinner("📍 R Tepeleri ve P-QRS-T Noktaları tespit ediliyor..."):
            _, rpeaks_info = detect_r_peaks(cleaned_signal, sampling_rate=fs)
            _, waves_info  = detect_ecg_waves(cleaned_signal, rpeaks_info, sampling_rate=fs)

        st.subheader("📊 Adım 2 — EKG Dalga Analizi (R, P, Q, S, T)")
        fig2 = _plot_waves(cleaned_signal, rpeaks_info, waves_info)
        st.pyplot(fig2)
        plt.close(fig2)

        # ADIM 4: Metrik analizi
        with st.spinner("📊 Sağlık metrikleri hesaplanıyor..."):
            r_peaks = rpeaks_info.get("ECG_R_Peaks", [])
            analysis_results = analyze_ecg_metrics(r_peaks=r_peaks, sampling_rate=fs)

        st.subheader("📋 Adım 3 — EKG Metrikleri ve Aritmi Analizi")

        if "error" in analysis_results:
            st.error(analysis_results["error"])
        else:
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Ortalama BPM", f"{analysis_results['mean_bpm']} bpm")
            col2.metric("Min BPM",      f"{analysis_results['min_bpm']} bpm")
            col3.metric("Maks BPM",     f"{analysis_results['max_bpm']} bpm")
            col4.metric("R-R Varyansı", f"%{analysis_results['rr_variance_pct']}")

            st.info(f"🫀 **Sistem Tespiti:** {analysis_results['status']}")

            st.subheader("⚠️ Uyarılar")
            for alert in analysis_results.get("alerts", []):
                if "✅" in alert:
                    st.success(alert)
                else:
                    st.warning(alert)

            # ADIM 5: AI Raporu
            if run_ai:
                st.subheader("🤖 Adım 4 — Gemini AI Kardiyoloji Raporu")
                with st.spinner("Gemini AI raporu hazırlanıyor, lütfen bekleyin..."):
                    report = generate_ecg_report(analysis_results)
                st.markdown(report)
            else:
                st.info("🤖 AI raporunu etkinleştirmek için sol panelden **'Gemini AI Raporu Oluştur'** seçeneğini işaretleyin.")

else:
    st.info("👈 Sol panelden bir EKG dosyası yükleyin ve **'Analizi Başlat'** butonuna tıklayın.")
    st.markdown("""
    ### 🗂️ Desteklenen Dosya Formatları
    | Format | Açıklama |
    |--------|----------|
    | `.csv` | Zaman–voltaj iki sütunlu CSV |
    | `.txt` | Boşlukla ayrılmış metin dosyası |
    | `.dat` | WFDB ikili kayıt — aynı isimli `.hea` gerekir |

    ### 🔬 Analiz Adımları
    1. **Sinyal Okuma** — Dosya formatına göre otomatik okuma
    2. **Filtreleme** — NeuroKit2 ile gürültü giderme
    3. **Dalga Tespiti** — R, P, Q, S, T noktaları
    4. **Metrik Hesaplama** — BPM, R-R varyansı, aritmi tespiti
    5. **AI Raporu** — Gemini ile kardiyoloji özet raporu *(isteğe bağlı)*
    """)
