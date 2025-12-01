# Usar imagen base de Python
FROM python:3.10-slim

# Establecer directorio de trabajo
WORKDIR /app

# Copiar archivo de requisitos
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY app.py .

# Exponer el puerto de Gradio
EXPOSE 7860

# Establecer variables de entorno por defecto
ENV MLFLOW_TRACKING_URI=http://mlflow-server:5000
# Comando para ejecutar la app
CMD ["python", "app.py"]
