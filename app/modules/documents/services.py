from __future__ import annotations

import json
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.documents.model import Document, DocumentChunk
from src.base_estruturada.chunking import (
    caminho_relativo_portavel,
    gerar_chunk_id,
    gerar_chunks,
    montar_metadata_base,
    selecionar_configuracao,
)
from src.base_estruturada.pipelines.pipeline_chunks import _indice_por_controle


SENSIBILIDADE_PADRAO = "publico"


def _data(valor: Any) -> date | None:
    if not valor:
        return None
    try:
        return date.fromisoformat(str(valor)[:10])
    except ValueError:
        return None


def _decimal(valor: Any) -> Decimal | None:
    if valor is None or valor == "":
        return None
    try:
        return Decimal(str(valor))
    except (InvalidOperation, ValueError):
        return None


def _document_source_file(metadata: dict[str, Any]) -> str:
    return "|".join(
        [
            str(metadata.get("baseId", "")),
            str(metadata.get("tipoEntidade", "")),
            str(metadata.get("numeroControlePNCP", "")),
            str(metadata.get("sequencialDocumento", "")),
        ]
    )


def _obter_ou_criar_documento(
    db: Session,
    corpus_version_id: int,
    metadata: dict[str, Any],
) -> tuple[Document, bool]:
    source_file = _document_source_file(metadata)
    documento = db.scalar(
        select(Document).where(
            Document.corpus_version_id == corpus_version_id,
            Document.source_file == source_file,
        )
    )
    if documento is not None:
        return documento, False

    documento = Document(
        corpus_version_id=corpus_version_id,
        source_file=source_file,
        base_id=str(metadata.get("baseId") or ""),
        doc_type=str(metadata.get("tipoEntidade") or ""),
        source_url=metadata.get("urlFontePncp"),
        sensitivity=SENSIBILIDADE_PADRAO,
    )
    db.add(documento)
    db.flush()
    return documento, True


def _criar_chunk(
    documento: Document,
    chunk_id: str,
    conteudo: str,
    metadata: dict[str, Any],
) -> DocumentChunk:
    valor = metadata.get("valorGlobal", metadata.get("valorTotalEstimado"))
    data_publicacao = metadata.get("dataAssinatura", metadata.get("dataAberturaProposta"))
    vigencia = metadata.get("dataVigenciaFim", metadata.get("dataEncerramentoProposta"))
    return DocumentChunk(
        document_id=documento.id,
        chunk_id=chunk_id,
        content=conteudo,
        doc_type=documento.doc_type,
        base_id=documento.base_id,
        sensitivity=documento.sensitivity,
        orgao=metadata.get("orgao"),
        modalidade=metadata.get("modalidade"),
        municipio=metadata.get("municipio"),
        fornecedor=metadata.get("fornecedor"),
        objeto=metadata.get("objeto"),
        valor=_decimal(valor),
        ano=metadata.get("ano"),
        data_publicacao=_data(data_publicacao),
        vigencia=_data(vigencia),
    )


def persistir_textos_ativos_pncp(
    db: Session,
    corpus_version_id: int,
    manifestos: dict[str, list[dict[str, Any]]],
    bases: dict[str, list[dict[str, Any]]],
    limite_textos: int | None = None,
    usar_langchain: bool = True,
    raiz_projeto: Path | None = None,
) -> dict[str, int]:
    """Persiste Document/DocumentChunk a partir de textoAtivo dos manifestos PNCP."""

    raiz = raiz_projeto or Path.cwd()
    indices = {
        origem: _indice_por_controle(registros)
        for origem, registros in bases.items()
    }
    resumo = {
        "textosLidos": 0,
        "documentosCriados": 0,
        "documentosReutilizados": 0,
        "chunksCriados": 0,
        "chunksReutilizados": 0,
        "textosSemArquivo": 0,
        "textosSemRegistroEstruturado": 0,
    }
    chunk_ids_vistos = set(db.scalars(select(DocumentChunk.chunk_id)).all())

    for origem, manifesto in manifestos.items():
        tipo_entidade = "contrato" if origem == "contratos" else "contratacao"
        for entidade_manifesto in manifesto:
            if not isinstance(entidade_manifesto, dict):
                continue

            controle = str(entidade_manifesto.get("numeroControlePNCP") or "")
            entidade = indices.get(origem, {}).get(controle)
            if entidade is None:
                resumo["textosSemRegistroEstruturado"] += 1
                continue

            for documento_pncp in entidade_manifesto.get("documentos") or []:
                if not isinstance(documento_pncp, dict):
                    continue

                documento_db: Document | None = None
                for registro_texto in documento_pncp.get("processamentoTexto") or []:
                    ativo = registro_texto.get("textoAtivo") or {}
                    caminho_texto = Path(str(ativo.get("caminho") or ""))
                    if not caminho_texto.is_file():
                        if ativo:
                            resumo["textosSemArquivo"] += 1
                        continue
                    if limite_textos is not None and resumo["textosLidos"] >= limite_textos:
                        db.commit()
                        return resumo

                    texto = caminho_texto.read_text(encoding="utf-8", errors="replace")
                    configuracao = selecionar_configuracao(
                        documento_pncp.get("tipoDocumentoNome"),
                        caminho_texto,
                    )
                    metadata = montar_metadata_base(
                        entidade=entidade,
                        documento=documento_pncp,
                        registro_texto=registro_texto,
                        tipo_entidade=tipo_entidade,
                        caminho_relativo=caminho_relativo_portavel(caminho_texto, raiz),
                    )

                    if documento_db is None:
                        documento_db, criado = _obter_ou_criar_documento(
                            db,
                            corpus_version_id,
                            metadata,
                        )
                        if criado:
                            resumo["documentosCriados"] += 1
                        else:
                            resumo["documentosReutilizados"] += 1

                    for indice, conteudo in enumerate(
                        gerar_chunks(texto, configuracao, usar_langchain=usar_langchain)
                    ):
                        chunk_id = gerar_chunk_id(metadata, indice, conteudo)
                        if chunk_id in chunk_ids_vistos:
                            resumo["chunksReutilizados"] += 1
                            continue

                        db.add(_criar_chunk(documento_db, chunk_id, conteudo, metadata))
                        chunk_ids_vistos.add(chunk_id)
                        resumo["chunksCriados"] += 1

                    resumo["textosLidos"] += 1

    db.commit()
    return resumo


