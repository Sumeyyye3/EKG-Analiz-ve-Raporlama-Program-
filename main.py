import argparse
import sys
import os

from transform_time_voltage import read_ecg_data
from signal_processing import cleaning_signals, save_ecg_comparison_plot
from coord_determ import all_save_png
from analyzer import analyze_ecg_metrics
from ai_report import generate_ecg_report


def main():
    parser = argparse.ArgumentParser(
        description="Akıllı EKG Analiz ve Aritmi İkaz Paneli (Terminal Sürümü)"
    )

    parser.add_argument(
        "file_path",
        type=str,
        help="Analiz edilecek EKG dosyasının yolu (.csv, .txt veya .dat)"
    )

    parser.add_argument(
        "--sampling_rate", "-sr",
        type=int,
        default=1000,
        help="Sinyalin örnekleme hızı (Hz cinsinden, varsayılan: 1000)"
    )

    parser.add_argument(
        "--output-dir", "-o",
        type=str,
        default="output",
        help="Grafiklerin kaydedileceği klasör (varsayılan: output)"
    )

    parser.add_argument(
        "--no-ai",
        action="store_true",
        help="Gemini AI raporu oluşturma adımını atla"
    )

    args = parser.parse_args()

    if not os.path.exists(args.file_path):
        print(f"HATA: '{args.file_path}' dosyası bulunamadı!")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("EKG ANALİZ VE ARİTMİ İKAZ SİSTEMİ BAŞLATILIYOR...")
    print("=" * 60)

    # 1) Veri okuma
    print(f"\n[1/5] Veri dosyası okunuyor: {args.file_path}")
    _, voltage = read_ecg_data(args.file_path)
    print(f"      -> Toplam {len(voltage)} örnek (sample) yüklendi.")

    sampling_rate = getattr(voltage, "attrs", {}).get("sampling_rate", args.sampling_rate)
    if sampling_rate != args.sampling_rate:
        print(f"      -> Dosyadan algılanan örnekleme hızı kullanılacak: {sampling_rate} Hz")

    # 2) Sinyal temizleme
    print("\n[2/5] Sinyal gürültüden arındırılıyor (Bandpass Filtreleme)...")
    cleaned_signal = cleaning_signals(
        ecg_signal=voltage,
        sampling_rate=sampling_rate
    )
    save_ecg_comparison_plot(voltage, cleaned_signal, output_dir=args.output_dir)
    print(f"      -> Grafik kaydedildi: {args.output_dir}/filtered_signal.png")

    # 3) R/P/Q/S/T tespiti (rpeaks_info burada bir kez hesaplanıp döndürülüyor)
    print("\n[3/5] R Tepeleri ve P-QRS-T Noktaları tespit ediliyor...")
    rpeaks_info, _ = all_save_png(
        cleaned_signal,
        sampling_rate=sampling_rate,
        output_dir=args.output_dir
    )
    print(f"      -> Grafik kaydedildi: {args.output_dir}/waves_detected.png")

    # 4) Metrik hesaplama
    print("\n[4/5] Sağlık metrikleri ve Aritmi analizi hesaplanıyor...")
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

    # 5) AI Raporu
    if not args.no_ai:
        print("\n[5/5] 🤖 Gemini AI Kardiyoloji Raporu Hazırlanıyor...")
        generate_ecg_report(analysis_results)
    else:
        print("\n[5/5] AI raporu atlandı (--no-ai bayrağı verildi).")

    print(f"\n✅ Tüm işlemler başarıyla tamamlandı. Grafikler '{args.output_dir}/' klasöründedir.\n")


if __name__ == "__main__":
    main()
