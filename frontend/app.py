# --- make repo root importable ---

import os, sys

import pandas as pd
import requests
import streamlit as st

THIS_DIR = os.path.dirname(__file__)
REPO_ROOT = os.path.abspath(os.path.join(THIS_DIR, ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from utils.rules import recommend_process


def run_characterization() -> None:
    """Renderiza la interfaz de caracterización de lotes."""

    st.title("Eco-Pilot · Módulo de Caracterización y Laboratorio (MVP)")

    api_url = st.text_input(
        "URL base de la API (opcional, por ejemplo http://localhost:8000)",
        value="http://localhost:8000",
    )

    uploaded_file = st.file_uploader(
        "Sube una plantilla Excel (con hojas 01_Lotes, 02_Muestras y 03_Geoquimica)",
        type=["xlsx"],
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
            if "lote_id" not in df_lotes.columns:
                st.warning(
                    "La hoja 01_Lotes no contiene la columna 'lote_id'. Revisa la plantilla."
                )
                return

            lote_ids = (
                df_lotes["lote_id"].dropna().astype(str).unique().tolist()
            )

            if not lote_ids:
                st.warning(
                    "No se encontraron valores válidos para 'lote_id' en la hoja 01_Lotes."
                )
                return

            selected_lote = st.sidebar.selectbox("Selecciona un lote", lote_ids)

            if not selected_lote:
                return

            st.header("Información del lote")
            st.dataframe(df_lotes[df_lotes["lote_id"].astype(str) == selected_lote])

            st.header("Muestras asociadas")
            muestras_sel = df_muestras[df_muestras["lote_id"].astype(str) == selected_lote]
            st.dataframe(muestras_sel)

            st.header("Resultados de geoquímica")
            geo_sel = df_geo[
                df_geo["muestra_id"].astype(str).isin(
                    muestras_sel["muestra_id"].astype(str)
                )
            ]
            st.dataframe(geo_sel)

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
            col2.metric(
                "Promedio S sulfuro (%)",
                f"{s_sulfuro_mean:.2f}" if s_sulfuro_mean is not None else "N/A",
            )
            col3.metric(
                "Promedio As (ppm)",
                f"{as_mean:.2f}" if as_mean is not None else "N/A",
            )

            if (
                not geo_sel.empty
                and "S_sulfuro_%" in geo_sel.columns
                and "As_ppm" in geo_sel.columns
            ):
                chart_data = pd.DataFrame(
                    {
                        "S_sulfuro_%": geo_sel["S_sulfuro_%"].astype(float),
                        "As_ppm": geo_sel["As_ppm"].astype(float),
                    }
                )
                st.bar_chart(chart_data)

            recomendacion = recommend_process(s_sulfuro_mean, as_mean)

            if api_url:
                try:
                    url = api_url.rstrip("/") + "/ml/predict"
                    payload = {
                        "s_sulfuro_pct": s_sulfuro_mean,
                        "as_ppm": as_mean,
                    }
                    resp = requests.post(url, json=payload)
                    if resp.status_code == 200:
                        recomendacion = resp.json().get(
                            "recommendation", recomendacion
                        )
                except Exception:
                    pass

            st.success(
                f"Recomendación para el lote {selected_lote}: {recomendacion}"
            )
    else:
        st.info("Por favor sube una plantilla para comenzar.")


if __name__ == "__main__":  # pragma: no cover
    st.set_page_config(
        page_title="Eco-Pilot · Caracterización y Laboratorio", layout="wide"
    )
    run_characterization()

