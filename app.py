import html
import json
import os
import re

import streamlit as st
from openai import APIConnectionError, APIStatusError, OpenAI

# ── Constants ────────────────────────────────────────────────────────────────

EMOTION_STYLES: dict[str, dict[str, str]] = {
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

SYSTEM_PROMPT = (
    "Si asistent na analýzu sentimentu. Odpovedaj iba validným JSON objektom."
)

USER_PROMPT_TEMPLATE = (
    "Analyzuj sentiment každej vety v nasledujúcom texte. Vráť výsledok v JSON formáte "
    "s poľom \"sentences\", kde každý objekt má \"text\" (vetu) a \"emotion\" "
    "(positive, negative alebo neutral).\n\nText: {text}\n\n"
    "Vráť iba JSON bez žiadneho ďalšieho textu:"
)

# ── Backend ──────────────────────────────────────────────────────────────────


@st.cache_resource
def get_openai_client() -> tuple[OpenAI, str]:
    """Create and cache an OpenAI-compatible client from environment variables.

    Cached globally so the client is reused across reruns and users.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    model = os.getenv("OPENAI_MODEL")

    missing = [
        name
        for name, val in [
            ("OPENAI_API_KEY", api_key),
            ("OPENAI_BASE_URL", base_url),
            ("OPENAI_MODEL", model),
        ]
        if not val
    ]
    if missing:
        raise RuntimeError(
            f"Chyba konfigurácie. Nastavte premenné prostredia: {', '.join(missing)}"
        )

    return OpenAI(api_key=api_key, base_url=base_url), model  # type: ignore[arg-type]


def _parse_json_response(response_text: str) -> dict:
    """Extract a JSON object from a potentially noisy LLM response.

    Tries a clean parse first; falls back to extracting the first {...} block
    (handles responses wrapped in markdown code fences or extra prose).
    """
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", response_text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    raise RuntimeError(
        f"Nepodarilo sa spracovať odpoveď z modelu.\n\nRaw odpoveď: {response_text}"
    )


@st.cache_data(show_spinner=False)
def analyze_sentiment(text: str) -> list[dict]:
    """Call the LLM and return a list of {text, emotion} sentence dicts.

    Results are cached by input text so repeated submissions don't hit the API.
    """
    client, model = get_openai_client()

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": USER_PROMPT_TEMPLATE.format(text=text)},
            ],
        )
    except APIConnectionError:
        raise RuntimeError(
            "Nedá sa pripojiť k OpenAI kompatibilnému API. "
            "Skontrolujte OPENAI_BASE_URL a dostupnosť služby."
        )
    except APIStatusError as e:
        raise RuntimeError(
            f"OpenAI API vrátilo chybu (status {e.status_code}): {e.message}"
        )

    content = response.choices[0].message.content if response.choices else None
    if not content:
        raise RuntimeError("Model nevrátil žiadny obsah odpovede.")

    result = _parse_json_response(content.strip())

    sentences = result.get("sentences")
    if not isinstance(sentences, list) or not sentences:
        raise RuntimeError("Odpoveď neobsahuje pole 'sentences' alebo je prázdne.")

    return sentences


# ── UI helpers ───────────────────────────────────────────────────────────────


def render_sentence(sentence: dict) -> None:
    """Render one sentence with a colour-coded emotion badge."""
    emotion = sentence.get("emotion", "neutral").lower()
    style = EMOTION_STYLES.get(emotion, EMOTION_STYLES["neutral"])
    # Escape model output before injecting into HTML to prevent XSS
    text = html.escape(sentence.get("text", ""))
    st.markdown(
        f"""<div style="background:{style['bg']};border-left:4px solid {style['border']};
color:{style['color']};padding:12px 16px;border-radius:8px;margin-bottom:10px;
font-size:1.05em;line-height:1.7;">{text}&nbsp;<span style="background:{style['badge_bg']};
color:white;padding:2px 10px;border-radius:12px;font-size:0.82em;font-weight:600;
text-transform:uppercase;">{style['label']}</span></div>""",
        unsafe_allow_html=True,
    )


def render_results(sentences: list[dict]) -> None:
    counts: dict[str, int] = {"positive": 0, "negative": 0, "neutral": 0}
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


# ── Main ─────────────────────────────────────────────────────────────────────


def main() -> None:
    st.set_page_config(page_title="Analýza sentimentu", page_icon="🎭")
    st.title("🎭 Analýza sentimentu")
    st.caption("AI detekcia emócií v texte")

    if "results" not in st.session_state:
        st.session_state.results = None

    text_input: str = st.text_area(
        "Zadajte váš text:",
        key="text_input",
        placeholder="Napíšte alebo vložte akýkoľvek text na analýzu...",
        height=180,
    )

    col1, col2 = st.columns([3, 1])
    analyze_clicked = col1.button("🔍 Analyzovať sentiment", use_container_width=True)

    if col2.button("🗑️ Vymazať", use_container_width=True):
        st.session_state.results = None
        st.session_state.pop("text_input", None)
        st.rerun()

    if analyze_clicked:
        if not text_input.strip():
            st.warning("Prosím, zadajte nejaký text na analýzu.")
        else:
            with st.spinner("Analyzujem sentiment..."):
                try:
                    st.session_state.results = analyze_sentiment(text_input)
                except RuntimeError as e:
                    st.error(str(e))
                    st.session_state.results = None

    if st.session_state.results:
        st.subheader("📊 Výsledky analýzy")
        render_results(st.session_state.results)


if __name__ == "__main__":
    main()
