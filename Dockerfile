FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir fastapi uvicorn pandas scikit-learn xgboost joblib

# Expose FastAPI port
EXPOSE 8000

# Run API
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]