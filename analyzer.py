try:
    import numpy as np
except ModuleNotFoundError as e:
    print(e)
    print("Bu nedenle poetry install komutuyla bağımlılıkları indir")
    exit(1)


def calculate_rr_intervals(
    r_peaks: list,
    sampling_rate: int = 1000
) -> np.ndarray:
    """R tepeleri arasındaki R-R aralıklarını saniye cinsinden hesaplar."""

    rr_intervals_samples = np.diff(r_peaks)
    rr_intervals_seconds = rr_intervals_samples / sampling_rate

    return rr_intervals_seconds


def calculate_bpm(
    rr_intervals: np.ndarray
) -> dict:
    """R-R aralıklarından anlık, ortalama, minimum ve maksimum BPM hesaplar."""

    instant_bpm = 60.0 / rr_intervals

    return {
        "instant_bpm": instant_bpm,
        "mean_bpm": round(float(np.mean(instant_bpm)), 1),
        "min_bpm": round(float(np.min(instant_bpm)), 1),
        "max_bpm": round(float(np.max(instant_bpm)), 1),
    }


def calculate_rr_variance(
    rr_intervals: np.ndarray
) -> float:
    """R-R aralıklarının değişim katsayısını yüzde olarak hesaplar."""

    rr_std = np.std(rr_intervals)
    rr_mean = np.mean(rr_intervals)

    rr_variance_pct = (rr_std / rr_mean) * 100

    return round(float(rr_variance_pct), 2)


def detect_alerts(
    mean_bpm: float,
    rr_variance_pct: float
) -> tuple[str, list]:
    """BPM ve R-R değişkenliğine göre kural tabanlı ikaz üretir."""

    alerts = []
    status = "Normal Sinüs Ritmi"

    # Taşikardi
    if mean_bpm > 100:
        alerts.append(
            "⚠️ Taşikardi Riski (Yüksek Kalp Atım Hızı)"
        )
        status = "Taşikardi Tespiti"

    # Bradikardi
    elif mean_bpm < 60:
        alerts.append(
            "⚠️ Bradikardi Riski (Düşük Kalp Atım Hızı)"
        )
        status = "Bradikardi Tespiti"

    # Düzensiz ritim
    if rr_variance_pct > 12.0:
        alerts.append(
            "⚠️ Düzensiz Ritim "
            "(Aritmi Riski - R-R Değişkenliği Yüksek)"
        )

        if status == "Normal Sinüs Ritmi":
            status = "Düzensiz Ritim (Aritmi)"

    if not alerts:
        alerts.append(
            "✅ Sinyal Değerleri Normal Aralıkta"
        )

    return status, alerts


def analyze_ecg_metrics(
    r_peaks: list,
    sampling_rate: int = 1000
) -> dict:
    """EKG metriklerini hesaplar ve aritmi ikazlarını üretir."""

    if len(r_peaks) < 2:
        return {
            "error": (
                "Yetersiz R-tepesi! "
                "Analiz için en az 2 R-tepesi gereklidir."
            )
        }

    # R-R hesapla
    rr_intervals = calculate_rr_intervals(
        r_peaks,
        sampling_rate
    )

    # BPM hesapla
    bpm_results = calculate_bpm(rr_intervals)

    # R-R varyansı hesapla
    rr_variance_pct = calculate_rr_variance(
        rr_intervals
    )

    # İkazları oluştur
    status, alerts = detect_alerts(
        bpm_results["mean_bpm"],
        rr_variance_pct
    )

    # Sonuçları birleştir
    return {
        "mean_bpm": bpm_results["mean_bpm"],
        "min_bpm": bpm_results["min_bpm"],
        "max_bpm": bpm_results["max_bpm"],
        "rr_variance_pct": rr_variance_pct,
        "status": status,
        "alerts": alerts,
        "total_beats": len(r_peaks),
    }
