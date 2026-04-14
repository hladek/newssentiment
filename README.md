# Aplikácia na analýzu sentimentu

Farebná Flask webová aplikácia, ktorá analyzuje sentiment textu pomocou OpenAI kompatibilného API.

## Vlastnosti

- 🎨 Krásne, farebné gradientové používateľské rozhranie
- 🤖 AI analýza sentimentu pomocou OpenAI kompatibilného API
- 📝 Analýza sentimentu po vetách
- 🎭 Farebné označenie viet (zelená=pozitívny, červená=negatívny, šedá=neutrálny)
- 📊 Štatistiky počtu pozitívnych, negatívnych a neutrálnych viet
- ⚡ Rýchly a responzívny dizajn

## Požiadavky

- Python 3.12 alebo vyššia verzia
- Dostupné OpenAI kompatibilné API
- Nakonfigurované premenné prostredia `OPENAI_API_KEY`, `OPENAI_BASE_URL` a `OPENAI_MODEL`

## Inštalácia

1. Nainštalujte Python závislosti:
```bash
pip install -r requirements.txt
```

2. Nastavte premenné prostredia:
```bash
export OPENAI_API_KEY="your-api-key"
export OPENAI_BASE_URL="https://your-openai-compatible-endpoint/v1"
export OPENAI_MODEL="your-model-name"
```

## Použitie

1. Spustite Flask aplikáciu:
```bash
python app.py
```

2. Otvorte prehliadač a prejdite na:
```
http://localhost:5448
```

3. Zadajte text do textového poľa a kliknite na "Analyzovať sentiment"

4. Aplikácia zobrazí každú vetu s farebným označením:
   - **Pozitívny** (zelené pozadie)
   - **Negatívny** (červené pozadie)
   - **Neutrálny** (šedé pozadie)

## Ako to funguje

1. Používateľ zadá text do webového formulára
2. Text sa odošle do Flask backendu
3. Backend použije OpenAI kompatibilné API na odoslanie promptu
4. Model analyzuje sentiment každej vety
5. Výsledky sa zobrazia ako zoznam farebne označených viet so štatistikami

## Očakávaný formát odpovede z modelu

Model by mal vrátiť JSON v nasledujúcom formáte:
```json
{
  "sentences": [
    {
      "text": "Text vety",
      "emotion": "positive"
    },
    {
      "text": "Ďalšia veta",
      "emotion": "negative"
    }
  ]
}
```

## Prispôsobenie

- **Zmena modelu**: Upravte premennú prostredia `OPENAI_MODEL`
- **Zmena API endpointu**: Upravte premennú prostredia `OPENAI_BASE_URL`
- **Zmena API kľúča**: Upravte premennú prostredia `OPENAI_API_KEY`
- **Úprava farieb**: Upravte CSS farby pre `.sentence-item.positive`, `.sentence-item.negative`, `.sentence-item.neutral` v `templates/index.html`
- **Zmena portu**: Upravte parameter `port` v `app.run()` v `app.py`

## Riešenie problémov

- **"Chyba konfigurácie"**: Skontrolujte, či sú nastavené `OPENAI_API_KEY`, `OPENAI_BASE_URL` a `OPENAI_MODEL`
- **"Nedá sa pripojiť k OpenAI kompatibilnému API"**: Skontrolujte `OPENAI_BASE_URL` a dostupnosť služby
- **Neplatný formát odpovede**: Skontrolujte, či model vracia správny JSON formát
- **Port sa už používa**: Zmeňte port v `app.py` na inú hodnotu (napr. 5001)
