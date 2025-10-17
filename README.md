# Aplikácia na analýzu sentimentu

Farebná Flask webová aplikácia, ktorá analyzuje sentiment textu pomocou jazykových modelov Ollama.

## Vlastnosti

- 🎨 Krásne, farebné gradientové používateľské rozhranie
- 🤖 AI analýza sentimentu pomocou Ollama Python API
- 📝 Analýza sentimentu po vetách
- 🎭 Farebné označenie viet (zelená=pozitívny, červená=negatívny, šedá=neutrálny)
- 📊 Štatistiky počtu pozitívnych, negatívnych a neutrálnych viet
- ⚡ Rýchly a responzívny dizajn

## Požiadavky

- Python 3.7 alebo vyššia verzia
- Nainštalovaná a spustená Ollama ([Inštalácia Ollama](https://ollama.ai))
- Stiahnutý jazykový model v Ollama (napr. llama2)

## Inštalácia

1. Nainštalujte Python závislosti:
```bash
pip install -r requirements.txt
```

2. Uistite sa, že Ollama beží:
```bash
ollama serve
```

3. Stiahnite jazykový model (ak ste tak ešte neurobili):
```bash
ollama pull llama2
```

## Použitie

1. Spustite Flask aplikáciu:
```bash
python app.py
```

2. Otvorte prehliadač a prejdite na:
```
http://localhost:5000
```

3. Zadajte text do textového poľa a kliknite na "Analyzovať sentiment"

4. Aplikácia zobrazí každú vetu s farebným označením:
   - **Pozitívny** (zelené pozadie)
   - **Negatívny** (červené pozadie)
   - **Neutrálny** (šedé pozadie)

## Ako to funguje

1. Používateľ zadá text do webového formulára
2. Text sa odošle do Flask backendu
3. Backend použije Ollama Python API na odoslanie promptu
4. Ollama analyzuje sentiment každej vety pomocou jazykového modelu
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

- **Zmena modelu**: Upravte `app.py` a zmeňte parameter `model='llama2'` vo funkcii `ollama.generate()`
- **Úprava farieb**: Upravte CSS farby pre `.sentence-item.positive`, `.sentence-item.negative`, `.sentence-item.neutral` v `templates/index.html`
- **Zmena portu**: Upravte parameter `port` v `app.run()` v `app.py`

## Riešenie problémov

- **"Nedá sa pripojiť k Ollama"**: Uistite sa, že Ollama beží príkazom `ollama serve`
- **Neplatný formát odpovede**: Skontrolujte, či model vracia správny JSON formát
- **Port sa už používa**: Zmeňte port v `app.py` na inú hodnotu (napr. 5001)
