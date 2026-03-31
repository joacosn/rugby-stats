import streamlit as st
import pandas as pd
import os

# ── Page config ───────────────────────────────────────────────
st.set_page_config(page_title="Rugby Club Stats", layout="wide")

st.title("🏉 Estadísticas del Club")
st.markdown("---")

# ── Load all match files from /data folder ────────────────────
DATA_DIR = "Data"

@st.cache_data(ttl=300)
def load_all_matches():
    tackles_list = []
    pases_list = []

    for filename in os.listdir(DATA_DIR):
        if not filename.endswith(".xlsx"):
            continue

        name = filename.replace(".xlsx", "")
        parts = name.split("_")
        if len(parts) != 3:
            continue

        division, our_team, opponent = parts
        filepath = os.path.join(DATA_DIR, filename)
        match_label = f"{division} | {our_team} vs {opponent}"

        df_tackles = pd.read_excel(filepath, sheet_name="tackles")
        df_tackles["partido"] = match_label
        tackles_list.append(df_tackles)

        df_pases = pd.read_excel(filepath, sheet_name="pases")
        df_pases["partido"] = match_label
        pases_list.append(df_pases)

    tackles = pd.concat(tackles_list, ignore_index=True) if tackles_list else pd.DataFrame()
    pases = pd.concat(pases_list, ignore_index=True) if pases_list else pd.DataFrame()

    return tackles, pases

tackles_df, pases_df = load_all_matches()

if tackles_df.empty:
    st.warning("No se encontraron archivos en la carpeta /Data. Subí al menos un archivo .xlsx para comenzar.")
    st.stop()

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
        filtered_tackles[["jugador", "positivos", "neutros", "negativos", "fallidos"]],
        use_container_width=True,
        hide_index=True
    )

with col2:
    st.subheader("Pases")
    st.dataframe(
        filtered_pases[["jugador", "acertado", "fallido"]],
        use_container_width=True,
        hide_index=True
    )
