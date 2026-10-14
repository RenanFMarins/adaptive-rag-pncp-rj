import logging
import unittest
from unittest.mock import patch

import httpx2 as httpx
from openai import DefaultHttpxClient, OpenAI

import llm_ecoa
from app.core.config import settings
from app.core.logging import _perf_run_id


def _response(content="resultado"):
    return {
        "id": "chatcmpl-test",
        "object": "chat.completion",
        "created": 1,
        "model": "test-model",
        "choices": [{
            "index": 0,
            "message": {"role": "assistant", "content": content},
            "finish_reason": "stop",
        }],
        "usage": {"prompt_tokens": 3, "completion_tokens": 2, "total_tokens": 5},
    }


def _client(handler):
    transport = httpx.MockTransport(handler)
    http_client = DefaultHttpxClient(transport=transport)
    return OpenAI(
        api_key="test-secret-key",
        base_url="https://provider.invalid/v1",
        http_client=http_client,
        max_retries=0,
    )


class AnalyzerFallbackTests(unittest.TestCase):
    def tearDown(self):
        llm_ecoa._analyzer_ecoa_client.cache_clear()
        llm_ecoa._analyzer_openai_client.cache_clear()

    def test_disabled_preserves_original_analyzer_path(self):
        with patch.object(settings, "analyzer_openai_fallback_enabled", False), \
                patch.object(llm_ecoa, "gerar_resposta", return_value="original") as original, \
                patch.object(llm_ecoa, "_analyzer_ecoa_client") as ecoa:
            self.assertEqual(llm_ecoa.gerar_resposta_analyzer("pergunta"), "original")
        original.assert_called_once_with("pergunta")
        ecoa.assert_not_called()

    def test_primary_success_does_not_call_openai(self):
        calls = []

        def primary(request):
            calls.append("ecoa")
            return httpx.Response(200, json=_response(), request=request)

        with patch.object(settings, "analyzer_openai_fallback_enabled", True), \
                patch.object(llm_ecoa, "_analyzer_ecoa_client", return_value=_client(primary)), \
                patch.object(llm_ecoa, "_analyzer_openai_client") as secondary:
            self.assertEqual(llm_ecoa.gerar_resposta_analyzer("pergunta"), "resultado")
        self.assertEqual(calls, ["ecoa"])
        secondary.assert_not_called()

    def test_connection_timeout_429_and_5xx_fall_back_once(self):
        failures = (
            lambda request: (_ for _ in ()).throw(httpx.ConnectError("falha", request=request)),
            lambda request: (_ for _ in ()).throw(httpx.ReadTimeout("lento", request=request)),
            lambda request: httpx.Response(429, json={"error": {"message": "limit"}}, request=request),
            lambda request: httpx.Response(503, json={"error": {"message": "down"}}, request=request),
        )
        for failure in failures:
            with self.subTest(failure=failure):
                calls = {"ecoa": 0, "openai": 0}

                def primary(request):
                    calls["ecoa"] += 1
                    return failure(request)

                def secondary(request):
                    calls["openai"] += 1
                    return httpx.Response(200, json=_response("fallback"), request=request)

                with patch.object(settings, "analyzer_openai_fallback_enabled", True), \
                        patch.object(llm_ecoa, "_analyzer_ecoa_client", return_value=_client(primary)), \
                        patch.object(llm_ecoa, "_analyzer_openai_client", return_value=_client(secondary)):
                    self.assertEqual(llm_ecoa.gerar_resposta_analyzer("pergunta"), "fallback")
                self.assertEqual(calls, {"ecoa": 1, "openai": 1})

    def test_non_eligible_error_is_propagated_without_fallback(self):
        def primary(request):
            return httpx.Response(400, json={"error": {"message": "bad"}}, request=request)

        with patch.object(settings, "analyzer_openai_fallback_enabled", True), \
                patch.object(llm_ecoa, "_analyzer_ecoa_client", return_value=_client(primary)), \
                patch.object(llm_ecoa, "_analyzer_openai_client") as secondary:
            with self.assertRaises(Exception) as caught:
                llm_ecoa.gerar_resposta_analyzer("pergunta")
        self.assertEqual(getattr(caught.exception, "status_code", None), 400)
        secondary.assert_not_called()

    def test_logs_correlation_provider_reason_and_no_sensitive_content(self):
        def primary(request):
            return httpx.Response(503, json={"error": {"message": "down"}}, request=request)

        def secondary(request):
            return httpx.Response(200, json=_response("conteudo-secreto"), request=request)

        token = _perf_run_id.set("run123")
        try:
            with patch.object(settings, "analyzer_openai_fallback_enabled", True), \
                    patch.object(settings, "rag_llm_http_log_enabled", True), \
                    patch.object(llm_ecoa, "_analyzer_ecoa_client", return_value=_client(primary)), \
                    patch.object(llm_ecoa, "_analyzer_openai_client", return_value=_client(secondary)), \
                    self.assertLogs("uvicorn.error", level=logging.INFO) as logs:
                result = llm_ecoa.gerar_resposta_analyzer("prompt-secreto")
        finally:
            _perf_run_id.reset(token)
        joined = "\n".join(logs.output)
        self.assertEqual(result, "conteudo-secreto")
        self.assertIn("run_id=run123", joined)
        self.assertIn("provedor=ecoa", joined)
        self.assertIn("provedor=openai", joined)
        self.assertIn("motivo=http_5xx", joined)
        self.assertIn("fallback=1", joined)
        self.assertNotIn("prompt-secreto", joined)
        self.assertNotIn("conteudo-secreto", joined)
        self.assertNotIn("test-secret-key", joined)

    def test_production_clients_disable_sdk_retries_and_use_configuration(self):
        transport = httpx.MockTransport(
            lambda request: httpx.Response(200, json=_response(), request=request)
        )
        observed = DefaultHttpxClient(transport=transport)
        with patch.object(settings, "analyzer_ecoa_timeout_seconds", 12.5), \
                patch.object(settings, "openai_api_key", type(settings.openai_api_key)("configured")), \
                patch.object(llm_ecoa, "_http_client_observado", return_value=observed):
            ecoa = llm_ecoa._analyzer_ecoa_client()
            self.assertEqual(ecoa.max_retries, 0)
            self.assertEqual(ecoa.timeout, 12.5)


if __name__ == "__main__":
    unittest.main()
