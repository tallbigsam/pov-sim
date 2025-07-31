# Use the official Python 3.8 image as the base image
FROM python:3.8-slim-buster

# Set the working directory inside the container
WORKDIR /python-docker

# Copy the requirements file into the container
COPY requirements.txt requirements.txt

# Install the required dependencies (including OpenTelemetry)
RUN pip3 install -r requirements.txt

# Copy the rest of your application code into the container
COPY . .

# Run OpenTelemetry bootstrap to ensure instrumentation is set up
RUN python3 -m opentelemetry.instrumentation.bootstrap -a install

# Expose port 5001
EXPOSE 5001

# Set OpenTelemetry environment variables
ENV OTEL_RESOURCE_ATTRIBUTES="service.name=flights,service.namespace=pov-sim,deployment.environment=dev"
ENV OTEL_EXPORTER_OTLP_ENDPOINT="http://alloy:4317"
ENV OTEL_EXPORTER_OTLP_PROTOCOL="grpc"
ENV OTEL_TRACES_EXPORTER="otlp"
ENV OTEL_METRICS_EXPORTER="otlp"
ENV OTEL_LOGS_EXPORTER="otlp"
ENV OTEL_PYTHON_DISABLED_INSTRUMENTATIONS=""
ENV OTEL_PYTHON_LOG_CORRELATION="true"

# Specify the command to run your Flask app with OpenTelemetry instrumentation
CMD ["opentelemetry-instrument", "flask", "run", "--host=0.0.0.0", "--port=5001"]
