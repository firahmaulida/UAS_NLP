"""
gradio_app/app.py
Jalankan: python gradio_app/app.py
Pastikan FastAPI sudah jalan dulu: python -m app.main
"""
import os
import tempfile
import requests
import gradio as gr
import scipy.io.wavfile
import numpy as np

API_BASE        = "http://127.0.0.1:8000"
REQUEST_TIMEOUT = 300   # 5 menit — Whisper di CPU butuh ~30-60 detik

print("--- Memulai Gradio App ---")


def check_api():
    try:
        r = requests.get(f"{API_BASE}/health", timeout=5)
        return "🟢 API Online — Siap digunakan!" if r.status_code == 200 else "🔴 API Error"
    except:
        return "🔴 API Offline — Jalankan: python -m app.main"


def voice_chat(audio):
    if audio is None:
        return None, "⚠️ Rekam suara dulu!", "", ""

    try:
        sr, audio_data = audio

        # Konversi ke int16 (format WAV standar)
        if audio_data.dtype != np.int16:
            audio_data = (audio_data * 32767).clip(-32768, 32767).astype(np.int16)

        # Simpan audio input
        os.makedirs("data", exist_ok=True)
        temp_input = "data/input_gradio.wav"
        scipy.io.wavfile.write(temp_input, sr, audio_data)

        print(f"[Gradio] Kirim ke {API_BASE}/voice-chat")
        print(f"[Gradio] Mohon tunggu 30-90 detik (Whisper berjalan di CPU)...")

        with open(temp_input, "rb") as f:
            response = requests.post(
                f"{API_BASE}/voice-chat",
                files={"file": ("voice.wav", f, "audio/wav")},
                timeout=REQUEST_TIMEOUT
            )

        if response.status_code != 200:
            try:
                detail = response.json().get("detail", response.text)
            except:
                detail = response.text
            return None, f"❌ Error Server: {detail}", "", ""

        data         = response.json()
        stt_text     = data.get("stt_text", "")
        llm_response = data.get("llm_response", "")
        audio_url    = data.get("audio_url", "")

        print(f"[Gradio] STT: {stt_text[:80]}")
        print(f"[Gradio] LLM: {llm_response[:80]}")

        # Download audio TTS → simpan ke file path untuk Gradio
        # PENTING: Gradio butuh file path lokal, bukan URL string!
        audio_out_path = None
        if audio_url:
            audio_resp = requests.get(f"{API_BASE}{audio_url}", timeout=60)
            if audio_resp.status_code == 200:
                tmp = tempfile.NamedTemporaryFile(
                    delete=False, suffix=".wav", dir="data"
                )
                tmp.write(audio_resp.content)
                tmp.close()
                audio_out_path = tmp.name
                print(f"[Gradio] Audio TTS: {audio_out_path}")

        return audio_out_path, "✅ Sukses! Dengarkan jawaban asisten.", stt_text, llm_response

    except requests.exceptions.ReadTimeout:
        return None, (
            f"❌ Timeout ({REQUEST_TIMEOUT}s).\n"
            "Whisper di CPU lambat. Coba rekam lebih pendek (5-10 detik)."
        ), "", ""
    except requests.exceptions.ConnectionError:
        return None, "❌ API Offline.\nJalankan: python -m app.main", "", ""
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return None, f"❌ Error: {str(e)}", "", ""


with gr.Blocks(
    title="Asisten Umrah 🕌",
    theme=gr.themes.Soft(primary_hue="emerald")
) as demo:

    gr.HTML("""
    <div style='text-align:center; padding:12px'>
        <h1 style='margin-bottom:4px'>🕌 Asisten Umrah</h1>
        <p style='color:gray; font-size:14px'>
            🎙️ Rekam Suara → 📝 Whisper STT → 🤖 Gemma-4 LLM → 🔊 Coqui TTS
        </p>
        <p style='color:orange; font-size:13px'>
            ⏳ Proses butuh 30-90 detik (Whisper berjalan di CPU)
        </p>
    </div>
    """)

    with gr.Row():
        status_api  = gr.Textbox(value=check_api(), label="Status API", interactive=False, scale=4)
        btn_refresh = gr.Button("🔄 Refresh", scale=1, size="sm")

    gr.Markdown("---")

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 🎤 Input Suara")
            audio_input = gr.Audio(
                sources=["microphone", "upload"],
                type="numpy",
                label="Rekam atau Upload Audio"
            )
            btn_kirim = gr.Button("🚀 Kirim ke Asisten", variant="primary", size="lg")
            gr.Markdown("""
**Cara pakai:**
1. Klik 🔴 mulai rekam
2. Bicara singkat (5-10 detik)
3. Klik ⏹ stop
4. Klik **Kirim ke Asisten**
5. Tunggu 30-90 detik
            """)

        with gr.Column(scale=1):
            gr.Markdown("### 🔊 Jawaban Asisten")
            audio_out = gr.Audio(
                type="filepath",
                label="Audio Jawaban (TTS)",
                interactive=False,
                autoplay=True
            )
            status_box = gr.Textbox(label="Status", interactive=False, lines=3)

    gr.Markdown("---")
    gr.Markdown("### 📄 Transkripsi & Jawaban Teks")
    with gr.Row():
        stt_box = gr.Textbox(
            label="📝 Yang Kamu Ucapkan (Whisper STT)",
            lines=3, interactive=False,
            placeholder="Transkripsi suaramu akan muncul di sini..."
        )
        llm_box = gr.Textbox(
            label="🤖 Jawaban Asisten (Gemma-4)",
            lines=3, interactive=False,
            placeholder="Respons asisten akan muncul di sini..."
        )

    btn_refresh.click(fn=check_api, outputs=status_api)
    btn_kirim.click(
        fn=voice_chat,
        inputs=[audio_input],
        outputs=[audio_out, status_box, stt_box, llm_box]
    )

if __name__ == "__main__":
    print("Gradio berjalan di http://127.0.0.1:7860")
    print("Pastikan FastAPI sudah jalan di port 8000!")
    demo.launch(server_name="127.0.0.1", server_port=7860, show_error=True)