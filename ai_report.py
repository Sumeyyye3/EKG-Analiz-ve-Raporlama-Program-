import os

try:
    from typing import Dict, Any
    from google import genai
    from google.genai import types
except:
    print("poetry install yaz")

def generate_ecg_report(analysis_results: Dict[str, Any]) -> str:
    """
    5. adımda hesaplanan EKG analiz metriklerini alır,
    Gemini 2.5 Flash modeline göndererek profesyonel Türkçe kardiyoloji raporu oluşturur.
    Raporu doğrudan terminale yazdırır ve metin olarak döndürür.
    """
    # 1. API Anahtarı Kontrolü
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        error_msg = "⚠️ HATA: GEMINI_API_KEY ortam değişkeni bulunamadı! Lütfen API anahtarınızı tanımlayın."
        print(error_msg)
        return error_msg

    # 2. Gemini Client Başlatma
    client = genai.Client(api_key=api_key)

    # 3. Metrikleri Sözlükten Çıkarma
    mean_bpm = analysis_results.get("mean_bpm", "Bilinmiyor")
    min_bpm = analysis_results.get("min_bpm", "Bilinmiyor")
    max_bpm = analysis_results.get("max_bpm", "Bilinmiyor")
    rr_variance = analysis_results.get("rr_variance_pct", "Bilinmiyor")
    status = analysis_results.get("status", "Bilinmiyor")
    alerts = ", ".join(analysis_results.get("alerts", []))
    total_beats = analysis_results.get("total_beats", "Bilinmiyor")

    # 4. Prompt Mühendisliği (Yapılandırılmış İstem)
    prompt = f"""
    Sen uzman bir kardiyoloji asistansın. Aşağıda otomatik analiz motorundan elde edilen EKG sayısal metrikleri ve ön bulgular yer almaktadır.

    [EKG ANALİZ METRİKLERİ]
    - Ortalama Kalp Atım Hızı (BPM): {mean_bpm} bpm
    - Minimum / Maksimum BPM: {min_bpm} / {max_bpm} bpm
    - Toplam Tespit Edilen Atım Sayısı: {total_beats}
    - R-R Aralık Varyansı (Ritim Düzensizlik Yüzdesi): %{rr_variance}
    - Otomatik Ön Durum Tespiti: {status}
    - Tetiklenen Sistem Uyarıları: {alerts}

    [GÖREV]
    Bu verileri değerlendirerek hasta veya takip eden hekim için Türkçe bir "EKG Özet Değerlendirme Raporu" oluştur.

    [RAPOR FORMATI]
    1. **Genel Değerlendirme**: Sinyal verilerinin ve ritmin kısa bir özeti.
    2. **Bulgular & Risk Analizi**: BPM ve R-R varyansı üzerinden taşikardi, bradikardi veya aritmi durumunun klinik yorumu.
    3. **Öneri & Uayrı**: Bunun otomatik bir analiz yazılımı çıktısı olduğunu ve kesin tanı için bir kardiyoloji uzmanına danışılması gerektiğini belirten standart tıbbi uyarı.
    """

    print("\n🤖 Gemini AI Rapor Oluşturuluyor, lütfen bekleyin...\n")

    try:
        # 5. Gemini 2.5 Flash Modeli Çağrısı
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.3, # Tıbbi tutarlılık için düşük yaratıcılık
            )
        )
        
        report_text = response.text

        # 6. Terminale Raporu Yazdırma
        print("=" * 60)
        print("📋 EKG ÖZET DEĞERLENDİRME RAPORU (AI DESTEKLİ)")
        print("=" * 60)
        print(report_text)
        print("=" * 60 + "\n")

        return report_text

    except Exception as e:
        error_msg = f"API Çağrısı Sırasında Hata Oluştu: {e}"
        print(error_msg)
        return error_msg

# ==========================================
# 5. ve 6. Adımları Birlikte Test Etmek İçin Örnek Çalıştırma Bloğu
# ==========================================
if __name__ == "__main__":
    # 5. Adımdan gelebilecek örnek bir test sözlüğü
    mock_analysis_results = {
        "mean_bpm": 108.5,
        "min_bpm": 95.0,
        "max_bpm": 122.0,
        "rr_variance_pct": 14.8,
        "status": "Taşikardi Tespiti",
        "alerts": ["⚠️ Taşikardi Riski (Yüksek Kalp Atım Hızı)", "⚠️ Düzensiz Ritim (Aritmi Riski - R-R Değişkenliği Yüksek)"],
        "total_beats": 18
    }

    # API Anahtarını terminalden vermediysen geçici olarak test için buradan set edebilirsin:
    # os.environ["GEMINI_API_KEY"] = "AIzaSy..."

    # Fonksiyonu çalıştır ve terminal çıktısını gör
    generate_ecg_report(mock_analysis_results)