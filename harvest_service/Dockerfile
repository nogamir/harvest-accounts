# Use Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /harvest_service

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Set env variables
ENV PYTHONUNBUFFERED=1

# Run the harvester
CMD ["python", "src/main.py"]
