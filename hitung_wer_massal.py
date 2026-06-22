import csv
import re
import os
from jiwer import wer, cer

# 1. KUNCI JAWABAN (Reference)
REFERENCE_MAP = {
    "1": "Aku mau book flight ke Jeddah minggu depan, bisa bantu schedule?",
    "2": "Aku butuh travel umrah simple tapi include Madinah visit",
    "3": "Can you help aku arrange transport dari Jeddah ke Madinah tomorrow",
    "4": "Explain step by step cara apply visa Saudi dengan benar",
    "5": "Ya akhi, uridu book flight ila Jeddah al-usbu'al qadim. Hal bisa bantu ajida afdhal schedule wa rihlatan mubashirah?",
    "6": "Uridu arrange transport min Jeddah ila Madinah ghadan",
    "7": "Book flight ke Jeddah lalu lanjut ke Madinah, schedule terbaik kapan",
    "8": "Uridu schedule trip dari Jeddah ke Makkah besok pagi",
    "9": "Mumkin book transport dari Makkah ke Madinah untuk besok?",
    "10": "Apa perbedaan umrah dan hajj secara detail dalam Islam",
    "11": "Kenapa fasting di Ramadan itu wajib bagi muslim",
    "12": "Bagaimana proses visa Saudi untuk umrah dari Indonesia sekarang",
    "13": "Jelaskan step by step cara booking flight ke Jeddah secara online",
    "14": "How to prepare dokumen umrah dari Indonesia dengan benar",
    "15": "Tolong buat checklist persiapan umrah termasuk barang wajib dibawa",
    "16": "Guide aku cara pilih hotel di Makkah dekat Haram dengan budget terbatas",
    "17": "Menurut kamu belajar bahasa Arab itu susah gak untuk pemula",
    "18": "I feel overwhelmed dengan persiapan umrah, ada tips sederhana?",
    "19": "Ahyanan saya bingung mulai dari mana untuk umrah",
    "20": "Translate ke English: aku mau pergi ke Makkah minggu depan"
}

def get_audio_id(filename):
    """Mencari angka nomor audio (contoh: audio01 -> 1)"""
    match = re.search(r'audio(\d+)', filename.lower())
    if match:
        return str(int(match.group(1))) # hilangkan angka 0 di depan (01 jadi 1)
    return None

def main():
    # Pastikan nama file input benar sesuai yang ada di folder kamu
    input_csv = "hasil_eksperimen_TOTAL_FINAL.csv" 
    output_csv = "hasil_evaluasi_WER_CER.csv"

    if not os.path.exists(input_csv):
        print(f"❌ Error: File {input_csv} tidak ditemukan!")
        return

    print("--- MEMULAI PERHITUNGAN WER/CER MASSAL ---")

    with open(input_csv, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        
        # --- DETEKSI KOLOM OTOMATIS ---
        # Cek apakah kolomnya bernama 'stt_transcription' atau 'stt_text'
        stt_col = 'stt_transcription' if 'stt_transcription' in fieldnames else 'stt_text'
        print(f"[INFO] Membaca transkripsi dari kolom: {stt_col}")

        rows = list(reader)
        new_fieldnames = fieldnames + ['reference_text', 'wer_score', 'cer_score']

    total_wer = 0
    total_cer = 0
    count = 0

    with open(output_csv, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=new_fieldnames, extrasaction='ignore')
        writer.writeheader()

        for row in rows:
            filename = row['filename']
            audio_id = get_audio_id(filename)
            hyp = row.get(stt_col, "").strip() # Mengambil hasil Whisper
            
            if audio_id in REFERENCE_MAP and hyp:
                ref = REFERENCE_MAP[audio_id]
                
                try:
                    # Proses hitung
                    w = wer(ref.lower(), hyp.lower())
                    c = cer(ref.lower(), hyp.lower())
                    
                    row['reference_text'] = ref
                    row['wer_score'] = round(w, 4)
                    row['cer_score'] = round(c, 4)
                    
                    total_wer += w
                    total_cer += c
                    count += 1
                except:
                    pass
            
            writer.writerow(row)

    if count > 0:
        print(f"\n✅ SELESAI memproses {count} data!")
        print(f"Rata-rata WER: {total_wer/count:.4f}")
        print(f"Rata-rata CER: {total_cer/count:.4f}")
        print(f"Hasil lengkap tersimpan di: {output_csv}")
    else:
        print("\n❌ Gagal menghitung. Pastikan ID audio (audio01, dst) cocok dengan Reference.")

if __name__ == "__main__":
    main()