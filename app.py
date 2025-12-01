import gradio as gr
import os
from google import genai
from google.genai import types  # AGREGAR ESTA LÍNEA
from dotenv import load_dotenv
import time
import mlflow
from datetime import datetime
import hashlib
import logging


# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Cargar variables de entorno
load_dotenv()

# Configurar MLflow
mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://mlflow-server:5000"))
mlflow.set_experiment("traduccion-genai")

# Configurar Gemini API
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

IDIOMAS = [
    "Español", "Inglés", "Francés", "Alemán", "Italiano",
    "Portugués", "Chino", "Japonés", "Coreano", "Árabe", "Ruso"
]


def traducir_texto(texto_original, idioma_objetivo):
    if not texto_original or not texto_original.strip():
        return "Por favor, ingresa un texto para traducir."
    
    if not idioma_objetivo:
        return "Por favor, selecciona un idioma objetivo."
    
    try:
        timestamp_inicio = datetime.now()
        prompt = f"Traduce esto al {idioma_objetivo}: {texto_original}"
        
        inicio = time.time()
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.1,
                max_output_tokens=1000,
            )
        )
        
        fin = time.time()
        latencia = (fin - inicio) * 1000
        traduccion = response.text.strip()
        
        # === CREAR ARCHIVO ===
        
        artifact_file = "traduccion.txt"
        
        with open(artifact_file, "w", encoding="utf-8") as f:
            f.write(f"Original: {texto_original}\n\n")
            f.write(f"Traducción: {traduccion}\n")
        
        logger.info(f"Archivo creado: {artifact_file}")
        
        # === REGISTRAR EN MLFLOW ===
        
        with mlflow.start_run() as run:
            # Obtener el run ID y experiment ID
            run_id = run.info.run_id
            experiment_id = run.info.experiment_id
            
            logger.info(f"Run ID: {run_id}")
            logger.info(f"Experiment ID: {experiment_id}")
            
            mlflow.log_param("idioma_objetivo", idioma_objetivo)
            mlflow.log_param("modelo", "gemini-2.5-flash")
            mlflow.log_metric("latency_ms", latencia)
            mlflow.log_metric("len_response", len(traduccion))
            mlflow.set_tag("timestamp", timestamp_inicio.isoformat())
            mlflow.set_tag("tipo_tarea", "traduccion")
            mlflow.set_tag("proveedor", "google-gemini")
            
            # === INTENTAR COPIAR CON DEBUG ===
            
            try:
                logger.info(f"Intentando registrar artifact: {artifact_file}")
                
                # Método 1: Usar mlflow.log_artifact()
                mlflow.log_artifact(artifact_file)
                
                logger.info(f"✅ Artifact registrado con mlflow.log_artifact()")
                
            except Exception as e:
                logger.error(f"Error con mlflow.log_artifact(): {e}")
                
                # Método 2: Copiar manualmente al directorio de artifacts
                try:
                    import shutil
                    
                    # Ruta donde MLflow guarda los artifacts
                    artifacts_dir = f"/mlflow/mlruns/{experiment_id}/{run_id}/artifacts"
                    
                    logger.info(f"Creando directorio: {artifacts_dir}")
                    os.makedirs(artifacts_dir, exist_ok=True)
                    
                    # Copiar el archivo
                    dest_file = os.path.join(artifacts_dir, artifact_file)
                    shutil.copy(artifact_file, dest_file)
                    
                    logger.info(f"✅ Archivo copiado manualmente a: {dest_file}")
                    
                except Exception as e2:
                    logger.error(f"Error copiando manualmente: {e2}")
                    import traceback
                    logger.error(traceback.format_exc())
        
        logger.info(f"✓ Traducción completada - Latencia: {latencia:.2f}ms")
        
        return traduccion
        
    except Exception as e:
        logger.error(f"✗ Error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return f"Error: {str(e)}"



# Interfaz Gradio
with gr.Blocks(title="Traductor con IA") as demo:
    gr.Markdown("# 🌐 Aplicación de Traducción con IA")
    gr.Markdown("Traduce texto a diferentes idiomas usando Gemini. Cada traducción se registra en MLflow.")

    with gr.Row():
        with gr.Column():
            texto_input = gr.Textbox(
                label="Texto Original",
                placeholder="Escribe o pega el texto que deseas traducir...",
                lines=6,
                max_lines=10
            )

            idioma_dropdown = gr.Dropdown(
                choices=IDIOMAS,
                label="Idioma Objetivo",
                value="Inglés",
                interactive=True
            )

            boton_traducir = gr.Button("Traducir", variant="primary")

        with gr.Column():
            texto_output = gr.Textbox(
                label="Texto Traducido",
                lines=6,
                max_lines=10,
                interactive=False
            )

    gr.Markdown("---")
    gr.Markdown("**Nota**: Accede a http://localhost:5000 para ver MLflow.")

    gr.Examples(
        examples=[
            ["Hola, ¿cómo estás?", "Inglés"],
            ["Buenos días", "Francés"],
            ["La tecnología es genial", "Alemán"]
        ],
        inputs=[texto_input, idioma_dropdown]
    )

    boton_traducir.click(
        fn=traducir_texto,
        inputs=[texto_input, idioma_dropdown],
        outputs=texto_output
    )

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )
