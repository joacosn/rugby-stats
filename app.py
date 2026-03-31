import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Rugby Club Stats", layout="wide")
st.title("Estadísticas PS")
st.markdown("---")

DATA_DIR = "Data"

@st.cache_data(ttl=300)

def load_all_matches():
    tackles_list = []
    pases_list = []

    files = os.listdir(DATA_DIR)

    # Find all tackles files and match with pases
    for filename in files:
        if not filename.endswith("_Tackles.csv"):
            continue

        base = filename.replace("_Tackles.csv", "")
        pases_file = base + "_Pases.csv"

        if pases_file not in files:
            continue

        parts = base.split("_")
        if len(parts) != 3:
            continue

        division, our_team, opponent = parts
        match_label = f"{division} | {our_team} vs {opponent}"

        df_tackles = pd.read_csv(os.path.join(DATA_DIR, filename))
        df_tackles["partido"] = match_label
        tackles_list.append(df_tackles)

        df_pases = pd.read_csv(os.path.join(DATA_DIR, pases_file))
        df_pases["partido"] = match_label
        pases_list.append(df_pases)

    tackles = pd.concat(tackles_list, ignore_index=True) if tackles_list else pd.DataFrame()
    pases = pd.concat(pases_list, ignore_index=True) if pases_list else pd.DataFrame()

    return tackles, pases

tackles_df, pases_df = load_all_matches()

if tackles_df.empty:
    st.warning("No se encontraron archivos en la carpeta /data. Subí al menos un par de archivos .csv para comenzar.")
    st.stop()
# st.write("Tackles columns:", tackles_df.columns.tolist())
# st.write("Pases columns:", pases_df.columns.tolist())
# ── Partido filter ────────────────────────────────────────────
partidos = ["Todos los partidos"] + sorted(tackles_df["partido"].unique().tolist())
selected_partido = st.selectbox("Seleccioná un partido", partidos)

if selected_partido != "Todos los partidos":
    filtered_tackles = tackles_df[tackles_df["partido"] == selected_partido]
    filtered_pases = pases_df[pases_df["partido"] == selected_partido]
else:
    filtered_tackles = tackles_df.copy()
    filtered_pases = pases_df.copy()

st.markdown("---")

# ── Tables ────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("Tackles")
    st.dataframe(
        filtered_tackles[["Jugador", "Positivo", "Neutro", "Negativo", "Fallido"]],
        use_container_width=True,
        hide_index=True
    )

with col2:
    st.subheader("Pases")
    st.dataframe(
        filtered_pases[["Jugador", "Acertado", "Fallido"]],
        use_container_width=True,
        hide_index=True
    )
