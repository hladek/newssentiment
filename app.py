from flask import Flask, render_template, request, jsonify
import ollama
import json
import re

app = Flask(__name__)

def analyze_sentiment_with_ollama(text):
    """Odoslanie textu do Ollama na analýzu sentimentu"""
    try:
        prompt = f"""Analyzuj sentiment každej vety v nasledujúcom texte. Vráť výsledok v JSON formáte s poľom "sentences", kde každý objekt má "text" (vetu) a "emotion" (positive, negative alebo neutral).

Text: {text}

Vráť iba JSON bez žiadneho ďalšieho textu:"""
        
        response = ollama.generate(
            model='gpt-oss',
            prompt=prompt
        )
        
        response_text = response['response'].strip()
        
        # Pokús sa parsovať JSON odpoveď
        try:
            # Nájdi JSON v odpovedi (môže byť obklopený iným textom)
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                sentiment_data = json.loads(json_match.group())
                return sentiment_data
            else:
                # Ak JSON nebol nájdený, skús parsovať celú odpoveď
                sentiment_data = json.loads(response_text)
                return sentiment_data
        except json.JSONDecodeError:
            # Ak sa nepodarí parsovať JSON, vráť chybu
            return {
                "error": True,
                "message": "Nepodarilo sa spracovať odpoveď z modelu",
                "raw_response": response_text
            }
            
    except ollama.ResponseError as e:
        return {
            "error": True,
            "message": f"Chyba Ollama: {str(e)}"
        }
    except Exception as e:
        error_message = str(e)
        if "connection" in error_message.lower():
            return {
                "error": True,
                "message": "Nedá sa pripojiť k Ollama. Uistite sa, že Ollama beží (ollama serve)"
            }
        return {
            "error": True,
            "message": f"Chyba: {error_message}"
        }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    text = request.json.get('text', '')
    
    if not text.strip():
        return jsonify({'error': 'Prosím, zadajte nejaký text na analýzu'}), 400
    
    result = analyze_sentiment_with_ollama(text)
    
    # Skontroluj, či je výsledok chybový
    if isinstance(result, dict) and result.get('error'):
        return jsonify({'error': result.get('message', 'Neznáma chyba')}), 500
    
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
