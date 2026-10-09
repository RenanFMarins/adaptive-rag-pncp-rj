"""
Persistência da base normativa (editais_normativo) no banco.

Lê data/processed/<versao>_editais_normativo.jsonl e grava cada trecho em
documents/document_chunks — as tabelas que o FTS5 indexa por trigger e que a
indexação do FAISS consulta. Enquanto os trechos ficam só no arquivo, uma
pergunta sobre lei ou decreto não encontra nada: o analisador escolhe a rota
documental e a recuperação volta vazia.

A tabela tem um conjunto fixo de colunas e não guarda metadado livre. Os
campos próprios da base normativa (artigo, cláusula, parte, overlap) seguem
no JSONL, que continua sendo a fonte completa, e podem ser derivados do
chunk_id, cujo formato é estável nos 794 trechos:

    editais_normativo:<documento>:<artigo ou cláusula>:p<parte>

O número da norma ou do edital vai em documents.title ("Decreto RJ 48.760",
"Lei 14.133"). A coluna vigencia fica vazia de propósito: ela significa fim
de vigência, e o que a base normativa tem é data de publicação, que já vai na
coluna própria — repetir uma na outra inventaria um dado que não existe.

Idempotente pelo chunk_id: rodar de novo ignora o que já está gravado e
continua de onde parou.

Uso:
    python -m app.modules.normative.persistencia --versao v1
"""

import argparse
import json
from datetime import date
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import SessionLocal, init_db
from app.modules.corpus.model import CorpusVersion
from app.modules.documents.model import Document, DocumentChunk

BASE_ID = "editais_normativo"
PASTA_PROCESSADOS = Path("data/processed")
TAMANHO_COMMIT = 500      # a cada N trechos novos o banco é gravado
STATUS_VERSAO = "ready"

# ---------------------------------------------------------------------------
# 1. Caminhos e nomes
# ---------------------------------------------------------------------------

def arquivo_da_versao(versao: str, pasta: Path = PASTA_PROCESSADOS) -> Path:
    """data/processed/v1_editais_normativo.jsonl"""
    return Path(pasta) / f"{versao}_{BASE_ID}.jsonl"


def nome_da_versao(versao: str) -> str:
    """
    Nome da linha em corpus_versions. Fica separado do corpus do PNCP
    (pncp-2026-08) porque as duas bases são coletadas e versionadas
    de formas diferentes.
    """
    return f"normativo-{versao}"


# ---------------------------------------------------------------------------
# 2. O que dá para derivar do chunk_id
# ---------------------------------------------------------------------------

def partes_do_chunk_id(chunk_id: str) -> dict | None:
    """
    Quebra o chunk_id nos quatro pedaços que ele carrega. Serve para montar a
    citação ("Art. 86 do Decreto 48.760") sem precisar de coluna no banco.

    Devolve None se o formato não for o esperado, para quem chama decidir o
    que fazer em vez de receber um pedaço errado em silêncio.
    """
    pedacos = chunk_id.split(":")
    if len(pedacos) != 4:
        return None
    base_id, documento, trecho, parte = pedacos
    if not parte.startswith("p") or not parte[1:].isdigit():
        return None
    return {
        "base_id": base_id,
        "documento": documento,
        "trecho": trecho,
        "parte": int(parte[1:]),
    }


# ---------------------------------------------------------------------------
# 3. Leitura do JSONL
# ---------------------------------------------------------------------------

def _data(texto) -> date | None:
    if not isinstance(texto, str) or not texto.strip():
        return None
    try:
        return date.fromisoformat(texto[:10])
    except ValueError:
        return None


def _titulo(metadata: dict) -> str | None:
    """
    Leis e decretos têm numero_norma; editais têm numero_edital.
    Os dois são o título do documento.
    """
    return metadata.get("numero_norma") or metadata.get("numero_edital")


def linha_valida(item) -> bool:
    """
    Uma linha só entra no banco se tiver o texto e os metadados obrigatórios
    do enunciado. O que não tiver é contado como inválido e o arquivo segue.
    """
    if not isinstance(item, dict):
        return False
    metadata = item.get("metadata")
    if not isinstance(metadata, dict):
        return False
    if not isinstance(item.get("texto"), str) or not item["texto"].strip():
        return False
    obrigatorios = ("source_file", "doc_type", "chunk_id", "sensitivity", "base_id")
    return all(isinstance(metadata.get(campo), str) and metadata[campo] for campo in obrigatorios)


# ---------------------------------------------------------------------------
# 4. Banco
# ---------------------------------------------------------------------------

def obter_ou_criar_versao(db: Session, versao: str) -> CorpusVersion:
    nome = nome_da_versao(versao)
    encontrada = db.scalar(select(CorpusVersion).where(CorpusVersion.version == nome))
    if encontrada is not None:
        return encontrada
    nova = CorpusVersion(version=nome, status=STATUS_VERSAO)
    db.add(nova)
    db.flush()
    return nova


