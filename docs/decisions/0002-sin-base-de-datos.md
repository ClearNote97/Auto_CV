# ADR-0002: AutoCV sobre ClearNote_Dev, sin capa de base de datos

- **Estado:** aceptada

## Contexto

AutoCV se reconstruyó sobre la plantilla insignia [ClearNote_Dev](https://github.com/ClearNote97/ClearNote_Dev),
que trae un stack full-stack en Python (PostgreSQL + SQLModel/SQLAlchemy + Alembic, backend, frontend web,
analytics). Pero AutoCV es una **herramienta CLI de un solo usuario** que genera un documento: no tiene
usuarios, ni multi-tenancy, ni estado persistente más allá de unos YAML.

## Decisión

Usar ClearNote_Dev por su estructura SDD, su Dev Container y su roster de agentes, pero **sin activar su capa
de datos**: ni Postgres, ni ORM, ni Alembic, ni gobernanza de DB. La fuente de datos son los YAML versionados
en git. El scaffold full-stack que no se usa se **podó** del repo (vive en la plantilla si algún día se necesita).

## Consecuencias

- **+** Entorno simple y reproducible: el Dev Container solo necesita Python + TeXLive, sin servicios que levantar.
- **+** El repo cuenta una historia coherente: una herramienta enfocada, no una app con backend fantasma.
- **+** Sin DB no hay secretos de conexión ni superficie de ataque de datos.
- **−** Si AutoCV creciera a multiusuario/web, habría que reintroducir esas capas (pero están a un `git clone` de la plantilla).
- **Reversibilidad:** el stack opcional sigue declarado (comentado) en `requirements.txt`; reactivarlo es descomentar.
