# --- make repo root importable ---

import os, sys

import altair as alt
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

            muestras_sel = df_muestras[
                df_muestras["lote_id"].astype(str) == selected_lote
            ]

            geo_sel = df_geo[
                df_geo["muestra_id"].astype(str).isin(
                    muestras_sel["muestra_id"].astype(str)
                )
            ].copy()

            if "muestra_id" in geo_sel.columns and "muestra_id" in df_muestras.columns:
                geo_sel = geo_sel.merge(
                    muestras_sel[["muestra_id", "lote_id"]],
                    on="muestra_id",
                    how="left",
                )

            global_s_mean = None
            global_as_mean = None
            if not df_geo.empty:
                if "S_sulfuro_%" in df_geo.columns:
                    global_s_mean = pd.to_numeric(
                        df_geo["S_sulfuro_%"], errors="coerce"
                    ).mean()
                if "As_ppm" in df_geo.columns:
                    global_as_mean = pd.to_numeric(
                        df_geo["As_ppm"], errors="coerce"
                    ).mean()

            numeric_geo_sel = geo_sel.copy()
            for col in ["S_sulfuro_%", "As_ppm"]:
                if col in numeric_geo_sel.columns:
                    numeric_geo_sel[col] = pd.to_numeric(
                        numeric_geo_sel[col], errors="coerce"
                    )

            # --- filtros conectados a session_state ---
            s_range = None
            as_range = None
            if "S_sulfuro_%" in numeric_geo_sel.columns:
                serie_s = numeric_geo_sel["S_sulfuro_%"].dropna()
                if not serie_s.empty:
                    s_min = float(serie_s.min())
                    s_max = float(serie_s.max())
                    if s_min == s_max:
                        st.session_state["s_sulfuro_range"] = (s_min, s_max)
                        s_range = (s_min, s_max)
                        st.sidebar.caption(
                            f"Todas las mediciones de S sulfuro coinciden en {s_min:.2f}%"
                        )
                    else:
                        default_range = st.session_state.get(
                            "s_sulfuro_range", (s_min, s_max)
                        )
                        default_min = (
                            float(default_range[0])
                            if default_range and default_range[0] is not None
                            else s_min
                        )
                        default_max = (
                            float(default_range[1])
                            if default_range and default_range[1] is not None
                            else s_max
                        )
                        default_min = max(s_min, min(default_min, s_max))
                        default_max = max(default_min, min(default_max, s_max))
                        s_range = st.sidebar.slider(
                            "Rango S sulfuro (%)",
                            min_value=float(s_min),
                            max_value=float(s_max),
                            value=(float(default_min), float(default_max)),
                            key="s_sulfuro_range",
                        )
                else:
                    st.session_state["s_sulfuro_range"] = None

            if "As_ppm" in numeric_geo_sel.columns:
                serie_as = numeric_geo_sel["As_ppm"].dropna()
                if not serie_as.empty:
                    as_min = float(serie_as.min())
                    as_max = float(serie_as.max())
                    if as_min == as_max:
                        st.session_state["as_ppm_range"] = (as_min, as_max)
                        as_range = (as_min, as_max)
                        st.sidebar.caption(
                            f"Todas las mediciones de As coinciden en {as_min:.2f} ppm"
                        )
                    else:
                        default_range = st.session_state.get(
                            "as_ppm_range", (as_min, as_max)
                        )
                        default_min = (
                            float(default_range[0])
                            if default_range and default_range[0] is not None
                            else as_min
                        )
                        default_max = (
                            float(default_range[1])
                            if default_range and default_range[1] is not None
                            else as_max
                        )
                        default_min = max(as_min, min(default_min, as_max))
                        default_max = max(default_min, min(default_max, as_max))
                        as_range = st.sidebar.slider(
                            "Rango As (ppm)",
                            min_value=float(as_min),
                            max_value=float(as_max),
                            value=(float(default_min), float(default_max)),
                            key="as_ppm_range",
                        )
                else:
                    st.session_state["as_ppm_range"] = None

            filtered_geo = numeric_geo_sel.copy()
            if s_range is not None and "S_sulfuro_%" in filtered_geo.columns:
                filtered_geo = filtered_geo[
                    filtered_geo["S_sulfuro_%"].between(
                        s_range[0], s_range[1], inclusive="both"
                    )
                ]
            if as_range is not None and "As_ppm" in filtered_geo.columns:
                filtered_geo = filtered_geo[
                    filtered_geo["As_ppm"].between(
                        as_range[0], as_range[1], inclusive="both"
                    )
                ]

            muestras_sel_ids = muestras_sel["muestra_id"].astype(str).unique()
            filtered_samples = (
                filtered_geo["muestra_id"].astype(str).nunique()
                if not filtered_geo.empty and "muestra_id" in filtered_geo.columns
                else 0
            )

            s_sulfuro_mean = (
                filtered_geo["S_sulfuro_%"].mean()
                if "S_sulfuro_%" in filtered_geo.columns
                and not filtered_geo["S_sulfuro_%"].dropna().empty
                else None
            )
            as_mean = (
                filtered_geo["As_ppm"].mean()
                if "As_ppm" in filtered_geo.columns
                and not filtered_geo["As_ppm"].dropna().empty
                else None
            )

            tabs = st.tabs(["Resumen", "Geoquímica", "Calidad de datos"])

            with tabs[0]:
                st.subheader("Resumen ejecutivo")

                lote_info = df_lotes[
                    df_lotes["lote_id"].astype(str) == selected_lote
                ].copy()
                lote_column_config = {}
                if "tonelaje_t" in lote_info.columns:
                    lote_column_config["tonelaje_t"] = st.column_config.NumberColumn(
                        "Tonelaje (t)", format="%d", help="Tonelaje reportado para el lote"
                    )
                if "ley_sulfuro" in lote_info.columns:
                    lote_column_config["ley_sulfuro"] = st.column_config.NumberColumn(
                        "Ley de sulfuro (%)", format="%.2f"
                    )
                st.dataframe(
                    lote_info,
                    hide_index=True,
                    column_config=lote_column_config or None,
                    use_container_width=True,
                )

                total_muestras = len(muestras_sel)
                base_samples = len(muestras_sel_ids)
                col1, col2, col3 = st.columns(3)
                col1.metric(
                    "Muestras registradas",
                    total_muestras,
                    delta=f"{base_samples} únicas",
                )

                if s_sulfuro_mean is not None:
                    delta_s = (
                        s_sulfuro_mean - global_s_mean
                        if global_s_mean is not None
                        else 0
                    )
                    col2.metric(
                        "Promedio S sulfuro (%)",
                        f"{s_sulfuro_mean:.2f}",
                        delta=(
                            f"{delta_s:+.2f} vs global"
                            if global_s_mean is not None
                            else ""
                        ),
                    )
                else:
                    col2.metric("Promedio S sulfuro (%)", "N/A", delta="Sin datos")

                if as_mean is not None:
                    delta_as = (
                        as_mean - global_as_mean
                        if global_as_mean is not None
                        else 0
                    )
                    col3.metric(
                        "Promedio As (ppm)",
                        f"{as_mean:.2f}",
                        delta=(
                            f"{delta_as:+.2f} vs global"
                            if global_as_mean is not None
                            else ""
                        ),
                    )
                else:
                    col3.metric("Promedio As (ppm)", "N/A", delta="Sin datos")

                cobertura_claves = 0.0
                claves = [c for c in ["S_sulfuro_%", "As_ppm"] if c in filtered_geo.columns]
                if claves and not filtered_geo.empty:
                    cobertura_claves = (
                        filtered_geo[claves].notna().all(axis=1).mean()
                    )
                st.progress(cobertura_claves if pd.notna(cobertura_claves) else 0.0)
                st.caption(
                    "Cobertura de datos clave: porcentaje de muestras filtradas con S sulfuro "
                    "y As disponibles."
                )

                muestras_completas = int(filtered_geo.dropna(subset=claves).shape[0]) if claves else 0
                delta_pct = (
                    (filtered_samples / base_samples - 1) * 100 if base_samples else 0
                )
                st.metric(
                    "Muestras con datos completos",
                    muestras_completas,
                    delta=f"{delta_pct:+.1f}% vs total lote",
                )

            with tabs[1]:
                st.subheader("Detalle geoquímico filtrado")

                geo_column_config = {}
                if "S_sulfuro_%" in filtered_geo.columns:
                    geo_column_config["S_sulfuro_%"] = st.column_config.NumberColumn(
                        "S sulfuro (%)", format="%.2f", help="Resultados de laboratorio"
                    )
                if "As_ppm" in filtered_geo.columns:
                    geo_column_config["As_ppm"] = st.column_config.NumberColumn(
                        "As (ppm)", format="%.2f"
                    )
                st.dataframe(
                    filtered_geo,
                    hide_index=True,
                    column_config=geo_column_config or None,
                    use_container_width=True,
                )

                if "S_sulfuro_%" in filtered_geo.columns and not filtered_geo.empty:
                    hist_s = (
                        alt.Chart(filtered_geo)
                        .mark_bar(opacity=0.75)
                        .encode(
                            x=alt.X(
                                "S_sulfuro_%:Q",
                                bin=alt.Bin(maxbins=30),
                                title="Distribución S sulfuro (%)",
                            ),
                            y=alt.Y("count()", title="Número de muestras"),
                        )
                    )
                    st.altair_chart(hist_s, use_container_width=True)

                if "As_ppm" in filtered_geo.columns and not filtered_geo.empty:
                    hist_as = (
                        alt.Chart(filtered_geo)
                        .mark_bar(opacity=0.75, color="#ff7f0e")
                        .encode(
                            x=alt.X(
                                "As_ppm:Q",
                                bin=alt.Bin(maxbins=30),
                                title="Distribución As (ppm)",
                            ),
                            y=alt.Y("count()", title="Número de muestras"),
                        )
                    )
                    st.altair_chart(hist_as, use_container_width=True)

                if "lote_id" in df_muestras.columns and "muestra_id" in df_geo.columns:
                    geo_all = df_geo.merge(
                        df_muestras[["muestra_id", "lote_id"]],
                        on="muestra_id",
                        how="left",
                    )
                    for col in ["S_sulfuro_%", "As_ppm"]:
                        if col in geo_all.columns:
                            geo_all[col] = pd.to_numeric(geo_all[col], errors="coerce")

                    if "S_sulfuro_%" in geo_all.columns:
                        bar_s = (
                            alt.Chart(
                                geo_all.dropna(subset=["S_sulfuro_%", "lote_id"])
                            )
                            .mark_bar()
                            .encode(
                                x=alt.X("lote_id:N", title="Lote"),
                                y=alt.Y(
                                    "mean(S_sulfuro_%):Q",
                                    title="S sulfuro promedio (%)",
                                ),
                                color=alt.condition(
                                    alt.datum.lote_id == selected_lote,
                                    alt.value("#1f77b4"),
                                    alt.value("#d3d3d3"),
                                ),
                            )
                        )
                        st.altair_chart(bar_s, use_container_width=True)

                    if "As_ppm" in geo_all.columns:
                        bar_as = (
                            alt.Chart(geo_all.dropna(subset=["As_ppm", "lote_id"]))
                            .mark_bar(color="#ff7f0e")
                            .encode(
                                x=alt.X("lote_id:N", title="Lote"),
                                y=alt.Y(
                                    "mean(As_ppm):Q", title="As promedio (ppm)"
                                ),
                                color=alt.condition(
                                    alt.datum.lote_id == selected_lote,
                                    alt.value("#ff7f0e"),
                                    alt.value("#fdd9b5"),
                                ),
                            )
                        )
                        st.altair_chart(bar_as, use_container_width=True)

                if (
                    "S_sulfuro_%" in filtered_geo.columns
                    and "As_ppm" in filtered_geo.columns
                    and "muestra_id" in filtered_geo.columns
                    and not filtered_geo.dropna(subset=["S_sulfuro_%", "As_ppm"]).empty
                ):
                    brush = alt.selection_interval(encodings=["x", "y"], name="seleccion")
                    scatter = (
                        alt.Chart(filtered_geo)
                        .mark_circle(size=90, opacity=0.85)
                        .encode(
                            x=alt.X("S_sulfuro_%:Q", title="S sulfuro (%)"),
                            y=alt.Y("As_ppm:Q", title="Arsénico (ppm)"),
                            tooltip=[
                                alt.Tooltip("muestra_id:N", title="Muestra"),
                                alt.Tooltip(
                                    "S_sulfuro_%:Q", title="S sulfuro (%)", format=".2f"
                                ),
                                alt.Tooltip("As_ppm:Q", title="As (ppm)", format=".2f"),
                            ],
                            color=alt.condition(
                                brush,
                                alt.value("#1f77b4"),
                                alt.value("#d3d3d3"),
                            ),
                        )
                        .add_selection(brush)
                    )

                    barras_filtradas = (
                        alt.Chart(filtered_geo)
                        .mark_bar()
                        .encode(
                            x=alt.X("muestra_id:N", title="Muestra"),
                            y=alt.Y("S_sulfuro_%:Q", title="S sulfuro (%)"),
                        )
                        .transform_filter(brush)
                    )

                    st.altair_chart(
                        (scatter & barras_filtradas).resolve_scale(y="independent"),
                        use_container_width=True,
                    )
                    st.caption(
                        "Selecciona un área en el scatter para analizar los valores de S sulfuro "
                        "de las muestras destacadas."
                    )
                else:
                    st.info(
                        "No hay datos numéricos válidos para graficar S sulfuro y As de las muestras."
                    )

            with tabs[2]:
                st.subheader("Indicadores de calidad de datos")

                total_unicos = base_samples
                datos_geo = filtered_samples
                pct_sin_geo = (
                    100 - (datos_geo / total_unicos * 100) if total_unicos else 0
                )

                col1, col2, col3 = st.columns(3)
                col1.metric(
                    "% muestras sin datos geoquímicos",
                    f"{pct_sin_geo:.1f}%",
                    delta=f"-{100 - pct_sin_geo:.1f}% con datos",
                )
                col2.metric(
                    "Muestras dentro del filtro",
                    datos_geo,
                    delta=(
                        f"{(datos_geo / total_unicos * 100):.1f}% del total"
                        if total_unicos
                        else "0%"
                    ),
                )
                col3.metric(
                    "Muestras fuera de rango",
                    max(total_unicos - datos_geo, 0),
                    delta="Revisión sugerida",
                )

                missing_metrics = []
                for col, label in [("S_sulfuro_%", "S sulfuro"), ("As_ppm", "As")]:
                    if col in numeric_geo_sel.columns:
                        missing_pct = (
                            numeric_geo_sel[col].isna().mean() * 100
                            if not numeric_geo_sel[col].empty
                            else 0
                        )
                        missing_metrics.append((label, missing_pct))

                if missing_metrics:
                    metric_cols = st.columns(len(missing_metrics))
                    for metric_col, (label, missing_pct) in zip(metric_cols, missing_metrics):
                        metric_col.metric(
                            f"% faltantes {label}", f"{missing_pct:.1f}%"
                        )

                calidad_df = []
                if claves:
                    for col in claves:
                        calidad_df.append(
                            {
                                "Variable": col,
                                "Completitud filtrada (%)": round(
                                    (1 - filtered_geo[col].isna().mean()) * 100, 1
                                ),
                            }
                        )
                if calidad_df:
                    st.dataframe(
                        pd.DataFrame(calidad_df),
                        hide_index=True,
                        use_container_width=True,
                    )
                st.caption(
                    "Estos indicadores se actualizan según los filtros activos, facilitando "
                    "el seguimiento de la calidad de los datos en tiempo real."
                )

            recomendacion = recommend_process(s_sulfuro_mean, as_mean)

            api_error = None
            if api_url and s_sulfuro_mean is not None and as_mean is not None:
                url = api_url.rstrip("/") + "/ml/predict"
                payload = {
                    "s_sulfuro_pct": s_sulfuro_mean,
                    "as_ppm": as_mean,
                }
                try:
                    resp = requests.post(url, json=payload, timeout=10)
                    resp.raise_for_status()
                except requests.exceptions.HTTPError as exc:
                    response = exc.response
                    if response is not None:
                        detail = response.text or response.reason
                        api_error = (
                            f"La API respondió con un error {response.status_code}: {detail}"
                        )
                    else:
                        api_error = f"La API respondió con un error: {exc}"
                except requests.exceptions.RequestException as exc:
                    api_error = f"No se pudo contactar con la API: {exc}"
                else:
                    try:
                        body = resp.json()
                    except ValueError:
                        api_error = "La API devolvió una respuesta inválida."
                    else:
                        recomendacion = body.get("recommendation", recomendacion)
            elif api_url:
                api_error = (
                    "La recomendación automática requiere promedios numéricos de "
                    "S sulfuro y As."
                )

            if api_error:
                st.warning(api_error)

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

