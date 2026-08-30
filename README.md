# 🫀 Akıllı EKG Analiz ve Aritmi İkaz Paneli (CLI Sürümü)

Python, **NeuroKit2** ve **Google Gemini (LLM)** kullanılarak geliştirilen; EKG (elektrokardiyogram) sinyallerini temizleyen, R-P-Q-S-T noktalarını tespit eden, kalp atım hızı ve ritim düzensizliği metriklerini hesaplayan ve isteğe bağlı olarak yapay zekâ destekli özet rapor üreten bir terminal (CLI) uygulamasıdır.

> Bu, projenin **sadeleştirilmiş sürümüdür**: Streamlit arayüzü (`app.py`) kaldırılmış, tek bir `main.py` giriş noktası etrafında toplanmıştır.

> ⚠️ **Önemli:** Bu araç bir **tıbbi teşhis cihazı değildir**. Ürettiği tüm ikaz ve raporlar otomatik bir yazılımın çıktısıdır; kesin tanı için mutlaka bir kardiyoloji uzmanına danışılmalıdır.

---

## 🎯 Proje Ne Yapar?

1. Sinyali gürültüden arındırır (bandpass filtreleme, NeuroKit2 ile).
2. R tepelerini ve P-QRS-T bileşenlerini tespit eder.
3. Ortalama, minimum ve maksimum **BPM** (dakikadaki atım) hesaplar.
4. **R-R aralıklarının** değişim katsayısını (varyansını) hesaplar.
5. Basit kural tabanlı bir motorla **taşikardi / bradikardi / aritmi** ikazları üretir.
6. Analiz grafiklerini `output/` klasörüne **PNG** olarak kaydeder.
7. İsteğe bağlı olarak metrikleri **Google Gemini** modeline göndererek Türkçe, doğal dilde bir "EKG Özet Değerlendirme Raporu" oluşturur.

---

## 📁 Proje Yapısı

```
.
├── main.py                     # Tek giriş noktası (CLI)
├── transform_time_voltage.py   # Dosya okuma (.csv / .txt / .dat+.hea)
├── signal_processing.py        # Sinyal temizleme + ham/temiz karşılaştırma grafiği
├── coord_determ.py             # R/P/Q/S/T tespiti + dalga grafiği
├── analyzer.py                 # BPM / R-R / ikaz hesaplama
├── ai_report.py                # Gemini AI rapor üretimi
├── pyproject.toml              # Poetry bağımlılıkları
├── .env                        # (Sizin oluşturacağınız) Gemini API anahtarı
└── output/                     # Çalıştırınca otomatik oluşur, PNG grafikler burada
```

---

## ⚙️ Kurulum

### 1) Python ve Poetry

- Python **3.10 – 3.12** arası bir sürüm gereklidir.
- Poetry kurulu değilse:
  ```bash
  pip install poetry
  ```
  veya resmi kurulum için: https://python-poetry.org/docs/#installation

### 2) Bağımlılıkları kurun

Tüm dosyaların bulunduğu klasörde:
```bash
poetry install
```
Bu komut `pandas`, `neurokit2`, `wfdb`, `matplotlib`, `google-genai`, `python-dotenv` gibi tüm gerekli kütüphaneleri kurar.

### 3) (İsteğe bağlı) Gemini API anahtarı

AI destekli rapor özelliğini kullanmak isterseniz, proje klasöründe bir `.env` dosyası oluşturup içine şunu yazın:
```
GEMINI_API_KEY=buraya_kendi_api_anahtariniz
```

API anahtarınız yoksa bu adımı atlayabilirsiniz — çalıştırırken `--no-ai` bayrağını kullanmanız yeterli.

---

## ▶️ Kullanım

Temel komut:
```bash
poetry run python main.py <dosya_yolu> [seçenekler]
```

### Parametreler

| Argüman | Zorunlu mu | Açıklama |
|---|---|---|
| `file_path` | Evet | Analiz edilecek `.csv`, `.txt` veya `.dat` dosyasının yolu |
| `--sampling_rate`, `-sr` | Hayır (varsayılan: `1000`) | Örnekleme hızı (Hz). `.dat` dosyalarında `.hea` header'ından otomatik okunursa bu değer göz ardı edilir |
| `--output-dir`, `-o` | Hayır (varsayılan: `output`) | Grafiklerin kaydedileceği klasör |
| `--no-ai` | Hayır | Verilirse Gemini AI rapor adımı tamamen atlanır (API anahtarı gerekmez) |

### Örnekler

**CSV dosyası ile (AI raporu dahil):**
```bash
poetry run python main.py ornek_ekg.csv --sampling_rate 500
```

