"""
Módulo para cargar y validar datos desde archivos YAML
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List


class DataLoaderError(Exception):
    """Excepción personalizada para errores de carga de datos"""

    pass


class DataLoader:
    """
    Clase para cargar datos YAML de una carpeta específica (por idioma)
    """

    def __init__(self, config):
        """
        Args:
            config: Instancia de la clase Config (del módulo config.py)
        """
        self.config = config

    def load_section(self, section: str, language: str) -> Any:
        """
        Carga un archivo YAML de una sección específica (por ejemplo, 'personales', 'experiencia', etc.)

        Args:
            section: Nombre del archivo (sin extensión .yaml)
            language: 'es' o 'en'

        Returns:
            Diccionario o lista con los datos de la sección
        """
        data_dir = self.config.get_data_dir() / language
        file_path = data_dir / f"{section}.yaml"
        if not file_path.exists():
            raise DataLoaderError(f"Archivo no encontrado: {file_path}")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                if data is None:
                    raise DataLoaderError(
                        f"El archivo {file_path} está vacío o mal formateado."
                    )
                return data
        except yaml.YAMLError as e:
            raise DataLoaderError(f"Error al leer {file_path}: {e}")

    def load_all_data(self, language: str) -> Dict[str, Any]:
        """
        Carga todos los archivos YAML de la carpeta de un idioma y los devuelve en un solo diccionario

        Args:
            language: 'es' o 'en'

        Returns:
            Diccionario con todas las secciones, por ejemplo:
            {
                'personales': {...},
                'experiencia': {...},
                ...
            }
        """
        data_dir = self.config.get_data_dir() / language
        if not data_dir.exists():
            raise DataLoaderError(f"La carpeta de datos no existe: {data_dir}")

        all_data = {}
        for file in data_dir.glob("*.yaml"):
            section = file.stem
            try:
                with open(file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    if data is None:
                        raise DataLoaderError(
                            f"El archivo {file} está vacío o mal formateado."
                        )
                    all_data[section] = data
            except yaml.YAMLError as e:
                raise DataLoaderError(f"Error al leer {file}: {e}")
        return all_data

    # (Opcional) Puedes agregar validaciones de estructura aquí si lo deseas


# === EJEMPLO DE USO ===

if __name__ == "__main__":
    from src.modules.config import load_config

    try:
        config = load_config()
        loader = DataLoader(config)
        data_es = loader.load_all_data("es")
        print("✅ Datos en español cargados correctamente.")
        for section, content in data_es.items():
            print(f"Sección: {section} - {type(content)}")
    except Exception as e:
        print(f"❌ Error: {e}")
