# Use Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /harvest_service

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app source
COPY code/ ./code

# Set env variables
ENV PYTHONUNBUFFERED=1

# Run the harvester
CMD ["python", "main.py"]





FROM python:3.11

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy both harvest_service and mongo_db
COPY . .

# Run the harvester
CMD ["python", "main.py"]
