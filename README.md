# Eco-Pilot · Plataforma de Biohidrometalurgia

MVP modular para caracterizar relaves, predecir rendimiento y recomendar recetas de
bio-lixiviación con control de gobernanza. Incluye API en FastAPI, pipelines de ML,
registro en MLflow y paneles Streamlit.

---

## Arquitectura y capas de IA (MVP → robusto)

0. **Capa de datos**
   - *Feature Store* (tabular + señales temporales): validación de unidades, outliers,
     imputación con reglas físico-químicas, balance de masa/átomo S–Fe–As.
   - *Timeseries Store*: curvas pH/Eh/DO/Fe(II)/Fe(III)/T por corrida.
   - *Vectorización metagenómica*: abundancias 16S/shotgun + genes (fer/fox/ars/sulf)
     → embeddings (p. ej., hashing + PCA/UMAP).

1. **Clasificador de ruta de proceso**
   - Entrada: ICP + mineralogía (QEMSCAN/XRD) + S_sulf/ANC/NPR + atributos físicos.
   - Modelo: árbol de decisión + reglas duras (explainable) → BIOX / Biolix Cu /
     Co-Ni / REE / Au post-BIOX.
   - Métrica: accuracy + matriz de confusión; penaliza errores de seguridad
     (ej. ignorar enargita).

2. **Predictores de rendimiento** (por ruta)
   - Boosted trees (CatBoost/LightGBM) para: % oxidación, extracción metal,
     ácido L/t, tiempo a Eh objetivo, PLS g/L.
   - Modelos híbridos físico-informados: ajustar parámetros cinéticos (k, n) de un
     modelo simple (pseudo-1er orden / shrinking-core); el ML aprende
     `k=f(mineralogía, pH, T, DO, Fe(III), D80, %sólidos, consorcio)`.
   - Secuencias (curvas densas): regressor de series (XGBoost con lags) o GRU
     ligera para perfilar evolución Eh/pH/Fe(III).
   - Incertidumbre: ensembles + MC-dropout o quantile loss para dar IC 90–95%.

3. **Recomendador de receta** (setpoints + consorcio)
   - Optimización Bayesiana multi-objetivo (TPE o Gaussian Process) con
     restricciones duras.
   - Objetivos: maximizar extracción (metal), minimizar ácido, maximizar
     estabilidad As; restricciones: pH 1.4–2.0, T 40–45 °C, Eh ≥ 400 mV,
     DO ≥ 6 mg/L, Fe(III) 10–20 g/L, %sólidos 15–20, D80 75–150 µm.
   - Selector de consorcio: clasificador/Ranker que mapea fingerprint
     mineralógico-microbiano → {A. ferrooxidans, Leptospirillum, A. caldus,
     Sulfobacillus, …}.
   - Explicabilidad: SHAP por receta + reglas visibles.

4. **Diseñador de experimentos (Active Learning)**
   - Expected Improvement / Upper Confidence Bound condicionado a seguridad
     → propone las 5–8 corridas que más reducen incertidumbre y maximizan
     ganancia esperada.
   - Balancea exploración (zonas inciertas) vs. explotación (recetas ya buenas).

5. **Monitoreo y gobernanza**
   - Data & concept drift (KS test, PSI) para detectar cambios de mineralogía.
   - Model cards: dominio válido, límites, métricas y riesgos.
   - Controles de seguridad: bloqueo de recomendaciones fuera de ventana
     operativa o que violen balances.

---

## Inputs y targets

**Inputs (ejemplos):**
- Químicos: Au_gpt, Ag_gpt, Cu_pct, Co_ppm, Ni_ppm, ΣREE_ppm, As_ppm, Sb_ppm,
  Fe_pct, S_total, S_sulf_pct, ANC_kgCaCO3t, NPR.
- Mineralogía %: pirita, arsenopirita, calcopirita, enargita, bornita,
  covelina, pentlandita/cobaltita, monacita/apatita, arcillas, carbonatos.
- Físico: D80, %arcillas, densidad pulpa, humedad.
- Operacionales: pH_set, T_set, Eh_obj, DO_set, FeIII_set, %sólidos, aireación,
  agitación, nutrientes, inoculo (vector).
- Metagenómica: embeddings de 16S/shotgun + genes (ars, fox, fer, sox).

**Targets:**
- % oxidación de sulfuro (t y final), extracción Cu/Co/Ni/Au/Ag/REE (%),
  PLS g/L, consumo ácido (L/t), tiempo a Eh objetivo, `escorodita_ok` (bool/score).

---

## Métricas por módulo

- **Regresión:** RMSE/MAE + P50/P90 error; pinball loss (cuantiles).
- **Clasificación:** F1/Recall (pondera seguridad) para `escorodita_ok` y ruta.
- **Optimización:** uplift vs baseline (receta humana), % recetas nuevas que superan
  baseline, costo/ensayo exitoso.

---

## Arquitectura de software

- **Ingesta:** FastAPI (Python) + validadores Pydantic; cargas CSV/Sheets.
- **Feature Store:** DuckDB/Parquet (MVP) → luego BigQuery/Feast.
- **Entrenamiento:** scikit-learn, LightGBM/CatBoost, optuna/hyperopt; gpytorch/bohb
  para BO.
