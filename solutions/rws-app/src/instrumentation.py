import functools
import json
from datetime import datetime
from typing import Any, Callable
import inspect
import os
import atexit
from dotenv import load_dotenv

from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter, AzureMonitorMetricExporter
from opentelemetry import trace, metrics
from opentelemetry.trace import Status, StatusCode
from opentelemetry.metrics import Observation, CallbackOptions
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

# Load environment variables
load_dotenv()

# Initialize Azure Monitor OpenTelemetry
connection_string = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
if not connection_string:
    raise ValueError("APPLICATIONINSIGHTS_CONNECTION_STRING must be set in environment variables")

# Create and configure trace provider
trace_exporter = AzureMonitorTraceExporter(
    connection_string=connection_string
)
trace_provider = TracerProvider(
    resource=Resource.create({
        "service.name": "rws-agent-service",
        "service.namespace": "rws-agents",
        "service.version": "1.0.0"
    })
)
trace_provider.add_span_processor(
    BatchSpanProcessor(trace_exporter)
)
trace.set_tracer_provider(trace_provider)

# Create and configure metrics provider
metric_exporter = AzureMonitorMetricExporter(
    connection_string=connection_string
)
metric_reader = PeriodicExportingMetricReader(metric_exporter)
metric_provider = MeterProvider(
    resource=Resource.create({
        "service.name": "rws-agent-service",
        "service.namespace": "rws-agents",
        "service.version": "1.0.0"
    }),
    metric_readers=[metric_reader]
)
metrics.set_meter_provider(metric_provider)

# Register cleanup handler
def cleanup_telemetry():
    """Ensure proper shutdown of telemetry pipeline"""
    trace_provider.shutdown()
    metric_provider.shutdown()

atexit.register(cleanup_telemetry)

# Get tracer and meter
tracer = trace.get_tracer(__name__)
meter = metrics.get_meter(__name__)

# Create metrics
agent_counter = meter.create_counter(
    "agent.calls",
    description="Number of agent function calls",
    unit="1"
)

agent_duration = meter.create_histogram(
    "agent.duration",
    description="Duration of agent operations",
    unit="s"
)

# Create observable metrics for real-time monitoring
def get_active_sessions_callback(options: CallbackOptions):
    count = len(AgentActionContext.active_sessions)
    return [Observation(count, {})]

active_sessions = meter.create_observable_gauge(
    "agent.active_sessions",
    callbacks=[get_active_sessions_callback],
    description="Number of active agent sessions",
    unit="1"
)

def track_agent_action(func: Callable) -> Callable:
    """
    Decorator to record agent actions in Azure Application Insights.
    Captures:
    - Agent name
    - Function name
    - Parameters
    - Timestamp
    - Call stack
    - Duration
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Get agent instance (self) if it's a method
        agent_instance = args[0] if args else None
        agent_name = getattr(agent_instance, 'name', 'Unknown') if hasattr(agent_instance, 'name') else 'Unknown'

        # Get function parameters
        params = {}
        try:
            # Get the actual parameter names from the function signature
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            # Convert parameters to a serializable format
            for key, value in bound_args.arguments.items():
                if key == 'self':
                    continue
                # Convert complex objects to string representation
                if isinstance(value, (dict, list)):
                    params[key] = json.dumps(value)
                else:
                    params[key] = str(value)
        except Exception as e:
            params['error'] = f"Failed to capture parameters: {str(e)}"

        # Get call stack for context (excluding the decorator frames)
        call_stack = []
        for frame in inspect.stack()[1:]:
            if frame.function != wrapper.__name__:
                call_stack.append({
                    'file': frame.filename,
                    'function': frame.function,
                    'line': frame.lineno
                })

        # Create span attributes
        attributes = {
            "agent.name": agent_name,
            "function.name": func.__name__,
            "parameters": json.dumps(params),
            "call_stack": json.dumps(call_stack[:3])
        }

        # Start a new span for this operation
        with tracer.start_as_current_span(
            f"agent_action.{func.__name__}",
            attributes=attributes
        ) as span:
            try:
                # Record the agent call
                agent_counter.add(1, attributes)
                
                # Execute the function and time it
                start_time = datetime.now()
                result = func(*args, **kwargs)
                duration = (datetime.now() - start_time).total_seconds()
                
                # Record the duration
                agent_duration.record(duration, attributes)
                
                # Set span status to success
                span.set_status(Status(StatusCode.OK))
                
                return result
                
            except Exception as e:
                # Set span status to error with description
                span.set_status(
                    Status(StatusCode.ERROR, str(e))
                )
                # Record the error
                span.record_exception(e)
                raise
        
        return result

    return wrapper

class AgentActionContext:
    """Context manager to track agent session information"""
    
    # Class variable to track active sessions
    active_sessions = set()
    
    def __init__(self, agent_name: str, session_id: str = None):
        self.agent_name = agent_name
        self.session_id = session_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.start_time = None
        self.span = None

    def __enter__(self):
        self.start_time = datetime.now()
        
        # Add session to active sessions
        AgentActionContext.active_sessions.add(self.session_id)
        
        # Create span attributes
        attributes = {
            "agent.name": self.agent_name,
            "session.id": self.session_id
        }
        
        # Start a new span for this session
        self.span = tracer.start_span(
            f"agent_session.{self.agent_name}",
            attributes=attributes
        )
        self.span.set_attribute("session.start_time", self.start_time.isoformat())
        
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            end_time = datetime.now()
            duration = (end_time - self.start_time).total_seconds()
            
            if self.span:
                # Add duration to span
                self.span.set_attribute("session.duration", duration)
                
                if exc_type:
                    # Record error information
                    self.span.set_status(
                        Status(StatusCode.ERROR, str(exc_val))
                    )
                    self.span.record_exception(exc_val)
                else:
                    self.span.set_status(Status(StatusCode.OK))
                
                # End the span
                self.span.end()
        finally:
            # Remove session from active sessions
            AgentActionContext.active_sessions.discard(self.session_id)
