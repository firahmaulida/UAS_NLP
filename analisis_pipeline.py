import os
import csv
import time
import shutil
import re
from datetime import datetime
from app.stt import transcribe_speech_to_text
from app.llm import get_gemini_response
from app.tts import transcribe_text_to_speech

# 1. KONFIGURASI PATH DINAMIS
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Gunakan folder audio yang sudah dibersihkan (sesuai saran aslab)
AUDIO_DIR = os.path.join(BASE_DIR, "data", "corpus", "audio")
OUTPUT_CSV = os.path.join(BASE_DIR, "hasil_eksperimen_FINAL_LENGKAP.csv")
TTS_RESULT_DIR = os.path.join(BASE_DIR, "data", "results_tts")

# 2. KONFIGURASI RATE LIMIT (Saran PDF Hal 9)
RPM_LIMIT = 12  # Kita set 12 agar lebih aman dari batas 15

class RateLimiter:
    def __init__(self, rpm_limit=12):
        self.rpm_limit = rpm_limit
        self.requests = []
    
    def wait_if_needed(self):
        now = time.time()
        # Hapus catatan request yang sudah lebih dari 1 menit
        self.requests = [t for t in self.requests if now - t < 60]
        if len(self.requests) >= self.rpm_limit:
            wait_time = 60 - (now - self.requests[0])
            print(f"\n[WAIT] Limit tercapai. Menunggu {wait_time:.1f} detik...")
            time.sleep(wait_time + 1)
            self.requests = []

    def record(self):
        self.requests.append(time.time())

# 3. FUNGSI PEMBERSIH (Agar CSV Rapi & TTS 100% Sukses)
def clean_text_for_csv(text):
    """Menghilangkan Enter agar CSV tetap satu baris"""
    if not text: return ""
    return text.replace('\n', ' ').replace('\r', ' ').replace('"', "'").strip()

def clean_text_for_tts(text):
    """Buang emoji & simbol agar tidak Kernel Error di TTS"""
    if not text: return "Baik akhi."
    # Buang karakter non-teks (emoji)
    text = text.encode('ascii', 'ignore').decode('ascii')
    # Buang simbol markdown
    text = re.sub(r'[*#_>-]', '', text)
    # Pastikan teks cukup panjang untuk Kernel VITS
    if len(text) < 15:
        text = "Alhamdulillah, " + text
    return text.strip()

def main():
    # Pastikan folder output ada
    if not os.path.exists(TTS_RESULT_DIR): os.makedirs(TTS_RESULT_DIR)
    if not os.path.exists(AUDIO_DIR):
        print(f"❌ Error: Folder {AUDIO_DIR} tidak ditemukan!")
        return

    limiter = RateLimiter(rpm_limit=RPM_LIMIT)
    folders = ['A', 'B'] 

    with open(OUTPUT_CSV, mode='w', newline='', encoding='utf-8') as f:
        fieldnames = ['folder', 'filename', 'stt_text', 'llm_response', 'tts_path', 'timestamp']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        print("--- MEMULAI ANALISIS FULL PIPELINE (100% SUCCESS TARGET) ---")

        for kelas in folders:
            path_kelas = os.path.join(AUDIO_DIR, kelas)
            if not os.path.exists(path_kelas): continue
            
            files = sorted([f for f in os.listdir(path_kelas) if f.endswith('.wav')])
            print(f"\n>>> Memproses Kelas {kelas} ({len(files)} file)")

            for idx, filename in enumerate(files, 1):
                full_audio_path = os.path.join(path_kelas, filename)
                print(f"[{idx}/{len(files)}] {filename}...", end=" ", flush=True)

                try:
                    # --- TAHAP 1: STT (LOKAL) ---
                    with open(full_audio_path, "rb") as af:
                        stt_raw = transcribe_speech_to_text(af.read())
                    stt_final = clean_text_for_csv(stt_raw)

                    # --- TAHAP 2: LLM (DENGAN RETRY & LIMITER) ---
                    limiter.wait_if_needed()
                    llm_final = "Gagal mendapatkan jawaban"
                    for attempt in range(3): # Coba sampai 3 kali jika server sibuk
                        res = get_gemini_response(stt_final)
                        if "Error" not in res and "ServerError" not in res:
                            llm_final = clean_text_for_csv(res)
                            limiter.record()
                            break
                        else:
                            print(f"(Retry {attempt+1})...", end=" ")
                            time.sleep(10)
                    
                    # --- TAHAP 3: TTS (DENGAN PEMBERSIH TEKS) ---
                    tts_path_csv = "FAILED"
                    if "Gagal" not in llm_final:
                        teks_bersih = clean_text_for_tts(llm_final)
                        temp_tts = transcribe_text_to_speech(teks_bersih)
                        
                        if temp_tts and os.path.exists(temp_tts):
                            new_name = f"res_{filename}"
                            final_dest = os.path.join(TTS_RESULT_DIR, new_name)
                            shutil.move(temp_tts, final_dest)
                            tts_path_csv = f"data/results_tts/{new_name}"

                    # --- TAHAP 4: SIMPAN HASIL ---
                    writer.writerow({
                        'folder': kelas,
                        'filename': filename,
                        'stt_text': stt_final,
                        'llm_response': llm_final,
                        'tts_path': tts_path_csv,
                        'timestamp': datetime.now().isoformat()
                    })
                    print("✅ DONE")

                except Exception as e:
                    print(f"❌ ERROR: {e}")

    print(f"\n✅ PROSES SELESAI!")
    print(f"CSV Final: {OUTPUT_CSV}")
    print(f"Total Suara: {len(os.listdir(TTS_RESULT_DIR))} file di folder results_tts")

if __name__ == "__main__":
    main()