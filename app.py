"""
Streamlit UI for the Eco‑Pilot Caracterización module.

This interface allows a user to upload a template Excel file with multiple
tabs (``01_Lotes``, ``02_Muestras``, ``03_Geoquimica``) and explore the
information interactively.  It also computes a simple recommendation using
rules defined in ``utils.rules``.  Optionally, data can be posted to the
REST API by specifying its URL and clicking the upload button.
"""

import streamlit as st
import pandas as pd
import requests

from utils.rules import recommend_process


st.set_page_config(page_title="Eco‑Pilot · Caracterización", layout="wide")

st.title("Eco‑Pilot · Módulo de Caracterización")

api_url = st.sidebar.text_input(
    "URL de la API (opcional)", value="http://localhost:8000"
)

uploaded_file = st.file_uploader(
    "Sube la plantilla Excel (con las pestañas 01_Lotes, 02_Muestras y 03_Geoquimica)",
    type=["xlsx"],
)

if uploaded_file:
    # Leer las distintas hojas
    xls = pd.ExcelFile(uploaded_file)
    try:
        df_lotes = pd.read_excel(xls, "01_Lotes")
        df_muestras = pd.read_excel(xls, "02_Muestras")
        df_geo = pd.read_excel(xls, "03_Geoquimica")
    except Exception as e:
        st.error(f"Error leyendo el archivo: {e}")
    else:
        # Selección de lote
        lote_ids = df_lotes["lote_id"].astype(str).dropna().unique().tolist()
        selected_lote = st.sidebar.selectbox("Selecciona un lote", lote_ids)

        # Mostrar info del lote
        st.header("Información del lote")
        st.dataframe(
            df_lotes[df_lotes["lote_id"].astype(str) == selected_lote]
        )

        # Filtrar y mostrar muestras
        st.header("Muestras asociadas")
        muestras_sel = df_muestras[
            df_muestras["lote_id"].astype(str) == selected_lote
        ]
        st.dataframe(muestras_sel)

        # Filtrar y mostrar geoquímica
        st.header("Resultados de geoquímica")
        geo_sel = df_geo[
            df_geo["muestra_id"].astype(str).isin(
                muestras_sel["muestra_id"].astype(str)
            )
        ]
        st.dataframe(geo_sel)

        # Calcular recomendación sencilla
        st.header("Recomendación de proceso (demo)")
        if not geo_sel.empty:
            # Tomar la media de S_sulfuro y As
            s_sulfuro_mean = None
            as_mean = None
            if "S_sulfuro_%" in geo_sel.columns:
                s_sulfuro_mean = geo_sel["S_sulfuro_%"].astype(float).mean()
            if "As_ppm" in geo_sel.columns:
                as_mean = geo_sel["As_ppm"].astype(float).mean()
            recomendacion = recommend_process(s_sulfuro_mean, as_mean)
            st.success(
                f"Recomendación para el lote {selected_lote}: {recomendacion}"
            )
        else:
            st.info(
                "No hay datos de geoquímica para este lote; no se puede calcular una recomendación."
            )

        # Botón para cargar datos a la API
        if st.button("Enviar datos a la API"):
            try:
                # Enviar lote seleccionado
                lotes_to_post = df_lotes[
                    df_lotes["lote_id"].astype(str) == selected_lote
                ]
                for _, lote_row in lotes_to_post.iterrows():
                    payload = lote_row.dropna().to_dict()
                    # Normalizar nombres de columnas según el esquema
                    payload = {
                        k: v
                        for k, v in payload.items()
                        if k
                        in [
                            "lote_id",
                            "deposito_id",
                            "nombre_lote",
                            "ubicacion_wgs84_lat",
                            "ubicacion_wgs84_lon",
                            "estado_lote",
                            "volumen_m3_estimado",
                            "densidad_t_m3_estimada",
                            "toneladas_estimadas",
                        ]
                    }
                    requests.post(f"{api_url}/lotes/", json=payload)
                # Enviar muestras con geoquímica asociada
                for _, muestra_row in muestras_sel.iterrows():
                    payload = muestra_row.dropna().to_dict()
                    geo_part = geo_sel[geo_sel["muestra_id"] == muestra_row["muestra_id"]]
                    geo_json = None
                    if not geo_part.empty:
                        row = geo_part.iloc[0].dropna().to_dict()
                        # Convertir nombres con % a sufijo _pct
                        def normalize_key(key):
                            if key.endswith("_%"):
                                return key[:-2] + "_pct"
                            return key
                        geo_json = {normalize_key(k): v for k, v in row.items() if k != "muestra_id"}
                    if geo_json:
                        payload["geoquimica"] = geo_json
                    requests.post(f"{api_url}/muestras/", json=payload)
                st.success("Datos enviados correctamente a la API.")
            except Exception as e:
                st.error(f"Error enviando datos: {e}")
else:
    st.info("Carga un archivo Excel para comenzar a trabajar.")