import os
import uuid
import tempfile
import atexit
from TTS.api import TTS

# Path dinamis
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Path ke folder utilitas TTS (untuk cache model)
COQUI_DIR = os.path.join(BASE_DIR, "coqui_utils")
os.makedirs(COQUI_DIR, exist_ok=True)

# Gunakan model Coqui TTS untuk bahasa Indonesia (VITS)
# Model akan di-download otomatis ke COQUI_DIR saat pertama kali dijalankan
TTS_MODEL_NAME = "tts_models/id_ID/glow-tts/glow-tts"
TTS_GPU_FLAG = False  # Set ke True jika punya GPU CUDA, False untuk CPU

# Inisialisasi TTS engine sekali saja (singleton pattern)
_tts_engine = None

# Track temp files untuk cleanup
_temp_files = []


def _cleanup_temp_files():
    """Bersihkan semua temp files yang telah dibuat"""
    for temp_file in _temp_files:
        try:
            if os.path.exists(temp_file):
                os.remove(temp_file)
                print(f"[CLEANUP] Deleted temp file: {temp_file}")
        except Exception as e:
            print(f"[WARNING] Could not delete {temp_file}: {e}")
    _temp_files.clear()


# Register cleanup saat program exit
atexit.register(_cleanup_temp_files)


def _get_tts_engine():
    """Dapatkan instance TTS engine (lazy loading)."""
    global _tts_engine
    if _tts_engine is None:
        try:
            print("[INFO] Loading Coqui TTS model...")
            _tts_engine = TTS(model_name=TTS_MODEL_NAME, gpu=TTS_GPU_FLAG)
        except Exception as e:
            print(f"[WARNING] Failed to load TTS model: {e}")
            print("[INFO] Fallback: akan menggunakan default model English")
            _tts_engine = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", gpu=TTS_GPU_FLAG)
    return _tts_engine


def transcribe_text_to_speech(text: str) -> str:
    """
    Fungsi untuk mengonversi teks menjadi suara menggunakan Coqui TTS.
    
    Args:
        text (str): Teks yang akan diubah menjadi suara.
    
    Returns:
        str: Path ke file audio hasil konversi (disimpan di temp).
              File akan otomatis dihapus saat program selesai.
    """
    path = _tts_with_coqui(text)
    if not isinstance(path, str) or "[ERROR]" not in path:
        _temp_files.append(path)  # Track untuk cleanup nanti
    return path


def _tts_with_coqui(text: str) -> str:
    """
    Generate speech dari text menggunakan Coqui TTS.
    Hasil akan disimpan di temp folder (otomatis dibersihkan).
    
    Args:
        text (str): Teks untuk di-synthesize
    
    Returns:
        str: Path ke file output atau error message
    """
    tmp_dir = tempfile.gettempdir()
    output_path = os.path.join(tmp_dir, f"tts_{uuid.uuid4()}.wav")
    
    try:
        engine = _get_tts_engine()
        # Synthesize teks menjadi speech dan simpan ke file
        engine.tts_to_file(
            text=text,
            file_path=output_path
        )
        print(f"[INFO] TTS Success: {output_path}")
        return output_path
    except Exception as e:
        print(f"[ERROR] TTS failed: {e}")
        return f"[ERROR] Failed to synthesize speech: {str(e)}"


# --- UNTUK MENGETES ---
if __name__ == "__main__":
    test_text = "Assalamualaikum, ini adalah tes dari Coqui TTS untuk menghasilkan suara bahasa Indonesia."
    print("Sedang memproses text-to-speech...")
    print(f"Input: {test_text}")
    print("-" * 50)
    
    result = transcribe_text_to_speech(test_text)
    print(f"Output: {result}")
    print("-" * 50)
    print("[INFO] Temp files akan dibersihkan otomatis saat program selesai")