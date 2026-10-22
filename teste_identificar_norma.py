
"""Teste de identificação normativa e reranking do RAG."""

import importlib
import pkgutil

import app.modules

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, configure_mappers


# ============================================================
# 1. REGISTRAR TODOS OS MODELOS SQLALCHEMY
# ============================================================

for modulo in pkgutil.walk_packages(
    app.modules.__path__,
    prefix="app.modules.",
):
    if modulo.name.endswith(".model"):
        importlib.import_module(modulo.name)

configure_mappers()


# ============================================================
# 2. IMPORTAR AS FUNÇÕES DO RAG
# ============================================================

from src.retrieve import (
    _identificar_norma,
    retrieve_hibrido,
)

from src.query.schemas import KnowledgeBase


# ============================================================
# 3. CONFIGURAÇÃO DO TESTE
# ============================================================

pergunta = (
    "Quais são as atribuições dos fiscais de contrato "
    "previstas no Decreto Estadual RJ nº 48.817/2023?"
)

documento_esperado = 1900

engine = create_engine("sqlite:///app.db")


# ============================================================
# 4. EXECUTAR TESTES
# ============================================================

try:
    with Session(engine) as db:

        print("=" * 65)
        print("TESTE 1 - IDENTIFICAÇÃO DA NORMA")
        print("=" * 65)

        documento_id = _identificar_norma(db, pergunta)

        print("Pergunta:", pergunta)
        print("Documento identificado:", documento_id)
        print("Documento esperado:", documento_esperado)

        if documento_id == documento_esperado:
            print("RESULTADO: identificação correta.")
        else:
            print("RESULTADO: identificação incorreta.")

        print("\n" + "=" * 65)
        print("TESTE 2 - RECUPERAÇÃO HÍBRIDA E RERANKING")
        print("=" * 65)

        resultados = retrieve_hibrido(
            db=db,
            pergunta=pergunta,
            top_k=10,
            bm25_k=20,
            dense_k=20,
            rrf_k=60,
            bases=[KnowledgeBase.NORMATIVA],
        )

        print("\nTotal de resultados:", len(resultados))
        print()

        # ----------------------------------------------------
        # EXIBIR RESULTADOS
        # ----------------------------------------------------

        for posicao, item in enumerate(resultados, start=1):

            metadata = item.metadata

            print(f"POSIÇÃO {posicao}")
            print("Chunk:", item.chunk_id)
            print("Documento:", metadata.get("tituloDocumento"))
            print("Document ID:", metadata.get("document_id"))
            print("Tipo:", metadata.get("doc_type"))
            print("BM25 rank:", item.bm25_rank)
            print("FAISS rank:", item.dense_rank)
            print("RRF score:", round(item.rrf_score, 6))

            texto = item.content[:250].replace("\n", " ")
            print("Texto:", texto)

            print("-" * 65)

        # ====================================================
        # 5. VERIFICAR CHUNKS DO DECRETO
        # ====================================================

        print("\n" + "=" * 65)
        print("TESTE 3 - CHUNKS DO DECRETO 48.817")
        print("=" * 65)

        chunks_decreto = [
            (posicao, item)
            for posicao, item in enumerate(resultados, start=1)
            if item.metadata.get("document_id") == documento_esperado
        ]

        print(
            "Quantidade de chunks do decreto no Top 10:",
            len(chunks_decreto),
        )

        if not chunks_decreto:
            print("RESULTADO: nenhum chunk do decreto encontrado.")
        else:
            for posicao, item in chunks_decreto:
                print()
                print("Posição:", posicao)
                print("Chunk:", item.chunk_id)

                if "preambulo" in item.chunk_id.lower():
                    print("Classificação: PREÂMBULO")
                else:
                    print("Classificação: POSSÍVEL ARTIGO")

                print(
                    "Texto:",
                    item.content[:350].replace("\n", " "),
                )

        # ====================================================
        # 6. AVALIAÇÃO DA RECUPERAÇÃO
        # ====================================================

        print("\n" + "=" * 65)
        print("TESTE 4 - AVALIAÇÃO DA RECUPERAÇÃO")
        print("=" * 65)

        artigos_decreto = [
            item
            for _, item in chunks_decreto
            if "preambulo" not in item.chunk_id.lower()
        ]

        if documento_id != documento_esperado:
            print("FALHA: norma não identificada corretamente.")

        elif not chunks_decreto:
            print(
                "FALHA: decreto identificado, "
                "mas seus chunks não foram recuperados."
            )

        elif not artigos_decreto:
            print(
                "ATENÇÃO: somente o preâmbulo do decreto "
                "foi recuperado."
            )

        else:
            print(
                "Foram recuperados",
                len(artigos_decreto),
                "chunks do decreto fora do preâmbulo."
            )
            print(
                "Ainda é necessário verificar se eles "
                "contêm as atribuições dos fiscais."
            )

        print("\nTeste concluído.")

finally:
    engine.dispose()
