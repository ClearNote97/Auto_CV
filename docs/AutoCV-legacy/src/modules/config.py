"""
Módulo para manejar configuración del proyecto
"""

# TODO: Implementar Config

"""
Módulo de configuración para AutoCV
Carga y valida la configuración desde archivos YAML y variables de entorno
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv


class ConfigError(Exception):
    """Excepción personalizada para errores de configuración"""

    pass


class Config:
    """
    Clase para manejar toda la configuración del proyecto AutoCV

    Carga configuración desde:
    - config/config.yaml (configuración general)
    - config/deepl_config.yaml (configuración de DeepL)
    - .env (variables de entorno sensibles)
    """

    def __init__(self, config_dir: str = "config"):
        """
        Inicializa la configuración

        Args:
            config_dir: Directorio donde están los archivos de configuración
        """
        self.config_dir = Path(config_dir)
        self._config = {}

        # Cargar variables de entorno desde .env
        load_dotenv()

        # Cargar configuraciones
        self._load_general_config()
        self._load_deepl_config()
        self._load_env_variables()
        self._validate_config()

    def _load_general_config(self):
        """Carga la configuración general desde config.yaml"""
        config_file = self.config_dir / "config.yaml"

        if not config_file.exists():
            raise ConfigError(f"Archivo de configuración no encontrado: {config_file}")

        try:
            with open(config_file, "r", encoding="utf-8") as f:
                general_config = yaml.safe_load(f)
                self._config.update(general_config)
        except yaml.YAMLError as e:
            raise ConfigError(f"Error al leer {config_file}: {e}")
        except Exception as e:
            raise ConfigError(f"Error inesperado al cargar {config_file}: {e}")

    def _load_deepl_config(self):
        """Carga la configuración de DeepL desde deepl_config.yaml"""
        deepl_config_file = self.config_dir / "deepl_config.yaml"

        if not deepl_config_file.exists():
            raise ConfigError(
                f"Archivo de configuración DeepL no encontrado: {deepl_config_file}"
            )

        try:
            with open(deepl_config_file, "r", encoding="utf-8") as f:
                deepl_config = yaml.safe_load(f)
                self._config.update(deepl_config)
        except yaml.YAMLError as e:
            raise ConfigError(f"Error al leer {deepl_config_file}: {e}")
        except Exception as e:
            raise ConfigError(f"Error inesperado al cargar {deepl_config_file}: {e}")

    def _load_env_variables(self):
        """Carga variables sensibles desde el entorno"""
        # API Key de DeepL (obligatoria)
        deepl_api_key = os.getenv("DEEPL_API_KEY")
        if not deepl_api_key:
            raise ConfigError(
                "DEEPL_API_KEY no encontrada en variables de entorno. "
                "Asegúrate de tener un archivo .env con tu clave de API."
            )

        # Agregar la API key a la configuración
        if "deepl" not in self._config:
            self._config["deepl"] = {}
        self._config["deepl"]["api_key"] = deepl_api_key

        # Permitir sobreescribir el nivel de log desde el entorno
        log_level = os.getenv("LOG_LEVEL")
        if log_level:
            if "logging" not in self._config:
                self._config["logging"] = {}
            self._config["logging"]["level"] = log_level.upper()

    def _validate_config(self):
        """Valida que la configuración tenga todos los parámetros esenciales"""
        required_sections = ["project", "languages", "paths", "latex", "output"]

        for section in required_sections:
            if section not in self._config:
                raise ConfigError(
                    f"Sección requerida '{section}' no encontrada en la configuración"
                )

        # Validar rutas críticas
        required_paths = ["data_dir", "templates_dir", "output_dir"]
        for path_key in required_paths:
            if path_key not in self._config["paths"]:
                raise ConfigError(f"Ruta requerida '{path_key}' no encontrada en paths")

        # Validar idiomas
        if (
            "source" not in self._config["languages"]
            or "target" not in self._config["languages"]
        ):
            raise ConfigError(
                "Idiomas 'source' y 'target' son requeridos en la configuración"
            )

        # Validar que las carpetas existan (crear si no existen)
        self._ensure_directories_exist()

    def _ensure_directories_exist(self):
        """Crea las carpetas necesarias si no existen"""
        paths_to_create = [
            self.get_data_dir(),
            self.get_templates_dir(),
            self.get_output_dir(),
            self.get_output_dir() / "pdf",
            self.get_output_dir() / "tex",
        ]

        for path in paths_to_create:
            path.mkdir(parents=True, exist_ok=True)

    # === MÉTODOS PÚBLICOS PARA ACCEDER A LA CONFIGURACIÓN ===

    def get(self, key: str, default: Any = None) -> Any:
        """
        Obtiene un valor de configuración usando notación de punto

        Args:
            key: Clave en formato 'seccion.subseccion.valor'
            default: Valor por defecto si no se encuentra la clave

        Returns:
            El valor de configuración o el valor por defecto

        Example:
            config.get('project.name')  # "AutoCV"
            config.get('latex.engine')  # "pdflatex"
        """
        keys = key.split(".")
        value = self._config

        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def get_project_info(self) -> Dict[str, str]:
        """Obtiene información del proyecto"""
        return self._config.get("project", {})

    def get_languages(self) -> Dict[str, str]:
        """Obtiene configuración de idiomas"""
        return self._config.get("languages", {})

    def get_source_language(self) -> str:
        """Obtiene el idioma fuente"""
        return self._config["languages"]["source"]

    def get_target_language(self) -> str:
        """Obtiene el idioma objetivo"""
        return self._config["languages"]["target"]

    def get_data_dir(self) -> Path:
        """Obtiene la ruta del directorio de datos"""
        return Path(self._config["paths"]["data_dir"])

    def get_templates_dir(self) -> Path:
        """Obtiene la ruta del directorio de plantillas"""
        return Path(self._config["paths"]["templates_dir"])

    def get_output_dir(self) -> Path:
        """Obtiene la ruta del directorio de salida"""
        return Path(self._config["paths"]["output_dir"])

    def get_latex_config(self) -> Dict[str, Any]:
        """Obtiene configuración de LaTeX"""
        return self._config.get("latex", {})

    def get_latex_engine(self) -> str:
        """Obtiene el motor de LaTeX"""
        return self._config["latex"]["engine"]

    def get_latex_options(self) -> list:
        """Obtiene las opciones de compilación de LaTeX"""
        return self._config["latex"].get("options", [])

    def get_deepl_config(self) -> Dict[str, Any]:
        """Obtiene configuración de DeepL"""
        return self._config.get("deepl", {})

    def get_deepl_api_key(self) -> str:
        """Obtiene la clave de API de DeepL"""
        return self._config["deepl"]["api_key"]

    def get_deepl_api_url(self) -> str:
        """Obtiene la URL de la API de DeepL"""
        return self._config["deepl"].get("api_url", "https://api-free.deepl.com")

    def get_translation_config(self) -> Dict[str, Any]:
        """Obtiene configuración de traducción"""
        return self._config.get("translation", {})

    def get_output_filename_format(self) -> str:
        """Obtiene el formato de nombre de archivo de salida"""
        return self._config["output"].get("filename_format", "CV_{nombre}_{idioma}.pdf")

    def get_log_level(self) -> str:
        """Obtiene el nivel de logging"""
        return self._config.get("logging", {}).get("level", "INFO")

    def __str__(self) -> str:
        """Representación en string de la configuración (sin datos sensibles)"""
        safe_config = self._config.copy()

        # Ocultar datos sensibles
        if "deepl" in safe_config and "api_key" in safe_config["deepl"]:
            safe_config["deepl"]["api_key"] = "***OCULTA***"

        return f"Config({safe_config})"

    def __repr__(self) -> str:
        return self.__str__()


# === FUNCIÓN DE CONVENIENCIA ===


def load_config(config_dir: str = "config") -> Config:
    """
    Función de conveniencia para cargar la configuración

    Args:
        config_dir: Directorio de configuración

    Returns:
        Instancia de Config cargada y validada
    """
    return Config(config_dir)


# === EJEMPLO DE USO ===

if __name__ == "__main__":
    # Ejemplo de cómo usar el módulo de configuración
    try:
        config = load_config()

        print("✅ Configuración cargada exitosamente")
        print(f"Proyecto: {config.get('project.name')}")
        print(f"Idioma fuente: {config.get_source_language()}")
        print(f"Idioma objetivo: {config.get_target_language()}")
        print(f"Directorio de datos: {config.get_data_dir()}")
        print(f"Motor LaTeX: {config.get_latex_engine()}")

    except ConfigError as e:
        print(f"❌ Error de configuración: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
