# Use an official Python runtime as a base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt
# Copy the rest of the application code
COPY . .

# Create non-privileged user
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser /app

# Expose the port Streamlit uses
EXPOSE 8501

# Run the Streamlit app
USER appuser
CMD ["streamlit", "run", "src/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
