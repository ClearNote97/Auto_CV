"""
Script para crear la estructura del proyecto AutoCV en la carpeta actual.
No crea .devcontainer, README.md ni requirements.txt.
"""

import os
from pathlib import Path


def create_directory_structure():
    """Crea la estructura de carpetas del proyecto AutoCV en la raíz actual"""
    directories = [
        "datos",
        "datos/es",
        "datos/en",
        "plantillas",
        "plantillas/estilos",
        "src",
        "src/modules",
        "src/utils",
        "output",
        "output/tex",
        "output/pdf",
        "config",
        "tests",
    ]
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"📁 Creada carpeta: {directory}")


def create_files():
    """Crea los archivos base del proyecto (sin .devcontainer, README.md ni requirements.txt)"""
    files_content = {
        # Archivos de datos YAML
        "datos/es/personales.yaml": "# Datos personales en español\n",
        "datos/es/experiencia.yaml": "# Experiencia laboral en español\n",
        "datos/es/educacion.yaml": "# Educación en español\n",
        "datos/es/certificaciones.yaml": "# Certificaciones en español\n",
        "datos/es/publicaciones.yaml": "# Publicaciones en español\n",
        "datos/es/aptitudes.yaml": "# Aptitudes y habilidades en español\n",
        "datos/es/otros.yaml": "# Otros datos en español\n",
        "datos/en/personales.yaml": "# Personal data in English\n",
        "datos/en/experiencia.yaml": "# Work experience in English\n",
        "datos/en/educacion.yaml": "# Education in English\n",
        "datos/en/certificaciones.yaml": "# Certifications in English\n",
        "datos/en/publicaciones.yaml": "# Publications in English\n",
        "datos/en/aptitudes.yaml": "# Skills and abilities in English\n",
        "datos/en/otros.yaml": "# Other data in English\n",
        # Plantillas LaTeX
        "plantillas/cv_template.tex": "% Plantilla LaTeX para CV\n% TODO: Definir plantilla\n",
        "plantillas/estilos/cv_styles.sty": "% Estilos personalizados para CV\n% TODO: Definir estilos\n",
        # Módulos Python principales
        "src/__init__.py": "",
        "src/main.py": '#!/usr/bin/env python3\n"""\nAutoCV - Generador automático de CV multiidioma\nPunto de entrada principal del proyecto\n"""\n\n# TODO: Implementar main.py\n',
        # Módulos específicos
        "src/modules/__init__.py": "",
        "src/modules/data_loader.py": '"""\nMódulo para cargar y guardar datos desde archivos YAML\n"""\n\n# TODO: Implementar DataLoader\n',
        "src/modules/translator.py": '"""\nMódulo para traducir datos usando la API de DeepL\n"""\n\n# TODO: Implementar Translator\n',
        "src/modules/template_renderer.py": '"""\nMódulo para renderizar plantillas LaTeX con datos\n"""\n\n# TODO: Implementar TemplateRenderer\n',
        "src/modules/pdf_generator.py": '"""\nMódulo para generar PDFs desde archivos LaTeX\n"""\n\n# TODO: Implementar PDFGenerator\n',
        "src/modules/config.py": '"""\nMódulo para manejar configuración del proyecto\n"""\n\n# TODO: Implementar Config\n',
        # Utilidades
        "src/utils/__init__.py": "",
        "src/utils/file_utils.py": '"""\nUtilidades para manejo de archivos\n"""\n\n# TODO: Implementar utilidades de archivos\n',
        "src/utils/validation.py": '"""\nUtilidades para validación de datos\n"""\n\n# TODO: Implementar validaciones\n',
        # Archivos de configuración
        "config/config.yaml": "# Configuración general del proyecto AutoCV\n# TODO: Definir configuración\n",
        "config/deepl_config.yaml": "# Configuración de DeepL API\n# TODO: Definir configuración DeepL\n",
        # Tests
        "tests/__init__.py": "",
        "tests/test_data_loader.py": '"""\nTests para el módulo data_loader\n"""\n\n# TODO: Implementar tests\n',
        "tests/test_translator.py": '"""\nTests para el módulo translator\n"""\n\n# TODO: Implementar tests\n',
        "tests/test_template_renderer.py": '"""\nTests para el módulo template_renderer\n"""\n\n# TODO: Implementar tests\n',
        # Archivos de proyecto
        ".env.example": "# Variables de entorno para AutoCV\n# TODO: Definir variables\n",
        ".gitignore": "# TODO: Definir .gitignore\n",
        "run.py": '#!/usr/bin/env python3\n"""\nScript de ejecución rápida para AutoCV\n"""\n\n# TODO: Implementar script de ejecución\n',
    }
    for file_path, content in files_content.items():
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"📄 Creado archivo: {file_path}")


def main():
    print("🚀 Creando estructura del proyecto AutoCV en la carpeta actual...")
    print("=" * 50)
    create_directory_structure()
    print("\n" + "=" * 50)
    create_files()
    print("\n" + "=" * 50)
    print(
        "✅ ¡Estructura del proyecto AutoCV creada exitosamente en la carpeta actual!"
    )
    print("\n📋 Próximos pasos:")
    print(
        "1. Copia tu devcontainer.json, Dockerfile, README.md y requirements.txt si aún no están en la raíz."
    )
    print("2. Abre el proyecto en VS Code con el devcontainer.")
    print("3. ¡Comienza el desarrollo! 🚀")


if __name__ == "__main__":
    main()
