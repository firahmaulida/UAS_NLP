"""
app/main.py — FastAPI Backend
Jalankan: python -m app.main
"""
import os
import re
import shutil
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from app.stt import transcribe_speech_to_text
from app.llm import get_gemini_response
from app.tts import transcribe_text_to_speech

app = FastAPI()

os.makedirs("data", exist_ok=True)
app.mount("/data", StaticFiles(directory="data"), name="data")


@app.get("/health")
def health():
    return {"status": "ok"}


def clean_for_tts(text: str) -> str:
    """
    Bersihkan teks sebelum masuk Coqui TTS.
    Mencegah Kernel Size Error akibat emoji, simbol, atau teks terlalu pendek.
    """
    if not text or len(text.strip()) < 2:
        return "Baik, ada yang bisa saya bantu?"
    # Jika teks adalah pesan error dari LLM, ganti dengan fallback
    if text.startswith("Error:") or "ServerError" in text or "{'error'" in text:
        return "Maaf, asisten sedang tidak tersedia. Silakan coba lagi."
    # Hapus emoji dan karakter non-ASCII
    text = text.encode("ascii", "ignore").decode("ascii")
    # Hapus simbol markdown dan karakter bermasalah untuk TTS
    text = re.sub(r"[*#_>/\\{}\[\]@~`]", "", text)
    # Normalkan whitespace
    text = re.sub(r"\s+", " ", text).strip()
    # Length guard — VITS butuh minimal 15 karakter
    if len(text) < 15:
        text = "Baik akhi, " + text
    return text


@app.post("/voice-chat")
async def voice_chat_endpoint(file: UploadFile = File(...)):
    try:
        # ── 1. Simpan audio input ──
        temp_input = "data/input_audio.wav"
        with open(temp_input, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        print(f"[API] Audio tersimpan: {temp_input}")

        # ── 2. STT (Whisper) ──
        print("[API] STT sedang berjalan... (Whisper di CPU butuh ~30-60 detik)")
        with open(temp_input, "rb") as f:
            stt_text = transcribe_speech_to_text(f.read())

        if not stt_text or not stt_text.strip():
            stt_text = "Maaf, suara tidak terdeteksi dengan jelas."
        print(f"[STT] {stt_text}")

        # ── 3. LLM (Gemma) ──
        print("[API] LLM sedang berjalan...")
        llm_text = get_gemini_response(stt_text)
        print(f"[LLM] {llm_text[:120]}")

        # ── 4. TTS (Coqui) ──
        print("[API] TTS sedang berjalan...")
        tts_clean = clean_for_tts(llm_text)
        print(f"[TTS] Input bersih: {tts_clean[:80]}")
        tts_output = transcribe_text_to_speech(tts_clean)

        # ── 5. Pindahkan audio ke lokasi statis ──
        response_path = "data/response.wav"
        if tts_output and os.path.exists(str(tts_output)) and "[ERROR]" not in str(tts_output):
            shutil.move(tts_output, response_path)
            print(f"[TTS] Disimpan ke {response_path}")
        else:
            print(f"[TTS ERROR] {tts_output}")
            return JSONResponse(status_code=500, content={"detail": f"TTS gagal: {tts_output}"})

        # ── 6. Return JSON ──
        return JSONResponse({
            "stt_text"    : stt_text,
            "llm_response": llm_text,
            "audio_url"   : "/audio/response"
        })

    except Exception as e:
        import traceback
        print(f"[ERROR]\n{traceback.format_exc()}")
        return JSONResponse(status_code=500, content={"detail": str(e)})


@app.get("/audio/response")
def serve_audio():
    """Serve file audio TTS hasil pipeline."""
    path = "data/response.wav"
    if not os.path.exists(path):
        return JSONResponse(status_code=404, content={"detail": "Audio tidak ditemukan."})
    return FileResponse(
        path=path,
        media_type="audio/wav",
        headers={"Cache-Control": "no-cache"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        timeout_keep_alive=300,
    )