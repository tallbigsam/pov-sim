from flasgger import Swagger
from flask import Flask, jsonify, request
from flask_cors import CORS
from utils import get_random_int
import logging
import os
from opentelemetry import metrics
from opentelemetry.metrics import Counter

# Import OpenTelemetry logging components
from opentelemetry import _logs
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.flask import FlaskInstrumentor

# Import OpenTelemetry tracing components
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# OTEL Metrics 

from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

from opentelemetry.metrics import set_meter_provider

import sys


app = Flask(__name__)
Swagger(app)
CORS(app)

# Add HTTP request metrics
meter = metrics.get_meter(__name__)
request_counter = meter.create_counter(
    name="http_requests_total",
    description="Total number of HTTP requests",
    unit="1"
)

@app.before_request
def before_request():
    request_counter.add(1, {
        "method": request.method,
        "endpoint": request.endpoint or "unknown"
    })
    print(f"\n\nRequest counter: {request_counter}\n\n", flush=True)
    sys.stdout.flush()

FlaskInstrumentor.instrument_app(app)



exporter = OTLPMetricExporter()
reader = PeriodicExportingMetricReader(exporter)
provider = MeterProvider(metric_readers=[reader])

set_meter_provider(provider)

# Configure basic logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Manually configure OpenTelemetry logging
resource = Resource.create({
    "service.name": os.getenv('OTEL_SERVICE_NAME', 'flights'),
    "service.namespace": "pov-sim",
    "deployment.environment": "dev"
})

# Create OTLP log exporter
otlp_exporter = OTLPLogExporter(
    endpoint=os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT', 'http://alloy:4317'),
    insecure=True  # Since we're using HTTP not HTTPS
)

# Set up the logger provider
logger_provider = LoggerProvider(resource=resource)
logger_provider.add_log_record_processor(BatchLogRecordProcessor(otlp_exporter))
_logs.set_logger_provider(logger_provider)

# Set up tracing
trace_exporter = OTLPSpanExporter(
    endpoint=os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT', 'http://alloy:4317'),
    insecure=True
)

tracer_provider = TracerProvider(resource=resource)
tracer_provider.add_span_processor(BatchSpanProcessor(trace_exporter))
trace.set_tracer_provider(tracer_provider)

# Create the OpenTelemetry logging handler
otel_handler = LoggingHandler(level=logging.INFO, logger_provider=logger_provider)

# Add the OpenTelemetry handler to the root logger
root_logger = logging.getLogger()
root_logger.addHandler(otel_handler)

logger = logging.getLogger(__name__)

# Debug: Print OpenTelemetry configuration
logger.info("=== OpenTelemetry Configuration ===")
logger.info(f"OTEL_EXPORTER_OTLP_ENDPOINT: {os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT')}")
logger.info(f"OTEL_EXPORTER_OTLP_PROTOCOL: {os.getenv('OTEL_EXPORTER_OTLP_PROTOCOL')}")
logger.info(f"OTEL_LOGS_EXPORTER: {os.getenv('OTEL_LOGS_EXPORTER')}")
logger.info("=== End Configuration ===")

# Test log to see if it gets exported
logger.info("Flask app starting - this should appear in Alloy if OpenTelemetry is working!")

# Debug: Check what logging handlers are installed
logger.info(f"Root logger handlers: {[type(h).__name__ for h in root_logger.handlers]}")
logger.info(f"App logger handlers: {[type(h).__name__ for h in logger.handlers]}")

# Check if OpenTelemetry logging handler is present
otel_handlers = [h for h in root_logger.handlers if 'LoggingHandler' in type(h).__name__]
logger.info(f"OpenTelemetry logging handlers found: {len(otel_handlers)}")

@app.route('/health', methods=['GET'])
def health():
    """Health endpoint
    ---
    responses:
      200:
        description: Returns healthy
    """
    logger.info("Health check requested")
    return jsonify({"status": "healthy"}), 200

@app.route("/", methods=['GET'])
def home():
    """No-op home endpoint
    ---
    responses:
      200:
        description: Returns ok
    """
    return jsonify({"message": "ok"}), 200

@app.route("/flights/<airline>", methods=["GET"])
def get_flights(airline):
    """Get flights endpoint. Optionally, set raise to trigger an exception.
    ---
    parameters:
      - name: airline
        in: path
        type: string
        enum: ["AA", "UA", "DL"]
        required: true
      - name: raise
        in: query
        type: str
        enum: ["500"]
        required: false
    responses:
      200:
        description: Returns a list of flights for the selected airline
    """
    status_code = request.args.get("raise")
    if status_code:
      logger.error(f"Intentionally raising {status_code} error for airline: {airline}")
      raise Exception(f"Encountered {status_code} error") # pylint: disable=broad-exception-raised
    random_int = get_random_int(100, 999)
    logger.info(f"Generated flight {random_int} for airline {airline}")
    return jsonify({airline: [random_int]}), 200

@app.route("/flight", methods=["POST"])
def book_flight():
    """Book flights endpoint. Optionally, set raise to trigger an exception.
    ---
    parameters:
      - name: passenger_name
        in: query
        type: string
        enum: ["John Doe", "Jane Doe"]
        required: true
      - name: flight_num
        in: query
        type: string
        enum: ["101", "202", "303", "404", "505", "606"]
        required: true
      - name: raise
        in: query
        type: str
        enum: ["500"]
        required: false
    responses:
      200:
        description: Booked a flight for the selected passenger and flight_num
    """
    status_code = request.args.get("raise")
    if status_code:
      logger.error(f"Exception raised for booking flight {flight_num} for passenger {passenger_name}")
      raise Exception(f"Encountered {status_code} error") # pylint: disable=broad-exception-raised
    passenger_name = request.args.get("passenger_name")
    flight_num = request.args.get("flight_num")
    booking_id = get_random_int(100, 999)
    
    # todo: emit a custom metric which allows us to track the number of airline bookings. 


    return jsonify({"passenger_name": passenger_name, "flight_num": flight_num, "booking_id": booking_id}), 200

if __name__ == "__main__":
    app.run(debug=True, port=5001)
