"""Config — única fuente de rutas/idiomas/engine para AutoCV.

Carga configuración desde:
- config/config.yaml       (general: project, languages, paths, latex, output)
- config/deepl_config.yaml (DeepL: api_url, timeout, retries, translation)
- .env                     (secretos: DEEPL_API_KEY)

Portado del legacy (`docs/AutoCV-legacy/src/modules/config.py`) — feature 001, Tarea 2.
Cambios respecto al legacy:
  1. Un solo docstring (el legacy tenía el header `# TODO` pegado sobre la implementación real).
  2. DEEPL_API_KEY es LAZY: no se exige al cargar la config; solo `get_deepl_api_key()` falla si
     falta. Así `render`/`compile` (que no traducen) no dependen de tener una key (principio 8).
  3. Nuevo `get_template_name()`: subcarpeta de la plantilla elegida (única realidad de config, CA5).
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv


class ConfigError(Exception):
    """Error de configuración de AutoCV."""


class Config:
    """Configuración del proyecto, con acceso por clave-punto (`config.get('latex.engine')`)."""

    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self._config: Dict[str, Any] = {}

        load_dotenv()

        self._load_general_config()
        self._load_deepl_config()
        self._load_env_variables()
        self._validate_config()

    def _load_general_config(self) -> None:
        config_file = self.config_dir / "config.yaml"
        if not config_file.exists():
            raise ConfigError(f"Archivo de configuración no encontrado: {config_file}")
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                self._config.update(yaml.safe_load(f) or {})
        except yaml.YAMLError as e:
            raise ConfigError(f"Error al leer {config_file}: {e}")

    def _load_deepl_config(self) -> None:
        deepl_config_file = self.config_dir / "deepl_config.yaml"
        if not deepl_config_file.exists():
            raise ConfigError(
                f"Archivo de configuración DeepL no encontrado: {deepl_config_file}"
            )
        try:
            with open(deepl_config_file, "r", encoding="utf-8") as f:
                self._config.update(yaml.safe_load(f) or {})
        except yaml.YAMLError as e:
            raise ConfigError(f"Error al leer {deepl_config_file}: {e}")

    def _load_env_variables(self) -> None:
        """Carga secretos del entorno. La API key es OPCIONAL al cargar (lazy)."""
        self._config.setdefault("deepl", {})
        # Puede ser None: solo se exige cuando alguien llama get_deepl_api_key().
        self._config["deepl"]["api_key"] = os.getenv("DEEPL_API_KEY")

        log_level = os.getenv("LOG_LEVEL")
        if log_level:
            self._config.setdefault("logging", {})
            self._config["logging"]["level"] = log_level.upper()

    def _validate_config(self) -> None:
        required_sections = ["project", "languages", "paths", "latex", "output"]
        for section in required_sections:
            if section not in self._config:
                raise ConfigError(
                    f"Sección requerida '{section}' no encontrada en la configuración"
                )

        for path_key in ["data_dir", "templates_dir", "output_dir"]:
            if path_key not in self._config["paths"]:
                raise ConfigError(f"Ruta requerida '{path_key}' no encontrada en paths")

        if "source" not in self._config["languages"] or "target" not in self._config["languages"]:
            raise ConfigError("Idiomas 'source' y 'target' son requeridos en la configuración")

        self._ensure_directories_exist()

    def _ensure_directories_exist(self) -> None:
        for path in [
            self.get_data_dir(),
            self.get_templates_dir(),
            self.get_output_dir(),
            self.get_output_dir() / "pdf",
            self.get_output_dir() / "tex",
        ]:
            path.mkdir(parents=True, exist_ok=True)

    # === Acceso ===

    def get(self, key: str, default: Any = None) -> Any:
        """Obtiene un valor con notación de punto: `config.get('latex.engine')`."""
        value: Any = self._config
        try:
            for k in key.split("."):
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    def get_project_info(self) -> Dict[str, str]:
        return self._config.get("project", {})

    def get_source_language(self) -> str:
        return self._config["languages"]["source"]

    def get_target_language(self) -> str:
        return self._config["languages"]["target"]

    def get_data_dir(self) -> Path:
        return Path(self._config["paths"]["data_dir"])

    def get_templates_dir(self) -> Path:
        return Path(self._config["paths"]["templates_dir"])

    def get_template_name(self) -> str:
        """Subcarpeta de la plantilla elegida (dentro de templates_dir). Default: 'cv_ds'."""
        return self._config["latex"].get("template", "cv_ds")

    def get_template_dir(self) -> Path:
        """Ruta a la plantilla elegida: templates_dir / template_name."""
        return self.get_templates_dir() / self.get_template_name()

    def get_output_dir(self) -> Path:
        return Path(self._config["paths"]["output_dir"])

    def get_latex_engine(self) -> str:
        return self._config["latex"]["engine"]

    def get_latex_options(self) -> list:
        return self._config["latex"].get("options", [])

    def get_main_template(self) -> str:
        return self._config["latex"].get("main_template", "cv_template.tex")

    def get_deepl_config(self) -> Dict[str, Any]:
        return self._config.get("deepl", {})

    def get_deepl_api_key(self) -> str:
        """Devuelve la API key de DeepL o falla claro si no está en el entorno."""
        key: Optional[str] = self._config.get("deepl", {}).get("api_key")
        if not key:
            raise ConfigError(
                "DEEPL_API_KEY no encontrada. Define un .env con tu clave para traducir "
                "(no hace falta para render/compile en un idioma ya disponible)."
            )
        return key

    def get_deepl_api_url(self) -> str:
        return self._config["deepl"].get("api_url", "https://api-free.deepl.com")

    def get_translation_config(self) -> Dict[str, Any]:
        return self._config.get("translation", {})

    def get_labels(self, lang: str) -> Dict[str, str]:
        """Etiquetas de la plantilla para un idioma (títulos de sección, textos fijos).

        Cae al idioma fuente si no hay entrada para `lang`.
        """
        labels = self._config.get("labels", {})
        return labels.get(lang) or labels.get(self.get_source_language(), {})

    def get_log_level(self) -> str:
        return self._config.get("logging", {}).get("level", "INFO")

    def __str__(self) -> str:
        """Representación segura: enmascara la API key."""
        safe = {**self._config, "deepl": {**self._config.get("deepl", {})}}
        if safe["deepl"].get("api_key"):
            safe["deepl"]["api_key"] = "***OCULTA***"
        return f"Config({safe})"

    __repr__ = __str__


def load_config(config_dir: str = "config") -> Config:
    """Carga y valida la configuración de AutoCV."""
    return Config(config_dir)
