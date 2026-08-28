import argparse
import sys
import os

from transform_time_voltage import read_ecg_data
from signal_processing import cleaning_signals
from coord_determ import all_save_png, detect_r_peaks
from analyzer import analyze_ecg_metrics
from ai_report import generate_ecg_report

def main():
    parser = argparse.ArgumentParser(
        description="Akıllı EKG Analiz ve Aritmi İkaz Paneli (Terminal Sürümü)"
    )
    
    parser.add_argument(
        "file_path", 
        type=str, 
        help="Analiz edilecek EKG dosyasının yolu (.csv veya .txt)"
    )
    
    parser.add_argument(
        "--sampling_rate", "-sr",
        type=int, 
        default=1000, 
        help="Sinyalin Örnekleme Hızı (Hz cinsinden, varsayılan: 1000)"
    )

    args = parser.parse_args()

    if not os.path.exists(args.file_path):
        print(f"❌ HATA: '{args.file_path}' dosyası bulunamadı!")
        sys.exit(1)

    print("\n" + "="*60)
    print("🫀 EKG ANALİZ VE ARİTMİ İKAZ SİSTEMİ BAŞLATILIYOR...")
    print("="*60)

    print(f"\n[1/5] 📂 Veri dosyası okunuyor: {args.file_path}")
    ecg_signal = read_ecg_data(args.file_path)
    print(f"      -> Toplam {len(ecg_signal)} örnek (sample) yüklendi.")

    print("\n[2/5] 🧹 Sinyal gürültüden arındırılıyor (Bandpass Filtreleme)...")
    cleaned_signal = cleaning_signals(
        ecg_signal=ecg_signal, 
        sampling_rate=args.sampling_rate
    )
    print("      -> Grafik kaydedildi: output/filtered_signal_split.png")

    print("\n[3/5] 📍 R Tepeleri ve P-QRS-T Noktaları tespit ediliyor...")
    all_save_png()
    print("      -> Grafik kaydedildi: output/waves_detected.png")
    _, rpeaks_info = detect_r_peaks(
            cleaned_signal, sampling_rate=args.sampling_rate
        )
    # STEP 4: Kural Tabanlı Metrik Analizi ve Uyarı Motoru
    print("\n[4/5] 📊 Sağlık metrikleri ve Aritmi analizi hesaplanıyor...")
    r_peaks = rpeaks_info.get("ECG_R_Peaks", [])
    analysis_results = analyze_ecg_metrics(
        r_peaks=r_peaks, 
        sampling_rate=args.sampling_rate
    )

    print("\n" + "-"*40)
    print("     📉 HESAPLANAN EKG METRİKLERİ")
    print("-" * 40)
    print(f" • Ortalama BPM : {analysis_results.get('mean_bpm')} bpm")
    print(f" • Min/Max BPM   : {analysis_results.get('min_bpm')} / {analysis_results.get('max_bpm')} bpm")
    print(f" • R-R Varyansı  : %{analysis_results.get('rr_variance_pct')}")
    print(f" • Sistem Tespiti: {analysis_results.get('status')}")
    print("\n ⚠️ UYARILAR:")
    for alert in analysis_results.get('alerts', []):
        print(f"   {alert}")
    print("-" * 40)

    print("\n[5/5] 🤖 Gemini AI Kardiyoloji Raporu Hazırlanıyor...")
    generate_ecg_report(analysis_results)

    print("\n✅ Tüm işlemler başarıyla tamamlandı. Oluşturulan grafikler 'output/' dizinindedir.\n")

if __name__ == "__main__":
    main()
