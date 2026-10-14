"""Filtros estruturados aplicados antes da fusão FTS5 + FAISS."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from sqlalchemy.orm import Session

from app.core.database import create_sqlite_engine, init_db
from app.modules.corpus.model import CorpusVersion
from app.modules.documents.model import Document, DocumentChunk
from src.index import indexar_chunks_incrementalmente
from src.query.base_catalog import resolver_base_ids
from src.query.schemas import KnowledgeBase, QueryFilters
from src.retrieve import (
    contar_chunks_por_base,
    resolver_chunk_ids_filtrados,
    retrieve_hibrido,
)


def fake_embedding(texto: str) -> list[float]:
    return [1.0, 0.0] if "alpha" in texto.lower() else [0.0, 1.0]


class RetrieveFiltersTests(unittest.TestCase):
    def setUp(self) -> None:
        self.engine = create_sqlite_engine("sqlite:///:memory:")
        init_db(self.engine)
        self.session = Session(self.engine)
        self.addCleanup(self.engine.dispose)
        self.addCleanup(self.session.close)

        corpus = CorpusVersion(version="filters-test", status="ready")
        documento_a = Document(
            corpus_version=corpus,
            source_file="pncp_rj_estruturada|contrato|111-2-000001/2026|1",
            title="Contrato Alpha",
            base_id="pncp_rj_estruturada",
            doc_type="contrato",
            sensitivity="publico",
        )
        documento_b = Document(
            corpus_version=corpus,
            source_file="pncp_rj_estruturada|contrato|222-2-000001/2025|1",
            title="Contrato Beta",
            base_id="pncp_rj_estruturada",
            doc_type="contrato",
            sensitivity="publico",
        )
        documento_normativo = Document(
            corpus_version=corpus,
            source_file="lei_14133.pdf",
            title="Lei 14.133/2021",
            base_id="editais_normativo",
            doc_type="norma",
            sensitivity="publico",
        )
        documento_conversacional = Document(
            corpus_version=corpus,
            source_file="email_teste.md",
            title="E-mail simulado",
            base_id="conversacional_pncp",
            doc_type="conversa",
            sensitivity="publico",
        )
        self.chunk_a = DocumentChunk(
            document=documento_a,
            chunk_id="chunk-a",
            content="alpha manutenção contratual",
            ano=2026,
            modalidade="Pregão Eletrônico",
            municipio="Rio de Janeiro",
            objeto="Manutenção de elevadores",
            valor=100.0,
        )
        self.chunk_b = DocumentChunk(
            document=documento_b,
            chunk_id="chunk-b",
            content="alpha manutenção contratual",
            ano=2025,
            modalidade="Dispensa",
            municipio="Niterói",
            objeto="Material hospitalar",
            valor=200.0,
        )
        self.chunk_normativo = DocumentChunk(
            document=documento_normativo,
            chunk_id="chunk-normativo",
            content="alpha requisitos de habilitação na Lei 14.133",
        )
        self.chunk_conversacional = DocumentChunk(
            document=documento_conversacional,
            chunk_id="chunk-conversacional",
            content="alpha troca de e-mails sobre habilitação",
        )
        self.session.add_all([
            self.chunk_a,
            self.chunk_b,
            self.chunk_normativo,
            self.chunk_conversacional,
        ])
        self.session.commit()

    def test_resolve_apenas_chunks_do_numero_pncp_solicitado(self) -> None:
        allowed = resolver_chunk_ids_filtrados(
            self.session,
            QueryFilters(numero_controle_pncp="111-2-000001/2026"),
        )

        self.assertEqual(allowed, {"chunk-a"})

    def test_retrieval_nao_mistura_chunks_de_outro_contrato(self) -> None:
        with TemporaryDirectory() as directory:
            indexar_chunks_incrementalmente(
                [
                    (self.chunk_a.chunk_id, self.chunk_a.content),
                    (self.chunk_b.chunk_id, self.chunk_b.content),
                ],
                fake_embedding,
                Path(directory),
            )
            results = retrieve_hibrido(
                self.session,
                "alpha manutenção",
                top_k=5,
                cache_dir=Path(directory),
                embedding_fn=fake_embedding,
                filters=QueryFilters(numero_controle_pncp="111-2-000001/2026"),
            )

        self.assertEqual([item.chunk_id for item in results], ["chunk-a"])
        self.assertTrue(
            all(
                item.metadata["numeroControlePNCP"] == "111-2-000001/2026"
                for item in results
            )
        )

    def test_combina_ano_modalidade_e_faixa_de_valor(self) -> None:
        allowed = resolver_chunk_ids_filtrados(
            self.session,
            QueryFilters(
                ano=2026,
                modalidade="pregão",
                valor_minimo=90,
                valor_maximo=110,
            ),
        )

        self.assertEqual(allowed, {"chunk-a"})

    def test_filtra_por_objeto(self) -> None:
        allowed = resolver_chunk_ids_filtrados(
            self.session,
            QueryFilters(objeto="elevadores"),
        )

        self.assertEqual(allowed, {"chunk-a"})

    def test_restringe_chunks_a_base_logica_solicitada(self) -> None:
        normativos = resolver_chunk_ids_filtrados(
            self.session,
            filters=None,
            base_ids=resolver_base_ids([KnowledgeBase.NORMATIVA]),
        )
        conversacionais = resolver_chunk_ids_filtrados(
            self.session,
            filters=None,
            base_ids=resolver_base_ids([KnowledgeBase.CONVERSACIONAL]),
        )
        agregados = resolver_chunk_ids_filtrados(
            self.session,
            filters=None,
            base_ids=resolver_base_ids([KnowledgeBase.AGREGADA]),
        )

        self.assertEqual(normativos, {"chunk-normativo"})
        self.assertEqual(conversacionais, {"chunk-conversacional"})
        self.assertEqual(agregados, {"chunk-a", "chunk-b"})

    def test_conta_chunks_por_base_para_auditoria(self) -> None:
        totais = contar_chunks_por_base(
            self.session,
            {"pncp_rj_estruturada", "editais_normativo"},
        )

        self.assertEqual(totais, {
            "editais_normativo": 1,
            "pncp_rj_estruturada": 2,
        })


if __name__ == "__main__":
    unittest.main()
