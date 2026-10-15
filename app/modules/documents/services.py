from __future__ import annotations

import json
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from collections.abc import Callable
from typing import Any, Iterable

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.text_normalization import normalizar_para_busca
from app.modules.documents.model import Document, DocumentCatalogEntry, DocumentChunk
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
    # Bases não-PNCP (por exemplo, a normativa) já possuem um nome de origem
    # estável. Nos chunks PNCP, a chave de negócio continua sendo o controle
    # do processo + sequência do documento.
    source_file = metadata.get("source_file")
    if isinstance(source_file, str) and source_file.strip():
        return "|".join(
            [
                str(metadata.get("base_id") or metadata.get("baseId") or ""),
                source_file.strip(),
            ]
        )
    return "|".join(
        [
            str(metadata.get("baseId", "")),
            str(metadata.get("tipoEntidade", "")),
            str(metadata.get("numeroControlePNCP", "")),
            str(metadata.get("sequencialDocumento", "")),
        ]
    )


def _atualizar_origem_documento(
    documento: Document,
    metadata: dict[str, Any],
) -> None:
    """Sincroniza os identificadores de origem quando o JSONL é reprocessado."""

    titulo = (
        metadata.get("tituloDocumento")
        or metadata.get("numero_norma")
        or metadata.get("numero_edital")
        or metadata.get("source_file")
    )
    if isinstance(titulo, str) and titulo.strip():
        documento.title = titulo.strip()

    url = metadata.get("urlFontePncp") or metadata.get("source_url")
    if isinstance(url, str) and url.strip():
        documento.source_url = url.strip()


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
        _atualizar_origem_documento(documento, metadata)
        return documento, False

    documento = Document(
        corpus_version_id=corpus_version_id,
        source_file=source_file,
        title=None,
        base_id=str(metadata.get("baseId") or metadata.get("base_id") or ""),
        doc_type=str(metadata.get("tipoEntidade") or metadata.get("doc_type") or ""),
        source_url=None,
        sensitivity=SENSIBILIDADE_PADRAO,
    )
    _atualizar_origem_documento(documento, metadata)
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
    data_publicacao = metadata.get(
        "dataAssinatura",
        metadata.get("dataAberturaProposta", metadata.get("data_publicacao")),
    )
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


def _data_hora(valor: Any) -> datetime | None:
    if not valor:
        return None
    try:
        return datetime.fromisoformat(str(valor).replace("Z", "+00:00"))
    except ValueError:
        return None


