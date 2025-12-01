# Laboratorio: App de Traducción con Docker y MLflow

Aplicación de traducción de texto usando **Gemini API** con tracking en **MLflow**, empaquetada en **contenedores Docker** y publicada en **Docker Hub**.

## 📋 Descripción

Esta aplicación permite traducir texto a múltiples idiomas utilizando el modelo Gemini 2.5-flash. Cada traducción se registra automáticamente en MLflow para tracking, incluyendo parámetros, métricas y artifacts.

**Características:**
- ✅ Interfaz web con Gradio
- ✅ Traducciones con Gemini API
- ✅ Tracking completo en MLflow
- ✅ Dockerización sin docker-compose
- ✅ Publicación en Docker Hub
- ✅ Ejecución remota

## 🏗️ Arquitectura

┌─────────────────────────────────────────────────────────┐
│ Docker Network │
├─────────────────────────────────────────────────────────┤
│ │
│ ┌──────────────────────┐ ┌──────────────────────┐ │
│ │ traductor-app │ │ mlflow-server │ │
│ ├──────────────────────┤ ├──────────────────────┤ │
│ │ Puerto: 7860 │────→│ Puerto: 5000 │ │
│ │ Gradio UI │ │ MLflow Tracking UI │ │
│ │ (Python 3.10) │ │ (Python 3.10) │ │
│ └──────────────────────┘ └──────────────────────┘ │
│ ↓ │
│ Volumen: mlflow_data │
│ (/mlflow/mlruns) │
│ │
└─────────────────────────────────────────────────────────┘

text

## 🚀 Inicio Rápido

