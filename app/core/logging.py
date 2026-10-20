"""
Log estruturado em JSONL (item 2.4 do enunciado).

Todo módulo do pipeline registra por onde passou, em
logs/pipeline-AAAA-MM-DD.jsonl, uma linha por evento. O `run_id` amarra todas
as etapas de uma mesma execução: sem ele, os logs são ruído.

A pasta logs/ é ignorada pelo Git.
"""

import json
import logging
import time
import uuid
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime
from pathlib import Path

PASTA_LOGS = Path("logs")

# Etapas da preparação do corpus. Complementam PIPELINE_STAGES
# (app/modules/rag/model.py), que cobre só a fase de consulta.
# Proposta ao time: acrescentar "coleta" e "ingestao" à lista canônica.
STAGE_COLETA = "coleta"
STAGE_INGESTAO = "ingestao"


_perf_run_id: ContextVar[str | None] = ContextVar("rag_perf_run_id", default=None)
_perf_logger = logging.getLogger("uvicorn.error")
_PERF_METRICS = frozenset({
    "chunks_elegiveis", "candidatos", "fontes", "vetores",
    "tentativa", "status_http", "retry", "espera_ms", "fallback",
    "tokens_entrada", "tokens_saida", "tokens_total",
})
_PERF_TEXT_METRICS = frozenset({"provedor", "motivo"})


def _perf_event(stage, status, duration_ms=None, exception=None, metrics=None):
    """Emite apenas campos técnicos; falhas de logging não afetam a consulta."""
    run_id = _perf_run_id.get()
    if run_id is None:
        return
    try:
        fields = [f"[RAG-PERF] run_id={run_id}", f"etapa={stage}"]
        if duration_ms is not None:
            fields.append(f"duracao_ms={duration_ms:.3f}")
        fields.append(f"status={status}")
        if exception is not None:
            fields.append(f"excecao={exception}")
        for key, value in (metrics or {}).items():
            if key in _PERF_METRICS and isinstance(value, (int, float)):
                fields.append(f"{key}={value}")
            elif key in _PERF_TEXT_METRICS and isinstance(value, str):
                seguro = "".join(c for c in value if c.isalnum() or c == "_")
                if seguro:
                    fields.append(f"{key}={seguro}")
        _perf_logger.info(" ".join(fields))
    except Exception:
        pass


def perf_event(stage, status, duration_ms=None, exception=None, **metrics):
    """Interface segura para eventos observacionais correlacionados."""
    _perf_event(stage, status, duration_ms, exception, metrics)


def current_perf_run_id():
    return _perf_run_id.get()


@contextmanager
def perf_stage(stage):
    """Mede somente etapas executadas dentro de uma requisição instrumentada."""
    metrics = {}
    from app.core.config import settings

    if _perf_run_id.get() is None or not settings.rag_perf_log_enabled:
        yield metrics
        return
    started = time.perf_counter()
    _perf_event(stage, "inicio")
    try:
        yield metrics
    except BaseException as error:
        _perf_event(stage, "erro", (time.perf_counter() - started) * 1000,
                    type(error).__name__, metrics)
        raise
    else:
        _perf_event(stage, "ok", (time.perf_counter() - started) * 1000, metrics=metrics)


class RagPerfMiddleware:
    """Observa o ciclo ASGI de POST /query/ask sem consumir ou alterar mensagens."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        from app.core.config import settings

        perf_enabled = settings.rag_perf_log_enabled
        llm_http_enabled = settings.rag_llm_http_log_enabled
        if (not (perf_enabled or llm_http_enabled) or scope["type"] != "http"
                or scope.get("method") != "POST" or scope.get("path") != "/query/ask"):
            await self.app(scope, receive, send)
            return
        started = time.perf_counter()
        token = _perf_run_id.set(novo_run_id())
        if perf_enabled:
            _perf_event("recebimento", "ok", (time.perf_counter() - started) * 1000)
            _perf_event("total", "inicio")
        response_status = None
        error_type = None

        async def observed_send(message):
            nonlocal response_status
            if message["type"] == "http.response.start":
                response_status = message["status"]
            await send(message)

        try:
            await self.app(scope, receive, observed_send)
        except BaseException as error:
            error_type = type(error).__name__
            raise
        finally:
            status = "erro" if error_type or (response_status is not None and response_status >= 400) else "ok"
            if perf_enabled:
                _perf_event("total", status, (time.perf_counter() - started) * 1000, error_type)
            _perf_run_id.reset(token)


def novo_run_id() -> str:
    """Identificador curto de uma execução inteira."""
    return uuid.uuid4().hex[:8]


def registrar(run_id, stage, status="ok", latencia_ms=None, entrada=None,
              saida=None, tokens=None, modelo=None, query_id=None, **extra):
    """Grava uma linha no log do dia, no formato do enunciado."""
    PASTA_LOGS.mkdir(parents=True, exist_ok=True)
    evento = {
        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
        "run_id": run_id,
        "query_id": query_id,
        "stage": stage,
        "status": status,
        "latencia_ms": latencia_ms,
        "input": entrada,
        "output": saida,
        # Coleta e ingestão não chamam o LLM: os tokens ficam zerados de
        # propósito, para o campo existir em toda etapa.
        "tokens": tokens or {"prompt": 0, "completion": 0, "total": 0},
        "modelo": modelo,
        "extra": extra,
    }
    arquivo = PASTA_LOGS / f"pipeline-{datetime.now():%Y-%m-%d}.jsonl"
    with arquivo.open("a", encoding="utf-8") as f:
        f.write(json.dumps(evento, ensure_ascii=False, default=str) + "\n")
    return evento


@contextmanager
def etapa(run_id, stage, entrada=None, **extra):
    """
    Mede a duração da etapa e registra o resultado. Se estourar exceção, grava
    com status "erro" e deixa a exceção subir — o log não engole o problema.

        with etapa(run_id, "coleta", entrada=url) as ev:
            conteudo = baixar(url)
            ev["saida"] = f"{len(conteudo)} bytes"
    """
    inicio = time.perf_counter()
    dados = {"saida": None}
    try:
        yield dados
    except Exception as erro:
        registrar(run_id, stage, "erro", int((time.perf_counter() - inicio) * 1000),
                  entrada, type(erro).__name__, **extra)
        raise
    registrar(run_id, stage, "ok", int((time.perf_counter() - inicio) * 1000),
              entrada, dados["saida"], **extra)
