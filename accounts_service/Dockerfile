# Use Python image
FROM python:3.11

# Set working directory
WORKDIR /accounts_service

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Set env variables
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8000

# Run FastAPI with Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

