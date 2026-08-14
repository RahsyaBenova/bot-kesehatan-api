def get_gemini_model():
    """Fungsi helper untuk inisialisasi Gemini API secara aman."""
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        return None, "API Key belum terpasang di Environment Variables Vercel."
    
    try:
        genai.configure(api_key=api_key)
        
        # Coba gunakan gemini-1.5-flash-latest atau models/gemini-1.5-flash
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash-latest",
            system_instruction=SYSTEM_INSTRUCTION
        )
        return model, None
    except Exception as e:
        # Fallback jika model flash spesifik belum terbaca di endpoint akun Anda
        try:
            model = genai.GenerativeModel(
                model_name="gemini-1.5-pro",
                system_instruction=SYSTEM_INSTRUCTION
            )
            return model, None
        except Exception as err:
            return None, str(err)
