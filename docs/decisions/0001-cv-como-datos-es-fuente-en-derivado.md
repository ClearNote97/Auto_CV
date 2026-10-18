# ADR-0001: El CV como datos — ES fuente única, EN derivado

- **Estado:** aceptada

## Contexto

Mantener un CV en Word es frágil: el formato se descuadra con cada cambio y la versión en inglés se mantiene
a mano (copiar-pegar), lo que casi garantiza dos versiones desincronizadas. No hay historial de qué cambió.

## Decisión

El CV se modela como **datos estructurados en YAML**, una sección por archivo (`personales`, `experiencia`,
`educacion`, …). El **español es la única fuente de verdad** (`data/es/`); el **inglés se deriva**
automáticamente (`data/en/`, vía DeepL — ver [ADR-0004](./0004-traduccion-lote-cache-no-traducir-glosario.md)).
`data/en` **nunca se edita a mano** y no se versiona (es regenerable).

## Consecuencias

- **+** Una sola edición en español; el inglés se genera. Cero copias desincronizadas.
- **+** Los datos son legibles, *diff-eables* y versionados en git: historial de qué cambió y cuándo.
- **+** Contenido separado de presentación: cambiar el texto no toca el diseño.
- **−** Depende de un servicio externo (DeepL) y de una API key para producir la versión en inglés.
- **−** Si DeepL traduce mal un término, hay que corregirlo con glosario/no-traducir, no editando `data/en`.
