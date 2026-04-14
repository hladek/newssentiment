import json
import os
import re

import streamlit as st
from openai import APIConnectionError, APIStatusError, OpenAI

EMOTION_STYLES = {
    "positive": {
        "bg": "#e8f5e9",
        "border": "#4caf50",
        "color": "#2e7d32",
        "badge_bg": "#4caf50",
        "label": "pozitívny ✅",
    },
    "negative": {
        "bg": "#ffebee",
        "border": "#f44336",
        "color": "#c62828",
        "badge_bg": "#f44336",
        "label": "negatívny ❌",
    },
    "neutral": {
        "bg": "#f5f5f5",
        "border": "#757575",
        "color": "#424242",
        "badge_bg": "#757575",
        "label": "neutrálny ➖",
    },
}


def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    model = os.getenv("OPENAI_MODEL")

    missing = [name for name, val in [
        ("OPENAI_API_KEY", api_key),
        ("OPENAI_BASE_URL", base_url),
        ("OPENAI_MODEL", model),
    ] if not val]

    if missing:
        raise RuntimeError(f"Chyba konfigurácie. Nastavte premenné prostredia: {', '.join(missing)}")

    return OpenAI(api_key=api_key, base_url=base_url), model


def analyze_sentiment(text):
    """Odoslanie textu do OpenAI kompatibilného API na analýzu sentimentu."""
    client, model = get_openai_client()

    prompt = f"""Analyzuj sentiment každej vety v nasledujúcom texte. Vráť výsledok v JSON formáte s poľom "sentences", kde každý objekt má "text" (vetu) a "emotion" (positive, negative alebo neutral).

Text: {text}

Vráť iba JSON bez žiadneho ďalšieho textu:"""

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "Si asistent na analýzu sentimentu. Odpovedaj iba validným JSON objektom.",
                },
                {"role": "user", "content": prompt},
            ],
        )
    except APIConnectionError:
        raise RuntimeError(
            "Nedá sa pripojiť k OpenAI kompatibilnému API. "
            "Skontrolujte OPENAI_BASE_URL a dostupnosť služby."
        )
    except APIStatusError as e:
        status_code = getattr(e, "status_code", "neznámy")
        raise RuntimeError(
            f"OpenAI kompatibilné API vrátilo chybu (status {status_code}): {e.message}"
        )

    if not response.choices or not response.choices[0].message.content:
        raise RuntimeError("Model nevrátil žiadny obsah odpovede")

    response_text = response.choices[0].message.content.strip()

    try:
        json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
        raw = json_match.group() if json_match else response_text
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise RuntimeError(
            f"Nepodarilo sa spracovať odpoveď z modelu: {e}\n\nRaw: {response_text}"
        )


def render_sentence(sentence):
    emotion = sentence.get("emotion", "neutral").lower()
    style = EMOTION_STYLES.get(emotion, EMOTION_STYLES["neutral"])
    text = sentence.get("text", "")
    st.markdown(
        f"""
        <div style="
            background:{style['bg']};
            border-left:4px solid {style['border']};
            color:{style['color']};
            padding:12px 16px;
            border-radius:8px;
            margin-bottom:10px;
            font-size:1.05em;
            line-height:1.7;
        ">
            {text}
            &nbsp;<span style="
                background:{style['badge_bg']};
                color:white;
                padding:2px 10px;
                border-radius:12px;
                font-size:0.82em;
                font-weight:600;
                text-transform:uppercase;
            ">{style['label']}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ── UI ──────────────────────────────────────────────────────────────────────

st.set_page_config(page_title="Analýza sentimentu", page_icon="🎭")

st.title("🎭 Analýza sentimentu")
st.caption("AI detekcia emócií v texte")

text_input = st.text_area(
    "Zadajte váš text:",
    placeholder="Napíšte alebo vložte akýkoľvek text na analýzu jeho sentimentu...",
    height=180,
)

col1, col2 = st.columns([3, 1])
analyze_clicked = col1.button("🔍 Analyzovať sentiment", use_container_width=True)
clear_clicked = col2.button("🗑️ Vymazať", use_container_width=True)

if clear_clicked:
    st.rerun()

if analyze_clicked:
    if not text_input.strip():
        st.warning("Prosím, zadajte nejaký text na analýzu.")
    else:
        with st.spinner("Analyzujem sentiment..."):
            try:
                result = analyze_sentiment(text_input)
            except RuntimeError as e:
                st.error(str(e))
                st.stop()

        sentences = result.get("sentences", [])
        if not sentences:
            st.error("Model nevrátil žiadne vety.")
            st.stop()

        st.subheader("📊 Výsledky analýzy")

        counts = {"positive": 0, "negative": 0, "neutral": 0}
        for sentence in sentences:
            emotion = sentence.get("emotion", "neutral").lower()
            counts[emotion] = counts.get(emotion, 0) + 1
            render_sentence(sentence)

        st.divider()
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("✅ Pozitívne", counts["positive"])
        m2.metric("❌ Negatívne", counts["negative"])
        m3.metric("➖ Neutrálne", counts["neutral"])
        m4.metric("📝 Celkom", len(sentences))
