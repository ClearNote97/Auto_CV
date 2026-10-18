# ADR-0004: Traducción — lote + cache por hash + no-traducir + glosario

- **Estado:** aceptada

## Contexto

El inglés se deriva del español con la API de DeepL ([ADR-0001](./0001-cv-como-datos-es-fuente-en-derivado.md)).
El legacy traducía **string por string** (una petición HTTP por texto, recursivamente): lento y quemaba la cuota.
Además, DeepL traduce *todo* lo que recibe, incluyendo cosas que no debería: nombres de empresa, fechas, y
términos ambiguos (ej. *"Actualidad"* → *"News"* en vez de *"Present"*).

## Decisión

El `translator`:

1. **Traduce en lote**: junta todos los strings de un documento y los manda en **una sola llamada** por archivo.
2. **Cachea por hash SHA256** del YAML fuente (en `.cache/translations/`, fuera de `data/`): solo re-traduce lo
   que cambió.
3. **No traduce** los valores bajo claves declaradas en `deepl_config.yaml → no_translate_keys` (empresa,
   institución, correo, URLs…): nombres propios e identificadores quedan intactos.
4. **Glosario** de override exacto (`glossary`): términos como *"Actualidad" → "Present"* no pasan por DeepL.
5. El import de `deepl` es **lazy** (solo al traducir de verdad): el módulo se importa sin la lib, y la red queda
   aislada en un único método, mockeable en tests.

## Consecuencias

- **+** Respeta la cuota de DeepL (una llamada por documento, cache evita re-traducir).
- **+** Nombres propios y términos ambiguos salen correctos sin editar `data/en` a mano.
- **+** La lógica es testeable sin red (mock del único punto de salida).
- **−** `no_translate_keys` y `glossary` son listas curadas a mano: un caso nuevo requiere añadirlo.
- **−** La cache asume que el `.tex`/plantilla no cambió; un cambio de plantilla no invalida la traducción (pero no la necesita).
