#!/usr/bin/env python3
"""
Smart Model Router for alforaijboard
Selects the best free model for each task type.

Available free providers:
  - Gemini 2.5 Flash: 1500 req/day, 1M context — via Google AI Studio
  - Groq (GPT-OSS 120B, Llama 4 Scout): 14400 req/day — very fast
  - OpenRouter free models: 50-1000 req/day
  - Solar Pro 4 via Nous: orchestration & reasoning

Routing strategy (Arabic / English only):
  - Analysis / reasoning tasks: Solar Pro 4 or DeepSeek V4
  - Writing / summarization: Qwen3.6 or GPT-OSS 120B
  - Market / data tasks: Gemini 2.5 Flash (large context)
  - Code tasks: Qwen3-Coder or Solar Pro 4
  - Fast / fallback: Groq Llama 4 Scout
"""

import os
import json
import time
import logging
from typing import Optional, Dict, Any

# ---------------------------------------------------------------------------
# Model configuration
# ---------------------------------------------------------------------------
MODEL_CONFIG = {
    "gemini-flash": {
        "name": "Gemini 2.5 Flash",
        "provider": "google-ai-studio",
        "endpoint": "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent",
        "api_key_env": "GEMINI_API_KEY",
        "context_window": 1_000_000,
        "free_rpd": 1500,
        "best_for": ["market_analysis", "data_insights", "long_context", "report_generation"],
        "priority": 1,
        "request_format": "google",
    },
    "gpt-oss-120b": {
        "name": "GPT-OSS 120B",
        "provider": "groq",
        "endpoint": "https://api.groq.com/openai/v1/chat/completions",
        "model_id": "openai/gpt-oss-120b",
        "api_key_env": "GROQ_API_KEY",
        "context_window": 128_000,
        "free_rpd": 14400,
        "best_for": ["writing", "general", "fast_response"],
        "priority": 2,
    },
    "groq-llama": {
        "name": "Llama 4 Scout (via Groq)",
        "provider": "groq",
        "endpoint": "https://api.groq.com/openai/v1/chat/completions",
        "model_id": "meta-llama/llama-4-scout-17b-16e-instruct",
        "api_key_env": "GROQ_API_KEY",
        "context_window": 10_000_000,
        "free_rpd": 14400,
        "best_for": ["fast_response", "general", "fallback"],
        "priority": 2,
    },
    "mimo-v2.5-pro": {
        "name": "MiMo-V2.5-Pro",
        "provider": "openrouter",
        "endpoint": "https://openrouter.ai/api/v1/chat/completions",
        "model_id": "xai/mimo-v2.5-pro",
        "api_key_env": "OPENROUTER_API_KEY",
        "context_window": 1_000_000,
        "free_rpd": 1000,
        "best_for": ["agentic_tasks", "coding", "long_context"],
        "priority": 3,
        "note": "Requires OpenRouter balance",
    },
    "qwen-coder": {
        "name": "Qwen3-Coder",
        "provider": "openrouter",
        "endpoint": "https://openrouter.ai/api/v1/chat/completions",
        "model_id": "qwen/qwen3-coder-480b",
        "api_key_env": "OPENROUTER_API_KEY",
        "context_window": 1_000_000,
        "free_rpd": 1000,
        "best_for": ["code_generation", "code_analysis", "automation"],
        "priority": 3,
        "note": "Requires OpenRouter balance",
    },
    "solar-pro4": {
        "name": "Solar Pro 4 (via Nous)",
        "provider": "nous",
        "endpoint": "https://api.nousresearch.com/v1/chat/completions",
        "model_id": "solar-pro4",
        "api_key_env": "NOUS_API_KEY",
        "context_window": 128_000,
        "best_for": ["reasoning", "analysis", "orchestration"],
        "priority": 1,
    },
}

