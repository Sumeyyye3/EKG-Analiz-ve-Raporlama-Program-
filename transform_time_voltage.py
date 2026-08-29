from typing import Any, Tuple
import os


def read_ecg_csv(file_path: Any,pandas) -> Tuple[Any, Any]:
    df = pandas.read_csv(file_path)

    time = df.iloc[:, 0]
    voltage = df.iloc[:, 1]
    
    return time, voltage


def read_ecg_txt(file_path: Any,pandas) -> Tuple[Any, Any]:
    """TXT formatındaki EKG verisini okur."""

    df = pandas.read_csv(file_path, sep=r'\s+', header=None, engine='python')
    
    if df.shape[1] >= 2:
        time = df.iloc[:, 0]
        voltage = df.iloc[:, 1]
    else:
        time = None
        voltage = df.iloc[:, 0]
        
    return time, voltage


def read_ecg_dat(file_path: Any, pandas, channel: int = 0) -> Tuple[Any, Any]:
    """WFDB formatındaki (.dat + .hea) EKG verisini okur.
 
    file_path, .dat dosyasının yoludur. Aynı klasörde AYNI İSİMLİ bir
    .hea header dosyası da bulunmak zorundadır (örn. 47.dat + 47.hea),
    çünkü örnekleme hızı, kanal sayısı ve kazanç (gain) gibi bilgiler
    .hea dosyasından okunur.
    """
    try:
        import wfdb
    except ModuleNotFoundError as e:
        print(e)
        print("Bu nedenle poetry install (veya pip install wfdb) komutuyla bağımlılıkları indir")
        raise
 
    import numpy as np
 
    record_name = os.path.splitext(file_path)[0]  # wfdb uzantısız isim ister
    hea_path = record_name + ".hea"
 
    if not os.path.exists(hea_path):
        raise FileNotFoundError(
            f"'{hea_path}' bulunamadı! .dat dosyasıyla aynı klasörde, "
            f"aynı isimli bir .hea dosyası da olmalı."
        )
 
    record = wfdb.rdrecord(record_name)
 
    n_channels = record.p_signal.shape[1]
    if channel >= n_channels:
        raise ValueError(
            f"Seçilen kanal ({channel}) mevcut değil. "
            f"Bu kayıtta {n_channels} kanal var (0..{n_channels - 1})."
        )
 
    fs = record.fs
    voltage_values = record.p_signal[:, channel]
 
    time = pandas.Series(np.arange(len(voltage_values)) / fs)
    voltage = pandas.Series(voltage_values)
 
    # Mevcut (time, voltage) arayüzünü bozmadan örnekleme hızını da taşıyoruz.
    # main.py bunu okumak isterse: voltage.attrs.get("sampling_rate")
    for s in (time, voltage):
        s.attrs["sampling_rate"] = fs
        s.attrs["n_channels"] = n_channels
 
    if n_channels > 1:
        print(
            f"ℹ️  Kayıtta {n_channels} kanal bulundu, varsayılan olarak "
            f"{channel}. kanal (index) kullanılıyor. Değiştirmek için "
            f"read_ecg_dat(file_path, pandas, channel=1) gibi çağırabilirsin."
        )
 
    return time, voltage
 
 
def read_ecg_data(file_path: str) -> Tuple[Any, Any]:
    try:
        import pandas
    except Exception as e:
        print("poetry install yapp")

    if file_path.endswith('.csv'):
        return read_ecg_csv(file_path, pandas)
    elif file_path.endswith('.txt'):
        return read_ecg_txt(file_path, pandas)
    elif file_path.endswith('.dat'):
        return read_ecg_dat(file_path, pandas)
    else:
        raise ValueError("Desteklenmeyen dosya biçimi! Lütfen .csv, .txt veya .dat (+ aynı isimli .hea) yükleyin.")
