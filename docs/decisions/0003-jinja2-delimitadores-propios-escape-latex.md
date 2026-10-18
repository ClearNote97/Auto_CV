# ADR-0003: Render con Jinja2 (delimitadores propios) + escape de LaTeX

- **Estado:** aceptada

## Contexto

El PDF se produce con LaTeX (plantilla AltaCV). Hay que inyectar los datos del YAML en un `.tex`. Dos choques
con LaTeX:

1. Los delimitadores por defecto de Jinja2 (`{{ }}`, `{% %}`) **chocan con las llaves de LaTeX** (`\cmd{...}`),
   produciendo renders rotos o ambiguos.
2. Los datos del usuario contienen **caracteres especiales de LaTeX** (`% & # _ $ { } ~ ^ \`). Sin escapar, un
   `%` comenta el resto de la línea (ej. *"+100% en ventas"* se corta en `+100`), un `&` rompe la compilación.

## Decisión

- Configurar Jinja2 con **delimitadores propios** que no aparecen en LaTeX: bloque `((* *))`, variable `((( )))`,
  comentario `((# #))`.
- **Escapar los especiales de LaTeX** en todos los valores de datos, de forma recursiva y en un solo paso
  (regex), **exentos los campos de URL/identificador** (`enlace`, `linkedin`, `github`, `correo`, `repo_url`)
  para no romper los enlaces.
- `autoescape=False` (es LaTeX, no HTML) y `Undefined` lenient (la plantilla usa `((* if opcional *))` para
  campos que pueden faltar; `StrictUndefined` los rompería).

## Consecuencias

- **+** El contenido del usuario puede tener `%`, `&`, etc. sin romper el PDF.
- **+** La plantilla LaTeX se lee natural, sin pelear con los delimitadores de Jinja.
- **−** El escape es específico de LaTeX: si se agregara otro backend de salida (HTML), necesitaría su propio escape.
- **−** Un campo nuevo que sea URL debe añadirse a la lista de exentos, o se escaparía y rompería el link.