# ---------------------------------------------------------------------------
# Task -> model routing table
# ---------------------------------------------------------------------------
TASK_ROUTING = {
    "market_analysis": ["gemini-flash", "solar-pro4"],
    "opportunity_analysis": ["solar-pro4", "mimo-v2.5-pro", "gemini-flash"],
    "data_insights": ["gemini-flash", "solar-pro4"],
    "writing": ["gpt-oss-120b", "groq-llama"],
    "summarization": ["gemini-flash", "gpt-oss-120b"],
    "report_generation": ["gemini-flash"],
    "code_generation": ["qwen-coder", "solar-pro4"],
    "code_analysis": ["qwen-coder", "solar-pro4"],
    "recommendation": ["solar-pro4", "mimo-v2.5-pro", "gemini-flash"],
    "general": ["gpt-oss-120b", "groq-llama"],
    "fast": ["groq-llama", "gpt-oss-120b"],
    "fallback": ["groq-llama", "gpt-oss-120b"],
}

# ---------------------------------------------------------------------------
# Usage tracker (persisted to disk)
# ---------------------------------------------------------------------------
usage_tracker: Dict[str, int] = {}

class SmartRouter:
    """Selects the best available free model for a given task type."""

    def __init__(self, usage_file: str = None):
        self.usage_file = usage_file or os.path.join(
            os.path.dirname(os.path.abspath(__file__)), ".router-usage.json"
        )
        self._load_usage()

    def _load_usage(self):
        if os.path.exists(self.usage_file):
            try:
                with open(self.usage_file) as f:
                    self.usage = json.load(f)
            except Exception:
                self.usage = {}
        else:
            self.usage = {}

    def _save_usage(self):
        with open(self.usage_file, "w") as f:
            json.dump(self.usage, f, indent=2)

    def route(self, task_type: str, priority_high: bool = False, prefer_fast: bool = False) -> Optional[Dict[str, Any]]:
        """
        Pick the best model for *task_type*.

        Args:
            task_type: one of the keys in TASK_ROUTING.
            priority_high: prefer higher-quality models even if slower.
            prefer_fast: prefer faster models even if lower quality.

        Returns:
            Model configuration dict, or None if nothing is reachable.
        """
        candidates = TASK_ROUTING.get(task_type, TASK_ROUTING["general"])

        def score(model_key: str) -> tuple:
            config = MODEL_CONFIG[model_key]
            sp = config["priority"]
            has_key = bool(os.environ.get(config["api_key_env"]))
            if has_key:
                sp -= 10
            if priority_high and config["priority"] <= 2:
                sp -= 2
            if prefer_fast and config["priority"] >= 3:
                sp += 1
            return (sp, model_key)

        for model_key in sorted(candidates, key=score):
            config = MODEL_CONFIG[model_key]
            api_key = os.environ.get(config["api_key_env"])
            if api_key:
                return {
                    "model_key": model_key,
                    "name": config["name"],
                    "provider": config["provider"],
                    "endpoint": config["endpoint"],
                    "api_key_env": config["api_key_env"],
                    "model_id": config.get("model_id"),
                    "context_window": config["context_window"],
                    "use_fallback": False,
                    "request_format": config.get("request_format", "openai"),
                }

        # Last resort: Google AI Studio without key (trial mode)
        for model_key in TASK_ROUTING.get("fallback", TASK_ROUTING["fast"]):
            config = MODEL_CONFIG[model_key]
            if config["provider"] == "google-ai-studio":
                return {
                    "model_key": model_key,
                    "name": config["name"],
                    "provider": config["provider"],
                    "endpoint": config["endpoint"],
                    "api_key_env": config["api_key_env"],
                    "model_id": None,
                    "context_window": config["context_window"],
                    "use_fallback": True,
                    "note": "No key required (trial mode — may have limits)",
                }

        return None

    def log_usage(self, model_key: str, tokens: int = 0, success: bool = True):
        today = time.strftime("%Y-%m-%d")
        key = f"{model_key}:{today}"
        if key not in self.usage:
            self.usage[key] = {"requests": 0, "tokens": 0, "success": 0, "fail": 0}
        self.usage[key]["requests"] += 1
        self.usage[key]["tokens"] += tokens
        if success:
            self.usage[key]["success"] += 1
        else:
            self.usage[key]["fail"] += 1
        self._save_usage()

    def get_usage_report(self) -> Dict[str, Any]:
        """Daily + total usage report."""
        report = {"today": {}, "total": {}}
        today = time.strftime("%Y-%m-%d")
        for key, data in self.usage.items():
            model_key = key.split(":")[0]
            report["total"].setdefault(model_key, {"requests": 0, "tokens": 0, "success": 0, "fail": 0})
            report["total"][model_key]["requests"] += data["requests"]
            report["total"][model_key]["tokens"] += data["tokens"]
            report["total"][model_key]["success"] += data["success"]
            report["total"][model_key]["fail"] += data["fail"]
            if key.startswith(today):
                report["today"][model_key] = data
        return report


