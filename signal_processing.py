import os

try:
    import matplotlib.pyplot as plt
    import neurokit2 as nk
    import pandas as pd
except ModuleNotFoundError as e:
    print(e)
    print("Bu nedenle poetry install komutuyla bağımlılıkları indir")
    exit(1)

def cleaning_signals(
    ecg_signal: pd.Series,
    sampling_rate: int = 1000
) -> pd.Series:
    """Ham EKG sinyalini NeuroKit2 kullanarak temizler."""

    cleaned_signal = nk.ecg_clean(
        ecg_signal,
        sampling_rate=sampling_rate
    )
    return pd.Series(cleaned_signal)


def save_ecg(
    ecg_signal: pd.Series,
    cleaned_signal: pd.Series,
    output_dir: str = "output"
) -> None:
    """Ham ve temizlenmiş EKG sinyalini karşılaştıran grafiği PNG olarak kaydeder."""

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    plt.figure(figsize=(12, 5))

    plt.plot(
        ecg_signal,
        label="Ham Sinyal (Raw)",
        color="gray",
        alpha=0.6,
        linewidth=1,
    )

    plt.plot(
        cleaned_signal,
        label="Temizlenmiş Sinyal (Filtered)",
        color="#1f77b4",
        linewidth=1.5,
    )

    plt.title(
        "EKG Sinyali Filtreleme Karşılaştırması",
        fontsize=14,
        fontweight="bold"
    )
    plt.xlabel("Örnek Numarası (Sample)", fontsize=10)
    plt.ylabel("Genlik (mV)", fontsize=10)
    plt.legend(loc="upper right")
    plt.grid(True, linestyle="--", alpha=0.5)

    plt.tight_layout()

    file_path = os.path.join(output_dir, "filtered_signal.png")
    plt.savefig(file_path, dpi=300)

    plt.close()