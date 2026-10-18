"""Translator — ES→EN con la lib oficial `deepl`, en lote y con cache por hash.

Reescritura del legacy (`docs/AutoCV-legacy/src/modules/translator.py`) — feature 001, Tarea 3.
Cambios respecto al legacy:
  1. Lib **oficial `deepl`** en vez de `requests` crudo.
  2. **Una llamada por documento** (batch de todos los strings del YAML) en vez de una petición HTTP
     por texto → respeta la cuota (criterio CA3).
  3. Cache SHA256 movido a **`.cache/translations/`** fuera de `data/` (criterio CA2).
  4. `import deepl` es **lazy** (solo al traducir de verdad): el módulo importa sin la lib instalada,
     y la lógica de lote/cache se testea con un mock (`_translate_batch` es el único punto de red).

Fuera de alcance (→ feature 003): glosario, skip por campo (emails/URLs), tuning fino de retries.
"""

import hashlib
from pathlib import Path
from typing import Any, Callable, Iterator, List

import yaml

# Mapeo idioma-config → código DeepL. El destino EN debe ser regional (EN-US/EN-GB);
# "EN" a secas está deprecado como target en la API de DeepL.
_DEEPL_SOURCE = {"es": "ES", "en": "EN"}
_DEEPL_TARGET = {"en": "EN-US", "es": "ES", "pt": "PT-PT"}


class TranslatorError(Exception):
    """Error de traducción de AutoCV."""


def _is_translatable(value: Any) -> bool:
    """True si es un string que vale la pena traducir (no vacío y con al menos una letra).

    Protege valores que nunca son prosa (teléfonos, fechas, números) de gastar cuota y de
    corromperse. El skip fino por campo (emails/URLs) llega en la feature 003.
    """
    return isinstance(value, str) and any(ch.isalpha() for ch in value)


def _collect(data: Any, out: List[str], skip_keys: set, glossary: dict, skip: bool = False) -> None:
    """Junta los strings a traducir, saltando valores bajo `skip_keys` y los del glosario.

    `skip` se propaga a los subárboles cuyo valor cuelga de una clave no-traducible.
    """
    if isinstance(data, dict):
        for k, v in data.items():
            _collect(v, out, skip_keys, glossary, skip=skip or (k in skip_keys))
    elif isinstance(data, list):
        for item in data:
            _collect(item, out, skip_keys, glossary, skip=skip)
    elif _is_translatable(data) and not skip and data.strip() not in glossary:
        out.append(data)


def _rebuild(data: Any, translated: Iterator[str], skip_keys: set, glossary: dict, skip: bool = False) -> Any:
    """Reconstruye la estructura consumiendo `translated` en el MISMO orden que `_collect`."""
    if isinstance(data, dict):
        return {k: _rebuild(v, translated, skip_keys, glossary, skip=skip or (k in skip_keys))
                for k, v in data.items()}
    if isinstance(data, list):
        return [_rebuild(item, translated, skip_keys, glossary, skip=skip) for item in data]
    if _is_translatable(data) and not skip:
        if data.strip() in glossary:  # override exacto (no pasa por DeepL)
            return glossary[data.strip()]
        return next(translated)
    return data


class Translator:
    """Traduce los YAML de `data/es` a `data/en`, saltando lo que no cambió (cache por hash)."""

    def __init__(self, config, cache_dir: str = ".cache/translations"):
        self.config = config
        data_dir = config.get_data_dir()
        self.source_lang = config.get_source_language()
        self.target_lang = config.get_target_language()
        self.es_dir = data_dir / self.source_lang
        self.en_dir = data_dir / self.target_lang
        self.cache_dir = Path(cache_dir)
        self._client = None  # lazy
        tcfg = config.get_translation_config()
        self.skip_keys = set(tcfg.get("no_translate_keys", []))
        self.glossary = dict(tcfg.get("glossary", {}))

    # --- cache ---

    @staticmethod
    def _file_hash(path: Path) -> str:
        sha = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha.update(chunk)
        return sha.hexdigest()

    def _hash_path(self, es_file: Path) -> Path:
        return self.cache_dir / f"{es_file.stem}.hash"

    def _needs_translation(self, es_file: Path) -> bool:
        hash_path = self._hash_path(es_file)
        en_file = self.en_dir / es_file.name
        if not hash_path.exists() or not en_file.exists():
            return True
        return hash_path.read_text().strip() != self._file_hash(es_file)

    def _save_hash(self, es_file: Path) -> None:
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._hash_path(es_file).write_text(self._file_hash(es_file))

    # --- DeepL (único punto de red; mockeable en tests) ---

    def _translate_batch(self, texts: List[str]) -> List[str]:
        """Traduce una lista de strings en UNA llamada a DeepL. Devuelve la lista traducida."""
        if not texts:
            return []
        import deepl  # lazy: solo se necesita al traducir de verdad

        if self._client is None:
            self._client = deepl.Translator(self.config.get_deepl_api_key())

        tcfg = self.config.get_translation_config()
        kwargs = {
            "source_lang": _DEEPL_SOURCE.get(self.source_lang, self.source_lang.upper()),
            "target_lang": _DEEPL_TARGET.get(self.target_lang, self.target_lang.upper()),
            "preserve_formatting": bool(tcfg.get("preserve_formatting", True)),
            "split_sentences": str(tcfg.get("split_sentences", "1")),
        }
        formality = tcfg.get("formality")
        if formality and formality != "default":
            kwargs["formality"] = formality  # solo si el target lo soporta

        results = self._client.translate_text(texts, **kwargs)
        # translate_text devuelve un TextResult o lista; normalizamos a lista de .text
        if not isinstance(results, list):
            results = [results]
        return [r.text for r in results]

    # --- orquestación ---

    def translate_data(self, data: Any) -> Any:
        """Traduce una estructura completa en lote, preservando claves y forma."""
        texts: List[str] = []
        _collect(data, texts, self.skip_keys, self.glossary)
        translated = self._translate_batch(texts)
        return _rebuild(data, iter(translated), self.skip_keys, self.glossary)

    def translate_file(self, es_file: Path, force: bool = False) -> bool:
        """Traduce un YAML fuente si cambió (o si force). Devuelve True si tradujo, False si cache hit."""
        if not force and not self._needs_translation(es_file):
            return False
        with open(es_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        translated = self.translate_data(data)
        self.en_dir.mkdir(parents=True, exist_ok=True)
        en_file = self.en_dir / es_file.name
        with open(en_file, "w", encoding="utf-8") as f:
            yaml.dump(translated, f, allow_unicode=True, sort_keys=False)
        self._save_hash(es_file)
        return True

    def translate_all(self, force: bool = False, log: Callable[[str], None] = print) -> None:
        """Traduce todos los `data/es/*.yaml` que hayan cambiado."""
        for es_file in sorted(self.es_dir.glob("*.yaml")):
            if self.translate_file(es_file, force=force):
                log(f"  ✓ {es_file.name} traducido")
            else:
                log(f"  - {es_file.name} sin cambios (cache hit)")


if __name__ == "__main__":
    from src.autocv.config import load_config

    try:
        Translator(load_config()).translate_all()
        print("✅ Traducción completada.")
    except Exception as e:
        print(f"❌ Error: {e}")
