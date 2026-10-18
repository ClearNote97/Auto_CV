# 00 — Propósito

## Misión

Que una persona mantenga su CV como **datos versionados** y obtenga, con **un solo comando**, un
PDF profesional y bilingüe (español fuente → inglés derivado) sin editar LaTeX ni traducir a mano.

## Problema

Hoy el CV se rehace a mano en editores visuales: cada actualización obliga a re-maquetar, a mantener
dos idiomas en paralelo y a re-traducir todo aunque cambie una línea. AutoCV ya existía como intento,
pero quedó a medias — **dos scripts que se corren por separado**, sin flujo único, con las publicaciones
que no resuelven y la traducción que quema cuota (una petición HTTP por texto). El resultado "funciona si
sabes exactamente qué dos cosas correr", que es otra forma de decir que no funciona. El dolor concreto:
actualizar el CV es caro, frágil y no reproducible.

## Para quién

- **Usa / decide / paga:** el autor del CV (usuario único). No hay multi-tenant, ni clientes externos,
  ni roles. Esto simplifica la gobernanza: no hay PII de terceros ni aislamiento por tenant.
- **Segundo lector:** cualquier reclutador que recibe el PDF final (consume el entregable, no el sistema).

## Métricas de éxito

- **Un comando** (`autocv build --lang both`) produce `output/` con el PDF en ES y EN desde `data/es/`.
- **Editar un YAML y reconstruir** refleja el cambio; la traducción **solo re-corre la sección que cambió**
  (cache por hash), sin gastar cuota de DeepL en lo que no se tocó.
- Las **publicaciones aparecen resueltas** en el PDF (biblatex/biber), no vacías ni con `[?]`.
- El **gate de calidad** (black + flake8 + mypy + pytest) pasa en verde en pre-commit.

---

> Cuando esta sección esté completa y estable, el resto de la constitución se lee **contra** ella:
> `02_scope` traza las fronteras del propósito, `01_principles` fija cómo se persigue y `03_stack` con qué.
