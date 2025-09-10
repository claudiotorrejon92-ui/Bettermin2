# Eco-Pilot · Caracterización (Módulo de Relaves)

Repositorio experimental que agrupa servicios y utilidades para la
caracterización de relaves dentro de **Eco‑Pilot**. Incluye un
back‑end basado en FastAPI, diversas herramientas de análisis y un
front‑end en Streamlit.

## Estructura del proyecto

```text
EcoPilot-Caracterizacion/
├── active_learning/    # Programación de experimentos y registro de resultados
├── api/                # Microservicios FastAPI (lotes, rutas, recomendaciones, etc.)
├── app/                # API monolítica original para CRUD y predicciones básicas
├── dashboard/          # Dashboard de ejemplo en Streamlit
├── ensemble/           # Predictores de desempeño basados en ensambles
├── explainability/     # Recetas de interpretabilidad (p.ej. SHAP)
├── features/           # Utilidades para ingeniería de atributos
├── frontend/           # Aplicaciones Streamlit
├── governance/         # Utilidades de gobernanza (p.ej. model cards)
├── ingestion/          # Scripts simples de ingestión de datos
├── inference/          # Scripts de despliegue/serving
├── monitoring/         # Detección de deriva y monitoreo
├── optimization/       # Optimización Bayesiana y espacio de búsqueda
├── storage/            # Feature store local con DuckDB/Parquet
├── validation/         # Chequeos y validaciones de datos
├── mlflow_logging.py   # Utilidades para registrar experimentos en MLflow
└── requirements.txt    # Dependencias de Python
```

## Endpoints disponibles en `api/`

| Archivo            | Endpoint(s)            | Método | Propósito |
|--------------------|-----------------------|--------|-----------|
| `lots.py`          | `/lots`, `/lots/{id}` | GET    | Listado de lotes y consulta individual |
| `route.py`         | `/route`              | GET    | Predice la ruta de procesamiento a partir de métricas geoquímicas |
| `recommendations.py` | `/recommendations` | GET    | Devuelve parámetros recomendados mediante optimización Bayesiana y explica con SHAP |
| `forecast.py`      | `/forecast`           | GET    | Pronostica el desempeño de una ruta en el tiempo |
| `modelcard.py`     | `/modelcard`          | GET    | Recupera la última model card generada |
| `runs.py`          | `/runs`, `/outcomes`  | POST   | Registra ejecuciones y resultados para aprendizaje activo |

## Cómo correr localmente

1. Crea y activa un entorno virtual (opcional) e instala las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

2. Levanta el back‑end principal:

   ```bash
   uvicorn app.main:app --reload
   ```

3. Microservicios adicionales (optimización, monitoreo y gobernanza) pueden
   ejecutarse en procesos separados:

   ```bash
   # Gestión de lotes
   uvicorn api.lots:app --reload

   # Predicción de ruta de procesamiento
   uvicorn api.route:app --reload

   # Recomendaciones vía optimización Bayesiana
   uvicorn api.recommendations:app --reload

   # Pronósticos de desempeño y monitoreo
   uvicorn api.forecast:app --reload

   # Exposición de model cards para gobernanza
   uvicorn api.modelcard:app --reload

   # Registro de corridas y resultados (aprendizaje activo)
   uvicorn api.runs:app --reload
   ```

4. En otra terminal levanta las interfaces Streamlit:

   ```bash
   streamlit run frontend/app.py
   streamlit run frontend/lab_ml_app.py  # Opcional: demo de laboratorio/ML
   streamlit run dashboard/app.py        # Opcional: dashboard adicional
   ```

5. Accede al back‑end en `http://localhost:8000` (o el puerto asignado por cada
   microservicio) y a las interfaces de Streamlit en `http://localhost:8501`.

## MLflow Tracking Server

El servidor de seguimiento de MLflow está disponible en `http://localhost:5000`.
Configura las credenciales mediante las variables de entorno:

```bash
export MLFLOW_TRACKING_URI=http://localhost:5000
export MLFLOW_TRACKING_USERNAME=admin
export MLFLOW_TRACKING_PASSWORD=mlflow
```

Estas variables permiten autenticar y registrar ejecuciones en el servidor.

## Archivos clave

- `mlflow_logging.py`: registro de métricas y artefactos en [MLflow](https://mlflow.org/).
- `storage/feature_store.py`: feature store local basado en
  [DuckDB](https://duckdb.org/) y archivos Parquet.
- `active_learning/scheduler.py`: programador de experimentos con estrategias EI/UCB.

## Licencia

Publicado bajo la licencia MIT. Consulta el archivo `LICENSE` para más detalles.
