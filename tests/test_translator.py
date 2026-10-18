"""Tests de translator con DeepL MOCKEADO (sin red): lote, cache, skip-keys y glosario."""

import yaml

from src.autocv import translator as T


def test_is_translatable():
    assert T._is_translatable("hola")
    assert not T._is_translatable("")
    assert not T._is_translatable("+57 300")  # sin letras
    assert not T._is_translatable(42)


def test_collect_respects_skip_and_glossary():
    skip = {"empresa"}
    gloss = {"Actualidad": "Present"}
    data = {
        "puesto": "Analista",
        "empresa": "ACME",
        "fecha_fin": "Actualidad",
        "items": ["Vendí mucho", 10],
    }
    out = []
    T._collect(data, out, skip, gloss)
    # empresa (skip), Actualidad (glosario) y el int quedan fuera
    assert out == ["Analista", "Vendí mucho"]


def test_rebuild_applies_skip_and_glossary():
    skip = {"empresa"}
    gloss = {"Actualidad": "Present"}
    data = {"puesto": "Analista", "empresa": "ACME", "fecha_fin": "Actualidad", "n": 10}
    out = []
    T._collect(data, out, skip, gloss)
    res = T._rebuild(data, iter(f"EN[{t}]" for t in out), skip, gloss)
    assert res["puesto"] == "EN[Analista]"
    assert res["empresa"] == "ACME"  # no traducido
    assert res["fecha_fin"] == "Present"  # glosario (no pasa por DeepL)
    assert res["n"] == 10


def test_translate_file_batch_and_cache(cfg):
    tr = T.Translator(cfg)
    calls = {"n": 0}

    def fake_batch(texts):
        calls["n"] += 1
        return [f"EN[{t}]" for t in texts]

    tr._translate_batch = fake_batch

    es_file = cfg.get_data_dir() / "es" / "experiencia.yaml"
    assert tr.translate_file(es_file) is True  # cache miss → traduce
    assert calls["n"] == 1  # UNA llamada por documento (lote)
    assert tr.translate_file(es_file) is False  # cache hit → no traduce
    assert calls["n"] == 1

    en = yaml.safe_load((cfg.get_data_dir() / "en" / "experiencia.yaml").read_text())
    exp = en["experiencia"][0]
    assert exp["empresa"] == "ACME S.A."  # skip-key preservado
    assert exp["fecha_fin"] == "Present"  # glosario
    assert exp["puesto"] == "EN[Analista]"
