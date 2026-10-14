"""Provedor de geração com Ecoa primária e Groq como fallback controlado.

Embeddings não passam por este módulo. O índice FAISS deve continuar usando
um único modelo de embedding para não misturar vetores incompatíveis.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Callable

from app.core.logging import novo_run_id, registrar
from llm_ecoa import GENERATION_MODEL as ECOA_MODEL
from llm_ecoa import gerar_resposta as gerar_resposta_ecoa


class LlmProviderError(RuntimeError):
    """Falha de geração depois de esgotar os provedores permitidos."""


@dataclass(frozen=True)
class LlmGeneration:
    """Texto gerado e metadados mínimos para auditoria."""

    content: str
    provider: str
    model: str
    fallback_used: bool = False
    fallback_reason: str | None = None

    def audit_metadata(self) -> dict[str, object]:
        return {
            "provider": self.provider,
            "model": self.model,
            "fallback_used": self.fallback_used,
            "fallback_reason": self.fallback_reason,
        }


TextGenerator = Callable[[str], str]


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().casefold() in {"1", "true", "t", "yes", "y", "sim", "s"}


def _fallback_habilitado() -> bool:
    return _env_bool("LLM_FALLBACK_ENABLED", True)


def _modelo_groq() -> str:
    return os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")


def _motivo_fallback(exc: Exception) -> str | None:
    """Classifica apenas falhas transitórias que justificam trocar de provedor."""

    if isinstance(exc, (TimeoutError, ConnectionError, OSError)):
        return "timeout_or_connection"

    # As classes OpenAI podem variar entre versões; por isso a classificação
    # usa também atributos estáveis em vez de exigir uma versão específica.
    error_name = type(exc).__name__
    if error_name in {"APITimeoutError", "APIConnectionError", "InternalServerError"}:
        return "timeout_or_connection"
    status_code = getattr(exc, "status_code", None)
    if isinstance(status_code, int) and status_code >= 500:
        return f"http_{status_code}"
    return None


def gerar_resposta_groq(prompt: str) -> str:
    """Gera texto via Groq somente quando a chave e o pacote estão disponíveis."""

    if not os.getenv("GROQ_API_KEY"):
        raise LlmProviderError(
            "Fallback Groq indisponível: configure GROQ_API_KEY no arquivo .env."
        )
    try:
        from langchain_groq import ChatGroq
    except ImportError as exc:
        raise LlmProviderError(
            "Fallback Groq indisponível: instale langchain-groq pelas dependências do projeto."
        ) from exc

    llm = ChatGroq(
        model=_modelo_groq(),
        temperature=float(os.getenv("GROQ_TEMPERATURE", "0")),
        timeout=float(os.getenv("GROQ_TIMEOUT_SECONDS", "45")),
        # A Groq é o último provedor desta chamada. Não prolongamos a espera
        # com retries internos invisíveis ao usuário.
        max_retries=0,
    )
    response = llm.invoke(prompt)
    content = getattr(response, "content", None)
    if content is None or not str(content).strip():
        raise LlmProviderError("Groq retornou uma resposta vazia.")
    return str(content)


def _registrar_fallback(motivo: str, model: str) -> None:
    """Registra a troca sem gravar prompt ou credenciais no log."""

    try:
        registrar(
            novo_run_id(),
            "llm_provider",
            status="fallback",
            saida="Ecoa indisponível; resposta gerada pelo fallback Groq.",
            modelo=model,
            provider="groq",
            fallback_reason=motivo,
        )
    except Exception:
        # Observabilidade não pode impedir uma resposta já disponível.
        pass


def gerar_resposta_com_fallback_detalhada(
    prompt: str,
    *,
    ecoa_fn: TextGenerator = gerar_resposta_ecoa,
    groq_fn: TextGenerator | None = None,
) -> LlmGeneration:
    """Tenta Ecoa e usa Groq apenas em falhas transitórias autorizadas."""

    try:
        return LlmGeneration(
            content=ecoa_fn(prompt),
            provider="ecoa",
            model=ECOA_MODEL,
        )
    except Exception as ecoa_error:
        motivo = _motivo_fallback(ecoa_error)
        if motivo is None or not _fallback_habilitado():
            raise

        gerador_groq = groq_fn or gerar_resposta_groq
        try:
            content = gerador_groq(prompt)
        except Exception as groq_error:
            raise LlmProviderError(
                "Ecoa falhou e o fallback Groq também não respondeu. "
                f"Ecoa={type(ecoa_error).__name__}; "
                f"Groq={type(groq_error).__name__}."
            ) from groq_error

        model = _modelo_groq()
        _registrar_fallback(motivo, model)
        return LlmGeneration(
            content=content,
            provider="groq",
            model=model,
            fallback_used=True,
            fallback_reason=motivo,
        )


def gerar_resposta_com_fallback(prompt: str) -> str:
    """Adaptador compatível com os pontos do projeto que esperam apenas texto."""

    return gerar_resposta_com_fallback_detalhada(prompt).content
