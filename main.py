import os
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# Konfigurasi Gemini API Key dari Environment Variable
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# System Prompt Khusus Kesehatan & Safety Disclaimer
SYSTEM_INSTRUCTION = """
Anda adalah "MedBot", asisten informasi kesehatan virtual yang ramah dan informatif.
Aturan Penting:
1. Anda HANYA memberikan informasi edukasi kesehatan umum dan navigasi awal.
2. Anda BUKAN dokter dan DILARANG memberikan diagnosis pasti atau meresepkan obat keras.
3. Selalu ingatkan pengguna untuk berkonsultasi langsung dengan dokter atau fasilitas kesehatan terdekat.
4. Jika pengguna menyebutkan gejala darurat (nyeri dada hebat, sesak nafas parah, perdarahan hebat, pingsan), SEGERA instruksikan mereka untuk menghubungi layanan darurat (118/119) atau ke IGD terdekat.
5. Gunakan bahasa Indonesia yang santun, empati, dan mudah dipahami.
"""

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=SYSTEM_INSTRUCTION
)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "Bot Konsultasi Kesehatan Aktif"})

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"error": "Pesan tidak boleh kosong"}), 400

    try:
        response = model.generate_content(user_message)
        return jsonify({
            "response": response.text,
            "disclaimer": "Informasi ini bersifat edukatif dan bukan pengganti diagnosis medis profesional."
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
