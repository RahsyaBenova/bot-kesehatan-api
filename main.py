import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai

app = Flask(__name__)

# Konfigurasi CORS agar bisa diakses dari lightenup.id dan mode development
CORS(app, origins=[
    "https://lightenup.id",
    "https://www.lightenup.id",
    "http://localhost:3000",
    "http://localhost:8000",
    "*"  # Gunakan wildcard '*' jika ingin bisa diakses dari preview deployment/testing
])

# System Prompt Khusus LightenUp.id
SYSTEM_INSTRUCTION = """
Anda adalah asisten konsultan kesehatan dan wellness virtual resmi untuk platform "LightenUp.id".
Karakter Anda: Empati, solutif, ramah, edukatif, dan profesional.

Panduan dan batasan:
1. Menyapa dan memberikan panduan gaya hidup sehat, manajemen stres, nutrisi, serta informasi kesehatan umum untuk pengguna LightenUp.id.
2. Anda BUKAN pengganti dokter atau tenaga medis berlisensi; DILARANG memberikan diagnosis mutlak atau meresepkan obat keras.
3. Selalu ingatkan pengguna untuk berkonsultasi langsung dengan fasilitas kesehatan atau dokter jika keluhan berlanjut.
4. Jika mendeteksi tanda bahaya/kondisi darurat medis atau krisis psikologis berat, arahkan pengguna segera ke IGD terdekat atau layanan darurat (118/119).
5. Format jawaban dengan rapi menggunakan poin-poin agar nyaman dibaca di tampilan web/mobile LightenUp.id.
"""

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
        "version": "1.0.0"
    }), 200


@app.route('/chat', methods=['POST'])
@app.route('/api/chat', methods=['POST'])
def chat():
    # Validasi body request
    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return jsonify({
            "status": "error",
            "message": "Payload JSON tidak valid. Contoh: {\"message\": \"pertanyaan\"}"
        }), 400

    user_message = data.get("message", "").strip()
    if not user_message:
        return jsonify({
            "status": "error",
            "message": "Pesan ('message') tidak boleh kosong."
        }), 400

    # Inisialisasi model
    model, init_error = get_gemini_model()
    if init_error:
        return jsonify({
            "status": "error",
            "message": init_error
        }), 500

    # Generate jawaban
    try:
        response = model.generate_content(user_message)
        reply_text = response.text if hasattr(response, 'text') else "Maaf, kami tidak dapat memproses permintaan ini saat ini."
        
        return jsonify({
            "status": "success",
            "source": "LightenUp.id AI Assistant",
            "response": reply_text,
            "disclaimer": "Informasi ini disediakan oleh LightenUp.id untuk tujuan edukasi dan bukan merupakan nasihat atau diagnosis medis profesional."
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
