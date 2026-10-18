# ADR-0005: Presentación — AltaCV, layout y etiquetas i18n

- **Estado:** aceptada

## Contexto

La capa de presentación (cómo se ve el CV) debe estar **separada** del contenido (los YAML) y soportar los dos
idiomas. Decisiones de diseño que surgieron al construir el documento:

## Decisión

- **Plantilla:** [AltaCV](https://github.com/liantze/AltaCV) (variante `cv_ds`), compilada con **`latexmk`** —
  que orquesta `pdflatex` + **`biber`** solo, para que las publicaciones resuelvan. La plantilla vive en
  `src/frontend/templates/` (es la capa de presentación) y se vendoriza **una sola**, sin el sample upstream.
- **Layout:** banda superior a **70/30** (Aptitudes Técnicas | Idiomas + Intereses apilados), y el resto
  (Experiencia, Educación, Publicaciones, Certificaciones) a **ancho completo** debajo. Las aptitudes van
  **por categorías** (subtítulos). Los chips se envuelven dentro de una caja del ancho de columna para no
  desbordar el borde.
- **i18n de etiquetas:** los **títulos de sección** y textos fijos (ej. *"¿Cómo hice este documento?"*) **no se
  traducen con DeepL**; se eligen de un diccionario por idioma en `config.yaml → labels` según el build.
- **Marca + numeración:** marca de agua (arriba-derecha) desde la página 2, número de página (centrado) desde la 1,
  y un link al repositorio en el footer — todo con `fancyhdr`.

## Consecuencias

- **+** Rediseñar el CV no toca el contenido, y viceversa. Calidad tipográfica de LaTeX.
- **+** Los títulos salen en el idioma correcto (los traduce un diccionario, no DeepL, que los dejaría inconsistentes).
- **+** Las publicaciones resuelven (biber) sin lógica manual.
- **−** LaTeX/AltaCV tiene su curva: ajustes de layout requieren saber TeX (documentado en los commits).
- **−** Añadir una etiqueta nueva a la plantilla implica declararla en `labels` para ambos idiomas.
