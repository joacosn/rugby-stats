import streamlit as st
import pandas as pd
import os
import plotly.express as px

# ── Page config ───────────────────────────────────────────────
st.set_page_config(page_title="Rugby Club Stats", layout="wide")

# ── Load all match files from /data folder ────────────────────
# Each file is named DIVISION_OURTEAM_OPPONENT.xlsx
# and has two sheets: Tackles and Pases

DATA_DIR = "data"

@st.cache_data(ttl=300)
def load_all_matches():
    tackles_list = []
    pases_list = []

    for filename in os.listdir(DATA_DIR):
        if not filename.endswith(".xlsx"):
            continue

        # Parse metadata from filename
        name = filename.replace(".xlsx", "")
        parts = name.split("_")
        if len(parts) != 3:
            continue  # Skip files that don't match expected naming

        division, our_team, opponent = parts
        filepath = os.path.join(DATA_DIR, filename)

        # Read Tackles sheet
        df_tackles = pd.read_excel(filepath, sheet_name="Tackles")
        df_tackles["division"] = division
        df_tackles["our_team"] = our_team
        df_tackles["opponent"] = opponent
        df_tackles["match"] = f"{our_team} vs {opponent}"
        tackles_list.append(df_tackles)

        # Read Pases sheet
        df_pases = pd.read_excel(filepath, sheet_name="Pases")
        df_pases["division"] = division
        df_pases["our_team"] = our_team
        df_pases["opponent"] = opponent
        df_pases["match"] = f"{our_team} vs {opponent}"
        pases_list.append(df_pases)

    tackles = pd.concat(tackles_list, ignore_index=True) if tackles_list else pd.DataFrame()
    pases = pd.concat(pases_list, ignore_index=True) if pases_list else pd.DataFrame()

    # Calculated metrics
    if not tackles.empty:
        tackles["total"] = tackles["positivo"] + tackles["neutro"] + tackles["negativo"] + tackles["fallido"]
        tackles["efectividad"] = ((tackles["positivo"] + tackles["neutro"]) / tackles["total"] * 100).round(1)

    if not pases.empty:
        pases["total"] = pases["acertado"] + pases["fallido"]
        pases["efectividad"] = (pases["acertado"] / pases["total"] * 100).round(1)

    return tackles, pases

tackles_df, pases_df = load_all_matches()

# ── Header ────────────────────────────────────────────────────
st.title("🏉 Estadísticas del Club")
st.markdown("---")

if tackles_df.empty:
    st.warning("No se encontraron archivos en la carpeta /data. Subí al menos un archivo .xlsx para comenzar.")
    st.stop()

# ── Sidebar filters ───────────────────────────────────────────
st.sidebar.header("Filtros")

divisions = ["Todas"] + sorted(tackles_df["division"].unique().tolist())
selected_division = st.sidebar.selectbox("División", divisions)

# Filter matches based on division
filtered_tackles = tackles_df.copy()
filtered_pases = pases_df.copy()

if selected_division != "Todas":
    filtered_tackles = filtered_tackles[filtered_tackles["division"] == selected_division]
    filtered_pases = filtered_pases[filtered_pases["division"] == selected_division]

matches = ["Todos los partidos"] + sorted(filtered_tackles["match"].unique().tolist())
selected_match = st.sidebar.selectbox("Partido", matches)

if selected_match != "Todos los partidos":
    filtered_tackles = filtered_tackles[filtered_tackles["match"] == selected_match]
    filtered_pases = filtered_pases[filtered_pases["match"] == selected_match]

players = ["Todos los jugadores"] + sorted(filtered_tackles["jugador"].unique().tolist())
selected_player = st.sidebar.selectbox("Jugador", players)

if selected_player != "Todos los jugadores":
    filtered_tackles = filtered_tackles[filtered_tackles["jugador"] == selected_player]
    filtered_pases = filtered_pases[filtered_pases["jugador"] == selected_player]

# ── Tabs ──────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📋 Partido", "🏆 Rankings", "👤 Jugador"])

# ── TAB 1: Match view ─────────────────────────────────────────
with tab1:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Tackles")
        st.dataframe(
            filtered_tackles[["jugador", "match", "positivo", "neutro", "negativo", "fallido", "efectividad"]],
            use_container_width=True,
            hide_index=True
        )

    with col2:
        st.subheader("Pases")
        st.dataframe(
            filtered_pases[["jugador", "match", "acertado", "fallido", "efectividad"]],
            use_container_width=True,
            hide_index=True
        )

# ── TAB 2: Rankings ───────────────────────────────────────────
with tab2:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Más tackles totales")
        rank_tackles = (
            filtered_tackles.groupby("jugador")["total"]
            .sum().reset_index()
            .sort_values("total", ascending=False)
        )
        fig1 = px.bar(rank_tackles, x="total", y="jugador", orientation="h",
                      color="total", color_continuous_scale="Reds")
        fig1.update_layout(showlegend=False, coloraxis_showscale=False, yaxis_title="")
        st.plotly_chart(fig1, use_container_width=True)

        st.subheader("Mejor efectividad en tackles (%)")
        rank_teff = (
            filtered_tackles.groupby("jugador")["efectividad"]
            .mean().round(1).reset_index()
            .sort_values("efectividad", ascending=False)
        )
        fig2 = px.bar(rank_teff, x="efectividad", y="jugador", orientation="h",
                      color="efectividad", color_continuous_scale="Greens")
        fig2.update_layout(showlegend=False, coloraxis_showscale=False, yaxis_title="")
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        st.subheader("Más pases totales")
        rank_pases = (
            filtered_pases.groupby("jugador")["total"]
            .sum().reset_index()
            .sort_values("total", ascending=False)
        )
        fig3 = px.bar(rank_pases, x="total", y="jugador", orientation="h",
                      color="total", color_continuous_scale="Blues")
        fig3.update_layout(showlegend=False, coloraxis_showscale=False, yaxis_title="")
        st.plotly_chart(fig3, use_container_width=True)

        st.subheader("Mejor efectividad en pases (%)")
        rank_peff = (
            filtered_pases.groupby("jugador")["efectividad"]
            .mean().round(1).reset_index()
            .sort_values("efectividad", ascending=False)
        )
        fig4 = px.bar(rank_peff, x="efectividad", y="jugador", orientation="h",
                      color="efectividad", color_continuous_scale="Purples")
        fig4.update_layout(showlegend=False, coloraxis_showscale=False, yaxis_title="")
        st.plotly_chart(fig4, use_container_width=True)

# ── TAB 3: Player profile ─────────────────────────────────────
with tab3:
    if selected_player == "Todos los jugadores":
        st.info("Seleccioná un jugador en el panel izquierdo para ver su perfil.")
    else:
        st.subheader(f"Perfil de {selected_player}")

        # Summary metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Tackles totales", int(filtered_tackles["total"].sum()))
        m2.metric("Efectividad tackles", f"{filtered_tackles['efectividad'].mean():.1f}%")
        m3.metric("Pases totales", int(filtered_pases["total"].sum()))
        m4.metric("Efectividad pases", f"{filtered_pases['efectividad'].mean():.1f}%")

        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Tackles por partido**")
            st.dataframe(
                filtered_tackles[["match", "positivo", "neutro", "negativo", "fallido", "efectividad"]],
                use_container_width=True, hide_index=True
            )

        with col2:
            st.markdown("**Pases por partido**")
            st.dataframe(
                filtered_pases[["match", "acertado", "fallido", "efectividad"]],
                use_container_width=True, hide_index=True
            )


And your `requirements.txt`:
streamlit
pandas
openpyxl
plotly
