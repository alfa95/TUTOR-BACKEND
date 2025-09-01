"""
Arize Phoenix Integration Service for LLM Observability

This service integrates Arize Phoenix for comprehensive LLM monitoring:
- Request/response logging
- Performance metrics
- Quality evaluation
- A/B testing support
- Real-time monitoring
"""

import time
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

try:
    import phoenix as px
    from phoenix.otel import register
    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk import trace as trace_sdk
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    PHOENIX_AVAILABLE = True
    PHOENIX_TRACING_AVAILABLE = True
    
except ImportError as e:
    PHOENIX_AVAILABLE = False
    PHOENIX_TRACING_AVAILABLE = False
    logging.warning(f"Arize Phoenix not available: {e}")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PhoenixIntegrationService:
    """
    Service for integrating Arize Phoenix with quiz-detail endpoint
    """
    
    def __init__(self, port: int = 6006, auto_start: bool = True):
        self.port = port
        self.auto_start = auto_start
        self.phoenix_available = PHOENIX_AVAILABLE
        self.session = None
        
        if self.phoenix_available:
            self._initialize_phoenix()
            if self.auto_start:
                self._auto_start_phoenix()
        else:
            logger.warning("Phoenix not available. Using fallback logging.")
    
    def _initialize_phoenix(self):
        """Initialize Phoenix session and configuration"""
        try:
            # Set up OpenTelemetry tracing to send to Phoenix
            # Use default Phoenix gRPC endpoint (port 4317)
            tracer_provider = register(
                project_name="tutor-backend-quiz-detail",
            )
            self.tracer = trace.get_tracer("tutor-backend-quiz-detail")
            
            # Store tracer provider to manually flush spans
            self.tracer_provider = tracer_provider
            
            logger.info(f"✅ Phoenix tracing initialized for port {self.port}")
            
        except Exception as e:
            logger.error(f"❌ Phoenix initialization failed: {e}")
            self.phoenix_available = False
            self.tracer = None
            self.tracer_provider = None
    
    def _auto_start_phoenix(self):
        """Auto-start Phoenix server on initialization"""
        try:
            # Check if Phoenix is already running
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', self.port))
            sock.close()
            
            if result == 0:
                logger.info(f"✅ Phoenix already running on port {self.port}")
                return
            
            # Start Phoenix server (newer API doesn't have open_browser parameter)
            logger.info(f"🚀 Starting Phoenix server on port {self.port}...")
            self.session = px.launch_app(port=self.port)
            logger.info(f"✅ Phoenix server started successfully!")
            logger.info(f"📊 Access Phoenix UI at: http://localhost:{self.port}")
            
            # Wait a moment for Phoenix to fully start
            import time
            time.sleep(2)
            
        except Exception as e:
            logger.warning(f"⚠️ Phoenix auto-start failed: {e}")
            logger.info("💡 Phoenix will still log traces, but UI won't be available")
            logger.info("💡 You can start Phoenix manually with: phoenix serve")
            self.session = None
    
    def log_quiz_detail_request(
        self,
        query: str,
        use_llm: bool,
        enable_reranking: bool,
        reranking_strategy: str,
        enable_evaluation: bool,
        ground_truth: Optional[str] = None
    ) -> str:
        """
        Log quiz-detail request with Phoenix tracing
        
        Returns:
            trace_id: Unique identifier for this request
        """
        if not self.phoenix_available or not self.tracer:
            return f"phoenix_unavailable_{int(time.time())}"
        
        try:
            # Create trace for the entire request
            trace_id = f"quiz_detail_{int(time.time() * 1000)}"
            
            with self.tracer.start_as_current_span("quiz_detail_request") as span:
                # Set span attributes
                span.set_attribute("endpoint", "quiz-detail")
                span.set_attribute("query", query[:100])  # Truncate long queries
                span.set_attribute("use_llm", use_llm)
                span.set_attribute("enable_reranking", enable_reranking)
                span.set_attribute("reranking_strategy", reranking_strategy)
                span.set_attribute("enable_evaluation", enable_evaluation)
                span.set_attribute("ground_truth_provided", ground_truth is not None)
                span.set_attribute("trace_id", trace_id)
                
                logger.info(f"🔍 Phoenix trace started: {trace_id}")
                
            return trace_id
                
        except Exception as e:
            logger.error(f"❌ Phoenix logging failed: {e}")
            return f"phoenix_error_{int(time.time())}"
    
    def log_search_results(
        self,
        trace_id: str,
        search_results: List[Dict],
        search_time: float,
        reranking_applied: bool
    ):
        """Log search results and performance metrics"""
        if not self.phoenix_available or not self.tracer:
            return
        
        try:
            with self.tracer.start_as_current_span("search_results") as span:
                # Set span attributes
                span.set_attribute("operation", "internet_search")
                span.set_attribute("results_count", len(search_results))
                span.set_attribute("search_time_ms", search_time * 1000)
                span.set_attribute("reranking_applied", reranking_applied)
                span.set_attribute("trace_id", trace_id)
                
                # Log individual search results as events
                for i, result in enumerate(search_results[:3]):  # Log first 3 results
                    span.add_event(
                        f"search_result_{i+1}",
                        {
                            "title": result.get("title", "No title")[:100],
                            "position": result.get("position", i+1),
                            "link": result.get("link", "")[:100]
                        }
                    )
                
                logger.info(f"🔍 Search results logged to Phoenix: {len(search_results)} results")
                
        except Exception as e:
            logger.error(f"❌ Phoenix search logging failed: {e}")
    
    def log_llm_enhancement(
        self,
        trace_id: str,
        query: str,
        search_results: List[Dict],
        llm_summary: str,
        llm_time: float,
        model_used: str
    ):
        """Log LLM enhancement details"""
        if not self.phoenix_available or not self.tracer:
            return
        
        try:
            with self.tracer.start_as_current_span("llm_enhancement") as span:
                # Set LLM enhancement attributes
                span.set_attribute("operation", "llm_enhancement")
                span.set_attribute("query", query[:100])  # Truncate long queries
                span.set_attribute("llm_time_ms", llm_time * 1000)
                span.set_attribute("model_used", model_used)
                span.set_attribute("summary_length", len(llm_summary))
                span.set_attribute("context_results", len(search_results))
                span.set_attribute("trace_id", trace_id)
                
                # Log LLM summary quality metrics as events
                span.add_event(
                    "llm_summary_metrics",
                    {
                        "summary_length": len(llm_summary),
                        "word_count": len(llm_summary.split()),
                        "has_analytical_content": any(word in llm_summary.lower() 
                                                    for word in ['because', 'therefore', 'however', 'theme']),
                        "grounding_indicator": "llm_enhanced"
                    }
                )
                
                logger.info(f"🤖 LLM enhancement logged to Phoenix: {model_used}")
                
        except Exception as e:
            logger.error(f"❌ Phoenix LLM logging failed: {e}")
    
    def log_ragas_evaluation(
        self,
        trace_id: str,
        evaluation_result: Dict,
        evaluation_time: float
    ):
        """Log RAGAS evaluation results"""
        if not self.phoenix_available or not self.tracer:
            return
        
        try:
            with self.tracer.start_as_current_span("ragas_evaluation") as span:
                # Set evaluation attributes
                span.set_attribute("operation", "ragas_evaluation")
                span.set_attribute("evaluation_time_ms", evaluation_time * 1000)
                span.set_attribute("trace_id", trace_id)
                
                # Get metrics from evaluation result
                if hasattr(evaluation_result, 'metrics'):
                    metrics = evaluation_result.metrics
                    span.set_attribute("context_precision", metrics.context_precision)
                    span.set_attribute("faithfulness", metrics.faithfulness)
                    span.set_attribute("answer_correctness", metrics.answer_correctness)
                    span.set_attribute("context_relevancy", metrics.context_relevancy)
                    span.set_attribute("overall_score", metrics.overall_score)
                    span.set_attribute("evaluation_method", getattr(metrics, 'metadata', {}).get('evaluation_method', 'unknown'))
                
                logger.info(f"📊 RAGAS evaluation logged to Phoenix")
                
        except Exception as e:
            logger.error(f"❌ Phoenix evaluation logging failed: {e}")
    
    def log_request_completion(
        self,
        trace_id: str,
        total_time: float,
        success: bool,
        error_message: Optional[str] = None
    ):
        """Log request completion and overall metrics"""
        if not self.phoenix_available or not self.tracer:
            return
        
        try:
            with self.tracer.start_as_current_span("request_completion") as span:
                span.set_attribute("operation", "request_completion")
                span.set_attribute("total_time_ms", total_time * 1000)
                span.set_attribute("success", success)
                span.set_attribute("trace_id", trace_id)
                
                if error_message:
                    span.set_attribute("error_message", error_message)
                
                if success:
                    logger.info(f"✅ Request completed successfully: {trace_id}")
                else:
                    logger.error(f"❌ Request failed: {trace_id} - {error_message}")
            
            # Force flush spans to ensure they're sent to Phoenix
            self._flush_spans()
                
        except Exception as e:
            logger.error(f"❌ Phoenix completion logging failed: {e}")
    
    def _flush_spans(self):
        """Force flush spans to Phoenix"""
        try:
            if self.tracer_provider:
                # Force flush all spans
                self.tracer_provider.force_flush(timeout_millis=5000)
                logger.debug("🔄 Spans flushed to Phoenix")
        except Exception as e:
            logger.error(f"❌ Failed to flush spans: {e}")
    
    def get_phoenix_url(self) -> str:
        """Get Phoenix UI URL"""
        return f"http://localhost:{self.port}"
    
    def start_phoenix_server(self):
        """Start Phoenix server on specified port"""
        if not self.phoenix_available:
            logger.warning("Phoenix not available. Cannot start server.")
            return False
        
        try:
            # Check if Phoenix is already running on the port
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', self.port))
            sock.close()
            
            if result == 0:
                logger.info(f"Phoenix already running on port {self.port}")
                return True
            
            # Start Phoenix server (newer API doesn't have open_browser parameter)
            self.session = px.launch_app(port=self.port)
            logger.info(f"🚀 Phoenix server started on port {self.port}")
            logger.info(f"📊 Access Phoenix UI at: {self.get_phoenix_url()}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start Phoenix server: {e}")
            logger.info("💡 Try starting Phoenix manually: phoenix serve")
            return False
    
    def log_custom_event(
        self,
        trace_id: str,
        event_name: str,
        attributes: Dict[str, Any]
    ):
        """Log custom event to Phoenix"""
        if not self.phoenix_available:
            return
        
        try:
            with span(
                f"{trace_id}_{event_name}",
                kind=SpanKind.INTERNAL,
                attributes=attributes
            ) as span:
                span.set_status(SpanStatusCode.OK)
                logger.info(f"📝 Custom event logged: {event_name}")
                
        except Exception as e:
            logger.error(f"❌ Phoenix custom event logging failed: {e}")


# Global instance
phoenix_integration_service = PhoenixIntegrationService(port=6006, auto_start=True) 