# Use a slim base image for smaller size
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app

# Copy requirements first for Docker layer caching optimization
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Copy the application code
COPY ./app /app/app

# Expose the port Uvicorn runs on
EXPOSE 8000

# Command to run the application using Uvicorn (production ready)
CMD ["uvicorn", "app.app.main:app", "--host", "0.0.0.0", "--port", "8000"]


