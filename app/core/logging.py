"""
Log estruturado em JSONL (item 2.4 do enunciado).

Todo módulo do pipeline registra por onde passou, em
logs/pipeline-AAAA-MM-DD.jsonl, uma linha por evento. O `run_id` amarra todas
as etapas de uma mesma execução: sem ele, os logs são ruído.

A pasta logs/ é ignorada pelo Git.
"""

import json
import time
import uuid
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

PASTA_LOGS = Path("logs")

# Etapas da preparação do corpus. Complementam PIPELINE_STAGES
# (app/modules/rag/model.py), que cobre só a fase de consulta.
# Proposta ao time: acrescentar "coleta" e "ingestao" à lista canônica.
STAGE_COLETA = "coleta"
STAGE_INGESTAO = "ingestao"


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
