# Step 1: Use an official Gradle image to build the application
FROM gradle:8.3.0-jdk17 AS build

# Set the working directory inside the container
WORKDIR /app

# Copy the entire project to the container
COPY . .

# Build the application
RUN gradle clean bootJar

# Step 2: Use a lightweight JDK image for running the app
FROM openjdk:17-jdk-slim

# Set the working directory for the runtime container
WORKDIR /app

# Copy the Grafana OpenTelemetry Java agent from the host
COPY grafana-opentelemetry-java.jar grafana-opentelemetry-java.jar

# Copy the JAR file from the build stage
COPY --from=build /app/build/libs/*.jar app.jar

# Expose the port the application runs on
EXPOSE 8080

# Set environment variables for OpenTelemetry
ENV OTEL_RESOURCE_ATTRIBUTES="service.name=airlines,service.namespace=pov-sim,deployment.environment=dev"
ENV OTEL_EXPORTER_OTLP_ENDPOINT="https://otlp-gateway-prod-gb-south-1.grafana.net/otlp"
ENV OTEL_EXPORTER_OTLP_HEADERS="Authorization=Basic MTI4OTk2NDpnbGNfZXlKdklqb2lNVFEwT1RVNE15SXNJbTRpT2lKemRHRmpheTB4TWpnNU9UWTBMVzkwYkhBdGQzSnBkR1V0Y0c5MkxYTnBiUzFrWldKMVoyZHBibWNpTENKcklqb2lOelZaTUVsQk9VdHBNVEpuWkRSNU5tbFBNRkJSVjBVMElpd2liU0k2ZXlKeUlqb2ljSEp2WkMxbllpMXpiM1YwYUMweEluMTk="
ENV OTEL_EXPORTER_OTLP_PROTOCOL="http/protobuf"
ENV OTEL_TRACES_EXPORTER="otlp"
ENV OTEL_METRICS_EXPORTER="otlp"
ENV OTEL_LOGS_EXPORTER="otlp"
ENV OTEL_LOG_LEVEL="DEBUG"

# Set the command to run the application with OpenTelemetry instrumentation
ENTRYPOINT ["java", "-javaagent:grafana-opentelemetry-java.jar", "-jar", "app.jar"]
