from pathlib import Path

import pytest
from sqlalchemy.orm import Session

from app.core.database import create_sqlite_engine, init_db
from app.modules.corpus.model import CorpusVersion
from app.modules.documents.model import Document, DocumentChunk
from eval.benchmark_hybrid import executar_comparacao
from src.index import indexar_chunks_incrementalmente


def fake_embedding(text: str) -> list[float]:
    lowered = text.lower()
    if "alpha" in lowered:
        return [1.0, 0.0]
    if "beta" in lowered:
        return [0.0, 1.0]
    return [0.5, 0.5]


@pytest.fixture()
def corpus(tmp_path: Path):
    engine = create_sqlite_engine(f"sqlite:///{tmp_path / 'benchmark.db'}")
    init_db(engine)
    with Session(engine) as db:
        version = CorpusVersion(version="benchmark-v1", status="ready")
        document = Document(
            corpus_version=version,
            source_file="norma.pdf",
            title="Norma sintética",
            base_id="editais_normativo",
            doc_type="lei",
            sensitivity="publico",
        )
        chunks = [
            DocumentChunk(
                document=document,
                chunk_id="editais_normativo:lei:1:p1",
                content="alpha alpha fiscalização",
                base_id="editais_normativo",
            ),
            DocumentChunk(
                document=document,
                chunk_id="editais_normativo:lei:2:p1",
                content="beta contratação",
                base_id="editais_normativo",
            ),
            DocumentChunk(
                document=document,
                chunk_id="editais_normativo:lei:3:p1",
                content="gamma planejamento",
                base_id="editais_normativo",
            ),
        ]
        db.add_all(chunks)
        db.commit()
        index_dir = tmp_path / "faiss"
        indexar_chunks_incrementalmente(
            [(chunk.chunk_id, chunk.content) for chunk in chunks],
            fake_embedding,
            index_dir,
            modelo_embedding="fake-v1",
            dimensao_embedding=2,
        )
    yield engine, index_dir
    engine.dispose()


def test_compara_mesmas_perguntas_metricas_e_corpus(corpus):
    engine, index_dir = corpus
    payload = {
        "corpus": "benchmark-v1",
        "base": "editais_normativo",
        "questions": [
            {
                "id": "A",
                "pergunta": "alpha",
                "fontes_esperadas": [
                    {"chunk_id_prefixo": "editais_normativo:lei:1:"}
                ],
            },
            {
                "id": "B",
                "pergunta": "beta",
                "fontes_esperadas": [
                    {"chunk_id_prefixo": "editais_normativo:lei:2:"}
                ],
            },
            {"id": "fora", "pergunta": "rota", "fontes_esperadas": []},
        ],
    }
    with Session(engine) as db:
        report = executar_comparacao(
            db,
            payload,
            index_dir=index_dir,
            embedding_fn=fake_embedding,
            top_ks=(1, 2),
            candidate_k=3,
        )

    assert report["questions_measured"] == 2
    assert report["questions_not_measured"] == 1
    assert report["index"]["vectors"] == 3
    assert report["index"]["state_sha256"]
    assert not report["index"]["path"].startswith("/")
    assert set(report["methods"]) == {"bm25", "faiss", "rrf"}
    for method in report["methods"].values():
        assert [question["id"] for question in method["questions"]] == ["A", "B"]
        assert method["aggregate"]["hit@1"] == 1.0
        assert method["aggregate"]["reciprocal_rank"] == 1.0


def test_rejeita_pool_menor_que_top_k(corpus):
    engine, index_dir = corpus
    payload = {
        "questions": [
            {
                "id": "A",
                "pergunta": "alpha",
                "fontes_esperadas": [{"chunk_id_prefixo": "lei:1:"}],
            }
        ]
    }
    with Session(engine) as db, pytest.raises(ValueError, match="candidate_k"):
        executar_comparacao(
            db,
            payload,
            index_dir=index_dir,
            embedding_fn=fake_embedding,
            top_ks=(10,),
            candidate_k=5,
        )
