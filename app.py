import streamlit as st
import pandas as pd
from io import BytesIO

# Carica database materiali
materials = pd.read_csv("materials.csv")

st.title("Preventivo Elettrico Prototipo")

# Carica file impianto
uploaded_file = st.file_uploader("Carica file impianto (CSV)", type=["csv"])
if uploaded_file:
    df_imp = pd.read_csv(uploaded_file)
    st.write("Dati impianto:")
    st.dataframe(df_imp)

    # Associazione materiali (default automatico)
    st.subheader("Seleziona materiali per ogni simbolo")
    df_imp['materiale_selezionato'] = df_imp['simbolo'].map({
        'presa': 'BL123',
        'interruttore': 'CH456',
        'cavo': 'NYM3X1.5'
    })
    st.write("Materiali preimpostati:")
    st.dataframe(df_imp[['simbolo', 'materiale_selezionato']])

    # Calcolo quantità
    df_count = df_imp.groupby('materiale_selezionato').agg({
        'simbolo': 'count',          # numero pezzi per prese/interruttori
        'lunghezza_cavo': 'sum'      # somma lunghezze per cavi
    }).reset_index().rename(columns={'simbolo':'quantità'})

    # Unisci con tabella materiali
    df_count = df_count.merge(materials, left_on='materiale_selezionato', right_on='codice_articolo')

    # Per i cavi, la quantità = lunghezza totale
    df_count['quantità'] = df_count.apply(lambda x: x['lunghezza_cavo'] if x['unita_di_misura']=='metro' else x['quantità'], axis=1)

    # Calcolo prezzo parziale
    df_count['prezzo_parziale'] = df_count['quantità'] * df_count['prezzo_unitario']

    # Mostra tabella finale
    st.subheader("Preventivo Materiali")
    st.dataframe(df_count[['materiale','marca','codice_articolo','unita_di_misura','quantità','prezzo_unitario','prezzo_parziale']])

    # Bottone per scaricare Excel
    output = BytesIO()
    df_count[['materiale','marca','codice_articolo','unita_di_misura','quantità','prezzo_unitario','prezzo_parziale']].to_excel(output, index=False)
    output.seek(0)
    st.download_button(
        label="Scarica preventivo Excel",
        data=output,
        file_name="preventivo.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
