# --- make repo root importable ---
import os, sys
import pandas as pd
import requests
import streamlit as st

THIS_DIR = os.path.dirname(__file__)
REPO_ROOT = os.path.abspath(os.path.join(THIS_DIR, ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)


def recommend_process(s_sulfuro_pct, as_ppm):
    """
    Devuelve una recomendación de proceso en función de la geoquímica.
    - Si s_sulfuro_pct es mayor que 1 % y as_ppm es nulo o ≤500 ppm, se recomienda BIOX.
    - Si as_ppm es mayor a 500 ppm, se sugiere riesgo de arsénico y considerar biolixiviación.
    - En cualquier otro caso, se recomienda preconcentración o biolixiviación.
    """
    if s_sulfuro_pct is None:
        return "Sin datos de S sulfuro"
    if s_sulfuro_pct > 1 and (as_ppm is None or as_ppm <= 500):
        return "BIOX"
    if as_ppm is not None and as_ppm > 500:
        return "Riesgo arsénico; considerar biolixiviación"
    return "Preconcentración o biolixiviación"


# Configuración y título de la aplicación
st.set_page_config(page_title="Eco-Pilot · Caracterización y Laboratorio", layout="wide")
st.title("Eco-Pilot · Módulo de Caracterización y Laboratorio (MVP)")

# Campo para URL base de la API (opcional)
api_url = st.text_input(
    "URL base de la API (opcional, por ejemplo http://localhost:8000)",
    value="http://localhost:8000"
)

# Cargador de archivo Excel
uploaded_file = st.file_uploader(
    "Sube una plantilla Excel (con hojas 01_Lotes, 02_Muestras y 03_Geoquimica)",
    type=["xlsx"]
)

if uploaded_file:
    xls = pd.ExcelFile(uploaded_file)
    try:
        df_lotes = pd.read_excel(xls, "01_Lotes")
        df_muestras = pd.read_excel(xls, "02_Muestras")
        df_geo = pd.read_excel(xls, "03_Geoquimica")
    except Exception as e:
        st.error(f"Error leyendo el archivo: {e}")
    else:
        lote_ids = df_lotes["lote_id"].astype(str).dropna().unique().tolist()
        selected_lote = st.sidebar.selectbox("Selecciona un lote", lote_ids)

        # Información del lote
        st.header("Información del lote")
        st.dataframe(df_lotes[df_lotes["lote_id"].astype(str) == selected_lote])

        # Muestras asociadas
        st.header("Muestras asociadas")
        muestras_sel = df_muestras[df_muestras["lote_id"].astype(str) == selected_lote]
        st.dataframe(muestras_sel)

        # Geoquímica asociada
        st.header("Resultados de geoquímica")
        geo_sel = df_geo[df_geo["muestra_id"].astype(str).isin(muestras_sel["muestra_id"].astype(str))]
        st.dataframe(geo_sel)

        # Cálculo de KPIs
        s_sulfuro_mean = None
        as_mean = None
        if not geo_sel.empty:
            if "S_sulfuro_%" in geo_sel.columns:
                s_sulfuro_mean = geo_sel["S_sulfuro_%"].astype(float).mean()
            if "As_ppm" in geo_sel.columns:
                as_mean = geo_sel["As_ppm"].astype(float).mean()

        st.subheader("Resumen del lote")
        col1, col2, col3 = st.columns(3)
        col1.metric("Número de muestras", len(muestras_sel))
        col2.metric("Promedio S sulfuro (%)",
                    f"{s_sulfuro_mean:.2f}" if s_sulfuro_mean is not None else "N/A")
        col3.metric("Promedio As (ppm)",
                    f"{as_mean:.2f}" if as_mean is not None else "N/A")

        # Gráfico de barras
        if not geo_sel.empty and "S_sulfuro_%" in geo_sel.columns and "As_ppm" in geo_sel.columns:
            chart_data = pd.DataFrame({
                "S_sulfuro_%": geo_sel["S_sulfuro_%"].astype(float),
                "As_ppm": geo_sel["As_ppm"].astype(float)
            })
            st.bar_chart(chart_data)

        # Recomendación según reglas básicas
        recomendacion = recommend_process(s_sulfuro_mean, as_mean)

        # Llamada a la API de ML (si disponible)
        if api_url:
            try:
                url = api_url.rstrip("/") + "/ml/predict"
                payload = {"s_sulfuro_pct": s_sulfuro_mean, "as_ppm": as_mean}
                resp = requests.post(url, json=payload)
                if resp.status_code == 200:
                    recomendacion = resp.json().get("recommendation", recomendacion)
            except Exception:
                pass

        st.success(f"Recomendación para el lote {selected_lote}: {recomendacion}")
else:
    st.info("Por favor sube una plantilla para comenzar.")
