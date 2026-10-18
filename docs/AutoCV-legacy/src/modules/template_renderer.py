"""
AutoCV - Generador Automático de CV
====================================
Renderiza tu CV en LaTeX y PDF usando datos YAML y Jinja2.
"""

import yaml
import os
import subprocess
import shutil
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
import argparse
import logging

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CVGenerator:
    def __init__(self, base_dir=None):
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self.data_dir = self.base_dir / "data"
        self.templates_dir = self.base_dir / "templates" / "cv_ds"
        self.output_dir = self.base_dir / "output"
        self.output_dir.mkdir(exist_ok=True)
        logger.info(f"Directorio base: {self.base_dir}")
        logger.info(f"Directorio de datos: {self.data_dir}")
        logger.info(f"Directorio de plantillas: {self.templates_dir}")
        logger.info(f"Directorio de salida: {self.output_dir}")

    def load_yaml_data(self, language="es"):
        lang_dir = self.data_dir / language
        if not lang_dir.exists():
            raise FileNotFoundError(f"Directorio de idioma no encontrado: {lang_dir}")

        data = {}
        yaml_files = [
            "personales.yaml",
            "experiencia.yaml",
            "educacion.yaml",
            "certificaciones.yaml",
            "publicaciones.yaml",
            "aptitudes.yaml",
            "otros.yaml"
        ]

        for yaml_file in yaml_files:
            file_path = lang_dir / yaml_file
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_data = yaml.safe_load(f)
                        key = yaml_file.replace('.yaml', '')
                        data[key] = file_data
                        logger.info(f"✓ Cargado: {yaml_file}")
                except Exception as e:
                    logger.error(f"✗ Error cargando {yaml_file}: {e}")
            else:
                logger.warning(f"⚠ Archivo no encontrado: {yaml_file}")

        # --- Preprocesamiento de campos para la plantilla ---
        personales = data.get('personales', {})
        if 'linkedin' in personales and personales['linkedin']:
            personales['linkedin'] = personales['linkedin'].replace('https://www.linkedin.com/in/', '').replace('/', '')
        if 'github' in personales and personales['github']:
            personales['github'] = personales['github'].replace('https://github.com/', '').replace('/', '')
        data['personales'] = personales

        return data

    def setup_jinja_environment(self):
        env = Environment(
        block_start_string='((*',
        block_end_string='*))',
        variable_start_string='(((',
        variable_end_string=')))',
        comment_start_string='((#',
        comment_end_string='#))',
        trim_blocks=True,
        autoescape=False,
        loader=FileSystemLoader(str(self.templates_dir))
    )
        return env

    def render_template(self, data, template_name="cv_template.tex"):
        env = self.setup_jinja_environment()
        try:
            template = env.get_template(template_name)
            logger.info(f"✓ Plantilla cargada: {template_name}")
        except Exception as e:
            logger.error(f"✗ Error cargando plantilla {template_name}: {e}")
            raise

        try:
            rendered_content = template.render(**data)
            logger.info("✓ Plantilla renderizada exitosamente")
            return rendered_content
        except Exception as e:
            logger.error(f"✗ Error renderizando plantilla: {e}")
            raise

    def save_tex_file(self, content, filename="cv_final.tex"):
        output_path = self.output_dir / filename
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"✓ Archivo LaTeX guardado: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"✗ Error guardando archivo LaTeX: {e}")
            raise

    def copy_template_files(self):
        files_to_copy = [
            "altacv.cls",
            "pubs-num.cfg",
            "pubs-authoryear.cfg"
        ]
        for file_name in files_to_copy:
            src_path = self.templates_dir / file_name
            dst_path = self.output_dir / file_name
            if src_path.exists():
                try:
                    shutil.copy2(src_path, dst_path)
                    logger.info(f"✓ Copiado: {file_name}")
                except Exception as e:
                    logger.warning(f"⚠ Error copiando {file_name}: {e}")
            else:
                logger.warning(f"⚠ Archivo no encontrado: {file_name}")

    def compile_pdf(self, tex_file_path, output_name="cv_final"):
        logger.info("🔄 Iniciando compilación de PDF...")
        original_cwd = os.getcwd()
        os.chdir(self.output_dir)
        try:
            for i in range(2):
                logger.info(f"📄 Compilación {i+1}/2...")
                result = subprocess.run([
                    'pdflatex',
                    '-interaction=nonstopmode',
                    '-halt-on-error',
                    str(tex_file_path.name)
                ],
                capture_output=True,
                text=True,
                cwd=self.output_dir
                )
                if result.returncode != 0:
                    logger.error("✗ Error en compilación de LaTeX:")
                    logger.error(result.stdout)
                    logger.error(result.stderr)
                    raise subprocess.CalledProcessError(result.returncode, 'pdflatex')
                else:
                    logger.info(f"✓ Compilación {i+1} exitosa")
            pdf_path = self.output_dir / f"{output_name}.pdf"
            if pdf_path.exists():
                logger.info(f"🎉 PDF generado exitosamente: {pdf_path}")
                return pdf_path
            else:
                raise FileNotFoundError("PDF no fue generado")
        finally:
            os.chdir(original_cwd)

    def clean_auxiliary_files(self):
        aux_extensions = ['.aux', '.log', '.out', '.fdb_latexmk', '.fls', '.synctex.gz']
        for ext in aux_extensions:
            for file_path in self.output_dir.glob(f"*{ext}"):
                try:
                    file_path.unlink()
                    logger.info(f"🧹 Eliminado: {file_path.name}")
                except Exception as e:
                    logger.warning(f"⚠ No se pudo eliminar {file_path.name}: {e}")

    def generate_cv(self, language="es", template_name="cv_template.tex", output_name="cv_final", clean_aux=True):
        logger.info("🚀 Iniciando generación de CV...")
        try:
            logger.info("📂 Cargando datos YAML...")
            data = self.load_yaml_data(language)
            logger.info("📋 Copiando archivos de plantilla...")
            self.copy_template_files()
            logger.info("🎨 Renderizando plantilla...")
            rendered_content = self.render_template(data, template_name)
            logger.info("💾 Guardando archivo LaTeX...")
            tex_path = self.save_tex_file(rendered_content, f"{output_name}.tex")
            logger.info("🔧 Compilando PDF...")
            pdf_path = self.compile_pdf(tex_path, output_name)
            if clean_aux:
                logger.info("🧹 Limpiando archivos auxiliares...")
                self.clean_auxiliary_files()
            logger.info("✅ ¡CV generado exitosamente!")
            logger.info(f"📄 Archivo LaTeX: {tex_path}")
            logger.info(f"📑 Archivo PDF: {pdf_path}")
            return tex_path, pdf_path
        except Exception as e:
            logger.error(f"❌ Error generando CV: {e}")
            raise

def main():
    parser = argparse.ArgumentParser(description="Generador Automático de CV")
    parser.add_argument(
        "--language", "-l",
        default="es",
        choices=["es", "en"],
        help="Idioma de los datos (es/en)"
    )
    parser.add_argument(
        "--template", "-t",
        default="cv_template.tex",
        help="Nombre de la plantilla LaTeX"
    )
    parser.add_argument(
        "--output", "-o",
        default="cv_final",
        help="Nombre base de los archivos de salida"
    )
    parser.add_argument(
        "--no-clean",
        action="store_true",
        help="No limpiar archivos auxiliares"
    )
    parser.add_argument(
        "--base-dir",
        help="Directorio base del proyecto"
    )

    args = parser.parse_args()

    try:
        generator = CVGenerator(base_dir=args.base_dir)
        tex_path, pdf_path = generator.generate_cv(
            language=args.language,
            template_name=args.template,
            output_name=args.output,
            clean_aux=not args.no_clean
        )
        print(f"\n🎉 ¡CV generado exitosamente!")
        print(f"📄 LaTeX: {tex_path}")
        print(f"📑 PDF: {pdf_path}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1
    return 0

if __name__ == "__main__":
    exit(main())