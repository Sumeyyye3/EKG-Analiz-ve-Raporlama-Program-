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

    signals, rpeaks_info = nk.ecg_peaks(
        cleaned_signal,
        sampling_rate=sampling_rate
    )

    return signals, rpeaks_info


def detect_ecg_waves(
    cleaned_signal: pd.Series,
    rpeaks_info: dict,
    sampling_rate: int = 1000
) -> tuple[pd.DataFrame, dict]:
    """EKG sinyalindeki P, Q, S ve T noktalarını tespit eder."""

    signals_delineated, waves_info = nk.ecg_delineate(
        cleaned_signal,
        rpeaks_info,
        sampling_rate=sampling_rate,
        method="peaks"
    )

    return signals_delineated, waves_info


def get_valid_peaks(
    waves_info: dict,
    peak_name: str
) -> list:
    """NaN olmayan peak noktalarını döndürür."""

    peaks = []

    for x in waves_info.get(peak_name, []):
        if not pd.isna(x):
            peaks.append(x)

    return peaks


def save_ecg_waves_plot(
    cleaned_signal: pd.Series,
    rpeaks_info: dict,
    waves_info: dict,
    output_dir: str = "output"
) -> None:
    """R, P, Q, S ve T noktalarını EKG grafiği üzerinde gösterip PNG olarak kaydeder."""

    os.makedirs(output_dir, exist_ok=True)

    r_peaks = rpeaks_info["ECG_R_Peaks"]

    p_peaks = get_valid_peaks(
        waves_info,
        "ECG_P_Peaks"
    )

    q_peaks = get_valid_peaks(
        waves_info,
        "ECG_Q_Peaks"
    )

    s_peaks = get_valid_peaks(
        waves_info,
        "ECG_S_Peaks"
    )

    t_peaks = get_valid_peaks(
        waves_info,
        "ECG_T_Peaks"
    )

    plt.figure(figsize=(14, 6))

    plt.plot(
        cleaned_signal,
        label="Temiz EKG Sinyali",
        color="black",
        alpha=0.7,
        linewidth=1.2
    )

    plt.scatter(
        r_peaks,
        cleaned_signal.iloc[r_peaks],
        color="red",
        marker="^",
        s=80,
        label="R Tepesi",
        zorder=5
    )

    if p_peaks:
        plt.scatter(
            p_peaks,
            cleaned_signal.iloc[p_peaks],
            color="blue",
            marker="o",
            s=50,
            label="P Dalgası",
            zorder=4
        )

    if q_peaks:
        plt.scatter(
            q_peaks,
            cleaned_signal.iloc[q_peaks],
            color="purple",
            marker="v",
            s=40,
            label="Q Dalgası",
            alpha=0.7
        )

    if s_peaks:
        plt.scatter(
            s_peaks,
            cleaned_signal.iloc[s_peaks],
            color="orange",
            marker="v",
            s=40,
            label="S Dalgası",
            alpha=0.7
        )

    if t_peaks:
        plt.scatter(
            t_peaks,
            cleaned_signal.iloc[t_peaks],
            color="green",
            marker="s",
            s=50,
            label="T Dalgası",
            zorder=4
        )

    plt.title(
        "EKG Dalga Analizi (R, P, Q, S, T Noktaları)",
        fontsize=14,
        fontweight="bold"
    )

    plt.xlabel("Örnek Numarası (Sample)")
    plt.ylabel("Genlik (mV)")
    plt.legend(loc="upper right")
    plt.grid(True, linestyle="--", alpha=0.5)

    plt.tight_layout()

    output_path = os.path.join(
        output_dir,
        "waves_detected.png"
    )

    plt.savefig(output_path, dpi=300)
    plt.close()


def peaks_save_png(
    cleaned_signal: pd.Series,
    sampling_rate: int = 1000,
    output_dir: str = "output"
) -> tuple[dict, dict]:
    _, rpeaks_info = detect_r_peaks(
        cleaned_signal,
        sampling_rate=sampling_rate
    )

    _, waves_info = detect_ecg_waves(
        cleaned_signal,
        rpeaks_info,
        sampling_rate=sampling_rate
    )

    save_ecg_waves_plot(
        cleaned_signal,
        rpeaks_info,
        waves_info,
        output_dir=output_dir
    )

    return rpeaks_info, waves_info