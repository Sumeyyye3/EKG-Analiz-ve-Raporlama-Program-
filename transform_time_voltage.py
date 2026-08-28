from typing import Any, Tuple


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