# ---------------------------------------------------------------------------
# Actual model call
# ---------------------------------------------------------------------------
def call_model(router: SmartRouter, task_type: str, messages: list, **kwargs) -> Optional[Dict[str, Any]]:
    """
    Call the model selected by *router* for *task_type*.

    Returns a dict with 'model_used', 'content', 'usage', 'raw',
    or None on failure.
    """
    routing = router.route(task_type, **kwargs.pop("routing_options", {}))
    if not routing:
        logging.warning("No model available for task: %s", task_type)
        return None

    model_key = routing["model_key"]
    provider = routing["provider"]
    api_key_env = routing["api_key_env"]
    api_key = os.environ.get(api_key_env)
    request_format = routing.get("request_format", "openai")

    if not api_key and not routing.get("use_fallback"):
        logging.warning("No API key for model %s (%s)", model_key, api_key_env)
        return None

    endpoint = routing["endpoint"]
    model_id = routing.get("model_id")
    headers = {"Content-Type": "application/json"}

    if api_key:
        if provider == "google-ai-studio":
            headers["x-goog-api-key"] = api_key
        elif provider in ("groq", "openrouter", "deepseek"):
            headers["Authorization"] = f"Bearer {api_key}"

    if request_format == "google":
        system_parts = []
        user_contents = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system":
                system_parts.append(content)
            else:
                mapped_role = "model" if role == "assistant" else role
                user_contents.append({"role": mapped_role, "parts": [{"text": content}]})
        payload = {"contents": user_contents}
        if system_parts:
            payload["systemInstruction"] = {"parts": [{"text": "\n\n".join(system_parts)}]}
        params = {k: v for k, v in kwargs.items() if k in ("temperature", "top_p")}
        payload.update(params)
    else:
        payload = {
            "messages": messages,
            **{k: v for k, v in kwargs.items() if k in ("temperature", "max_tokens", "top_p", "frequency_penalty")},
        }
        if model_id:
            payload["model"] = model_id

    try:
        import requests
        resp = requests.post(endpoint, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        if provider == "google-ai-studio":
            content = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
        else:
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        input_tokens = sum(len(m.get("content", "")) for m in messages) // 4
        output_tokens = len(content) // 4
        router.log_usage(model_key, tokens=input_tokens + output_tokens, success=True)
        return {"model_used": model_key, "content": content, "usage": {"input_tokens": input_tokens, "output_tokens": output_tokens}, "raw": data}
    except Exception as exc:
        logging.error("Failed to call %s: %s", model_key, exc)
        router.log_usage(model_key, success=False)
        return None


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    router = SmartRouter()

    tasks = [
        ("market_analysis", "Real estate market analysis"),
        ("opportunity_analysis", "Lead opportunity analysis"),
        ("writing", "Write a report"),
        ("summarization", "Summarize meeting"),
        ("code_generation", "Write Python code"),
        ("code_analysis", "Review Python code"),
        ("general", "General conversation"),
        ("fast", "Fast response needed"),
    ]

    print("=== Smart Model Router Test ===")
    for task_type, description in tasks:
        routing = router.route(task_type)
        status = "OK" if routing else "NONE"
        key_status = "HAS_KEY" if (routing and os.environ.get(routing["api_key_env"])) else "NO_KEY"
        model_name = routing["name"] if routing else "NONE"
        print(f"{status}  {task_type:25s} -> {model_name:30s}  [{key_status}]")

    print()
    print("=== Current Usage Report ===")
    print(json.dumps(router.get_usage_report(), indent=2, ensure_ascii=False))