def _criar_documento(corpus_version_id: int, metadata: dict) -> Document:
    return Document(
        corpus_version_id=corpus_version_id,
        source_file=metadata["source_file"],
        title=_titulo(metadata),
        base_id=metadata["base_id"],
        doc_type=metadata["doc_type"],
        source_url=None,
        sensitivity=metadata["sensitivity"],
    )


def _criar_chunk(documento: Document, texto: str, metadata: dict) -> DocumentChunk:
    return DocumentChunk(
        document_id=documento.id,
        chunk_id=metadata["chunk_id"],
        content=texto,
        doc_type=documento.doc_type,
        base_id=documento.base_id,
        sensitivity=documento.sensitivity,
        orgao=metadata.get("orgao"),
        ano=metadata.get("ano"),
        data_publicacao=_data(metadata.get("data_publicacao")),
        vigencia=None,
    )


# ---------------------------------------------------------------------------
# 5. Persistência
# ---------------------------------------------------------------------------

def persistir_jsonl(
    db: Session,
    corpus_version_id: int,
    arquivo: Path,
    tamanho_commit: int = TAMANHO_COMMIT,
) -> dict:
    """
    Percorre o JSONL e grava o que ainda não está no banco.

    A idempotência é pelo chunk_id: uma segunda execução lê o arquivo inteiro
    de novo, pula o que já existe e grava só o que falta.
    """
    arquivo = Path(arquivo)
    if not arquivo.is_file():
        raise FileNotFoundError(f"JSONL da base normativa não encontrado: {arquivo}")
    if tamanho_commit <= 0:
        raise ValueError("tamanho_commit deve ser maior que zero.")

    resumo = {
        "linhas": 0,
        "invalidas": 0,
        "documentos_criados": 0,
        "documentos_reaproveitados": 0,
        "chunks_criados": 0,
        "chunks_ja_existentes": 0,
    }

    ja_no_banco = set(db.scalars(select(DocumentChunk.chunk_id)).all())
    documentos: dict[str, Document] = {}
    desde_o_commit = 0

    with arquivo.open(encoding="utf-8") as entrada:
        for linha in entrada:
            if not linha.strip():
                continue
            try:
                item = json.loads(linha)
            except json.JSONDecodeError:
                resumo["invalidas"] += 1
                continue
            if not linha_valida(item):
                resumo["invalidas"] += 1
                continue

            resumo["linhas"] += 1
            metadata = item["metadata"]
            chunk_id = metadata["chunk_id"]
            if chunk_id in ja_no_banco:
                resumo["chunks_ja_existentes"] += 1
                continue

            source_file = metadata["source_file"]
            documento = documentos.get(source_file)
            if documento is None:
                documento = db.scalar(
                    select(Document).where(
                        Document.corpus_version_id == corpus_version_id,
                        Document.source_file == source_file,
                    )
                )
                if documento is None:
                    documento = _criar_documento(corpus_version_id, metadata)
                    db.add(documento)
                    db.flush()
                    resumo["documentos_criados"] += 1
                else:
                    resumo["documentos_reaproveitados"] += 1
                documentos[source_file] = documento

            db.add(_criar_chunk(documento, item["texto"], metadata))
            ja_no_banco.add(chunk_id)
            resumo["chunks_criados"] += 1
            desde_o_commit += 1
            if desde_o_commit >= tamanho_commit:
                db.commit()
                desde_o_commit = 0

    db.commit()
    return resumo


def persistir(versao: str = "v1", arquivo: Path | None = None) -> dict:
    """Abre o banco, garante a versão do corpus e grava o JSONL da versão."""
    caminho = Path(arquivo) if arquivo else arquivo_da_versao(versao)
    init_db()
    with SessionLocal() as db:
        corpus = obter_ou_criar_versao(db, versao)
        resumo = persistir_jsonl(db, corpus.id, caminho)
    return resumo


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Persistência da base normativa no banco")
    parser.add_argument("--versao", default="v1")
    parser.add_argument("--arquivo", default=None)
    args = parser.parse_args()
    relatorio = persistir(args.versao, args.arquivo)
    print(
        f"  [versao]    {nome_da_versao(args.versao)}\n"
        f"  [linhas]    {relatorio['linhas']} lidas · {relatorio['invalidas']} inválidas\n"
        f"  [documento] {relatorio['documentos_criados']} criados · "
        f"{relatorio['documentos_reaproveitados']} reaproveitados\n"
        f"  [trecho]    {relatorio['chunks_criados']} gravados · "
        f"{relatorio['chunks_ja_existentes']} já estavam no banco"
    )
