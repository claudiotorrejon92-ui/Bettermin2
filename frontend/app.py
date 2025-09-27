# --- make repo root importable ---

import os, sys
from io import BytesIO

import altair as alt
import pandas as pd
import requests
import streamlit as st

THIS_DIR = os.path.dirname(__file__)
REPO_ROOT = os.path.abspath(os.path.join(THIS_DIR, ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from utils.rules import recommend_process


LOTES_SCHEMA = {"lote_id": str}
MUESTRAS_SCHEMA = {"muestra_id": str, "lote_id": str}
GEOQUIMICA_SCHEMA = {
    "muestra_id": str,
    "S_sulfuro_%": float,
    "As_ppm": float,
}


def _ensure_manual_defaults() -> None:
    if "manual_data" not in st.session_state:
        st.session_state["manual_data"] = {
            "01_Lotes": pd.DataFrame(columns=list(LOTES_SCHEMA.keys())),
            "02_Muestras": pd.DataFrame(columns=list(MUESTRAS_SCHEMA.keys())),
            "03_Geoquimica": pd.DataFrame(columns=list(GEOQUIMICA_SCHEMA.keys())),
        }


def _normalize_dataframe(df: pd.DataFrame, schema: dict[str, type], name: str) -> pd.DataFrame:
    df = df.copy()
    missing_columns = [col for col in schema if col not in df.columns]
    if missing_columns:
        raise ValueError(
            f"La hoja {name} no contiene las columnas obligatorias: {', '.join(missing_columns)}"
        )

    for column, dtype in schema.items():
        if dtype is str:
            df[column] = df[column].apply(
                lambda x: str(x).strip() if pd.notnull(x) else pd.NA
            )
            if df[column].isna().any():
                raise ValueError(
                    f"La columna '{column}' en la hoja {name} tiene valores vacíos."
                )
        elif dtype is float:
            df[column] = pd.to_numeric(df[column], errors="coerce")
            if df[column].isna().any():
                raise ValueError(
                    f"La columna '{column}' en la hoja {name} debe contener solo valores numéricos."
                )

    return df


def run_characterization() -> None:
    """Renderiza la interfaz de caracterización de lotes."""

    st.title("Eco-Pilot · Módulo de Caracterización y Laboratorio (MVP)")

    api_url = st.text_input(
        "URL base de la API (opcional, por ejemplo http://localhost:8000)",
        value="http://localhost:8000",
    )

    modo_captura = st.radio(
        "Selecciona cómo deseas cargar los datos",
        ("Subir plantilla", "Ingresar datos manualmente"),
        horizontal=True,
    )

    df_lotes = None
    df_muestras = None
    df_geo = None
    data_ready = False

    if modo_captura == "Subir plantilla":
        uploaded_file = st.file_uploader(
            "Sube una plantilla Excel (con hojas 01_Lotes, 02_Muestras y 03_Geoquimica)",
            type=["xlsx"],
        )

        if uploaded_file:
            xls = pd.ExcelFile(uploaded_file)
            try:
                df_lotes_raw = pd.read_excel(xls, "01_Lotes")
                df_muestras_raw = pd.read_excel(xls, "02_Muestras")
                df_geo_raw = pd.read_excel(xls, "03_Geoquimica")
                df_lotes = _normalize_dataframe(
                    df_lotes_raw, LOTES_SCHEMA, "01_Lotes"
                )
                df_muestras = _normalize_dataframe(
                    df_muestras_raw, MUESTRAS_SCHEMA, "02_Muestras"
                )
                df_geo = _normalize_dataframe(
                    df_geo_raw, GEOQUIMICA_SCHEMA, "03_Geoquimica"
                )
            except ValueError as e:
                st.error(str(e))
            except Exception as e:
                st.error(f"Error leyendo el archivo: {e}")
            else:
                data_ready = True
                st.session_state["df_lotes"] = df_lotes
                st.session_state["df_muestras"] = df_muestras
                st.session_state["df_geo"] = df_geo
                st.session_state["data_source"] = "Subir plantilla"
    else:
        _ensure_manual_defaults()
        manual_data = st.session_state["manual_data"]

        with st.form("manual_data_form"):
            tabs = st.tabs(["01_Lotes", "02_Muestras", "03_Geoquimica"])
            with tabs[0]:
                lotes_data = st.data_editor(
                    manual_data["01_Lotes"],
                    num_rows="dynamic",
                    key="manual_lotes_editor",
                )
            with tabs[1]:
                muestras_data = st.data_editor(
                    manual_data["02_Muestras"],
                    num_rows="dynamic",
                    key="manual_muestras_editor",
                )
            with tabs[2]:
                geo_data = st.data_editor(
                    manual_data["03_Geoquimica"],
                    num_rows="dynamic",
                    key="manual_geo_editor",
                )

            submitted = st.form_submit_button("Guardar datos capturados")

        if submitted:
            try:
                lotes_norm = _normalize_dataframe(
                    pd.DataFrame(lotes_data), LOTES_SCHEMA, "01_Lotes"
                )
                muestras_norm = _normalize_dataframe(
                    pd.DataFrame(muestras_data), MUESTRAS_SCHEMA, "02_Muestras"
                )
                geo_norm = _normalize_dataframe(
                    pd.DataFrame(geo_data), GEOQUIMICA_SCHEMA, "03_Geoquimica"
                )
                if lotes_norm.empty or muestras_norm.empty or geo_norm.empty:
                    raise ValueError(
                        "Todas las hojas deben contener al menos una fila de datos."
                    )
            except ValueError as e:
                st.error(str(e))
            else:
                st.session_state["manual_data"] = {
                    "01_Lotes": lotes_norm.copy(),
                    "02_Muestras": muestras_norm.copy(),
                    "03_Geoquimica": geo_norm.copy(),
                }
                st.session_state["df_lotes"] = lotes_norm
                st.session_state["df_muestras"] = muestras_norm
                st.session_state["df_geo"] = geo_norm
                st.session_state["data_source"] = "Ingresar datos manualmente"
                st.success("Datos guardados correctamente.")

        if st.session_state.get("data_source") == "Ingresar datos manualmente":
            df_lotes = st.session_state.get("df_lotes")
            df_muestras = st.session_state.get("df_muestras")
            df_geo = st.session_state.get("df_geo")
            if (
                isinstance(df_lotes, pd.DataFrame)
                and isinstance(df_muestras, pd.DataFrame)
                and isinstance(df_geo, pd.DataFrame)
            ):
                data_ready = True

    if not data_ready:
        st.info("Carga una plantilla o ingresa datos manualmente para comenzar.")
        return

    lote_ids = df_lotes["lote_id"].dropna().astype(str).unique().tolist()

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

    with BytesIO() as output:
        with pd.ExcelWriter(output) as writer:
            df_lotes.to_excel(writer, sheet_name="01_Lotes", index=False)
            df_muestras.to_excel(writer, sheet_name="02_Muestras", index=False)
            df_geo.to_excel(writer, sheet_name="03_Geoquimica", index=False)
        output.seek(0)
        st.download_button(
            "Descargar captura en Excel",
            data=output.read(),
            file_name="ecopilot_captura.xlsx",
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "spreadsheetml.sheet"
            ),
        )

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
        chart_data = geo_sel[["muestra_id", "S_sulfuro_%", "As_ppm"]].copy()
        chart_data["S_sulfuro_%"] = pd.to_numeric(
            chart_data["S_sulfuro_%"], errors="coerce"
        )
        chart_data["As_ppm"] = pd.to_numeric(
            chart_data["As_ppm"], errors="coerce"
        )
        chart_data = chart_data.dropna(subset=["S_sulfuro_%", "As_ppm"])

        if not chart_data.empty:
            scatter = (
                alt.Chart(chart_data)
                .mark_circle(size=90)
                .encode(
                    x=alt.X("S_sulfuro_%:Q", title="S sulfuro (%)"),
                    y=alt.Y("As_ppm:Q", title="Arsénico (ppm)"),
                    tooltip=[
                        alt.Tooltip("muestra_id:N", title="Muestra"),
                        alt.Tooltip("S_sulfuro_%:Q", title="S sulfuro (%)", format=".2f"),
                        alt.Tooltip("As_ppm:Q", title="As (ppm)", format=".2f"),
                    ],
                )
                .interactive()
            )
            st.altair_chart(scatter, use_container_width=True)
            st.caption(
                "Cada punto representa una muestra. S sulfuro se expresa en porcentaje "
                "en peso y As en partes por millón (ppm)."
            )
        else:
            st.info(
                "No hay datos numéricos válidos para graficar S sulfuro y As de las muestras."
            )

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
                recomendacion = resp.json().get("recommendation", recomendacion)
        except Exception:
            pass

    st.success(f"Recomendación para el lote {selected_lote}: {recomendacion}")


if __name__ == "__main__":  # pragma: no cover
    st.set_page_config(
        page_title="Eco-Pilot · Caracterización y Laboratorio", layout="wide"
    )
    run_characterization()

