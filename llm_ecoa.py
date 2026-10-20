import os
from dotenv import load_dotenv
from openai import DefaultHttpxClient, OpenAI

from app.core.config import settings
from app.core.llm_http_observability import (
    http_request_hook,
    http_response_hook,
    llm_http_operation,
    log_current_usage,
)

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
ECOA_TIMEOUT_SECONDS = float(os.getenv("ECOA_TIMEOUT_SECONDS", "30"))

# Cliente OpenAI apontando para o servidor Ollama
http_client = DefaultHttpxClient(event_hooks={
    "request": [http_request_hook],
    "response": [http_response_hook],
})
client = OpenAI(
    base_url=OLLAMA_URL,
    api_key=OLLAMA_API_KEY,
    http_client=http_client,
    timeout=settings.ecoa_timeout_seconds,
    # Falhas transitórias devem chegar logo ao fallback configurável.
    max_retries=0,
)


def _chat_completion(
    llm_client: OpenAI,
    model: str,
    prompt: str,
    reasoning_effort: str | None = None,
):
    request_options = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "max_tokens": GENERATION_MAX_TOKENS,
        "temperature": 0.2,
    }
    if reasoning_effort is not None:
        request_options["reasoning_effort"] = reasoning_effort
    return llm_client.chat.completions.create(**request_options)


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
    reasoning_effort = (
        "none" if settings.generation_disable_thinking else None
    )
    return _conteudo_resposta(
        _chat_completion(
            client,
            GENERATION_MODEL,
            prompt,
            reasoning_effort=reasoning_effort,
        )
    )


def gerar_resposta_analyzer(prompt: str) -> str:
    """Usa Ecoa e o fallback configurável para o Query Analyzer."""

    # Importação tardia evita ciclo: o provedor recebe ``gerar_resposta`` como
    # callback e não cria embeddings nem altera o cliente Ecoa.
    from app.core.llm_provider import gerar_com_fallback

    return gerar_com_fallback(
        prompt,
        operation="analyzer",
        # O Analyzer precisa manter o comportamento histórico: a opção de
        # desativar thinking é exclusiva da geração final RAG.
        ecoa_fn=lambda texto: _conteudo_resposta(
            _chat_completion(client, GENERATION_MODEL, texto)
        ),
        ecoa_model=GENERATION_MODEL,
    ).content


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
