from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

from app.core.llm_provider import (
    LlmProviderError,
    gerar_resposta_com_fallback_detalhada,
)


class LlmProviderTests(unittest.TestCase):
    def test_usa_ecoa_quando_primaria_responde(self):
        groq = Mock(return_value="não deveria ser chamada")

        result = gerar_resposta_com_fallback_detalhada(
            "pergunta",
            ecoa_fn=lambda _prompt: "resposta Ecoa",
            groq_fn=groq,
        )

        self.assertEqual(result.content, "resposta Ecoa")
        self.assertEqual(result.provider, "ecoa")
        self.assertFalse(result.fallback_used)
        groq.assert_not_called()

    @patch("app.core.llm_provider._registrar_fallback")
    def test_timeout_da_ecoa_usa_groq(self, registrar_fallback):
        result = gerar_resposta_com_fallback_detalhada(
            "pergunta",
            ecoa_fn=lambda _prompt: (_ for _ in ()).throw(TimeoutError()),
            groq_fn=lambda _prompt: "resposta Groq",
        )

        self.assertEqual(result.content, "resposta Groq")
        self.assertEqual(result.provider, "groq")
        self.assertTrue(result.fallback_used)
        self.assertEqual(result.fallback_reason, "timeout_or_connection")
        registrar_fallback.assert_called_once()

    def test_erro_de_validacao_nao_dispara_fallback(self):
        groq = Mock(return_value="resposta Groq")

        with self.assertRaisesRegex(RuntimeError, "resposta inválida"):
            gerar_resposta_com_fallback_detalhada(
                "pergunta",
                ecoa_fn=lambda _prompt: (_ for _ in ()).throw(
                    RuntimeError("resposta inválida")
                ),
                groq_fn=groq,
            )

        groq.assert_not_called()

    def test_dupla_falha_expoe_erro_claro(self):
        with self.assertRaises(LlmProviderError) as captured:
            gerar_resposta_com_fallback_detalhada(
                "pergunta",
                ecoa_fn=lambda _prompt: (_ for _ in ()).throw(ConnectionError()),
                groq_fn=lambda _prompt: (_ for _ in ()).throw(RuntimeError("indisponível")),
            )

        self.assertIn("Ecoa falhou", str(captured.exception))
        self.assertIn("fallback Groq", str(captured.exception))
