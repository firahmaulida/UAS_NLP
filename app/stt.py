import os
import torch
import whisper
import tempfile

# 1. Path dinamis untuk model Whisper
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Lazy loading Whisper model
_whisper_model = None


def _get_whisper_model():
    """Load Whisper model sekali saja (lazy loading)"""
    global _whisper_model
    if _whisper_model is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"[INFO] Loading Whisper STT model on {device}...")
        _whisper_model = whisper.load_model("small", device=device)
    return _whisper_model


def transcribe_speech_to_text(audio_source):
    """
    Transcribe audio file atau bytes menjadi teks.
    
    Args:
        audio_source: Path ke file audio atau bytes data
    
    Returns:
        str: Hasil transkrip teks (default bahasa Indonesia)
    """
    model = _get_whisper_model()
    if model is None:
        raise RuntimeError("Whisper STT model tidak dapat dimuat")

    temp_path = None
    try:
        # Handle bytes input
        if isinstance(audio_source, (bytes, bytearray)):
            temp_f = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            temp_f.write(audio_source)
            temp_f.close()
            temp_path = temp_f.name
            audio_path = temp_path
        else:
            audio_path = audio_source

        # Transcribe dengan bahasa Indonesia
        result = model.transcribe(audio_path, language="id", task="transcribe")
        return result.get("text", "").strip()
        
    finally:
        # Cleanup temp file
        if temp_path is not None:
            try:
                os.remove(temp_path)
            except OSError:
                pass


# --- UNTUK MENGETES ---
if __name__ == "__main__":
    test_audio = "data/corpus/audio/A/2222_audio1.wav"  # Sesuaikan dengan file audio mu
    
    if os.path.exists(test_audio):
        print("Sedang memproses speech-to-text...")
        hasil = transcribe_speech_to_text(test_audio)
        print("-" * 50)
        print(f"Result: {hasil}")
        print("-" * 50)
    else:
        print(f"[ERROR] File audio tidak ditemukan: {test_audio}")