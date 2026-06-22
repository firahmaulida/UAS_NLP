import os
import csv
import shutil
import re
import time
from app.tts import transcribe_text_to_speech

# 1. Konfigurasi
INPUT_CSV = "hasil_eksperimen_RAPI.csv" 
OUTPUT_CSV = "hasil_eksperimen_TOTAL_FINAL.csv"
FINAL_TTS_DIR = os.path.join("data", "results_tts")

def super_clean_text(text):
    if not text or len(str(text)) < 2: 
        return "Alhamdulillah, process complete."
    text = str(text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[*#_>/\\-]', '', text)
    text = text.replace('\n', ' ').replace('\r', ' ')
    text = re.sub(r'\s+', ' ', text).strip()
    if len(text) < 15: text = "Baik akhi, " + text
    return text

def main():
    # Folder tidak dihapus di sini supaya kalau mau lanjut (resume) bisa, 
    # tapi karena tadi terlanjur error, kita biarkan buat ulang saja.
    if not os.path.exists(FINAL_TTS_DIR):
        os.makedirs(FINAL_TTS_DIR, exist_ok=True)

    if not os.path.exists(INPUT_CSV):
        print(f"❌ Error: File {INPUT_CSV} tidak ditemukan!")
        return

    print(f"--- MEMULAI REBUILD TTS (VERSI ANTI-GHOST COLUMN) ---")

    with open(INPUT_CSV, mode='r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        rows = list(reader)
        total = len(rows)

    target_col = 'tts_file_path' if 'tts_file_path' in fieldnames else 'tts_path'

    with open(OUTPUT_CSV, mode='w', newline='', encoding='utf-8') as outfile:
        # PERBAIKAN UTAMA: Menambahkan extrasaction='ignore'
        writer = csv.DictWriter(outfile, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()

        for idx, row in enumerate(rows, 1):
            filename = row['filename']
            teks_jawaban = row['llm_response']

            if not teks_jawaban or "Gagal" in teks_jawaban or "Error" in teks_jawaban:
                row[target_col] = "FAILED (No Text)"
                writer.writerow(row)
                continue

            # Trik: Lewati file yang sudah sukses terbentuk di folder agar cepat (Resume)
            clean_name = f"res_{filename.replace('.wav', '')}.wav"
            final_dest = os.path.join(FINAL_TTS_DIR, clean_name)
            
            if os.path.exists(final_dest):
                print(f"[{idx}/{total}] {filename} already exists. Skipping...", end="\r")
                row[target_col] = f"data/results_tts/{clean_name}"
                writer.writerow(row)
                continue

            print(f"[{idx}/{total}] Processing: {filename}...", end=" ", flush=True)

            success = False
            for attempt in range(1, 4):
                try:
                    teks_bersih = super_clean_text(teks_jawaban)
                    temp_path = transcribe_text_to_speech(teks_bersih)
                    
                    if temp_path and os.path.exists(temp_path):
                        shutil.move(temp_path, final_dest)
                        row[target_col] = f"data/results_tts/{clean_name}"
                        print("✅ OK")
                        success = True
                        break 
                    else:
                        raise Exception("TTS Fail")
                except Exception as e:
                    if attempt < 3:
                        time.sleep(1)
                    else:
                        print(f"❌ FAILED: {e}")
                        row[target_col] = "FAILED"

            writer.writerow(row)

    print(f"\n✅ REBUILD SELESAI!")
    print(f"File CSV: {OUTPUT_CSV}")

if __name__ == "__main__":
    main()