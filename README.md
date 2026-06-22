# 🕋 Asisten Umrah: Multilingual Speech-to-Speech System

> **UAS Praktikum Pemrosesan Bahasa Alami 2025/2026**  
> Implementasi Sistem Speech-to-Speech End-to-End dengan Dukungan Code-Switching (ID-EN-AR).

## 📝 Deskripsi Proyek

Proyek ini merupakan sistem chatbot berbasis suara yang dirancang khusus untuk membantu jamaah dalam domain perjalanan Umrah dan Haji. Sistem ini mampu menangani fenomena _code-switching_ (percampuran bahasa Indonesia, Inggris, dan Arab) secara _end-to-end_ melalui pipeline integrasi STT, LLM, dan TTS.

### Alur Kerja (Pipeline):

`Input Suara (User)` -> `Audio Preprocessing (FFmpeg)` -> `STT (OpenAI Whisper)` -> `LLM (Google Gemma-4-31b-it)` -> `TTS (Coqui VITS Indonesian)` -> `Output Suara (Asisten)`

## 🚀 Fitur Utama

- **Multilingual Support:** Mampu mengenali dan merespons dalam campuran 3 bahasa (Indonesia, Inggris, Arab).
- **Robust Pipeline:** Dilengkapi dengan _Rate Limiter_ dan _Auto-Retry_ untuk menangani batasan API Google AI Studio.
- **Data Integrity (Rebuilder):** Menyediakan skrip khusus untuk merekonstruksi seluruh database suara balasan agar sinkron dengan data teks di CSV.
- **Data Cleaning:** Pembersihan teks otomatis guna menjamin stabilitas modul TTS (Anti-Kernel Error).
- **Batch Processing:** Script otomatis untuk melakukan evaluasi massal terhadap 571 data audio korpus.

## 🛠️ Teknologi yang Digunakan

| Komponen     | Teknologi      | Varian/Model                        |
| :----------- | :------------- | :---------------------------------- |
| **STT**      | OpenAI Whisper | `base` (Python Version)             |
| **LLM**      | Google GenAI   | `gemma-4-31b-it`                    |
| **TTS**      | Coqui TTS      | `Indonesian VITS Lokal (Wikidepia)` |
| **Backend**  | FastAPI        | REST API Framework                  |
| **Frontend** | Gradio         | Web Interface                       |
| **Tooling**  | FFmpeg         | Audio Resampling & Normalization    |

## 📦 Struktur Folder

```text
.
├── app/
│   ├── main.py             # Entry point Backend (FastAPI)
│   ├── stt.py              # Modul Speech-to-Text
│   ├── llm.py              # Modul Large Language Model
│   ├── tts.py              # Modul Text-to-Speech
│   └── coqui_utils/        # Folder model TTS (.pth & .json)
├── data/
│   ├── corpus/             # Dataset audio input (Kelas A & B)
│   ├── results_tts/        # Hasil suara balasan chatbot final
│   └── audio_standardized/ # Audio hasil preprocessing
├── gradio_app/
│   └── app.py              # Entry point Frontend (Gradio UI)
├── preprocess_audio.py     # Script standardisasi audio massal
├── analisis_pipeline.py    # Script evaluasi massal 571 audio
├── tts_final_rebuilder.py  # Script penyelamatan & rebuild suara massal
├── hitung_wer_massal.py    # Script perhitungan akurasi WER/CER
├── .env                    # API Key (Jangan di-upload!)
├── .gitignore              # Mengabaikan file sensitif & venv
└── requirements.txt        # Daftar library python
```

## ⚙️ Cara Instalasi

1. **Clone Repository:**

   ```bash
   git clone https://github.com/username/UAS-Praktikum-Pemrosesan-Bahasa-Alami.git
   cd UAS-Praktikum-Pemrosesan-Bahasa-Alami
   ```

2. **Setup Virtual Environment:**

   ```bash
   python -m venv env
   .\env\Scripts\activate  # Windows
   source env/bin/activate # Linux/Mac
   ```

3. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   pip install -U google-genai jiwer pandas
   ```

4. **FFmpeg:**
   Pastikan file `ffmpeg.exe` berada di folder utama proyek (untuk pengguna Windows).

## 🏃 Cara Menjalankan

Pastikan kamu menjalankan dua terminal secara bersamaan:

**Terminal 1 (Backend):**

```bash
python -m app.main
```

**Terminal 2 (Frontend):**

```bash
python gradio_app/app.py
```

Akses chatbot melalui browser di: `http://127.0.0.1:7860`

## 📊 Analisis & Eksperimen

Untuk menjalankan pengujian massal terhadap seluruh korpus audio:

1. **Preprocessing:** `python preprocess_audio.py`
2. **Evaluasi Pipeline:** `python analisis_pipeline.py`
3. **Penyelamatan TTS:** `python tts_final_rebuilder.py` (Gunakan ini jika ada kegagalan sintesis suara pada tahap evaluasi).
4. **Hitung Akurasi:** `python hitung_wer_massal.py`

## 👤 Identitas

- **Nama:** Firah Maulida
- **NPM:** 2308107010034
- **Kelas:** Praktikum NLP Kelas A
