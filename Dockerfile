# Use official lightweight Python image.
FROM python:3.11-slim

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

# Install production dependencies.
RUN pip install --no-cache-dir -r requirements.txt

# Run the web service on container startup.
# Cloud Run expects the app to listen on the port defined by the PORT environment variable.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
