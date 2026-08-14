import os
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# Definisikan instruksi sistem untuk LightenUp.id
SYSTEM_INSTRUCTION = """
Anda adalah AI asisten kesehatan mental untuk platform LightenUp.id. 
Tugas Anda adalah mendengarkan dengan empati, memberikan respon yang menenangkan, 
dan membantu pengguna merefleksikan emosi mereka. 
Catatan: Anda bukan pengganti psikolog profesional. 
Jika pengguna menunjukkan tanda bahaya atau melukai diri sendiri, arahkan ke bantuan profesional.
"""

def get_gemini_model():
    """Fungsi helper untuk inisialisasi Gemini API secara aman."""
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return None, "API Key belum terpasang di Environment Variables Vercel."
    
    try:
        genai.configure(api_key=api_key)
        # Rekomendasi 2026: Gunakan "gemini-1.5-flash" (tanpa -latest) untuk stabilitas produksi
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=SYSTEM_INSTRUCTION
        )
        return model, None
    except Exception as e:
        try:
            model = genai.GenerativeModel(
                model_name="gemini-2.5-flash",
                system_instruction=SYSTEM_INSTRUCTION
            )
            return model, None
        except Exception as err:
            return None, str(err)

@app.route('/api/chat', methods=['POST'])
def chat():
    # 1. Ambil pesan dari frontend website
    data = request.get_json() or {}
    user_message = data.get("message")
    chat_history = data.get("history", []) # Opsional: untuk mempertahankan konteks percakapan
    
    if not user_message:
        return jsonify({"error": "Pesan tidak boleh kosong"}), 400

    # 2. Panggil fungsi model Gemini
    model, error_msg = get_gemini_model()
    if error_msg:
        return jsonify({"error": error_msg}), 500

    try:
        # 3. Kirim pesan ke Gemini
        # Jika menggunakan chat history, gunakan model.start_chat()
        if chat_history:
            chat_session = model.start_chat(history=chat_history)
            response = chat_session.send_message(user_message)
        else:
            response = model.generate_content(user_message)
            
        # 4. Kembalikan respon ke frontend
        return jsonify({
            "success": True,
            "reply": response.text
        })

    except Exception as e:
        return jsonify({"error": f"Gagal memproses pesan: {str(e)}"}), 500

# Diperlukan agar Flask bisa berjalan di Vercel Serverless
def handler(request, client):
    return app(request)
