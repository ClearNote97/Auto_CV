"""
Módulo para traducir archivos YAML de data/es/ a data/en/ usando DeepL,
con detección de cambios por hash para evitar traducciones innecesarias.
"""

import os
import yaml
import hashlib
import requests
from pathlib import Path
from typing import Any, Dict
from src.modules.config import load_config

DEEPL_API_URL = "https://api-free.deepl.com/v2/translate"


class TranslatorError(Exception):
    pass


class Translator:
    def __init__(self, config):
        self.config = config
        self.api_key = config.get_deepl_api_key()
        self.source_lang = config.get_source_language()
        self.target_lang = config.get_target_language()
        self.data_dir = config.get_data_dir()
        self.es_dir = self.data_dir / "es"
        self.en_dir = self.data_dir / "en"
        self.en_dir.mkdir(parents=True, exist_ok=True)

    def _file_hash(self, file_path: Path) -> str:
        """Calcula el hash SHA256 de un archivo."""
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    def _hash_file_path(self, yaml_file: Path) -> Path:
        """Devuelve la ruta del archivo hash asociado a un YAML."""
        return self.en_dir / f"{yaml_file.stem}.hash"

    def _should_translate(self, es_file: Path) -> bool:
        """Determina si el archivo debe ser traducido (hash diferente o no existe)."""
        hash_path = self._hash_file_path(es_file)
        current_hash = self._file_hash(es_file)
        if not hash_path.exists():
            return True
        with open(hash_path, "r") as f:
            saved_hash = f.read().strip()
        return current_hash != saved_hash

    def _save_hash(self, es_file: Path):
        """Guarda el hash SHA256 del archivo en español."""
        hash_path = self._hash_file_path(es_file)
        current_hash = self._file_hash(es_file)
        with open(hash_path, "w") as f:
            f.write(current_hash)

    def _translate_text(self, text: str) -> str:
        """Traduce un texto usando la API de DeepL."""
        if not text.strip():
            return text
        data = {
            "auth_key": self.api_key,
            "text": text,
            "source_lang": self.source_lang.upper(),
            "target_lang": self.target_lang.upper(),
            "preserve_formatting": 1,
        }
        response = requests.post(DEEPL_API_URL, data=data)
        if response.status_code != 200:
            print("Respuesta completa de la API:", response.text)
            raise TranslatorError(f"Error en la API de DeepL: {response.text}")
        result = response.json()
        return result["translations"][0]["text"]

    def _translate_data(self, data: Any) -> Any:
        """Traduce recursivamente todos los textos en un dict/list."""
        if isinstance(data, dict):
            return {k: self._translate_data(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._translate_data(item) for item in data]
        elif isinstance(data, str):
            return self._translate_text(data)
        else:
            return data

    def translate_all(self):
        """Traduce todos los archivos YAML de data/es/ a data/en/ si han cambiado."""
        for es_file in self.es_dir.glob("*.yaml"):
            print(f"Procesando {es_file.name}...")
            if not self._should_translate(es_file):
                print(f"  - Sin cambios, se omite la traducción.")
                continue
            with open(es_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
            print(f"  - Traduciendo...")
            translated_data = self._translate_data(data)
            en_file = self.en_dir / es_file.name
            with open(en_file, "w", encoding="utf-8") as f:
                yaml.dump(translated_data, f, allow_unicode=True, sort_keys=False)
            self._save_hash(es_file)
            print(f"  - Traducción guardada en {en_file.name} y hash actualizado.")


# === EJEMPLO DE USO ===

if __name__ == "__main__":
    try:
        config = load_config()
        translator = Translator(config)
        translator.translate_all()
        print("✅ Traducción completada.")
    except Exception as e:
        print(f"❌ Error: {e}")
