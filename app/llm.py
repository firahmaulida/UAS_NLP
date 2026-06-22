import os
from dotenv import load_dotenv
from google import genai

# 1. Ambil Key dari .env agar aman
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY").strip()

# 2. Inisialisasi Client (Persis kode praktikum kamu)
client = genai.Client(api_key=api_key)

def get_gemini_response(user_text):
    """
    Fungsi ini mengikuti logika Colab praktikum kamu.
    """
    try:
        # Gunakan model yang tersedia di API Gemini.
        # Nama model harus menggunakan format `models/<nama-model>`.
        response = client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents=f"Kamu asisten Umrah. Gunakan gaya bahasa Code-Switching (Indo-English-Arabic). Balas singkat.\n\nUser: {user_text}"
        )
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

# --- UNTUK MENGETES ---
if __name__ == "__main__":
    test_input = "aku mau buk fly ke jadah minggu depan bisa bantu schedule"
    print("Sedang memproses jawaban (ikut gaya praktikum)...")
    
    jawaban = get_gemini_response(test_input)
    print("-" * 30)
    print("Jawaban Gemini:", jawaban)
    print("-" * 30)