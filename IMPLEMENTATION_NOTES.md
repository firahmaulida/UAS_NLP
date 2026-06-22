# 📋 Implementasi Checklist - UAS Praktikum Pemrosesan Bahasa Alami

## ✅ Status: SELESAI DIPERBAIKI

---

### 1. ✅ **Virtual Environment (venv)**

- **Status**: ✓ SESUAI
- **Lokasi**: `env/` folder
- **Catatan**: Sudah ada dan dikonfigurasi

---

### 2. ✅ **Coqui TTS Versi Terbaru + Transformers v5.0**

- **Status**: ✓ SUDAH DIPERBAIKI
- **Perubahan**:
  - `coqui-tts==0.26.0` → `coqui-tts==0.27.05`
  - `transformers==4.51.3` → `transformers==5.0`
- **File**: `requirements.txt`
- **Action**: Jalankan `pip install -r requirements.txt` untuk update

---

### 3. ✅ **Model Gemma-4 (bukan Gemini-2.5)**

- **Status**: ✓ SUDAH DIPERBAIKI
- **Perubahan**:
  - Model: `gemini-2.5-flash` → `gemma-4-31b-it`
  - Sesuai dengan instruksi UAS
- **File**: `app/llm.py` baris ~38
- **Catatan**: Pastikan API key punya akses ke model Gemma-4

---

### 4. ✅ **Text Normalization**

- **Status**: ✓ SUDAH DIIMPLEMENTASI
- **Fitur**:
  - Strip whitespace
  - Hapus extra spaces
  - Standarkan format teks
  - Preserve karakter Arab (untuk teks Umrah)
- **File**: `app/llm.py` (fungsi `normalize_text()`)
- **Location**: Teks dinormalisasi sebelum dikirim ke Gemini

---

### 5. ✅ **Rate Limiting & RPM/RPD Monitoring**

- **Status**: ✓ SUDAH DIIMPLEMENTASI
- **Fitur**:
  - Class `RateLimiter` untuk tracking requests
  - Monitor RPM (Requests Per Minute) = 15
  - Monitor RPD (Requests Per Day) = 32000
  - Auto-delay jika limit tercapai
- **File**: `analisis_pipeline.py`
- **Setting**: Dapat dikonfigurasi di variabel `RPM_LIMIT` dan `RPD_LIMIT`

---

### 6. ✅ **.env & .gitignore - Keamanan**

- **Status**: ✓ SUDAH DIPERBAIKI
- **Perubahan**:
  - `.env`: API KEY diganti dengan placeholder `your_gemini_api_key_here`
  - `.gitignore`: Dibuat lengkap (kosong sebelumnya)
  - `.env.example`: Template untuk setup baru
- **File**:
  - `.env` (jangan commit!)
  - `.gitignore` (include `.env`)
  - `.env.example` (untuk dokumentasi)
- **⚠️ PENTING**: Regenerate API KEY di Google Console karena sudah terekspos

---

### 7. ✅ **Path Dinamis (os.path)**

- **Status**: ✓ SUDAH DIPERBAIKI
- **Perubahan**:
  - Semua path menggunakan `os.path.join()` dan `os.path.abspath()`
  - Kompatibel dengan Windows dan Linux
  - Tidak ada hardcoded path lagi
- **File**:
  - `app/stt.py`
  - `app/tts.py`
  - `app/llm.py`
  - `app/main.py`
  - `analisis_pipeline.py`

---

### 8. ✅ **Temp File Cleanup**

- **Status**: ✓ SUDAH DIPERBAIKI
- **Fitur**:
  - STT: Cleanup temp audio file setelah transcribe
  - TTS: Track dan cleanup via `atexit` handler
  - Semua temp file dihapus otomatis saat program selesai
- **File**:
  - `app/stt.py` (native cleanup in try-finally)
  - `app/tts.py` (atexit handler)

---

### 9. ✅ **Complete Pipeline Integration**

- **Status**: ✓ SUDAH DIIMPLEMENTASI
- **Fitur**:
  - STT → LLM → TTS dalam satu workflow
  - Interactive CLI untuk testing
  - Error handling lengkap
  - Timestamp tracking untuk setiap request
- **File**: `app/main.py` (baru, previously empty)
- **Usage**: `python -m app.main`

---

### 10. ✅ **G2P (Grapheme to Phoneme) Support**