**AI raporu olmadan, hızlı test:**
```bash
poetry run python main.py ornek_ekg.csv --no-ai
```

**Farklı bir çıktı klasörüne kaydetme:**
```bash
poetry run python main.py ornek_ekg.csv -o sonuclar/hasta_123
```

**WFDB (.dat) formatı ile:**
```bash
poetry run python main.py kayit.dat
```
> `.dat` dosyasını verirken **aynı klasörde, aynı isimli bir `.hea` dosyasının** da bulunması zorunludur (örn. `kayit.dat` + `kayit.hea`). Kod `.hea`'yi otomatik bulur; `.hea` dosyasını ayrıca argüman olarak vermenize gerek yoktur. Örnekleme hızı da genelde `.hea` içinden otomatik okunur.

---

## 🗂️ Desteklenen Dosya Formatları

| Format | Açıklama |
|--------|----------|
| `.csv` | İlk sütun zaman, ikinci sütun voltaj olacak şekilde iki sütunlu CSV |
| `.txt` | Boşlukla ayrılmış, başlıksız metin dosyası (1. sütun zaman, 2. sütun voltaj; tek sütunsa doğrudan voltaj kabul edilir) |
| `.dat` + `.hea` | WFDB ikili kayıt formatı — iki dosya da aynı klasörde, aynı isimli olmalı (örn. `100.dat` + `100.hea`) |

---

## 🖥️ Çalıştırma Adım Adım Ne Yapar?

```
main()
 ├─ [1/5] read_ecg_data(file_path)              → transform_time_voltage.py
 │         Dosya uzantısına göre .csv/.txt/.dat okuma fonksiyonlarından
 │         doğru olanını seçer.
 │
 ├─ [2/5] cleaning_signals(voltage, sr)          → signal_processing.py
 │         NeuroKit2 ecg_clean ile sinyal temizlenir.
 │         save_ecg_comparison_plot(...) çağrılır
 │         → output/filtered_signal.png kaydedilir.
 │
 ├─ [3/5] all_save_png(cleaned_signal, sr, output_dir) → coord_determ.py
 │         ├─ detect_r_peaks()   → R tepeleri bulunur (NeuroKit2 ecg_peaks)
 │         ├─ detect_ecg_waves() → P, Q, S, T noktaları bulunur (ecg_delineate)
 │         └─ save_ecg_waves_plot(...)
 │              → output/waves_detected.png kaydedilir.
 │         rpeaks_info ve waves_info döndürülür (tekrar hesaplama yapılmaz).
 │
 ├─ [4/5] analyze_ecg_metrics(r_peaks, sr)       → analyzer.py
 │         ├─ calculate_rr_intervals()
 │         ├─ calculate_bpm()
 │         ├─ calculate_rr_variance()
 │         └─ detect_alerts()
 │         → BPM, R-R varyansı, durum ve ikaz listesi terminale yazdırılır.
 │
 └─ [5/5] generate_ecg_report(analysis_results)  → ai_report.py  (--no-ai verilmediyse)
           GEMINI_API_KEY kontrol edilir, prompt hazırlanır,
           Gemini modeline gönderilir, Türkçe rapor terminale yazdırılır.
```

Çalıştırma bittiğinde `output/` klasöründe (veya `--output-dir` ile belirttiğiniz klasörde) şu iki grafik oluşur:
- `filtered_signal.png` — ham ve temizlenmiş sinyal karşılaştırması
- `waves_detected.png` — R/P/Q/S/T noktalarının işaretlendiği sinyal grafiği

---

## ⚠️ Kural Tabanlı İkazlar

| Koşul | Uyarı |
|---|---|
| Ortalama BPM > 100 | ⚠️ Taşikardi Riski (Yüksek Kalp Atım Hızı) |
| Ortalama BPM < 60 | ⚠️ Bradikardi Riski (Düşük Kalp Atım Hızı) |
| R-R değişim katsayısı > %12 | ⚠️ Düzensiz Ritim (Aritmi Riski) |
| Yukarıdakilerin hiçbiri | ✅ Sinyal Değerleri Normal Aralıkta |

---

## 🧩 Modül / Fonksiyon Haritası

### `transform_time_voltage.py`
| Fonksiyon | Görevi |
|---|---|
| `read_ecg_csv(file_path, pandas)` | CSV dosyasından zaman/voltaj sütunlarını okur |
| `read_ecg_txt(file_path, pandas)` | Boşlukla ayrılmış TXT dosyasını okur |
| `read_ecg_dat(file_path, pandas, channel=0)` | WFDB `.dat`+`.hea` kaydını `wfdb` ile okur, örnekleme hızını `voltage.attrs["sampling_rate"]` içine ekler |
| `read_ecg_data(file_path)` | Uzantıya göre doğru okuma fonksiyonunu çağıran giriş noktası |

