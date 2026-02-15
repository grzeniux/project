# Dockerfile
FROM python:3.9-slim

# Create a non-root user
RUN useradd -ms /bin/bash appuser
WORKDIR /home/appuser/app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Change ownership of the app directory
RUN chown -R appuser:appuser /home/appuser/app

# Switch to the non-root user
USER appuser

# Command to run the application
CMD ["python", "main.py"]
