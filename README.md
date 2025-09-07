# Eco-Pilot · Caracterización (Módulo de Relaves)

Este repositorio proporciona una estructura inicial sólida para el módulo de **caracterización de relaves** de Eco‑Pilot.  La aplicación se divide en un **back‑end** basado en FastAPI y un **front‑end** en Streamlit, junto con utilidades y un motor de reglas sencillo.  El objetivo es que sirva como punto de partida que puedas ampliar con más modelos, reglas o servicios.

## Estructura del proyecto

```text
EcoPilot-Caracterizacion/
├── app/                  # Backend FastAPI (modelos, rutas y configuración de la BD)
│   ├── __init__.py
│   ├── db.py            # Configuración de SQLAlchemy y sesión
│   ├── models.py        # Modelos de SQLAlchemy (Lote, Muestra, Geoquimica)
│   ├── schemas.py       # Esquemas de Pydantic para validación y serialización
│   ├── main.py          # Punto de entrada para la app FastAPI
│   └── routes/          # Rutas de la API (controladores)
│       ├── __init__.py
│       ├── lotes.py     # Endpoints CRUD para lotes
│       └── muestras.py  # Endpoints CRUD para muestras (y geoquímica asociada)
├── frontend/
│   └── app.py           # Aplicación Streamlit para cargar/consultar datos
├── utils/
│   ├── __init__.py
│   └── rules.py         # Motor de reglas simple
├── .github/workflows/ci.yml  # GitHub Actions para CI (lint y tests)
├── .gitignore
├── Dockerfile           # Construcción de contenedor
├── LICENSE              # Licencia MIT
├── README.md            # Este archivo
├── requirements.txt     # Dependencias de Python
└── tests/               # Directorio para pruebas (opcional)
```

## Cómo correr localmente

1. Crea y activa un entorno virtual (opcional pero recomendado) y luego instala las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

2. Inicializa la base de datos y levanta la API:

   ```bash
   uvicorn app.main:app --reload
   ```

3. En otra terminal, corre la aplicación Streamlit:

   ```bash
   streamlit run frontend/app.py
   ```

4. Accede a la API en `http://localhost:8000` y a la interfaz de Streamlit en `http://localhost:8501`.

## Base de datos

Por defecto el backend utiliza SQLite (`app.db`) para facilitar la puesta en marcha.  Los modelos de SQLAlchemy y los esquemas de Pydantic están definidos en `app/models.py` y `app/schemas.py`.  Para cambiar a otro motor (PostgreSQL, MySQL, etc.), ajusta la constante `DATABASE_URL` en `app/db.py`.

## Ejecutar pruebas

El repositorio incluye un ejemplo básico de pruebas en el directorio `tests/`.  Para ejecutarlas:

```bash
pytest
```

## Licencia

Publicado bajo la licencia MIT.  Consulta el archivo `LICENSE` para más detalles.