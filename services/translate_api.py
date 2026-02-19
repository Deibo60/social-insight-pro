import requests

# MyMemory API — gratuita, sin autenticación requerida
# Documentación: https://mymemory.translated.net/doc/spec.php
BASE_URL = "https://api.mymemory.translated.net/get"

def translate_to_spanish(text: str) -> dict:
    """
    Traduce cualquier texto al español usando MyMemory API.
    Devuelve diccionario con: translated_text, detected_lang, quality, original
    """
    try:
        params = {
            "q":    text,
            "langpair": "en|es",   # inglés → español
        }
        response = requests.get(BASE_URL, params=params, timeout=8)
        data     = response.json()

        match   = data.get("responseData", {})
        translated = match.get("translatedText", "")
        quality    = match.get("match", 0)

        # DetectedLanguage viene en matches[0] a veces
        detected = "en"
        matches  = data.get("matches", [])
        if matches:
            detected = matches[0].get("source-language", "en")

        return {
            "success":         True,
            "original":        text,
            "translated_text": translated,
            "detected_lang":   detected,
            "quality":         round(float(quality) * 100) if quality else 100,
        }

    except Exception as e:
        return {
            "success":         False,
            "original":        text,
            "translated_text": "",
            "error":           str(e),
        }