import streamlit as st
from analyzer import score_image
import cv2
import numpy as np

st.set_page_config(page_title="Best Shot Finder", page_icon="📸")
st.title("📸 Best Shot Finder")
st.markdown("Lade ein Foto hoch und analysiere Schärfe und Belichtung!")

uploaded_file = st.file_uploader("Wähle ein Bild aus", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Bild einlesen und anzeigen
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, 1)

    st.image(image, channels="BGR", caption="Dein hochgeladenes Bild", use_column_width=True)

    # Analyse starten
    with st.spinner("Analysiere Bild..."):
        score, sharpness, brightness = score_image(image)

    # Ergebnisse anzeigen
    st.subheader("🔍 Analyse-Ergebnisse")
    st.metric("Gesamtscore", f"{score:.2f}")
    st.metric("Schärfe", f"{sharpness:.2f}")
    st.metric("Helligkeit", f"{brightness:.2f}")

    # Optional: Bewertung interpretieren
    st.markdown("---")
    if score > 70:
        st.success("🔥 Top Shot! Scharf & gut belichtet.")
    elif score > 50:
        st.info("👍 Solides Bild, aber da geht noch mehr.")
    else:
        st.warning("👀 Eventuell unscharf oder unter-/überbelichtet.")
