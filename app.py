import streamlit as st

st.set_page_config(page_title="RD Calculator", layout="centered")

st.title("🖨️ RD Calculator – Tiefdruck Angebotskalkulation")
st.write("Willkommen! Diese App hilft dir bei der Berechnung von Abschnitten im Tiefdruck.")

st.subheader("📐 Abschnittsdaten eingeben")
breite = st.text_input("Breite (mm)")
hoehe = st.text_input("Höhe (mm)")
seiten = st.text_input("Seitenanzahl")

if breite and hoehe and seiten:
    st.success(f"Eingaben erhalten: {breite} × {hoehe} mm bei {seiten} Seiten")
