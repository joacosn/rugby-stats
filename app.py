import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Rugby Club Stats", layout="wide")

DATA_DIR = "Data"

@st.cache_data(ttl=300)
def load_all_matches():
    tackles_list = []
    pases_list = []

    files = os.listdir(DATA_DIR)

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

    # Calculated columns
    if not tackles.empty:
        tackles["Total"] = tackles["Positivo"] + tackles["Neutro"] + tackles["Negativo"] + tackles["Fallido"]
        tackles["Eficiencia %"] = ((tackles["Positivo"] + tackles["Neutro"]) / tackles["Total"] * 100).round(1)

    if not pases.empty:
        pases["Total"] = pases["Acertado"] + pases["Fallido"]
        pases["Eficiencia %"] = (pases["Acertado"] / pases["Total"] * 100).round(1)

    return tackles, pases

tackles_df, pases_df = load_all_matches()

if tackles_df.empty:
    st.warning("No se encontraron archivos en la carpeta /data. Subí al menos un par de archivos .csv para comenzar.")
    st.stop()

# ── Sidebar navigation ────────────────────────────────────────
st.sidebar.title("🏉 Rugby Club Stats")
page = st.sidebar.radio("Navegación", ["Resumen del Partido", "Rankings", "Gráficos"])

partidos = sorted(tackles_df["partido"].unique().tolist())

# ── PAGE 1: Match Summary ─────────────────────────────────────
if page == "Resumen del Partido":
    st.title("📋 Resumen del Partido")

    selected_partido = st.selectbox("Seleccioná un partido", partidos)

    ft = tackles_df[tackles_df["partido"] == selected_partido].copy()
    fp = pases_df[pases_df["partido"] == selected_partido].copy()

    st.markdown("---")

    # Team headline metrics
    total_tackles = ft["Total"].sum()
    team_tackle_eff = ((ft["Positivo"].sum() + ft["Neutro"].sum()) / ft["Total"].sum() * 100).round(1)
    total_pases = fp["Total"].sum()
    team_pase_eff = (fp["Acertado"].sum() / fp["Total"].sum() * 100).round(1)

    st.subheader("Métricas del equipo")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Tackles", int(total_tackles))
    m2.metric("Eficiencia Tackles", f"{team_tackle_eff}%")
    m3.metric("Total Pases", int(total_pases))
    m4.metric("Eficiencia Pases", f"{team_pase_eff}%")

    st.markdown("---")

    # Per player breakdown
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Tackles por jugador")
        st.dataframe(
            ft[["Jugador", "Positivo", "Neutro", "Negativo", "Fallido", "Total", "Eficiencia %"]],
            use_container_width=True,
            hide_index=True
        )

    with col2:
        st.subheader("Pases por jugador")
        st.dataframe(
            fp[["Jugador", "Acertado", "Fallido", "Total", "Eficiencia %"]],
            use_container_width=True,
            hide_index=True
        )

# ── PAGE 2: Rankings ──────────────────────────────────────────
elif page == "Rankings":
    st.title("🏆 Rankings")
    st.info("Próximamente...")

# ── PAGE 3: Charts ────────────────────────────────────────────
elif page == "Gráficos":
    st.title("📊 Gráficos")
    st.info("Próximamente...")
