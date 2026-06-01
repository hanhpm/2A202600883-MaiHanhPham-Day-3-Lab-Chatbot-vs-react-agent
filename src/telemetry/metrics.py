import time
from typing import Dict, Any, List
from src.telemetry.logger import logger
import json


class PerformanceTracker:
    """
    Tracking industry-standard metrics for LLMs and agents.
    """
    def __init__(self):
        self.session_metrics = []

    def track_request(self, provider: str, model: str, usage: Dict[str, int], latency_ms: int):
        """
        Logs a single request metric to our telemetry.
        """
        metric = {
            "provider": provider,
            "model": model,
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0),
            "latency_ms": latency_ms,
            "cost_estimate": self._calculate_cost(model, usage)
        }
        self.session_metrics.append(metric)
        logger.log_event("LLM_METRIC", metric)

    def _calculate_cost(self, model: str, usage: Dict[str, int]) -> float:
        """
        Calculate estimated pricing based on token usage.
        For mock model, use simplified pricing.
        """
        total_tokens = usage.get("total_tokens", 0)
        # Simplified: 1000 tokens ≈ 0.01 cost unit
        return (total_tokens / 1000) * 0.01

    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics from all logged metrics.
        """
        if not self.session_metrics:
            return {"status": "No metrics available"}

        total_tokens = sum(m["total_tokens"] for m in self.session_metrics)
        total_cost = sum(m["cost_estimate"] for m in self.session_metrics)
        avg_latency = sum(m["latency_ms"] for m in self.session_metrics) / len(self.session_metrics)
        
        return {
            "total_requests": len(self.session_metrics),
            "total_tokens": total_tokens,
            "total_cost_estimate": round(total_cost, 4),
            "avg_latency_ms": round(avg_latency, 2),
            "max_latency_ms": max(m["latency_ms"] for m in self.session_metrics),
            "min_latency_ms": min(m["latency_ms"] for m in self.session_metrics),
        }

    def export_metrics_summary(self, output_file: str = "metrics_summary.json"):
        """
        Export metrics summary to a JSON file.
        """
        summary = self.get_summary()
        with open(output_file, "w") as f:
            json.dump(summary, f, indent=2)
        logger.log_event("METRICS_EXPORTED", {"file": output_file})


# Global tracker instance
tracker = PerformanceTracker()
