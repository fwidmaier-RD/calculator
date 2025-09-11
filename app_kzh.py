import streamlit as st
import pandas as pd

#Import JSON und OS für künftige Anwendungen
import json
import os

# JSON-Datei mit Zylinderformaten laden
def lade_zylinderformate(pfad="zylinderformate.json"):
    try:
        with open(pfad, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Fehler beim Laden der Zylinderformate: {e}")
        return {}

zylinder_data = lade_zylinderformate()


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
    st.title("Drucklegung und Kalkulation Doppelnutzen - am kopf zusammenhängend Produktion V1")

   
    # Eingaben Objekt
    st.subheader("📋 Angaben Objekt")

    format_breite = st.number_input("Format Endprodukt horizontal (mm)", min_value=100, max_value=600, value=200)
    format_hoehe = st.number_input("Format Endprodukt vertikal (mm)", min_value=100, max_value=600, value=250)
    seiten = st.number_input("Anzahl Seiten Endprodukt", min_value=4, step=4, value=48)

    # Beschnittabfrage
    beschnitt_aktiv = st.checkbox("Mit Beschnitt rechnen?", value=True)
    if beschnitt_aktiv:
        beschnitt = st.number_input("Beschnitt je Seite (mm)", min_value=0.0, max_value=10.0, value=3.0, step=0.5)
        if beschnitt < 3.0:
            st.warning("⚠️ Der Beschnitt ist für diese Produktionsart zu klein (mindestens 3 mm empfohlen).")
    else:
        beschnitt = 0.0
        format_hoehe += 3  # automatische Erhöhung bei Produktion ohne Beschnitt

    # Berechnung Rohproduktwerte
    format1_roh = format_breite + beschnitt 
    format2_roh = format_hoehe + 2 * beschnitt
    lagen_roh = seiten / 2

    # Anzeige Rohprodukt
    rohprodukt_data = pd.DataFrame({
        "Parameter": [
            "Rohformat horizontal (mm)",
            "Rohformat vertikal (mm)"
        ],
        "Wert": [
            format1_roh,
            format2_roh
        ]
    })
    rohprodukt_data["Wert"] = rohprodukt_data["Wert"].apply(
        lambda v: f"{v:.0f}" if v == int(v) else f"{v:.2f}"
    ).astype(str)

    st.subheader("📄 Rohprodukt")
    st.table(rohprodukt_data)

    # Berechnung Abschnittswerte
    seiten_abschnitt = seiten
    stranganzahl = seiten_abschnitt / 2
    bahnbreite_abschnitt = format2_roh * 2
    strangbreite_abschnitt = format1_roh

    abschnitt_data = pd.DataFrame({
        "Parameter": [
            "Seiten Abschnitt",
            "Erforderliche Stränge",
            "Bahnlänge Abschnitt Doppelnutzen hor (mm)",
            "Strangbreite Abschnitt Doppelnutzen vert (mm)"
        ],
        "Wert": [
            seiten_abschnitt,
            stranganzahl,
            bahnbreite_abschnitt,
            strangbreite_abschnitt
        ]
    })
    abschnitt_data["Wert"] = abschnitt_data["Wert"].apply(
        lambda v: f"{v:.0f}" if v == int(v) else f"{v:.2f}"
    ).astype(str)

    st.subheader("✂️ Abschnitt")
    st.table(abschnitt_data)




    # 🔍 Validierung der Abschnittswerte (nur Doppelstrang-Produktion)
    st.subheader("✅ Validierung der Abschnittswerte")


    abschnitt_valide = False
    doppelstrang_valide = False

    # Regel 1: 2 bis 16 Stränge – immer zulässig
    if 2 <= stranganzahl <= 16:
        doppelstrang_valide = True

    # Regel 2: 22–64 Stränge – nur wenn Vielfaches von 2, 3 oder 4 × [11–16]
    elif 22 <= stranganzahl <= 64:
        for faktor in [2, 3, 4]:
            for basis in range(11, 17):
                if stranganzahl == faktor * basis:
                    doppelstrang_valide = True
                    break
    
    # Ergebnis anzeigen
    if doppelstrang_valide:
        st.success("✅ Doppelstrang-Produktion möglich.")
        abschnitt_valide = True
    else:
        if stranganzahl < 2:
            st.error("❌ Doppelstrang-Produktion nicht möglich (Weniger als 2 Stränge).")
        elif stranganzahl > 64:
            st.error("❌ Doppelstrang-Produktion nicht möglich (Mehr als 64 Stränge).")
        else:
            st.error("❌ Doppelstrang-Produktion nicht möglich (Ungültige Stranganzahl für Doppelstrang-Verfahren).")

    # Validierung Bahnbreite Abschnitt
    if bahnbreite_abschnitt < 300:
        st.error("❌ Bahnlänge Abschnitt hor ist zu kurz. Mindestwert: 300 mm.")
        abschnitt_valide = False
    else:
        st.success("✅ Bahnlänge Abschnitt hor ist gültig (≥ 300 mm).")

    # Validierung Strangbreite Abschnitt
    if strangbreite_abschnitt < 195:
        st.warning("⚠️ Strangbreite unter 195 mm – Machbarkeit muss technisch geprüft werden!")
    elif strangbreite_abschnitt > 400:
        st.error("❌ Strangbreite Abschnitt vert ist zu breit. Maximalwert: 400 mm.")
        abschnitt_valide = False
    else:
        st.success("✅ Strangbreite Abschnitt vert ist gültig (195–400 mm).")

    # Stop, wenn ungültig
    if not abschnitt_valide:
        st.warning("❌ Da der Abschnitt nicht valide ist, lässt sich dieses Objekt nicht produzieren.\n\n👉 Bitte passe Deine Angaben an!")
        st.stop()



    # 🔍 Drucklegung – Variantenprüfung

    # Vorbereitung: Definition aller Standardvarianten
    varianten_info = [
        ("4U ohne Sammeln", 1, 2, 2, 4),
        ("4U mit Sammeln", 2, 2, 1, 8),
        ("6U ohne Sammeln", 1, 3, 3, 4),
        ("6U mit Sammeln", 3, 3, 1, 12),
        ("8U ohne Sammeln", 1, 4, 4, 4),
        ("8U mit 1× Sammeln", 2, 4, 2, 8),
        ("8U mit 2× Sammeln", 4, 4, 1, 16)
    ]

    varianten = []

    # Schleife für Standard- und Doppelstrangvarianten
    for name, sammelteiler, umbruch, nutzen, seitenregel in varianten_info:
        for ist_doppelstrang in [False, True]:
            variant_name = f"{name} (Doppelstrang)" if ist_doppelstrang else name
            faktor = 2 if ist_doppelstrang else 1

            try:
                anzahl_strang = (stranganzahl / sammelteiler) / faktor
                zylinder = umbruch * bahnbreite_abschnitt
                bahnbreite = anzahl_strang * strangbreite_abschnitt * faktor

                status = "✅ Möglich"
                gruende = []

                # Regel: Maximale Stranganzahl
                if ist_doppelstrang:
                    if anzahl_strang > 16:
                        status = "❌ Nicht möglich"
                        gruende.append("Mehr als 16 Stränge (Doppelstrang)")
                else:
                    if anzahl_strang > 10:
                        status = "❌ Nicht möglich"
                        gruende.append("Mehr als 10 Stränge")

                # Prüfung Zylinderumfang
                if zylinder < 790 or zylinder > 1530:
                    status = "❌ Nicht möglich"
                    gruende.append("Zylinderumfang nicht im zulässigen Bereich")

                # Prüfung Bahnbreite
                if bahnbreite < 800 or bahnbreite > 2670:
                    status = "❌ Nicht möglich"
                    gruende.append("Bahnbreite nicht im zulässigen Bereich")

                # Prüfung Seitenregel Doppelstrang neu
                if seiten % 2 != 0:
                    status = "❌ Nicht möglich"
                    gruende.append("Seitenanzahl nicht durch 2 teilbar")

                varianten.append({
                    "Variante": variant_name,
                    "Nutzen": nutzen,
                    "Stränge": int(anzahl_strang),
                    "theor. Zylinderumfang": f"{int(zylinder)} mm",
                    "Bahnbreite": f"{int(bahnbreite)} mm",
                    "Status": status,
                    "Grund": ", ".join(gruende) if gruende else ""
                })

            except Exception as e:
                continue

    # In DataFrame umwandeln und auf Doppelstrang-Varianten filtern
    df_varianten = pd.DataFrame(varianten)
    df_varianten = df_varianten[["Variante", "Nutzen", "Stränge", "theor. Zylinderumfang", "Bahnbreite", "Status", "Grund"]]
    df_varianten = df_varianten[df_varianten["Variante"].str.contains("Doppelstrang")]

    # Anzeige der Tabelle
    st.subheader("🔍 Drucklegung – Variantenprüfung")
    
    # Infobox Doppelnutzen-Produktion
    st.info("ℹ️ Je Abschnitt werden 2 Nutzen erzeugt.\nDie Anzahl Nutzen in der folgenden Tabelle bezieht sich auf den Abschnitt und nicht auf das Endprodukt.")               
    
    st.table(df_varianten)




    # 📊 Kalkulation – Eingaben
    st.subheader("\U0001F4CA Kalkulation")

    # Eingabefelder für Kalkulation
    auflage = st.number_input("Auflage (Stück)", min_value=1000, step=1000, format="%d", value=500000)
    auflage_rechnerisch = auflage / 2
    st.markdown(f"**Benötigte Anzahl Abschnitte wg. Doppelnutzen:** {auflage_rechnerisch:,.0f}".replace(",", "."))

    # Je nach Bezug mit rechnerischer Auflage rechnen!
    # Da wir im Doppelnutzen arbeiten, reicht die halbe Auflage zur Produktion


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


    # Alle Zylinderformate aus der JSON-Datei extrahieren und sortieren
    zylinder_umfaenge = sorted({z for maschine in zylinder_data.values() for z in maschine})


    # Funktion zur Ermittlung des passenden Zylinders
    def naechster_zylinder(theor_umfang):
        theor_wert = int(theor_umfang.replace(" mm", ""))
        for z in zylinder_umfaenge:
            if z >= theor_wert:
                return z
        return "-"


    # Tabelle Papier
    papier_data = {}

    for index, row in df_gueltig.iterrows():
        variante = row["Variante"]
        bahnbreite = int(row["Bahnbreite"].replace(" mm", ""))
        theor_zyl = int(row["theor. Zylinderumfang"].replace(" mm", ""))
        nutzen = int(row["Nutzen"])
        zylinder = naechster_zylinder(row["theor. Zylinderumfang"])

        delta_zyl = zylinder - theor_zyl if isinstance(zylinder, int) else "-"
        papier_roh = (format1_roh / 1000) * (format2_roh / 1000) * (seiten / 2) * (papiergewicht / 1_000_000) * auflage
        papier_netto = (bahnbreite / 1000) * (zylinder / 1000) * (auflage_rechnerisch / nutzen) * (papiergewicht / 1_000_000)
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
    st.markdown("#### 🧻 Papier")
    st.table(df_papier)

    # Tabelle Farbe

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

    # Tabelle Maschine
    maschinen_data = {}

    for index, row in df_gueltig.iterrows():
        variante = row["Variante"]
        nutzen = int(row["Nutzen"])
        zylinder = naechster_zylinder(row["theor. Zylinderumfang"])

        # Berechnungen
        umdrehungen = auflage_rechnerisch / nutzen
        geschwindigkeit = (bahngeschwindigkeit * 1_000_000) / zylinder
        maschinenstunden_netto = umdrehungen / geschwindigkeit
        ruesten = 3
        maschinenstunden_brutto = maschinenstunden_netto + ruesten
        kosten_maschine = maschinenstunden_brutto * maschinenpreis

        maschinen_data[variante] = {
            "Umdrehungen": f"{umdrehungen:,.0f}".replace(",", "."),
            "Geschwindigkeit (u/h)": f"{geschwindigkeit:,.0f}".replace(",", "."),
            "Maschinenstunden Netto": f"{maschinenstunden_netto:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "Rüsten, Einrichten": f"{ruesten}",
            "Maschinenstunden Brutto": f"{maschinenstunden_brutto:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "Kosten Maschine (€)": f"{kosten_maschine:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        }

    # Tabelle anzeigen
    st.markdown("#### ⚙️ Maschine")
    df_maschine = pd.DataFrame(maschinen_data)
    st.table(df_maschine)

    # Neue Tabelle "Kosten"
    kosten_data = {}

    try:
        for variante in df_gueltig["Variante"]:
            # Werte aus den Tabellen abrufen und korrekt formatieren (Euro-Zeichen und Leerzeichen entfernen)
            kosten_papier_str = df_papier.at["Kosten Papier (€)", variante].replace(".", "").replace(",", ".").replace(" €", "")
            kosten_farbe_str = df_farbe.at["Kosten Farbe (€)", variante].replace(".", "").replace(",", ".").replace(" €", "")
            kosten_maschine_str = df_maschine.at["Kosten Maschine (€)", variante].replace(".", "").replace(",", ".").replace(" €", "")

            # Umwandlung in float
            kosten_papier = float(kosten_papier_str)
            kosten_farbe = float(kosten_farbe_str)
            kosten_maschine = float(kosten_maschine_str)

            # Gesamtkosten berechnen
            kosten_gesamt = kosten_papier + kosten_farbe + kosten_maschine
            kosten_pro_tausend = kosten_gesamt / (auflage / 1000)
            kosten_pro_stueck = kosten_gesamt / auflage

            kosten_data[variante] = {
                "Kosten gesamt (€)": f"{kosten_gesamt:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                "Kosten / 1.000 (€)": f"{kosten_pro_tausend:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
                "Kosten / Stück (€)": f"{kosten_pro_stueck:,.4f}".replace(",", "X").replace(".", ",").replace("X", ".")
            }
    except Exception as e:
        st.error("Fehler bei der Berechnung der Gesamtkosten.")
        st.write(e)

    # Falls erfolgreich, als DataFrame anzeigen
    if kosten_data:
        df_kosten = pd.DataFrame(kosten_data)
        st.markdown("#### 🪙 Kosten")
        st.table(df_kosten)