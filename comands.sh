# Crear red
docker network create traductor-network

# Construir imagen MLflow
docker build -f Dockerfile.mlflow -t mlflow-server:latest .

# Ejecutar MLflow
docker run -d `
  --name mlflow-server `
  --network traductor-network `
  -p 5000:5000 `
  -v mlflow_data:/mlflow/mlruns `
  -e MLFLOW_DISABLE_HOST_HEADER_VALIDATION=true `
  mlflow-server:latest

# Construir imagen App
docker build -t traductor-app:1.0.0 .

# Ejecutar App
docker run -d `
  --name traductor-app `
  --network traductor-network `
  -p 7860:7860 `
  -e GOOGLE_API_KEY=tu_clave_aqui `
  -e MLFLOW_TRACKING_URI=http://mlflow-server:5000 `
  traductor-app:1.0.0
