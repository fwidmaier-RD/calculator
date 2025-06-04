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

    # 📊 Kalkulation – Eingaben
    st.subheader("\U0001F4CA Kalkulation")

    # Eingabefelder für Kalkulation
    auflage = st.number_input("Auflage (Stück)", min_value=1000, step=1000, format="%d", value=500000)
    papierpreis = st.number_input("Preis Papier (€/t)", min_value=0.0, value=600.0, step=10.0)
    papiergewicht = st.number_input("Papiergewicht (g/m²)", min_value=30.0, max_value=150.0, value=42.0, step=0.5)
    papierqualitaet = st.text_input("Papierqualität (z.\u202fB. LWC, SC, UWF)", value="LWC")
    maschinenpreis = st.number_input("Preis Maschinenstunde (€)", min_value=0.0, value=1000.0, step=50.0)
    bahngeschwindigkeit = st.number_input("Bahngeschwindigkeit (km/h)", min_value=10.0, max_value=60.0, value=39.5, step=0.5)


    # Auswahlfeld für Farbauftrag
    farboption = st.selectbox(
        "Farbauftrag",
        options=["Gering", "Mittel", "Hoch"],
        index=1,
        help="Auswahl des Farbauftrags: Gering = 1,0 g/m², Mittel = 1,1 g/m², Hoch = 1,2 g/m²"
    )

    # Zuordnung des numerischen Werts
    farbauftrag = {
        "Gering": 1.0,
        "Mittel": 1.1,
        "Hoch": 1.2
    }[farboption]

    # Neues Eingabefeld: Preis Farbe (Euro/kg)
    preis_farbe = st.number_input("Preis Farbe (€/kg)", min_value=0.0, value=3.0, step=0.1)

    # Nur gültige Varianten übernehmen
    df_gueltig = df_varianten[df_varianten["Status"] == "✅ Möglich"].copy()

    # Liste der zulässigen Zylinderumfänge
    zylinder_umfaenge = [790, 800, 820, 840, 860, 880, 940, 980, 1040, 1200, 1530]

    # Funktion zur Ermittlung des passenden Zylinders
    def naechster_zylinder(theor_umfang):
        theor_wert = int(theor_umfang.replace(" mm", ""))
        for z in zylinder_umfaenge:
            if z >= theor_wert:
                return z
        return "-"

    # Berechnungen
    papier_data = {}

    for index, row in df_gueltig.iterrows():
        variante = row["Variante"]
        bahnbreite = int(row["Bahnbreite"].replace(" mm", ""))
        theor_zyl = int(row["theor. Zylinderumfang"].replace(" mm", ""))
        nutzen = int(row["Nutzen"])
        zylinder = naechster_zylinder(row["theor. Zylinderumfang"])

        delta_zyl = zylinder - theor_zyl if isinstance(zylinder, int) else "-"
        papier_roh = (format1_roh / 1000) * (format2_roh / 1000) * (seiten / 2) * (papiergewicht / 1_000_000) * auflage
        papier_netto = (bahnbreite / 1000) * (zylinder / 1000) * (auflage / nutzen) * (papiergewicht / 1_000_000)
        papier_zuschlag = papier_netto * 0.05 + 1
        papier_summe = papier_netto + papier_zuschlag
        kosten_papier = papier_summe * papierpreis

        papier_data[variante] = {
            "Bahnbreite (mm)": f"{bahnbreite:,}".replace(",", "."),
            "Zylinder (mm)": f"{zylinder:,}".replace(",", "."),
            "Delta Rohprodukt/Zylinder (mm)": f"{delta_zyl:,}".replace(",", ".") if isinstance(delta_zyl, int) else "-",
            "Papier Rohprodukt (t)": f"{papier_roh:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "Papier Netto (Zylinder) (t)": f"{papier_netto:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "Papier Zuschlag & Rüsten (t)": f"{papier_zuschlag:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "Summe Papier Brutto (t)": f"{papier_summe:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "Kosten Papier (€)": f"{kosten_papier:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        }

    # Tabelle generieren und anzeigen
    df_papier = pd.DataFrame(papier_data)
    st.markdown("#### 📄 Papier")
    st.table(df_papier)

    # Neue Tabelle: Farbe

    # 1. Bedruckte Fläche (m²)
    df_farbe = pd.DataFrame(index=["Bedruckte Fläche (m²)", "Farbverbrauch (kg)", "Kosten Farbe (€)"])

    for variante in df_gueltig["Variante"]:
        # Rohdaten berechnen
        bedruckte_flaeche = (format1_roh / 1000) * (format2_roh / 1000) * seiten * auflage
        farbverbrauch = (bedruckte_flaeche * farbauftrag) / 1000  # in kg
        kosten_farbe = farbverbrauch * preis_farbe

        # Formatierte Einträge mit deutschem Zahlensystem (Tausenderpunkt, Komma als Dezimalzeichen)
        df_farbe[variante] = [
            f"{bedruckte_flaeche:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " m²",
            f"{farbverbrauch:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " kg",
            f"{kosten_farbe:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " €",
        ]

    # Anzeige
    st.markdown("#### 🎨 Farbe")
    st.table(df_farbe)

    # Neue Tabelle Maschine: Nur für gültige Varianten
    maschinen_data = {}

    for index, row in df_gueltig.iterrows():
        variante = row["Variante"]
        nutzen = int(row["Nutzen"])
        zylinder = naechster_zylinder(row["theor. Zylinderumfang"])

        # Berechnungen
        umdrehungen = auflage / nutzen
        geschwindigkeit = zylinder * 63.29113924
        netto_stunden = umdrehungen / geschwindigkeit
        ruestzeit = 3
        brutto_stunden = netto_stunden + ruestzeit
        kosten_maschine = brutto_stunden * maschinenpreis

        maschinen_data[variante] = {
            "Umdrehungen": f"{umdrehungen:,.0f}".replace(",", "."),
            "Geschwindigkeit (u/h)": f"{geschwindigkeit:,.0f}".replace(",", "."),
            "Maschinenstunden Netto": f"{netto_stunden:,.2f}".replace(",", "."),
            "Rüsten, Einrichten": f"{ruestzeit:,.0f}".replace(",", "."),
            "Maschinenstunden Brutto": f"{brutto_stunden:,.2f}".replace(",", "."),
            "Kosten Maschine (€)": f"{kosten_maschine:,.2f}".replace(",", ".")
        }

    # Tabelle anzeigen
    st.markdown("#### 💡 Maschine")
    df_maschine = pd.DataFrame(maschinen_data)
    st.table(df_maschine)
