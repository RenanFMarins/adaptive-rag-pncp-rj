from __future__ import annotations

from uuid import uuid4

from sqlalchemy.orm import Session

from app.modules.query.model import Query, Response, ResponseSource
from src.retrieve import RankedChunk


def persistir_resultado_rag(
    db: Session,
    pergunta: str,
    resposta: str,
    sources: list[RankedChunk],
    is_refusal: bool = False,
) -> tuple[Query, Response]:
    query = Query(
        run_id=str(uuid4()),
        text=pergunta,
    )
    db.add(query)
    db.flush()

    response = Response(
        query_id=query.id,
        answer=resposta,
        is_refusal=is_refusal,
    )
    db.add(response)
    db.flush()

    for rank, source in enumerate(sources, start=1):
        document_chunk_id = source.metadata.get("id")

        if not isinstance(document_chunk_id, int):
            raise ValueError(
                f"RankedChunk {source.chunk_id} não possui "
                "DocumentChunk.id válido nos metadados."
            )

        db.add(
            ResponseSource(
                response_id=response.id,
                chunk_id=document_chunk_id,
                rank=rank,
                relevance_score=source.rrf_score,
            )
        )

    db.commit()
    db.refresh(query)
    db.refresh(response)

    return query, response