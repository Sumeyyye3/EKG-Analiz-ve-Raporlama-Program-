# 🫀 Akıllı EKG Analiz ve Aritmi İkaz Paneli

Python, **NeuroKit2**, **Streamlit** ve **LLM** kullanılarak geliştirilen EKG analiz ve aritmi ikaz sistemi.

## 🎯 Proje

Kullanıcının yüklediği **CSV/TXT EKG verilerini** analiz eder.

Sistem:

- EKG sinyalini temizler ve filtreler.
- **R tepelerini ve P-QRS-T** bileşenlerini tespit eder.
- Ortalama ve anlık **BPM** hesaplar.
- **R-R aralıklarını** analiz eder.
- Temel ritim düzensizlikleri için ikaz üretir.
- Analiz grafiklerini **PNG** olarak kaydeder.
- Sonuçları **Streamlit Dashboard** üzerinde gösterir.
- EKG metriklerini **LLM'e göndererek özet rapor** oluşturur.

## ⚠️ Akıllı İkazlar

| Koşul | Uyarı |
|---|---|
| BPM > 100 | ⚠️ Taşikardi Riski |
| BPM < 60 | ⚠️ Bradikardi Riski |
| R-R belirgin düzensiz | ⚠️ Düzensiz Ritim |

## 🔄 Sistem Akışı

```text
EKG (CSV / TXT / Sentetik)
          ↓
       NeuroKit2
          ↓
   Sinyal Temizleme
          ↓
 P-QRS-T + R Peak Detection
          ↓
    BPM + R-R Analizi
          ↓
      Kural Motoru
       ↙       ↘
 Streamlit     LLM
 Dashboard     Rapor