### `signal_processing.py`
| Fonksiyon | Görevi |
|---|---|
| `cleaning_signals(ecg_signal, sampling_rate)` | NeuroKit2 `ecg_clean` ile sinyali temizler |
| `save_ecg_comparison_plot(ecg_signal, cleaned_signal, output_dir)` | Ham/temiz sinyal karşılaştırma grafiğini PNG olarak kaydeder |

### `coord_determ.py`
| Fonksiyon | Görevi |
|---|---|
| `detect_r_peaks(cleaned_signal, sampling_rate)` | NeuroKit2 `ecg_peaks` ile R tepelerini bulur |
| `detect_ecg_waves(cleaned_signal, rpeaks_info, sampling_rate)` | NeuroKit2 `ecg_delineate` ile P, Q, S, T noktalarını bulur |
| `get_valid_peaks(waves_info, peak_name)` | NaN olmayan peak indekslerini filtreler |
| `save_ecg_waves_plot(...)` | R/P/Q/S/T noktalarını grafikte gösterip PNG olarak kaydeder |
| `all_save_png(cleaned_signal, sampling_rate, output_dir)` | Yukarıdaki fonksiyonları sırayla çağırır, `(rpeaks_info, waves_info)` döndürür |

### `analyzer.py`
| Fonksiyon | Görevi |
|---|---|
| `calculate_rr_intervals(r_peaks, sampling_rate)` | R tepeleri arasındaki süreleri (saniye) hesaplar |
| `calculate_bpm(rr_intervals)` | Anlık/ortalama/min/maks BPM hesaplar |
| `calculate_rr_variance(rr_intervals)` | R-R değişim katsayısını (%) hesaplar |
| `detect_alerts(mean_bpm, rr_variance_pct)` | Kurallara göre durum ve ikaz listesi üretir |
| `analyze_ecg_metrics(r_peaks, sampling_rate)` | Tüm hesaplamaları birleştirip tek bir sonuç sözlüğü döndürür |

### `ai_report.py`
| Fonksiyon | Görevi |
|---|---|
| `generate_ecg_report(analysis_results)` | Metrikleri Google Gemini API'sine gönderir, Türkçe özet rapor üretip döndürür |

### `main.py`
| Fonksiyon | Görevi |
|---|---|
| `main()` | CLI giriş noktası; argümanları okur, yukarıdaki tüm modülleri sırasıyla çağırır |

---

## 🧪 Test Verisi Olmadan Deneme

Elinizde gerçek bir EKG dosyası yoksa, NeuroKit2'nin sentetik EKG üretme özelliğiyle hızlıca test verisi oluşturabilirsiniz:

```bash
poetry run python -c "
import neurokit2 as nk
import pandas as pd

ecg = nk.ecg_simulate(duration=15, sampling_rate=500, heart_rate=75)
pd.DataFrame({'time': [i/500 for i in range(len(ecg))], 'voltage': ecg}).to_csv('test_ekg.csv', index=False)
print('test_ekg.csv oluşturuldu.')
"
poetry run python main.py test_ekg.csv --sampling_rate 500 --no-ai
```

`.dat`/`.hea` formatını denemek isterseniz `wfdb.wrsamp()` fonksiyonuyla da benzer şekilde sentetik bir kayıt üretebilirsiniz — isterseniz bunun için de hazır bir script hazırlayabilirim.

---

## 📦 Bağımlılıklar (`pyproject.toml`)

- `pandas` — veri okuma/işleme
- `neurokit2` — EKG temizleme, peak/dalga tespiti
- `wfdb` — `.dat`/`.hea` formatı okuma
- `matplotlib` — grafik çizimi
- `google-genai` — Gemini API istemcisi
- `python-dotenv` — `.env` dosyasından ortam değişkeni yükleme

Python sürümü: `>=3.10,<3.13`

---

## 🐞 Bilinen Sınırlamalar

- Gemini modeli çağrısı sırasında kullanılan model adının (`ai_report.py` içinde) güncel/kullanılabilir olduğunu Google AI Studio dokümantasyonundan doğrulamanız önerilir.
- `read_ecg_dat` şu an sadece tek kanal (`channel=0`) okur; çok kanallı kayıtlarda farklı bir kanal istiyorsanız `transform_time_voltage.py` içindeki çağrıyı `channel=1` gibi değiştirmeniz gerekir (şu an `main.py` bu parametreyi CLI argümanı olarak sunmuyor).
- `.txt` dosyalarında başlık satırı (header) desteklenmiyor; dosyanın doğrudan sayısal verilerle başlaması gerekir.