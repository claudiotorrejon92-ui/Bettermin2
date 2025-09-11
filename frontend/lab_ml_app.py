import io

import joblib
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


def run_lab_ml() -> None:
    """Interface for simple laboratory ML experiments."""

    st.title("Eco-Pilot • ML de laboratorio (MVP)")
    st.caption(
        "Carga tus ensayos (CSV), entrena Regresión y Random Forest, compara métricas y descarga modelos."
    )

    with st.expander("📄 Instrucciones rápidas", expanded=True):
        st.markdown(
            "- El CSV debe tener columnas numéricas (features) y **una columna objetivo** con la variable a predecir."
            "- Ejemplo objetivo: `Cu_recovery_pct`."
            "- El sistema dividirá automáticamente en train/test (75/25) y calculará R² y MAE."
            "- Puedes **elegir features** (por defecto toma todas las numéricas excepto el objetivo)."
        )

    uploaded = st.file_uploader("Sube tu CSV de ensayos de laboratorio", type=["csv"])

    if uploaded is not None:
        data = pd.read_csv(uploaded)
        st.subheader("Vista previa de datos")
        st.dataframe(data.head())

        numeric_cols = [c for c in data.columns if pd.api.types.is_numeric_dtype(data[c])]
        if not numeric_cols:
            st.error("El CSV no contiene columnas numéricas.")
            st.stop()
        target_col = st.selectbox(
            "🎯 Columna objetivo (target a predecir)",
            options=numeric_cols,
            index=len(numeric_cols) - 1 if numeric_cols else 0,
        )

        default_features = [c for c in numeric_cols if c != target_col]
        feats = st.multiselect(
            "🧪 Variables (features) para el modelo",
            options=numeric_cols,
            default=default_features,
        )

        if target_col in feats:
            st.error("La columna objetivo no puede estar entre las features. Quítala de la selección.")
        elif len(feats) == 0:
            st.warning("Selecciona al menos una feature para entrenar.")
        else:
            X = data[feats].to_numpy()
            y = data[target_col].to_numpy()

            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.25, random_state=42
            )

            scaler = StandardScaler()
            X_train_s = scaler.fit_transform(X_train)
            X_test_s = scaler.transform(X_test)

            lin = LinearRegression()
            lin.fit(X_train_s, y_train)
            y_pred_lin = lin.predict(X_test_s)

            r2_lin = r2_score(y_test, y_pred_lin)
            mae_lin = mean_absolute_error(y_test, y_pred_lin)

            rf = RandomForestRegressor(
                n_estimators=400,
                max_depth=None,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1,
            )
            rf.fit(X_train, y_train)
            y_pred_rf = rf.predict(X_test)

            r2_rf = r2_score(y_test, y_pred_rf)
            mae_rf = mean_absolute_error(y_test, y_pred_rf)

            st.subheader("📊 Métricas")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Regresión lineal • R²", f"{r2_lin:.3f}")
                st.metric("Regresión lineal • MAE (%)", f"{mae_lin:.3f}")
            with col2:
                st.metric("Random Forest • R²", f"{r2_rf:.3f}")
                st.metric("Random Forest • MAE (%)", f"{mae_rf:.3f}")

            def scatter_pred(y_true, y_pred, title):
                fig, ax = plt.subplots()
                ax.scatter(y_true, y_pred, alpha=0.6)
                ax.plot([min(y_true), max(y_true)], [min(y_true), max(y_true)])
                ax.set_xlabel("Real")
                ax.set_ylabel("Predicción")
                ax.set_title(title)
                st.pyplot(fig)

            st.subheader("📈 Ajuste de modelos (Predicción vs Real)")
            c1, c2 = st.columns(2)
            with c1:
                scatter_pred(y_test, y_pred_lin, "Regresión lineal")
            with c2:
                scatter_pred(y_test, y_pred_rf, "Random Forest")

            try:
                importances = rf.feature_importances_
                imp_df = pd.DataFrame(
                    {"feature": feats, "importance": importances}
                ).sort_values("importance", ascending=False)
                st.subheader("🌲 Importancia de variables (Random Forest)")
                st.dataframe(imp_df)

                fig, ax = plt.subplots()
                ax.bar(imp_df["feature"], imp_df["importance"])
                ax.set_xticklabels(imp_df["feature"], rotation=45, ha="right")
                ax.set_title("Importancia de variables")
                ax.set_xlabel("Variables")
                ax.set_ylabel("Importancia")
                st.pyplot(fig)
            except Exception as e:  # pragma: no cover - visual aid only
                st.info(f"No se pudieron calcular importancias: {e}")

            st.subheader("🧠 Recomendación del sistema")
            if r2_rf >= r2_lin and mae_rf <= mae_lin:
                st.success(
                    "Para estos datos, **Random Forest** rinde mejor. Úsalo como modelo base del MVP."
                )
            else:
                st.warning(
                    "Para estos datos, **Regresión lineal** es competitiva. Considera mejorar features o probar XGBoost."
                )

            st.subheader("💾 Descargar modelos entrenados")
            buf_lin = io.BytesIO()
            joblib.dump(
                {"scaler": scaler, "model": lin, "features": feats, "target": target_col},
                buf_lin,
            )
            st.download_button(
                "Descargar paquete Regresión (joblib)",
                data=buf_lin.getvalue(),
                file_name="linreg_joblib.pkl",
            )

            buf_rf = io.BytesIO()
            joblib.dump({"model": rf, "features": feats, "target": target_col}, buf_rf)
            st.download_button(
                "Descargar paquete Random Forest (joblib)",
                data=buf_rf.getvalue(),
                file_name="rf_joblib.pkl",
            )
    else:
        st.info(
            "Sube un CSV para comenzar. Puedes probar con la plantilla que te dejamos junto con esta app."
        )


if __name__ == "__main__":  # pragma: no cover
    st.set_page_config(page_title="Eco-Pilot | ML laboratorio", layout="wide")
    run_lab_ml()

