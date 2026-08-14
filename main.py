import os
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai

app = Flask(__name__)

# Konfigurasi CORS
CORS(app, origins=[
    "https://lightenup.id",
    "https://www.lightenup.id",
    "http://localhost:3000",
    "http://localhost:8000",
    "*"
])

# System Prompt yang dioptimasi untuk Plain Text bersih (Tanpa simbol Markdown)
SYSTEM_INSTRUCTION = """
Anda adalah asisten konsultan kesehatan dan wellness virtual resmi untuk platform "LightenUp.id".
Karakter Anda: Empati, solutif, ramah, edukatif, dan profesional.

ATURAN FORMAT PENULISAN (SANGAT PENTING):
1. JANGAN GUNAKAN SIMBOL MARKDOWN SAMA SEKALI (Dilarang menggunakan tanda bintang ganda **, bintang tunggal *, tanda pagar #, backtick `, atau garis miring _).
2. Tuliskan jawaban dalam bentuk TEKS BIASA (Plain Text) yang bersih dan mengalir.
3. Untuk membuat daftar poin atau rincian:
   - Gunakan nomor biasa (1., 2., 3.) atau tanda strip minus (-) biasa.
   - Jangan menebalkan judul poin dengan tanda bintang (**). Tulis judul langsung seperti biasa diikuti tanda titik dua (:).
4. Pisahkan setiap paragraf atau poin dengan jarak satu baris kosong (enter 2 kali) agar tetap rapi dibaca.

PANDUAN MEDIS & KONTEN:
1. Berikan panduan gaya hidup sehat, manajemen stres, nutrisi, dan info kesehatan umum.
2. Anda BUKAN pengganti dokter berlisensi; DILARANG memberikan diagnosis mutlak atau meresepkan obat keras.
3. Selalu ingatkan pengguna untuk berkonsultasi ke fasilitas kesehatan jika keluhan berlanjut.
4. Jika ada kondisi darurat medis atau krisis berat, arahkan segera ke IGD/faskes terdekat atau hotline 118/119.
"""

def clean_markdown(text: str) -> str:
    """Failsafe untuk menghapus sisa-sisa simbol markdown jika AI masih memunculkannya."""
    if not text:
        return ""
    # Hapus bold/italic markdown (**text**, *text*, __text__, _text_)
    text = re.sub(r'[*_]{1,3}(.*?)[*_]{1,3}', r'\1', text)
    # Hapus heading (### Heading)
    text = re.sub(r'#+\s*', '', text)
    # Ganti bullet asterisk (* item) menjadi strip (- item)
    text = re.sub(r'^\s*\*\s+', '- ', text, flags=re.MULTILINE)
    return text.strip()

def get_gemini_model():
    """Helper inisialisasi Gemini API"""
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return None, "API Key belum terpasang di Environment Variables."
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=SYSTEM_INSTRUCTION
        )
        return model, None
    except Exception as e:
        return None, str(e)


@app.route('/', methods=['GET'])
def root():
    return jsonify({
        "status": "success",
        "service": "LightenUp.id Health & Wellness Bot API",
        "version": "1.1.0"
    }), 200


@app.route('/chat', methods=['POST'])
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return jsonify({
            "status": "error",
            "message": "Payload JSON tidak valid."
        }), 400

    user_message = data.get("message", "").strip()
    if not user_message:
        return jsonify({
            "status": "error",
            "message": "Pesan ('message') tidak boleh kosong."
        }), 400

    model, init_error = get_gemini_model()
    if init_error:
        return jsonify({
            "status": "error",
            "message": init_error
        }), 500

    try:
        response = model.generate_content(user_message)
        raw_text = response.text if hasattr(response, 'text') else ""
        
        # Bersihkan sisa format jika ada
        clean_text = clean_markdown(raw_text)
        
        return jsonify({
            "status": "success",
            "source": "LightenUp.id AI Assistant",
            "response": clean_text,
            "disclaimer": "Informasi ini disediakan oleh LightenUp.id untuk tujuan edukasi dan bukan merupakan diagnosis medis resmi dari dokter."
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Gagal menghasilkan respon: {str(e)}"
        }), 500


@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "status": "error",
        "message": "Endpoint tidak ditemukan. Gunakan POST /chat"
    }), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