- **Status**: ⚠️ AVAILABLE (Belum digunakan)
- **Package**: `g2p-id==0.0.4` sudah di `requirements.txt`
- **Catatan**: Jika TTS masih terdengar tidak natural, bisa implementasi G2P
- **Dokumentasi**: Lihat `analisis_pipeline.py` comment untuk implementasi

---

## 📦 File yang Sudah Diperbaiki

| File                   | Perubahan                            | Status |
| ---------------------- | ------------------------------------ | ------ |
| `requirements.txt`     | Coqui TTS 0.27.05 + Transformers 5.0 | ✓      |
| `app/llm.py`           | Model Gemma-4 + Text normalization   | ✓      |
| `app/stt.py`           | Path dinamis + cleanup               | ✓      |
| `app/tts.py`           | Path dinamis + auto cleanup          | ✓      |
| `app/main.py`          | Complete pipeline (baru)             | ✓      |
| `analisis_pipeline.py` | Path dinamis + RPM/RPD monitoring    | ✓      |
| `.gitignore`           | Baru dibuat (sebelumnya kosong)      | ✓      |
| `.env`                 | API KEY diamankan                    | ✓      |
| `.env.example`         | Template baru                        | ✓      |

---

## 🔧 Setup Instructions (PENTING!)

### 1. **Regenerate API Key** (Karena sudah terekspos)

```bash
# 1. Buka https://aistudio.google.com/apikey
# 2. Delete API key lama
# 3. Generate API key baru
# 4. Copy ke .env
```

### 2. **Setup dari Awal**

```bash
# Clone repo atau buka folder project
cd "d:\UAS ML\UAS-Praktikum-Pemrosesan-Bahasa-Alami"

# Activate virtual environment
env\Scripts\activate

# Update dependencies
pip install -r requirements.txt

# Copy .env.example ke .env dan isi API key
copy .env.example .env
# Edit .env dan isi GEMINI_API_KEY dengan key baru

# Test pipeline
python -m app.main
```

### 3. **Run Analisis Pipeline**

```bash
python analisis_pipeline.py
```

### 4. **Test Individual Components**

```bash
# Test STT
python app/stt.py

# Test TTS
python app/tts.py

# Test LLM
python app/llm.py
```

---

## ⚠️ Important Notes

1. **API Key Exposure**: API key lama sudah terekspos di git history. **HARUS** regenerate di Google Console!
2. **Gemma-4 Access**: Pastikan akun Google memiliki akses ke model `gemma-4-31b-it`
3. **Rate Limiting**: RPM default 15 req/min (sesuai free tier Gemini). Sesuaikan jika ada upgrade akun
4. **Windows vs Linux**: Code sudah kompatibel, gunakan Python 3.11+ untuk consistency
5. **GPU Support**: TTS akan auto-detect GPU jika ada (CUDA). Set `TTS_GPU_FLAG=True` di `tts.py` jika ingin force GPU

---

## 📊 Implementasi Summary

| Requirement     | Before      | After            | Status     |
| --------------- | ----------- | ---------------- | ---------- |
| venv            | ✓ Ada       | ✓ Ada            | ✓ OK       |
| Coqui TTS       | 0.26.0      | 0.27.05          | ✓ UPDATED  |
| Transformers    | 4.51.3      | 5.0              | ✓ UPDATED  |
| Model           | gemini-2.5  | gemma-4-31b      | ✓ FIXED    |
| RPM/RPD         | Jeda manual | Smart monitoring | ✓ IMPROVED |
| Text Norm       | ✗ Tidak ada | ✓ Implementasi   | ✓ ADDED    |
| Path Dynamic    | ⚠️ Partial  | ✓ Complete       | ✓ FIXED    |
| Cleanup         | ✓ Partial   | ✓ Auto           | ✓ IMPROVED |
| .env/.gitignore | ⚠️ Risky    | ✓ Aman           | ✓ SECURED  |

---

## 🚀 Next Steps

1. **URGENT**: Regenerate API key di Google Console
2. Update `.env` dengan API key baru
3. Run `pip install -r requirements.txt` untuk install dependencies terbaru
4. Test dengan `python -m app.main`
5. Jika ada issue dengan TTS sound quality, implement G2P dari `g2p-id`

---

**Last Updated**: May 20, 2026  
**Version**: 1.0 (Implementation Complete)
