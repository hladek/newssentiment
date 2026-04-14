import json
import os
import re

from flask import Flask, jsonify, render_template, request
from openai import APIConnectionError, APIStatusError, OpenAI

app = Flask(__name__)

def get_openai_settings():
    required_settings = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "OPENAI_BASE_URL": os.getenv("OPENAI_BASE_URL"),
        "OPENAI_MODEL": os.getenv("OPENAI_MODEL"),
    }
    missing_settings = [name for name, value in required_settings.items() if not value]
    if missing_settings:
        missing_list = ", ".join(missing_settings)
        raise RuntimeError(f"Chyba konfigurácie. Nastavte premenné prostredia: {missing_list}")

    return required_settings


def analyze_sentiment_with_openai(text):
    """Odoslanie textu do OpenAI kompatibilného API na analýzu sentimentu."""
    settings = get_openai_settings()
    client = OpenAI(
        api_key=settings["OPENAI_API_KEY"],
        base_url=settings["OPENAI_BASE_URL"],
    )

    prompt = f"""Analyzuj sentiment každej vety v nasledujúcom texte. Vráť výsledok v JSON formáte s poľom "sentences", kde každý objekt má "text" (vetu) a "emotion" (positive, negative alebo neutral).

Text: {text}

Vráť iba JSON bez žiadneho ďalšieho textu:"""

    try:
        response = client.chat.completions.create(
            model=settings["OPENAI_MODEL"],
            messages=[
                {
                    "role": "system",
                    "content": "Si asistent na analýzu sentimentu. Odpovedaj iba validným JSON objektom.",
                },
                {"role": "user", "content": prompt},
            ],
        )
    except APIConnectionError:
        return {
            "error": True,
            "message": "Nedá sa pripojiť k OpenAI kompatibilnému API. Skontrolujte OPENAI_BASE_URL a dostupnosť služby."
        }
    except APIStatusError as e:
        status_code = getattr(e, "status_code", "neznámy")
        return {
            "error": True,
            "message": f"OpenAI kompatibilné API vrátilo chybu (status {status_code}): {e.message}"
        }

    if not response.choices or not response.choices[0].message.content:
        return {
            "error": True,
            "message": "Model nevrátil žiadny obsah odpovede"
        }

    response_text = response.choices[0].message.content.strip()

    try:
        json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
        if json_match:
            sentiment_data = json.loads(json_match.group())
            return sentiment_data

        sentiment_data = json.loads(response_text)
        return sentiment_data
    except json.JSONDecodeError:
        return {
            "error": True,
            "message": "Nepodarilo sa spracovať odpoveď z modelu",
            "raw_response": response_text
        }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/senti')
def index2():
    return render_template('index.html')

@app.route('/senti/analyze', methods=['POST'])
def analyze():
    payload = request.get_json(silent=True) or {}
    text = payload.get('text', '')
    
    if not text.strip():
        return jsonify({'error': 'Prosím, zadajte nejaký text na analýzu'}), 400
    
    try:
        result = analyze_sentiment_with_openai(text)
    except RuntimeError as e:
        return jsonify({'error': str(e)}), 500
    
    # Skontroluj, či je výsledok chybový
    if isinstance(result, dict) and result.get('error'):
        return jsonify({'error': result.get('message', 'Neznáma chyba')}), 500
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5448)
