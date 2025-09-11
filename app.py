"""Dashboard principal para módulos de Streamlit."""

import streamlit as st

from frontend.app import run_characterization
from frontend.lab_ml_app import run_lab_ml


def main() -> None:
    st.set_page_config(page_title="Eco-Pilot Dashboard", layout="wide")

    module = st.sidebar.radio(
        "Selecciona un módulo", ["Caracterización", "ML laboratorio"]
    )

    if module == "Caracterización":
        run_characterization()
    else:
        run_lab_ml()


if __name__ == "__main__":  # pragma: no cover
    main()

