try:
    import numpy as np
    import neurokit2 as nk
    import pandas as pd
except ModuleNotFoundError as e:
    print(e)
    print("Bu nedenle poetry install komutuyla bağımlılıkları indir")
    exit(1)


def calculate_rr_intervals(
    r_peaks: list,
    sampling_rate: int = 1000
) -> np.ndarray:
    """R tepeleri arasındaki süreleri (saniye) hesaplar."""
    r_peaks_arr = np.array(r_peaks)
    return np.diff(r_peaks_arr) / sampling_rate


def calculate_bpm(
    r_peaks: list,
    sampling_rate: int = 1000
) -> dict:
    """NeuroKit2 (nk.ecg_rate) kullanarak R tepelerinden BPM istatistiklerini hesaplar."""
    bpm_series = nk.ecg_rate(
        r_peaks,
        sampling_rate=sampling_rate,
        desired_length=None
    )

    return {
        "mean_bpm": round(float(np.mean(bpm_series)), 1),
        "min_bpm": round(float(np.min(bpm_series)), 1),
        "max_bpm": round(float(np.max(bpm_series)), 1),
    }


def calculate_rr_variance(
    r_peaks: list,
    sampling_rate: int = 1000
) -> float:
    """NeuroKit2'nin HRV (Time-Domain) modülü ile R-R değişim katsayısını (%) hesaplar."""
    hrv_metrics = nk.hrv_time(r_peaks, sampling_rate=sampling_rate)

    sdnn = hrv_metrics["HRV_SDNN"].iloc[0]
    meannn = hrv_metrics["HRV_MeanNN"].iloc[0]
    rr_variance_pct = (sdnn / meannn) * 100

    return round(float(rr_variance_pct), 2)


def detect_alerts(
    mean_bpm: float,
    rr_variance_pct: float
) -> tuple[str, list]:
    """BPM ve R-R değişkenliğine göre kural tabanlı ikaz üretir."""
    alerts = []
    status = "Normal Sinüs Ritmi"

    if mean_bpm > 100:
        alerts.append("Taşikardi Riski (Yüksek Kalp Atım Hızı)")
        status = "Taşikardi Tespiti"

    elif mean_bpm < 60:
        alerts.append("Bradikardi Riski (Düşük Kalp Atım Hızı)")
        status = "Bradikardi Tespiti"

    if rr_variance_pct > 12.0:
        alerts.append("Düzensiz Ritim (Aritmi Riski - R-R Değişkenliği Yüksek)")

        if status == "Normal Sinüs Ritmi":
            status = "Düzensiz Ritim (Aritmi)"

    if not alerts:
        alerts.append("Sinyal Değerleri Normal Aralıkta")

    return status, alerts


def analyze_ecg_metrics(
    r_peaks: list,
    sampling_rate: int = 1000
) -> dict:
    """EKG metriklerini hesaplar ve aritmi ikazlarını üretir."""
    if len(r_peaks) < 2:
        return {
            "error": "Yetersiz R-tepesi! Analiz için en az 2 R-tepesi gereklidir."
        }

    bpm_results = calculate_bpm(r_peaks, sampling_rate=sampling_rate)

    rr_variance_pct = calculate_rr_variance(r_peaks, sampling_rate=sampling_rate)

    status, alerts = detect_alerts(bpm_results["mean_bpm"], rr_variance_pct)

    return {
        "mean_bpm": bpm_results["mean_bpm"],
        "min_bpm": bpm_results["min_bpm"],
        "max_bpm": bpm_results["max_bpm"],
        "rr_variance_pct": rr_variance_pct,
        "status": status,
        "alerts": alerts,
        "total_beats": len(r_peaks),
    }