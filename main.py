def read_ecg_csv(file_path: Any,pandas) -> Tuple[Any, Any]:
    df = pandas.read_csv(file_path)
    
    # .iloc[:, 0] -> Tüm satırlar, 0. (ilk) sütun (Zaman)
    # .iloc[:, 1] -> Tüm satırlar, 1. (ikinci) sütun (Voltaj)
    time = df.iloc[:, 0]
    voltage = df.iloc[:, 1]
    
    return time, voltage


def read_ecg_txt(file_path: Any,pandas) -> Tuple[Any, Any]:
    """TXT formatındaki EKG verisini okur."""
    # sep=r'\s+' -> Boşluk veya Tab karakterlerine göre sütunları ayırır
    # header=None -> İlk satırı veri olarak okur, başlık sanmaz
    df = pandas.read_csv(file_path, sep=r'\s+', header=None, engine='python')
    
    # Eğer dosyada 2 sütun varsa (Zaman ve Voltaj)
    if df.shape[1] >= 2:
        time = df.iloc[:, 0]
        voltage = df.iloc[:, 1]
    else:
        # Tek sütun varsa (Sadece Voltaj yazıyorsa)
        time = None
        voltage = df.iloc[:, 0]
        
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
    else:
        raise ValueError("Desteklenmeyen dosya biçimi! Lütfen .csv veya .txt yükleyin.")