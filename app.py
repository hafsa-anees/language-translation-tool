import io
import time
import streamlit as st
from deep_translator import GoogleTranslator, MyMemoryTranslator
from gtts import gTTS

# ---------- Page setup ----------
st.set_page_config(page_title="Language Translator", page_icon="🌐")
st.title("🌐 Language Translation Tool")

# ---------- Languages ----------
LANGUAGES = GoogleTranslator().get_supported_languages(as_dict=True)
names = sorted(LANGUAGES.keys())

# ---------- MyMemory ke liye code badalne wala function ----------
def to_mymemory_code(code):
    # MyMemory ko en-GB, ur-PK jaisa format chahiye
    special = {
        "en": "en-GB", "ur": "ur-PK", "hi": "hi-IN", "ar": "ar-SA",
        "fr": "fr-FR", "de": "de-DE", "es": "es-ES", "it": "it-IT",
        "pt": "pt-PT", "ru": "ru-RU", "tr": "tr-TR", "ja": "ja-JP",
        "ko": "ko-KR", "zh-CN": "zh-CN", "zh-TW": "zh-TW", "fa": "fa-IR",
        "bn": "bn-IN", "pa": "pa-IN", "ps": "ps-PK", "sd": "sd-PK",
    }
    return special.get(code, code)

# ---------- Translate function (retry + backup) ----------
def smart_translate(text, source, target):
    # Pehle Google ko 3 baar try karo
    for attempt in range(3):
        try:
            return GoogleTranslator(source=source, target=target).translate(text)
        except Exception:
            time.sleep(2)

    # Google na chale to MyMemory (backup)
    src = "en-GB" if source == "auto" else to_mymemory_code(source)
    tgt = to_mymemory_code(target)
    return MyMemoryTranslator(source=src, target=tgt).translate(text)

# ---------- Language selection ----------
col1, col2 = st.columns(2)
with col1:
    source_name = st.selectbox("From (Source)", ["auto detect"] + names,
                               index=names.index("english") + 1)
with col2:
    target_name = st.selectbox("To (Target)", names, index=names.index("urdu"))

# ---------- Text input ----------
text = st.text_area("Enter text to translate", height=150,
                    placeholder="Yahan text likhein...")

# ---------- Translate button ----------
if st.button("Translate", type="primary"):
    if not text.strip():
        st.warning("Please enter some text first.")
    else:
        try:
            source_code = "auto" if source_name == "auto detect" else LANGUAGES[source_name]
            target_code = LANGUAGES[target_name]

            with st.spinner("Translating..."):
                result = smart_translate(text, source_code, target_code)

            st.session_state["result"] = result
            st.session_state["target_code"] = target_code
        except Exception as e:
            st.error(f"Translation failed: {str(e)[:300]}")

# ---------- Output display ----------
if "result" in st.session_state:
    st.subheader("Translated Text")
    st.code(st.session_state["result"], language=None, wrap_lines=True)

    if st.button("🔊 Listen"):
        try:
            tts = gTTS(text=st.session_state["result"],
                       lang=st.session_state["target_code"])
            audio_bytes = io.BytesIO()
            tts.write_to_fp(audio_bytes)
            st.audio(audio_bytes.getvalue(), format="audio/mp3")
        except Exception:
            st.error("Is language ke liye text-to-speech supported nahi hai.")