def persistir_catalogo_documentos_pncp(
    db: Session,
    manifestos: Iterable[tuple[str, str, Path]],
    tamanho_commit: int = 1_000,
) -> dict[str, int]:
    """Persiste manifestos originais do PNCP como catálogo, sem baixar nada.

    Cada tupla é ``(tipo_entidade, periodo_coleta, caminho_manifesto)``. A
    idempotência usa ``tipo + numeroControlePNCP + sequencialDocumento``. Em
    uma nova listagem, título, URL e demais informações são atualizados, mas
    nenhum arquivo é consultado na rede.
    """

    if tamanho_commit <= 0:
        raise ValueError("tamanho_commit deve ser maior que zero.")

    existentes = {
        (
            item.tipo_entidade,
            item.numero_controle_pncp,
            item.sequencial_documento,
        ): item
        for item in db.scalars(select(DocumentCatalogEntry)).all()
    }
    resumo = {
        "manifestosLidos": 0,
        "entidadesLidas": 0,
        "documentosLidos": 0,
        "catalogados": 0,
        "atualizados": 0,
        "ignoradosInvalidos": 0,
    }
    pendentes_commit = 0

    for tipo_entidade, periodo_coleta, caminho in manifestos:
        if tipo_entidade not in {"contrato", "contratacao"}:
            raise ValueError(f"Tipo de entidade inválido: {tipo_entidade}")
        if not caminho.is_file():
            raise FileNotFoundError(f"Manifesto não encontrado: {caminho}")
        try:
            entidades = json.loads(caminho.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Manifesto JSON inválido: {caminho}") from exc
        if not isinstance(entidades, list):
            raise ValueError(f"Manifesto deve conter uma lista: {caminho}")

        resumo["manifestosLidos"] += 1
        for entidade in entidades:
            if not isinstance(entidade, dict):
                resumo["ignoradosInvalidos"] += 1
                continue
            resumo["entidadesLidas"] += 1
            controle = entidade.get("numeroControlePNCP")
            documentos = entidade.get("documentos") or []
            if not isinstance(controle, str) or not controle or not isinstance(documentos, list):
                resumo["ignoradosInvalidos"] += 1
                continue

            for documento in documentos:
                if not isinstance(documento, dict):
                    resumo["ignoradosInvalidos"] += 1
                    continue
                sequencial_documento = documento.get("sequencialDocumento")
                if not isinstance(sequencial_documento, int):
                    resumo["ignoradosInvalidos"] += 1
                    continue
                resumo["documentosLidos"] += 1
                chave = (tipo_entidade, controle, sequencial_documento)
                item = existentes.get(chave)
                valores = {
                    "cnpj_orgao": str(
                        documento.get("cnpj") or entidade.get("cnpjOrgao") or ""
                    ) or None,
                    "ano": documento.get("anoCompra") or entidade.get(
                        "anoContrato" if tipo_entidade == "contrato" else "anoCompra"
                    ),
                    "sequencial_entidade": documento.get("sequencialCompra") or entidade.get(
                        "sequencialContrato" if tipo_entidade == "contrato" else "sequencialCompra"
                    ),
                    "tipo_documento": documento.get("tipoDocumentoNome"),
                    "titulo": documento.get("titulo"),
                    "url_download": documento.get("url") or documento.get("uri"),
                    "uri_original": documento.get("uri"),
                    "data_publicacao_pncp": _data_hora(documento.get("dataPublicacaoPncp")),
                    "status_ativo": documento.get("statusAtivo"),
                    "periodo_coleta": periodo_coleta,
                    "manifesto_origem": caminho.as_posix(),
                }
                if item is None:
                    item = DocumentCatalogEntry(
                        tipo_entidade=tipo_entidade,
                        numero_controle_pncp=controle,
                        sequencial_documento=sequencial_documento,
                        **valores,
                    )
                    db.add(item)
                    existentes[chave] = item
                    resumo["catalogados"] += 1
                else:
                    for campo, valor in valores.items():
                        setattr(item, campo, valor)
                    resumo["atualizados"] += 1
                pendentes_commit += 1
                if pendentes_commit >= tamanho_commit:
                    db.commit()
                    pendentes_commit = 0

    db.commit()
    return resumo


def _url_canonica_pncp_catalogo(item: DocumentCatalogEntry) -> str | None:
    """Monta uma URL PNCP estável sem reaproveitar portas temporárias da API."""

    if not (
        item.cnpj_orgao
        and item.ano is not None
        and item.sequencial_entidade is not None
    ):
        return item.url_download
    recurso = "contratos" if item.tipo_entidade == "contrato" else "compras"
    return (
        "https://pncp.gov.br/pncp-api/v1/orgaos/"
        f"{item.cnpj_orgao}/{recurso}/{item.ano}/"
        f"{item.sequencial_entidade}/arquivos/{item.sequencial_documento}"
    )


def serializar_catalogo_documento(item: DocumentCatalogEntry) -> dict[str, Any]:
    """Formato público do catálogo usado pelo endpoint e pelo fallback RAG."""

    return {
        "id": item.id,
        "tipoEntidade": item.tipo_entidade,
        "numeroControlePNCP": item.numero_controle_pncp,
        "cnpjOrgao": item.cnpj_orgao,
        "ano": item.ano,
        "sequencialEntidade": item.sequencial_entidade,
        "sequencialDocumento": item.sequencial_documento,
        "tipoDocumento": item.tipo_documento,
        "titulo": item.titulo,
        "urlDownload": _url_canonica_pncp_catalogo(item),
        "urlOriginal": item.url_download,
        "dataPublicacaoPncp": (
            item.data_publicacao_pncp.isoformat()
            if item.data_publicacao_pncp is not None
            else None
        ),
        "statusAtivo": item.status_ativo,
        "periodoColeta": item.periodo_coleta,
    }


def consultar_catalogo_documentos_pncp(
    db: Session,
    *,
    numero_controle_pncp: str | None = None,
    tipo_entidade: str | None = None,
    tipo_documento: str | None = None,
    titulo: str | None = None,
    limite: int = 20,
) -> list[dict[str, Any]]:
    """Consulta localmente o catálogo PNCP, sem acionar a API externa."""

    if not any([numero_controle_pncp, tipo_entidade, tipo_documento, titulo]):
        raise ValueError("Informe ao menos um filtro para consultar o catálogo.")
    if not 1 <= limite <= 100:
        raise ValueError("limite deve estar entre 1 e 100.")

    consulta = select(DocumentCatalogEntry)
    if numero_controle_pncp:
        consulta = consulta.where(
            DocumentCatalogEntry.numero_controle_pncp == numero_controle_pncp.strip()
        )
    if tipo_entidade:
        consulta = consulta.where(DocumentCatalogEntry.tipo_entidade == tipo_entidade)
    for coluna, valor in (
        (DocumentCatalogEntry.tipo_documento, tipo_documento),
        (DocumentCatalogEntry.titulo, titulo),
    ):
        if valor and valor.strip():
            consulta = consulta.where(
                func.normalizar_busca(coluna).like(
                    f"%{normalizar_para_busca(valor)}%"
                )
            )

    consulta = consulta.order_by(
        DocumentCatalogEntry.periodo_coleta.desc(),
        DocumentCatalogEntry.sequencial_documento.asc(),
    ).limit(limite)
    return [serializar_catalogo_documento(item) for item in db.scalars(consulta)]


def persistir_chunks_jsonl_normativos(
    db: Session,
    corpus_version_id: int,
    arquivo_chunks: Path,
    urls_por_arquivo: dict[str, str] | None = None,
    tamanho_commit: int = 500,
) -> dict[str, int]:
    """Persiste o JSONL da base normativa no SQLite, sem FAISS/embeddings."""

    if not arquivo_chunks.is_file():
        raise FileNotFoundError(f"Arquivo de chunks não encontrado: {arquivo_chunks}")
    urls_por_arquivo = urls_por_arquivo or {}
    resumo = {
        "linhasLidas": 0,
        "linhasInvalidas": 0,
        "documentosCriados": 0,
        "documentosReutilizados": 0,
        "chunksCriados": 0,
        "chunksReutilizados": 0,
    }
    chunk_ids_vistos = set(db.scalars(select(DocumentChunk.chunk_id)).all())
    documentos_cache: dict[str, Document] = {}
    pendentes_commit = 0

    with arquivo_chunks.open(encoding="utf-8") as arquivo:
        for linha in arquivo:
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
            conteudo = item.get("texto")
            metadata = item.get("metadata")
            if not isinstance(conteudo, str) or not isinstance(metadata, dict):
                resumo["linhasInvalidas"] += 1
                continue
            chunk_id = metadata.get("chunk_id")
            source_file = metadata.get("source_file")
            if not isinstance(chunk_id, str) or not chunk_id or not isinstance(source_file, str):
                resumo["linhasInvalidas"] += 1
                continue
            resumo["linhasLidas"] += 1
            metadata = dict(metadata)
            metadata["source_url"] = urls_por_arquivo.get(source_file)
            chave_documento = _document_source_file(metadata)
            documento = documentos_cache.get(chave_documento)
            if documento is None:
                documento, criado = _obter_ou_criar_documento(
                    db, corpus_version_id, metadata
                )
                documentos_cache[chave_documento] = documento
                resumo["documentosCriados" if criado else "documentosReutilizados"] += 1
            if chunk_id in chunk_ids_vistos:
                resumo["chunksReutilizados"] += 1
                continue
            db.add(_criar_chunk(documento, chunk_id, conteudo, metadata))
            chunk_ids_vistos.add(chunk_id)
            resumo["chunksCriados"] += 1
            pendentes_commit += 1
            if pendentes_commit >= tamanho_commit:
                db.commit()
                pendentes_commit = 0
    db.commit()
    return resumo


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
    progresso: Callable[[int, int], None] | None = None,
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

    # O JSONL é percorrido duas vezes: primeiro para informar o total na barra
    # e depois para persistir. A segunda passagem continua sendo a fonte de
    # verdade; não carregamos todos os chunks em memória.
    with arquivo_chunks.open(encoding="utf-8") as arquivo:
        total_linhas = sum(1 for linha in arquivo if linha.strip())
    if progresso is not None:
        progresso(0, total_linhas)

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
    linhas_processadas = 0

    with arquivo_chunks.open(encoding="utf-8") as arquivo:
        for numero_linha, linha in enumerate(arquivo, start=1):
            if not linha.strip():
                continue
            linhas_processadas += 1
            try:
                item = json.loads(linha)
            except json.JSONDecodeError:
                resumo["linhasInvalidas"] += 1
                if progresso is not None:
                    progresso(linhas_processadas, total_linhas)
                continue

            if not isinstance(item, dict):
                resumo["linhasInvalidas"] += 1
                if progresso is not None:
                    progresso(linhas_processadas, total_linhas)
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
                if progresso is not None:
                    progresso(linhas_processadas, total_linhas)
                continue

            resumo["linhasLidas"] += 1
            tipo_entidade = str(metadata.get("tipoEntidade") or "")
            if tipos_entidade is not None and tipo_entidade not in tipos_entidade:
                resumo["linhasIgnoradasTipo"] += 1
                if progresso is not None:
                    progresso(linhas_processadas, total_linhas)
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

            if chunk_id in chunk_ids_vistos:
                resumo["chunksReutilizados"] += 1
                if progresso is not None:
                    progresso(linhas_processadas, total_linhas)
                continue

            db.add(_criar_chunk(documento, chunk_id, conteudo, metadata))
            chunk_ids_vistos.add(chunk_id)
            resumo["chunksCriados"] += 1
            novos_desde_commit += 1
            if novos_desde_commit >= tamanho_commit:
                db.commit()
                novos_desde_commit = 0

            if progresso is not None:
                progresso(linhas_processadas, total_linhas)

    db.commit()
    return resumo