def persistir_chunks_jsonl_pncp(
    db: Session,
    corpus_version_id: int,
    arquivo_chunks: Path,
    tipos_entidade: set[str] | None = None,
    limite_chunks_novos: int | None = None,
    tamanho_commit: int = 500,
) -> dict[str, int]:
    """Persiste o JSONL canônico de chunks sem extrair ou dividir texto outra vez.

    O arquivo JSONL é a fronteira entre o processamento documental e o banco.
    A idempotência é baseada no ``chunk_id``: uma nova execução percorre o
    arquivo novamente, ignora os chunks existentes e continua nos pendentes.
    """

    if not arquivo_chunks.is_file():
        raise FileNotFoundError(f"Arquivo de chunks não encontrado: {arquivo_chunks}")
    if tamanho_commit <= 0:
        raise ValueError("tamanho_commit deve ser maior que zero.")

    resumo = {
        "linhasLidas": 0,
        "linhasInvalidas": 0,
        "linhasIgnoradasTipo": 0,
        "documentosCriados": 0,
        "documentosReutilizados": 0,
        "chunksCriados": 0,
        "chunksReutilizados": 0,
    }
    chunk_ids_vistos = set(db.scalars(select(DocumentChunk.chunk_id)).all())
    documentos_cache: dict[str, Document] = {}
    novos_desde_commit = 0

    with arquivo_chunks.open(encoding="utf-8") as arquivo:
        for numero_linha, linha in enumerate(arquivo, start=1):
            if not linha.strip():
                continue
            try:
                item = json.loads(linha)
            except json.JSONDecodeError:
                resumo["linhasInvalidas"] += 1
                continue

            if not isinstance(item, dict):
                resumo["linhasInvalidas"] += 1
                continue
            chunk_id = item.get("chunk_id")
            conteudo = item.get("content")
            metadata = item.get("metadata")
            if (
                not isinstance(chunk_id, str)
                or not chunk_id
                or not isinstance(conteudo, str)
                or not isinstance(metadata, dict)
            ):
                resumo["linhasInvalidas"] += 1
                continue

            resumo["linhasLidas"] += 1
            tipo_entidade = str(metadata.get("tipoEntidade") or "")
            if tipos_entidade is not None and tipo_entidade not in tipos_entidade:
                resumo["linhasIgnoradasTipo"] += 1
                continue
            if chunk_id in chunk_ids_vistos:
                resumo["chunksReutilizados"] += 1
                continue
            if (
                limite_chunks_novos is not None
                and resumo["chunksCriados"] >= limite_chunks_novos
            ):
                break

            chave_documento = _document_source_file(metadata)
            documento = documentos_cache.get(chave_documento)
            if documento is None:
                documento, criado = _obter_ou_criar_documento(
                    db,
                    corpus_version_id,
                    metadata,
                )
                documentos_cache[chave_documento] = documento
                if criado:
                    resumo["documentosCriados"] += 1
                else:
                    resumo["documentosReutilizados"] += 1

            db.add(_criar_chunk(documento, chunk_id, conteudo, metadata))
            chunk_ids_vistos.add(chunk_id)
            resumo["chunksCriados"] += 1
            novos_desde_commit += 1
            if novos_desde_commit >= tamanho_commit:
                db.commit()
                novos_desde_commit = 0

    db.commit()
    return resumo