- **Pipelines:** Prefect/Temporal o Airflow ligero.
- **Model Registry:** MLflow (artefactos + métricas + versiones).
- **Servicio de inferencia:** FastAPI + onnxruntime/lightgbm nativo; requiere un
  archivo JSON con la lista ordenada de *features* y valida su presencia.
- **Panel:** Streamlit → más tarde React + backend.
- **Observabilidad:** Evidently AI (drift) + Prometheus/Grafana para KPIs.

---

## API (contratos mínimos)

| Endpoint                | Método | Descripción                                                         |
|------------------------|--------|---------------------------------------------------------------------|
| `POST /lots`           | POST   | Crea lote con ICP/mineralogía/físico.                              |
| `GET /route`           | GET    | Predice ruta de proceso.                                           |
| `GET /recommendations` | GET    | Devuelve top‑k recetas (setpoints + consorcio + SHAP).             |
| `POST /runs`           | POST   | Registra corridas (diseñador de experimentos).                     |
| `POST /timeseries`     | POST   | Sube curvas Eh/pH/Fe(III)/PLS.                                     |
| `POST /outcomes`       | POST   | Sube resultados de corridas.                                       |
| `GET /forecast`        | GET    | Pronostica evolución de variables operativas.                      |
| `GET /modelcard`       | GET    | Obtiene model card y límites de uso.                               |

---

## Reglas físico-químicas integradas

- **BIOX:** pH 1.6–1.9; 40–45 °C; Eh 430–480 mV; Fe(III) 10–20 g/L;
  DO ≥6 mg/L; %sólidos 15–20; D80 75–150 µm.
- **Biolix Cu mesófila:** pH 1.6–1.8; 35–40 °C; Eh 420–460 mV;
  Fe(III) 8–15 g/L; %sólidos 10–15.
- **Co/Ni sulfuros:** pH 1.6–1.8; 40–45 °C; Eh 450–500 mV.
- **As alto (enargita/arsenopirita):** escorodita (Fe:As≈1.8–2.0; pH 1.5–2.0;
  90–95 °C) en etapa separada.
- **REE en fosfatos:** desviar a bio-weathering heterotrófico (pH 2–4; C orgánico).

---

## Pseudocódigo del optimizador

```python
# Dado un lote, buscar la mejor receta bajo restricciones
space = {
  "pH": (1.6, 1.9),
  "T": (40, 45),
  "Eh": (430, 480),
  "DO": (6, 9),
  "FeIII": (10, 20),
  "%sol": (15, 20),
  "D80": (75, 150),
  "aireacion": ("low", "high"),
  "consorcio": ["AF+L", "AF+L+AC", "L+SB", "mix"]
}
# Objetivo compuesto (Eco-Score local):
# 0.6*extraccion_norm - 0.25*acido_norm + 0.15*estabilidad_As
def objective(x):
    y = predictor(x)            # model ensemble + physics
    if violates_constraints(x): return -1e9
    return 0.6*y["extr_norm"] - 0.25*y["acid_norm"] + 0.15*y["as_stab"]

best = bayes_optimize(objective, space, n_init=12, n_iter=40,
                      constraints=hard_rules)
return top_k(best, k=5)  # 5 recetas
```

---

## Estructura del repositorio

```text
EcoPilot/
├── active_learning/    # Programación de experimentos y registro de resultados
├── api/                # Endpoints FastAPI (lots, route, recommendations, forecast…)
├── dashboard/          # Panel Streamlit
├── ensemble/           # Predictores de desempeño
├── explainability/     # Recetas SHAP y reglas
├── features/           # Ingeniería de atributos
├── frontend/           # Apps Streamlit
├── governance/         # Model cards y controles
├── ingestion/          # Ingesta/validación de datos
├── monitoring/         # Drift y métricas
├── optimization/       # Búsqueda bayesiana
├── storage/            # Feature & TimeSeries Store (DuckDB/Parquet)
├── validation/         # Balance de masa/átomo y reglas físico-químicas
├── mlflow_logging.py   # Registro en MLflow
└── requirements.txt    # Dependencias
```

---

## Ejecución local

```bash
pip install -r requirements.txt

# API principal
uvicorn app.main:app --reload

# Microservicios (correr en terminales separadas)
uvicorn api.lots:app --reload
uvicorn api.route:app --reload
uvicorn api.recommendations:app --reload
uvicorn api.forecast:app --reload
uvicorn api.modelcard:app --reload
uvicorn api.runs:app --reload

# Paneles
streamlit run frontend/app.py
streamlit run dashboard/app.py
```

### Frontend

#### Demo Catálogo Bio-Mineral (Vite + React)

```bash
cd frontend/catalogo-bio-mineral-demo

# instalar dependencias
npm install        # o pnpm install

# ambiente de desarrollo
npm run dev        # o pnpm dev
```

### MLflow Tracking Server (opcional)

```bash
export MLFLOW_TRACKING_URI=http://localhost:5000
export MLFLOW_TRACKING_USERNAME=admin
export MLFLOW_TRACKING_PASSWORD=mlflow
```

---

## Licencia

MIT. Ver `LICENSE`.

