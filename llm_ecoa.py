import os
import time
from functools import lru_cache
from dotenv import load_dotenv
from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    DefaultHttpxClient,
    OpenAI,
)

from app.core.config import settings
from app.core.llm_http_observability import (
    http_request_hook,
    http_response_hook,
    llm_http_operation,
    log_current_usage,
)
from app.core.logging import perf_event

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Configurações obtidas com fallback seguro
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ecoa-llm.duckdns.org:11434/v1")
OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY", "ollama")
GENERATION_MODEL = os.getenv(
    "GENERATION_MODEL", "qcwind/qwen3-8b-instruct-Q4-K-M")
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL", "xagi/qwen3-embedding:0.6b-q4_k_m")
GENERATION_MAX_TOKENS = int(os.getenv("GENERATION_MAX_TOKENS", "3072"))

# Cliente OpenAI apontando para o servidor Ollama
http_client = DefaultHttpxClient(event_hooks={
    "request": [http_request_hook],
    "response": [http_response_hook],
})
client = OpenAI(
    base_url=OLLAMA_URL,
    api_key=OLLAMA_API_KEY,
    http_client=http_client,
)


def _chat_completion(llm_client: OpenAI, model: str, prompt: str):
    return llm_client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=GENERATION_MAX_TOKENS,
        temperature=0.2,
    )


def _conteudo_resposta(response) -> str:
    log_current_usage(getattr(response, "usage", None))
    choice = response.choices[0]
    content = choice.message.content
    finish_reason = getattr(choice, "finish_reason", None)
    if finish_reason == "length":
        raise RuntimeError(
            "LLM truncou a resposta por limite de tokens "
            f"(finish_reason={finish_reason!r}, "
            f"max_tokens={GENERATION_MAX_TOKENS!r}, "
            f"model={getattr(response, 'model', None)!r}, "
            f"id={getattr(response, 'id', None)!r})"
        )
    if content is None or not content.strip():
        raise RuntimeError(
            "LLM retornou resposta vazia "
            f"(finish_reason={finish_reason!r}, "
            f"model={getattr(response, 'model', None)!r}, "
            f"id={getattr(response, 'id', None)!r})"
        )
    return content


def gerar_resposta(prompt: str) -> str:
    """Gera texto pelo cliente ECOA compartilhado com o restante do RAG."""
    return _conteudo_resposta(_chat_completion(client, GENERATION_MODEL, prompt))


def _http_client_observado() -> DefaultHttpxClient:
    return DefaultHttpxClient(event_hooks={
        "request": [http_request_hook],
        "response": [http_response_hook],
    })


@lru_cache(maxsize=1)
def _analyzer_ecoa_client() -> OpenAI:
    return OpenAI(
        base_url=OLLAMA_URL,
        api_key=OLLAMA_API_KEY,
        http_client=_http_client_observado(),
        timeout=settings.analyzer_ecoa_timeout_seconds,
        max_retries=0,
    )


@lru_cache(maxsize=1)
def _analyzer_openai_client() -> OpenAI:
    api_key = settings.openai_api_key.get_secret_value()
    if not api_key:
        raise RuntimeError(
            "ANALYZER_OPENAI_FALLBACK_ENABLED exige OPENAI_API_KEY configurada."
        )
    return OpenAI(
        api_key=api_key,
        http_client=_http_client_observado(),
        max_retries=0,
    )


def _motivo_fallback(error: Exception) -> str | None:
    if isinstance(error, APITimeoutError):
        return "timeout"
    if isinstance(error, APIConnectionError):
        return "erro_conexao"
    if isinstance(error, APIStatusError):
        if error.status_code == 429:
            return "http_429"
        if error.status_code >= 500:
            return "http_5xx"
    return None


def _resposta_analyzer_provedor(
    provider: str,
    llm_client: OpenAI,
    model: str,
    prompt: str,
) -> str:
    started = time.perf_counter()
    perf_event("analyzer_provider", "inicio", provedor=provider)
    try:
        with llm_http_operation("analyzer", provider=provider):
            result = _conteudo_resposta(_chat_completion(llm_client, model, prompt))
    except BaseException as error:
        perf_event(
            "analyzer_provider", "erro",
            (time.perf_counter() - started) * 1000,
            type(error).__name__, provedor=provider,
        )
        raise
    perf_event(
        "analyzer_provider", "ok",
        (time.perf_counter() - started) * 1000,
        provedor=provider,
    )
    return result


def gerar_resposta_analyzer(prompt: str) -> str:
    """Usa ECOA e, quando explicitamente habilitado, OpenAI como fallback."""
    if not settings.analyzer_openai_fallback_enabled:
        return gerar_resposta(prompt)
    primary_started = time.perf_counter()
    try:
        return _resposta_analyzer_provedor(
            "ecoa", _analyzer_ecoa_client(), GENERATION_MODEL, prompt
        )
    except Exception as error:
        motivo = _motivo_fallback(error)
        if motivo is None:
            raise
        perf_event(
            "analyzer_fallback", "inicio",
            (time.perf_counter() - primary_started) * 1000,
            provedor="openai", motivo=motivo, fallback=1,
        )
        return _resposta_analyzer_provedor(
            "openai", _analyzer_openai_client(), settings.analyzer_openai_model, prompt
        )


def gerar_embedding(texto: str) -> list[float]:
    """Exemplo simples de geração de embedding vetorial para um texto."""
    with llm_http_operation("embedding"):
        response = client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=texto,
        )
        log_current_usage(getattr(response, "usage", None))
    return response.data[0].embedding


if __name__ == "__main__":
    print("=== Exemplo de Geração de Texto (LLM) ===")
    prompt_exemplo = "O que é Retrieval-Augmented Generation (RAG)? Responda em duas frases."
    print(f"Prompt: {prompt_exemplo}")
    resposta = gerar_resposta(prompt_exemplo)
    print(f"Resposta:\n{resposta}\n")

    print("=== Exemplo de Embeddings ===")
    texto_exemplo = "RAG combina recuperação de informação e modelos de linguagem."
    print(f"Texto: {texto_exemplo}")
    vetor = gerar_embedding(texto_exemplo)
    print(f"Dimensão do vetor gerado: {len(vetor)}")
    print(f"Primeiros 5 valores: {vetor[:5]}...\n")
