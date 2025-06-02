import streamlit as st
import pandas as pd

def check_password():
    def password_entered():
        if st.session_state["password"] == "leiste-mart-lohn-hortense":
            st.session_state["authenticated"] = True
        else:
            st.session_state["authenticated"] = False
            st.error("Falsches Passwort. Bitte erneut versuchen.")

    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        st.title("🔒 Zugang geschützt")
        st.text_input("Bitte Passwort eingeben:", type="password", on_change=password_entered, key="password")
        return False
    else:
        return True

if check_password():

    # Titel
    st.title("Drucklegung und Kalkulation geheftete Objekte V1")

    st.subheader("Angaben Objekt")

    # Eingaben: Format und Seiten
    format_breite = st.number_input("Format Endprodukt horizontal (mm)", min_value=100, max_value=400, value=202)
    format_hoehe = st.number_input("Format Rohprodukt vertikal (mm)", min_value=100, max_value=400, value=275)
    seiten = st.number_input("Anzahl Seiten Endprodukt", min_value=4, step=4, value=48)

    # Beschnittabfrage
    beschnitt_aktiv = st.checkbox("Mit Beschnitt rechnen?", value=True)
    if beschnitt_aktiv:
        beschnitt = st.number_input("Beschnitt je Seite (mm)", min_value=0.0, max_value=10.0, value=2.0, step=0.5)
    else:
        beschnitt = 0.0

    # Weitere produktspezifische Angaben
    papierqualitaet = st.text_input("Papierqualität (z. B. LWC, SC, UWF)", value="LWC")
    papierpreis = st.number_input("Preis Papier (€/t)", min_value=0.0, value=600.0, step=10.0)
    auflage = st.number_input("Auflage (Stück)", min_value=1000, step=1000, value=500000)
    papiergewicht = st.number_input("Papiergewicht (g/m²)", min_value=30.0, max_value=150.0, value=42.0, step=0.5)

    # Berechnung Rohproduktwerte
    format1_roh = format_breite + beschnitt
    format2_roh = format_hoehe + 2 * beschnitt
    lagen_roh = seiten / 2

    # Anzeige Rohprodukt
    daten_rohprodukt = pd.DataFrame({
        "Parameter": [
            "Format Rohprodukt horizontal (mm)",
            "Format Rohprodukt vertikal (mm)"
        ],
        "Wert": [
            format1_roh,
            format2_roh
        ]
    })
    for i, v in enumerate(daten_rohprodukt["Wert"]):
        daten_rohprodukt.at[i, "Wert"] = f"{v:.0f}" if v == int(v) else f"{v:.2f}"

    st.subheader("📄 Rohprodukt")
    st.table(daten_rohprodukt)

    # Berechnung Abschnittswerte
    seiten_abschnitt = seiten / 2
    stranganzahl = seiten_abschnitt / 2
    bahnbreite_abschnitt = format1_roh * 2
    strangbreite_abschnitt = format2_roh

    daten_abschnitt = pd.DataFrame({
        "Parameter": [
            "Seiten Abschnitt",
            "Erforderliche Stränge",
            "Bahnlänge Abschnitt hor",
            "Strangbreite Abschnitt vert"
        ],
        "Wert": [
            seiten_abschnitt,
            stranganzahl,
            bahnbreite_abschnitt,
            strangbreite_abschnitt
        ]
    })
    for i, v in enumerate(daten_abschnitt["Wert"]):
        daten_abschnitt.at[i, "Wert"] = f"{v:.0f}" if v == int(v) else f"{v:.2f}"

    st.subheader("📐 Abschnitt")
    st.table(daten_abschnitt)

    # Validierung Abschnitt
    st.subheader("✅ Validierung der Abschnittswerte")
    if 2 <= stranganzahl <= 10:
        st.success("✅ Erforderliche Stränge liegen im zulässigen Bereich (2–10).")
    elif stranganzahl > 10:
        if stranganzahl % 2 == 0 or stranganzahl % 3 == 0:
            if stranganzahl <= 40:
                st.success("✅ Erforderliche Stränge > 10 sind zulässig (Teilbarkeit durch 2 oder 3 und ≤ 40).")
            else:
                st.error("❌ Erforderliche Stränge überschreiten das Maximum von 40.")
        else:
            st.error("❌ Erforderliche Stränge > 10 müssen durch 2 oder 3 teilbar sein.")
    else:
        st.error("❌ Erforderliche Stränge müssen mindestens 2 betragen.")

    if bahnbreite_abschnitt < 300:
        st.error("❌ Bahnlänge Abschnitt hor ist zu kurz. Mindestwert: 300 mm.")
    else:
        st.success("✅ Bahnlänge Abschnitt hor ist gültig (≥ 300 mm).")

    if strangbreite_abschnitt < 195:
        st.error("❌ Strangbreite Abschnitt vert ist zu schmal. Mindestwert: 195 mm.")
    elif strangbreite_abschnitt > 400:
        st.error("❌ Strangbreite Abschnitt vert ist zu breit. Maximalwert: 400 mm.")
    else:
        st.success("✅ Strangbreite Abschnitt vert ist gültig (195–400 mm).")

    # Papierverbrauch Netto
    st.subheader("📦 Papierverbrauch Netto")
    flaeche_netto = (format1_roh / 1000) * (format2_roh / 1000) * lagen_roh
    flaeche_auflage = flaeche_netto * auflage
    gewicht_netto = flaeche_auflage * papiergewicht / 1000

    st.write(f"Fläche Netto Rohprodukt (m²): **{flaeche_netto:,.2f}**")
    st.write(f"Fläche Netto Auflage Rohprodukt (m²): **{flaeche_auflage:,.2f}**")
    st.write(f"Gewicht Netto (t): **{gewicht_netto:,.2f}**")

    # Drucklegung Variantenprüfung
    def naechster_zylinder(theor_umfang):
        theor_wert = int(theor_umfang.replace(" mm", ""))
        for z in [790, 800, 820, 840, 860, 880, 940, 980, 1040, 1200, 1530]:
            if z >= theor_wert:
                return z
        return "-"

    varianten_info = [
        ("4U ohne Sammeln", 1, 2, 2),
        ("4U mit Sammeln", 2, 2, 1),
        ("6U ohne Sammeln", 1, 3, 3),
        ("6U mit Sammeln", 3, 3, 1),
        ("8U ohne Sammeln", 1, 4, 4),
        ("8U mit 1× Sammeln", 2, 4, 2),
        ("8U mit 2× Sammeln", 4, 4, 1),
    ]

    varianten = []
    for name, sammelteiler, umbruch, nutzen in varianten_info:
        try:
            anzahl_strang = stranganzahl / sammelteiler
            zylinder = umbruch * bahnbreite_abschnitt
            bahnbreite = anzahl_strang * strangbreite_abschnitt

            status = "✅ Möglich"
            grund = ""

            if anzahl_strang > 10:
                status = "❌ Nicht möglich"
                grund = "Mehr als 10 Stränge"
            elif zylinder < 790 or zylinder > 1530:
                status = "❌ Nicht möglich"
                grund = "Zylinderumfang nicht im zulässigen Bereich"
            elif bahnbreite < 800 or bahnbreite > 2670:
                status = "❌ Nicht möglich"
                grund = "Bahnbreite nicht im zulässigen Bereich"

            varianten.append({
                "Variante": name,
                "Nutzen": nutzen,
                "Stränge": int(anzahl_strang),
                "theor. Zylinderumfang": f"{int(zylinder)} mm",
                "Bahnbreite": f"{int(bahnbreite)} mm",
                "Status": status,
                "Grund": grund
            })
        except:
            continue

    df_varianten = pd.DataFrame(varianten)
    df_varianten = df_varianten[["Variante", "Nutzen", "Stränge", "theor. Zylinderumfang", "Bahnbreite", "Status", "Grund"]]

    st.subheader("🔍 Drucklegung – Variantenprüfung")
    st.table(df_varianten)

    # Kalkulation Varianten → Tabelle Zylinder
    st.subheader("📊 Kalkulation")

    # Nur gültige Varianten übernehmen
    df_zylinder = df_varianten[df_varianten["Status"] == "✅ Möglich"].copy()

    # Zylinder passend und Delta
    df_zylinder["Zylinderumfang passend"] = df_zylinder["theor. Zylinderumfang"].apply(naechster_zylinder)
    df_zylinder["Zylinderumfang Delta"] = df_zylinder.apply(
        lambda row: f"{int(row['Zylinderumfang passend']) - int(row['theor. Zylinderumfang'].replace(' mm',''))} mm" if row["Zylinderumfang passend"] != "-" else "-",
        axis=1
    )

    # Papier Rohprodukt
    papier_roh_m2 = (format1_roh / 1000) * (format2_roh / 1000) * (auflage / 2)
    df_zylinder["Papier Rohprodukt (m²)"] = f"{papier_roh_m2:,.2f} m²"

    st.table(
        df_zylinder.set_index("Variante")
    )
