"""DataLoader — carga y valida datos YAML por sección/idioma.

Portado del legacy (`docs/AutoCV-legacy/src/modules/data_loader.py`) — feature 001, Tarea 2.
Sin cambios de lógica (estaba bien hecho); solo se ajusta el import de ejemplo a `src.autocv`.
La validación profunda de forma por sección llega en la feature 002.
"""

from typing import Any

import yaml


class DataLoaderError(Exception):
    """Error al cargar datos YAML de AutoCV."""


class DataLoader:
    """Carga datos YAML de una carpeta por idioma (usa Config como única fuente de rutas)."""

    def __init__(self, config):
        """Args: config — instancia de `src.autocv.config.Config`."""
        self.config = config

    def load_section(self, section: str, language: str) -> Any:
        """Carga una sección (`personales`, `experiencia`, …) de un idioma (`es`/`en`)."""
        data_dir = self.config.get_data_dir() / language
        file_path = data_dir / f"{section}.yaml"
        if not file_path.exists():
            raise DataLoaderError(f"Archivo no encontrado: {file_path}")
        try:
            with open(file_path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise DataLoaderError(f"Error al leer {file_path}: {e}")
        if data is None:
            raise DataLoaderError(f"El archivo {file_path} está vacío o mal formateado.")
        return data

    def load_all_data(self, language: str) -> dict[str, Any]:
        """Carga todas las secciones YAML de un idioma en un solo diccionario por sección."""
        data_dir = self.config.get_data_dir() / language
        if not data_dir.exists():
            raise DataLoaderError(f"La carpeta de datos no existe: {data_dir}")

        all_data: dict[str, Any] = {}
        for file in sorted(data_dir.glob("*.yaml")):
            try:
                with open(file, encoding="utf-8") as f:
                    data = yaml.safe_load(f)
            except yaml.YAMLError as e:
                raise DataLoaderError(f"Error al leer {file}: {e}")
            if data is None:
                raise DataLoaderError(f"El archivo {file} está vacío o mal formateado.")
            all_data[file.stem] = data
        return all_data


if __name__ == "__main__":
    from src.autocv.config import load_config

    try:
        loader = DataLoader(load_config())
        data_es = loader.load_all_data("es")
        print("✅ Datos en español cargados correctamente.")
        for section, content in data_es.items():
            print(f"Sección: {section} - {type(content).__name__}")
    except Exception as e:
        print(f"❌ Error: {e}")
