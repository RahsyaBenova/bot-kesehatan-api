import os
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# System Prompt Khusus Edukasi Medis & Keamanan
SYSTEM_INSTRUCTION = """
Anda adalah asisten konsultan informasi kesehatan virtual yang empati, ramah, dan profesional.
Aturan penting:
1. Berikan edukasi dan saran pertolongan pertama/gaya hidup sehat secara umum.
2. Anda BUKAN dokter pengganti; jangan memberikan diagnosis mutlak atau meresepkan obat keras.
3. Selalu sarankan pengguna berkonsultasi langsung dengan dokter jika gejala menetap atau memburuk.
4. Jika terdapat tanda gawat darurat (sesak napas berat, nyeri dada kiri, pingsan, perdarahan hebat), segera instruksikan untuk ke IGD/faskes terdekat.
"""

def get_gemini_model():
    """Fungsi helper untuk inisialisasi Gemini API secara aman."""
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return None, "API Key belum terpasang di Environment Variables Vercel."
    
    try:
        genai.configure(api_key=api_key)
        # Inisialisasi model
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=SYSTEM_INSTRUCTION
        )
        return model, None
    except Exception as e:
        return None, str(e)


# Endpoint Health Check (Root)
@app.route('/', methods=['GET'])
def root():
    return jsonify({
        "status": "success",
        "message": "Bot Konsultasi Kesehatan Aktif dan Siap Digunakan."
    }), 200


# Endpoint Konsultasi Chat (POST)
@app.route('/chat', methods=['POST'])
@app.route('/api/chat', methods=['POST'])
def chat():
    # 1. Validasi Body JSON
    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return jsonify({
            "status": "error",
            "message": "Payload request harus berupa JSON yang valid (contoh: {\"message\": \"pertanyaan Anda\"})."
        }), 400

    user_message = data.get("message", "").strip()
    if not user_message:
        return jsonify({
            "status": "error",
            "message": "Field 'message' tidak boleh kosong."
        }), 400

    # 2. Inisialisasi Model AI
    model, init_error = get_gemini_model()
    if init_error:
        return jsonify({
            "status": "error",
            "message": init_error
        }), 500

    # 3. Generate Respon dari Gemini
    try:
        response = model.generate_content(user_message)
        
        # Validasi respon teks
        reply_text = response.text if hasattr(response, 'text') else "Maaf, AI tidak dapat menghasilkan jawaban untuk permintaan ini."
        
        return jsonify({
            "status": "success",
            "response": reply_text,
            "disclaimer": "Informasi ini bersifat edukatif dan bukan pengganti diagnosis medis resmi dari dokter."
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Gagal menghasilkan respon: {str(e)}"
        }), 500


# Fallback untuk route yang tidak ditemukan
@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "status": "error",
        "message": "Endpoint tidak ditemukan. Gunakan POST /chat atau GET /"
    }), 404


if __name__ == '__main__':
    # Untuk testing lokal
    app.run(host='0.0.0.0', port=5000, debug=True)