### Requisitos
- Docker 20.10+
- Docker Hub account (para publicación)
- Google Gemini API key ([obtener aquí](https://ai.google.dev/))

### Paso 1: Clonar el repositorio

git clone https://github.com/C-Ford17/Laboratorio-MLFLOW-with-Docker.git
cd Laboratorio-MLFLOW-with-Docker

text

### Paso 2: Crear archivo `.env`

echo "GOOGLE_API_KEY=tu_clave_gemini_aqui" > .env


**⚠️ IMPORTANTE:** Nunca commitear `.env` a Git. Ya está en `.gitignore`.

### Paso 3: Ejecutar con Docker (Sin docker-compose)

#### A. Crear red
docker network create traductor-network

#### B. Levantar MLflow
docker build -f Dockerfile.mlflow -t mlflow-server:latest .

docker run -d
--name mlflow-server
--network traductor-network
-p 5000:5000
-v mlflow_data:/mlflow/mlruns
-e MLFLOW_DISABLE_HOST_HEADER_VALIDATION=true
mlflow-server:latest

#### C. Construir imagen de la app
docker build -t traductor-app:1.0.0 .

#### D. Ejecutar la app
docker run -d
--name traductor-app
--network traductor-network
-p 7860:7860
-e GOOGLE_API_KEY=$(cat .env | grep GOOGLE_API_KEY | cut -d '=' -f 2)
-e MLFLOW_TRACKING_URI=http://mlflow-server:5000
traductor-app:1.0.0

#### E. Acceder
- **Gradio UI:** http://localhost:7860
- **MLflow Dashboard:** http://localhost:5000

## 📦 Publicación en Docker Hub

### Paso 1: Login
docker login

Ingresar usuario y contraseña

### Paso 2: Taggear imagen
docker tag traductor-app:1.0.0 ford17/traductor-genai:1.0.0
docker tag traductor-app:1.0.0 ford17/traductor-genai:latest

### Paso 3: Push

docker push ford17/traductor-genai:1.0.0
docker push ford17/traductor-genai:latest

Verificar en: https://hub.docker.com/r/ford17/traductor-genai

## 🌍 Ejecución Remota (Desde Docker Hub)

### Opción 1: Misma máquina (simular remoto)

Limpiar todo
docker stop mlflow-server traductor-app 2>/dev/null
docker rm mlflow-server traductor-app 2>/dev/null
docker rmi mlflow-server:latest traductor-app:1.0.0 2>/dev/null
docker volume rm mlflow_data 2>/dev/null
docker network rm traductor-network 2>/dev/null

Crear red
docker network create traductor-network

MLflow
docker build -f Dockerfile.mlflow -t mlflow-server:latest .
docker run -d
--name mlflow-server
--network traductor-network
-p 5000:5000
-v mlflow_data:/mlflow/mlruns
-e MLFLOW_DISABLE_HOST_HEADER_VALIDATION=true
mlflow-server:latest

sleep 10

### App desde Docker Hub
docker pull ford17/traductor-genai:1.0.0

docker run -d
--name traductor-app
--network traductor-network
-p 7860:7860
-e GOOGLE_API_KEY=tu_clave_aqui
-e MLFLOW_TRACKING_URI=http://mlflow-server:5000
ford17/traductor-genai:1.0.0

sleep 5

Verificar
docker ps
docker logs traductor-app

### Opción 2: Otra máquina
En máquina remota
docker pull ford17/traductor-genai:1.0.0
docker network create traductor-network

Levantar MLflow en máquina remota (o usar remoto)
docker run -d --name mlflow-server --network traductor-network -p 5000:5000 -v mlflow_data:/mlflow/mlruns mlflow-server:latest

Ejecutar app
docker run -d
--name traductor-app
--network traductor-network
-p 7860:7860
-e GOOGLE_API_KEY=tu_clave
-e MLFLOW_TRACKING_URI=http://mlflow-server:5000
ford17/traductor-genai:1.0.0


## 📊 Datos Registrados en MLflow

Cada traducción registra:

**Parámetros:**
- `idioma_objetivo`: Idioma seleccionado
- `modelo`: gemini-2.5-flash
- `temperatura`: 0.1
- `prompt_hash`: Hash del texto original
- `len_texto_original`: Longitud del texto

**Métricas:**
- `latency_ms`: Tiempo de respuesta (ms)
- `len_response`: Caracteres de la traducción
- `tokens_aprox`: Tokens aproximados

**Artifacts:**
- `traduccion.txt`: Pareja original/traducción

## 🛠️ Comandos Útiles

Ver contenedores corriendo
docker ps

Ver logs
docker logs -f traductor-app
docker logs -f mlflow-server

Detener contenedores
docker stop traductor-app mlflow-server

Eliminar contenedores
docker rm traductor-app mlflow-server

Eliminar volumen
docker volume rm mlflow_data

Eliminar red
docker network rm traductor-network

Limpiar todo
docker system prune -a


## 📈 Observaciones de Rendimiento

- **Latencia promedio:** 1.3-1.5 segundos
- **Calidad de traducción:** Excelente (Gemini 2.5-flash)
- **Tamaño imagen:** ~1.2GB (python:3.10-slim + deps)
- **Memoria RAM:** ~500MB por contenedor
- **Almacenamiento MLflow:** ~10KB por run

## 📁 Estructura del Proyecto

Laboratorio-MLFLOW-with-Docker/
├── app.py # Código principal (Gradio + MLflow)
├── Dockerfile # Imagen app
├── Dockerfile.mlflow # Imagen MLflow
├── docker-compose.yml # Orquestación (referencia)
├── requirements.txt # Dependencias Python
├── .env # Variables de entorno (NO commitear)
├── .gitignore # Archivos a ignorar
├── README.md # Este archivo
├── DOCUMENTACION.md # Documentación técnica
└── mlruns/ # Datos MLflow (generado)


## 🔐 Seguridad

- ✅ API key pasada como variable de entorno
- ✅ `.env` en `.gitignore`
- ✅ No hay credenciales en imágenes
- ✅ Volúmenes Docker con datos persistentes

## 📝 Problemas Comunes

### "Connection refused" en MLflow
→ Esperar 10+ segundos a que MLflow inicie

### "Invalid Host header" en MLflow
→ Variable `MLFLOW_DISABLE_HOST_HEADER_VALIDATION=true` no configurada

### Archivo `.txt` no aparece en MLflow
→ Verificar que el volumen está compartido correctamente

### Docker Hub push lento
→ Normal para imágenes >1GB. Paciencia o reducir tamaño con multi-stage build

## 📚 Referencias

- [Gradio Docs](https://www.gradio.app/)
- [MLflow Tracking](https://mlflow.org/docs/latest/tracking.html)
- [Docker Compose](https://docs.docker.com/compose/)
- [Google Gemini API](https://ai.google.dev/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)


## 📄 Licencia

Este proyecto es de código abierto bajo licencia MIT.

---

**Última actualización:** Noviembre 2, 2025
