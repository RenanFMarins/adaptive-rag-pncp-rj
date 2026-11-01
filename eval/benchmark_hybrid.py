"""Compara BM25, FAISS e RRF no mesmo corpus e conjunto de julgamentos.

O SQLite é aberto somente para leitura e o FAISS nunca é reconstruído. Cada
pergunta gera um único embedding, reutilizado pelo ranking denso e pela fusão.
Os julgamentos por prefixo continuam parciais, como na linha de base lexical.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app.core.config import resolver_caminho_indice_faiss
from app.core.database.readonly import readonly_session
from eval.benchmark import (
    DEFAULT_QUESTIONS,
    DEFAULT_TOP_KS,
    _avaliar_ranking,
    _consulta_elegivel,
    _percentil,
    _prefixos_esperados,
    carregar_perguntas,
)
from llm_ecoa import gerar_embedding
from src.fts import buscar_fts5
from src.index import auditar_indice_faiss
from src.retrieve import buscar_dense, reciprocal_rank_fusion

DEFAULT_DATABASE_URL = "sqlite:///./app.db"
EmbeddingFn = Callable[[str], list[float]]


def _identidade_publica_indice(index_dir: Path) -> tuple[str, str | None]:
    resolved = index_dir.resolve()
    try:
        public_path = str(resolved.relative_to(Path.cwd().resolve()))
    except ValueError:
        public_path = resolved.name
    state_path = resolved / "estado_indexacao.json"
    state_hash = (
        hashlib.sha256(state_path.read_bytes()).hexdigest()
        if state_path.is_file()
        else None
    )
    return public_path, state_hash


def _agregar(
    questions: Sequence[dict[str, Any]],
    metric_keys: Sequence[str],
) -> dict[str, float]:
    return {
        key: round(
            sum(question["metrics"][key] for question in questions) / len(questions),
            6,
        )
        for key in metric_keys
    }


def _latencias(values: Sequence[float]) -> dict[str, float]:
    return {
        "mean": round(sum(values) / len(values), 3),
        "p50": round(_percentil(values, 0.50) or 0.0, 3),
        "p95": round(_percentil(values, 0.95) or 0.0, 3),
        "max": round(max(values), 3),
    }


def executar_comparacao(
    db: Session,
    payload: dict[str, Any],
    *,
    index_dir: Path,
    embedding_fn: EmbeddingFn = gerar_embedding,
    top_ks: Sequence[int] = DEFAULT_TOP_KS,
    candidate_k: int = 50,
    rrf_k: int = 60,
) -> dict[str, Any]:
    """Executa os três métodos com perguntas, corpus e cortes idênticos."""

    normalized_top_ks = tuple(sorted(set(int(k) for k in top_ks if int(k) > 0)))
    if not normalized_top_ks:
        raise ValueError("Informe ao menos um top-k positivo.")
    if candidate_k < max(normalized_top_ks):
        raise ValueError("candidate_k deve ser maior ou igual ao maior top-k.")
    if rrf_k <= 0:
        raise ValueError("rrf_k deve ser maior que zero.")

    measurable = [
        question
        for question in payload["questions"]
        if _prefixos_esperados(question)
    ]
    if not measurable:
        raise ValueError("Não há perguntas com fontes esperadas para medir recuperação.")

    eligible = _consulta_elegivel(payload.get("base"))
    allowed_chunk_ids = set(db.scalars(eligible)) if eligible is not None else None
    method_questions: dict[str, list[dict[str, Any]]] = {
        "bm25": [],
        "faiss": [],
        "rrf": [],
    }
    method_latencies: dict[str, list[float]] = {name: [] for name in method_questions}

    for question in measurable:
        text = str(question["pergunta"])
        expected = _prefixos_esperados(question)

        started = time.perf_counter()
        lexical = buscar_fts5(
            db,
            text,
            candidate_k,
            eligible_chunks=eligible,
        )
        lexical_ms = (time.perf_counter() - started) * 1000

        started = time.perf_counter()
        dense = buscar_dense(
            text,
            candidate_k,
            index_dir,
            embedding_fn=embedding_fn,
            allowed_chunk_ids=allowed_chunk_ids,
        )
        dense_ms = (time.perf_counter() - started) * 1000

        started = time.perf_counter()
        fused_scores = reciprocal_rank_fusion([lexical, dense], k=rrf_k)
        fused = sorted(fused_scores, key=fused_scores.get, reverse=True)
        fusion_ms = (time.perf_counter() - started) * 1000

        rankings = {
            "bm25": [chunk_id for chunk_id, _score in lexical],
            "faiss": [chunk_id for chunk_id, _score in dense],
            "rrf": fused,
        }
        latencies = {
            "bm25": lexical_ms,
            "faiss": dense_ms,
            "rrf": lexical_ms + dense_ms + fusion_ms,
        }
        for method, ranking in rankings.items():
            metrics = _avaliar_ranking(ranking, expected, normalized_top_ks)
            method_questions[method].append(
                {
                    "id": question["id"],
                    "type": question.get("tipo"),
                    "expected_prefixes": list(expected),
                    "ranking": ranking[: max(normalized_top_ks)],
                    "latency_ms": round(latencies[method], 3),
                    "metrics": {
                        key: round(value, 6) for key, value in metrics.items()
                    },
                }
            )
            method_latencies[method].append(latencies[method])

    metric_keys = tuple(method_questions["bm25"][0]["metrics"])
    methods: dict[str, Any] = {}
    for method in ("bm25", "faiss", "rrf"):
        methods[method] = {
            "aggregate": _agregar(method_questions[method], metric_keys),
            "latency_ms": _latencias(method_latencies[method]),
            "questions": method_questions[method],
        }

    bm25_aggregate = methods["bm25"]["aggregate"]
    deltas = {
        method: {
            key: round(methods[method]["aggregate"][key] - bm25_aggregate[key], 6)
            for key in metric_keys
        }
        for method in ("faiss", "rrf")
    }
    audit = auditar_indice_faiss(index_dir)
    public_index_path, state_sha256 = _identidade_publica_indice(index_dir)
    return {
        "schema_version": 1,
        "benchmark": "bm25_faiss_rrf_same_judgments",
        "corpus": payload.get("corpus"),
        "base": payload.get("base"),
        "label_policy": "reviewed_expected_chunk_prefixes",
        "questions_total": len(payload["questions"]),
        "questions_measured": len(measurable),
        "questions_not_measured": len(payload["questions"]) - len(measurable),
        "top_ks": list(normalized_top_ks),
        "candidate_k": candidate_k,
        "rrf_k": rrf_k,
        "index": {
            "path": public_index_path,
            "state_sha256": state_sha256,
            "model": audit.modelo_embedding,
            "dimension": audit.dimensao,
            "vectors": audit.total_vetores,
            "inconsistencies": audit.inconsistencias,
        },
        "methods": methods,
        "delta_vs_bm25": deltas,
        "limitations": [
            "Os julgamentos por prefixo são parciais e não enumeram todo chunk relevante.",
            "Latência FAISS inclui a geração remota do embedding da pergunta.",
            "A latência RRF representa a execução sequencial de BM25, FAISS e fusão.",
            "Perguntas sem fontes esperadas não entram nas métricas de recuperação.",
        ],
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compara BM25, FAISS e RRF com o mesmo benchmark PNCP/RJ."
    )
    parser.add_argument("--database-url", default=DEFAULT_DATABASE_URL)
    parser.add_argument("--index-dir", type=Path)
    parser.add_argument("--questions", type=Path, default=DEFAULT_QUESTIONS)
    parser.add_argument("--top-k", nargs="+", type=int, default=DEFAULT_TOP_KS)
    parser.add_argument("--candidate-k", type=int, default=50)
    parser.add_argument("--rrf-k", type=int, default=60)
    parser.add_argument("--output", type=Path)
    return parser


def main() -> int:
    args = _parser().parse_args()
    payload = carregar_perguntas(args.questions)
    index_dir = resolver_caminho_indice_faiss(args.index_dir)
    with readonly_session(args.database_url) as db:
        report = executar_comparacao(
            db,
            payload,
            index_dir=index_dir,
            top_ks=args.top_k,
            candidate_k=args.candidate_k,
            rrf_k=args.rrf_k,
        )
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
