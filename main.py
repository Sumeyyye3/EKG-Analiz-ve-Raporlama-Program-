import sys
import os

from transform_time_voltage import read_ecg_data
from signal_processing import cleaning_signals, save_ecg
from coord_determ import peaks_save_png
from analyzer import analyze_ecg_metrics
from ai_report import generate_ecg_report


def main():
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = "test_ekg.csv"

    output_dir = "output"
    default_sampling_rate = 1000
    enable_ai = True

    if not os.path.exists(file_path):
        print(f"HATA: '{file_path}' dosyası bulunamadı!")
        print("Kullanım: python main.py <dosya_yolu>")
        sys.exit(1)

    print("\n" + "=" * 47)
    print("EKG ANALİZ VE ARİTMİ İKAZ SİSTEMİ BAŞLATILIYOR...")
    print("=" * 47)

    print(f"\n[1/5] Veri dosyası okunuyor: {file_path}")
    _, voltage = read_ecg_data(file_path)
    print(f"      -> Toplam {len(voltage)} örnek (sample) yüklendi.")

    sampling_rate = getattr(voltage, "attrs", {}).get("sampling_rate", default_sampling_rate)

    print("\n[2/5] Sinyal gürültüden arındırılıyor (Bandpass Filtreleme)...")
    cleaned_signal = cleaning_signals(
        ecg_signal=voltage,
        sampling_rate=sampling_rate
    )
    save_ecg(voltage, cleaned_signal, output_dir=output_dir)
    print(f"      -> Grafik kaydedildi: {output_dir}/filtered_signal.png")

    print("\n[3/5] R Tepeleri ve P-QRS-T Noktaları tespit ediliyor ...")
    rpeaks_info, _ = peaks_save_png(
        cleaned_signal,
        sampling_rate=sampling_rate,
        output_dir=output_dir
    )
    print(f"      -> Grafik kaydedildi: {output_dir}/waves_detected.png")

    print("\n[4/5] Sağlık metrikleri ve Aritmi analizi hesaplanıyor (NeuroKit2 HRV)...")
    r_peaks = rpeaks_info.get("ECG_R_Peaks", [])
    analysis_results = analyze_ecg_metrics(
        r_peaks=r_peaks,
        sampling_rate=sampling_rate
    )

    if "error" in analysis_results:
        print(f"\nHATA: {analysis_results['error']}")
        sys.exit(1)

    print("\n" + "-" * 40)
    print("     HESAPLANAN EKG METRİKLERİ")
    print("-" * 40)
    print(f" • Ortalama BPM : {analysis_results['mean_bpm']} bpm")
    print(f" • Min/Max BPM  : {analysis_results['min_bpm']} / {analysis_results['max_bpm']} bpm")
    print(f" • R-R Varyansı : %{analysis_results['rr_variance_pct']}")
    print(f" • Sistem Tespiti: {analysis_results['status']}")
    print("\n UYARILAR:")
    for alert in analysis_results.get("alerts", []):
        print(f"   {alert}")
    print("-" * 40)

    if enable_ai:
        print("\n[5/5] 🤖 Gemini AI Kardiyoloji Raporu Hazırlanıyor...")
        generate_ecg_report(analysis_results)

    print(f"\n✅ Tüm işlemler başarıyla tamamlandı. Grafikler '{output_dir}/' klasöründedir.\n")


if __name__ == "__main__":
    main()