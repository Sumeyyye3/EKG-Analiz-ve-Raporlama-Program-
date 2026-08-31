import os

try:
    import matplotlib.pyplot as plt
    import neurokit2 as nk
    import pandas as pd
except ModuleNotFoundError as e:
    print(e)
    print("Bu nedenle poetry install komutuyla bağımlılıkları indir")
    exit(1)


def detect_r_peaks(
    cleaned_signal: pd.Series,
    sampling_rate: int = 1000
) -> tuple[pd.Series, dict]:
    """EKG sinyalindeki R tepelerini tespit eder."""
    return nk.ecg_peaks(cleaned_signal, sampling_rate=sampling_rate)


def detect_ecg_waves(
    cleaned_signal: pd.Series,
    rpeaks_info: dict,
    sampling_rate: int = 1000
) -> tuple[pd.DataFrame, dict]:
    """EKG sinyalindeki P, Q, S ve T noktalarını tespit eder."""
    return nk.ecg_delineate(
        cleaned_signal,
        rpeaks_info,
        sampling_rate=sampling_rate,
        method="peaks"
    )


def save_ecg_waves_plot(
    cleaned_signal: pd.Series,
    rpeaks_info: dict,
    sampling_rate: int = 1000,
    output_dir: str = "output"
) -> None:
    """NeuroKit2'nin yerleşik show=True seçeneğiyle dalga grafiğini çizer ve kaydeder."""
    os.makedirs(output_dir, exist_ok=True)

    _, waves_info = nk.ecg_delineate(
        cleaned_signal,
        rpeaks_info,
        sampling_rate=sampling_rate,
        method="peaks",
        show=True,
        show_type="peaks"
    )

    output_path = os.path.join(output_dir, "waves_detected.png")
    plt.savefig(output_path, dpi=300)
    plt.close()


def peaks_save_png(
    cleaned_signal: pd.Series,
    sampling_rate: int = 1000,
    output_dir: str = "output"
) -> tuple[dict, dict]:
    """Süreçleri çalıştırır, grafiği kaydeder ve veri sözlüklerini döndürür."""
    _, rpeaks_info = detect_r_peaks(cleaned_signal, sampling_rate=sampling_rate)
    _, waves_info = detect_ecg_waves(cleaned_signal, rpeaks_info, sampling_rate=sampling_rate)

    save_ecg_waves_plot(
        cleaned_signal,
        rpeaks_info,
        sampling_rate=sampling_rate,
        output_dir=output_dir
    )

    return rpeaks_info, waves_info