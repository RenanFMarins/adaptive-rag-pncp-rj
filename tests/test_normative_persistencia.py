"""
Testes da persistência da base normativa (app/modules/normative/persistencia.py).

Rodam sem internet e sem tocar no app.db: cada teste cria um banco SQLite em
memória e um JSONL pequeno numa pasta temporária (tmp_path).

    pytest tests/test_normative_persistencia.py -v
"""

import json
import os
from unittest.mock import patch

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

with patch.dict(os.environ, {"DATABASE_URL": "sqlite:///:memory:"}):
    from app.core.database import create_sqlite_engine, init_db

from app.modules.corpus.model import CorpusVersion
from app.modules.documents.model import Document, DocumentChunk
from app.modules.normative import persistencia


# --- apoio -----------------------------------------------------------------

def trecho(chunk_id, source_file, texto="Art. 1º Esta lei entra em vigor.", **extra):
    metadata = {
        "source_file": source_file,
        "base_id": "editais_normativo",
        "sensitivity": "publico",
        "doc_type": "lei",
        "chunk_id": chunk_id,
        "data_publicacao": "2021-04-01",
        "ano": 2021,
        "parte": 1,
        "tem_overlap": False,
    }
    metadata.update(extra)
    return {"texto": texto, "metadata": metadata}


def escrever_jsonl(pasta, nome, itens):
    caminho = pasta / nome
    caminho.write_text(
        "\n".join(json.dumps(item, ensure_ascii=False) for item in itens) + "\n",
        encoding="utf-8",
    )
    return caminho


@pytest.fixture
def db():
    engine = create_sqlite_engine("sqlite:///:memory:")
    init_db(bind=engine)
    with Session(engine) as sessao:
        yield sessao


@pytest.fixture
def versao(db):
    return persistencia.obter_ou_criar_versao(db, "v1")


# --- caminhos e nomes ------------------------------------------------------

def test_arquivo_da_versao():
    caminho = persistencia.arquivo_da_versao("v1")
    assert caminho.name == "v1_editais_normativo.jsonl"


def test_versao_do_normativo_nao_colide_com_a_do_pncp():
    assert persistencia.nome_da_versao("v1") == "normativo-v1"
    assert persistencia.nome_da_versao("v2") == "normativo-v2"


# --- partes_do_chunk_id: a citação sem coluna no banco ---------------------

def test_deriva_norma_artigo_e_parte_do_chunk_id():
    partes = persistencia.partes_do_chunk_id(
        "editais_normativo:decreto-48760-2023-pca:art-86:p2"
    )
    assert partes == {
        "base_id": "editais_normativo",
        "documento": "decreto-48760-2023-pca",
        "trecho": "art-86",
        "parte": 2,
    }


def test_chunk_id_fora_do_formato_devolve_none():
    assert persistencia.partes_do_chunk_id("editais_normativo:lei:art-1") is None
    assert persistencia.partes_do_chunk_id("a:b:c:parte2") is None


# --- linha_valida: os 5 metadados obrigatórios -----------------------------

def test_linha_sem_metadado_obrigatorio_e_invalida():
    item = trecho("editais_normativo:lei:art-1:p1", "lei.pdf")
    del item["metadata"]["sensitivity"]
    assert persistencia.linha_valida(item) is False


def test_linha_sem_texto_e_invalida():
    item = trecho("editais_normativo:lei:art-1:p1", "lei.pdf", texto="   ")
    assert persistencia.linha_valida(item) is False


def test_linha_completa_e_valida():
    assert persistencia.linha_valida(trecho("editais_normativo:lei:art-1:p1", "lei.pdf"))


# --- versão do corpus ------------------------------------------------------

def test_versao_e_criada_uma_vez_so(db):
    primeira = persistencia.obter_ou_criar_versao(db, "v1")
    segunda = persistencia.obter_ou_criar_versao(db, "v1")
    assert primeira.id == segunda.id
    assert len(db.scalars(select(CorpusVersion)).all()) == 1


# --- gravação --------------------------------------------------------------

def test_grava_documento_e_trecho(db, versao, tmp_path):
    arquivo = escrever_jsonl(tmp_path, "v1_editais_normativo.jsonl", [
        trecho("editais_normativo:lei-14133:art-1:p1", "lei-14133.html",
               numero_norma="Lei 14.133"),
    ])
    resumo = persistencia.persistir_jsonl(db, versao.id, arquivo)

    assert resumo["chunks_criados"] == 1
    assert resumo["documentos_criados"] == 1

    chunk = db.scalar(select(DocumentChunk))
    assert chunk.base_id == "editais_normativo"
    assert chunk.doc_type == "lei"
    assert chunk.sensitivity == "publico"
    assert chunk.content.startswith("Art. 1º")
    assert chunk.data_publicacao.isoformat() == "2021-04-01"


def test_numero_da_norma_vai_para_o_titulo(db, versao, tmp_path):
    arquivo = escrever_jsonl(tmp_path, "v1_editais_normativo.jsonl", [
        trecho("editais_normativo:decreto-48760:art-1:p1", "decreto-48760.pdf",
               doc_type="decreto", numero_norma="Decreto RJ 48.760"),
    ])
    persistencia.persistir_jsonl(db, versao.id, arquivo)
    assert db.scalar(select(Document)).title == "Decreto RJ 48.760"


def test_numero_do_edital_tambem_vai_para_o_titulo(db, versao, tmp_path):
    arquivo = escrever_jsonl(tmp_path, "v1_editais_normativo.jsonl", [
        trecho("editais_normativo:edital-48:clausula-1:p1", "edital-48.pdf",
               doc_type="edital", numero_edital="Edital 48/2025",
               orgao="Prefeitura de Bom Jardim"),
    ])
    persistencia.persistir_jsonl(db, versao.id, arquivo)
    documento = db.scalar(select(Document))
    assert documento.title == "Edital 48/2025"
    assert db.scalar(select(DocumentChunk)).orgao == "Prefeitura de Bom Jardim"


def test_vigencia_fica_vazia(db, versao, tmp_path):
    # vigencia significa fim de vigência; a base normativa tem data de
    # publicação, que já vai na coluna própria.
    arquivo = escrever_jsonl(tmp_path, "v1_editais_normativo.jsonl", [
        trecho("editais_normativo:lei-14133:art-1:p1", "lei-14133.html"),
    ])
    persistencia.persistir_jsonl(db, versao.id, arquivo)
    assert db.scalar(select(DocumentChunk)).vigencia is None


def test_trechos_do_mesmo_arquivo_dividem_um_documento(db, versao, tmp_path):
    arquivo = escrever_jsonl(tmp_path, "v1_editais_normativo.jsonl", [
        trecho("editais_normativo:lei-14133:art-1:p1", "lei-14133.html"),
        trecho("editais_normativo:lei-14133:art-2:p1", "lei-14133.html"),
        trecho("editais_normativo:decreto-48760:art-1:p1", "decreto-48760.pdf"),
    ])
    resumo = persistencia.persistir_jsonl(db, versao.id, arquivo)
    assert resumo["chunks_criados"] == 3
    assert resumo["documentos_criados"] == 2


def test_rodar_de_novo_nao_duplica(db, versao, tmp_path):
    arquivo = escrever_jsonl(tmp_path, "v1_editais_normativo.jsonl", [
        trecho("editais_normativo:lei-14133:art-1:p1", "lei-14133.html"),
        trecho("editais_normativo:lei-14133:art-2:p1", "lei-14133.html"),
    ])
    persistencia.persistir_jsonl(db, versao.id, arquivo)
    segunda = persistencia.persistir_jsonl(db, versao.id, arquivo)

    assert segunda["chunks_criados"] == 0
    assert segunda["chunks_ja_existentes"] == 2
    assert len(db.scalars(select(DocumentChunk)).all()) == 2


def test_continua_de_onde_parou(db, versao, tmp_path):
    arquivo = escrever_jsonl(tmp_path, "v1_editais_normativo.jsonl", [
        trecho("editais_normativo:lei-14133:art-1:p1", "lei-14133.html"),
    ])
    persistencia.persistir_jsonl(db, versao.id, arquivo)

    arquivo = escrever_jsonl(tmp_path, "v1_editais_normativo.jsonl", [
        trecho("editais_normativo:lei-14133:art-1:p1", "lei-14133.html"),
        trecho("editais_normativo:lei-14133:art-2:p1", "lei-14133.html"),
    ])
    segunda = persistencia.persistir_jsonl(db, versao.id, arquivo)

    assert segunda["chunks_criados"] == 1
    assert segunda["chunks_ja_existentes"] == 1
    assert len(db.scalars(select(DocumentChunk)).all()) == 2


def test_linha_quebrada_nao_derruba_o_arquivo(db, versao, tmp_path):
    caminho = tmp_path / "v1_editais_normativo.jsonl"
    caminho.write_text(
        json.dumps(trecho("editais_normativo:lei:art-1:p1", "lei.html")) + "\n"
        + "{ isso nao e json\n"
        + json.dumps(trecho("editais_normativo:lei:art-2:p1", "lei.html")) + "\n",
        encoding="utf-8",
    )
    resumo = persistencia.persistir_jsonl(db, versao.id, caminho)
    assert resumo["chunks_criados"] == 2
    assert resumo["invalidas"] == 1


def test_data_invalida_nao_derruba_o_trecho(db, versao, tmp_path):
    arquivo = escrever_jsonl(tmp_path, "v1_editais_normativo.jsonl", [
        trecho("editais_normativo:lei:art-1:p1", "lei.html",
               data_publicacao="indisponivel"),
    ])
    persistencia.persistir_jsonl(db, versao.id, arquivo)
    assert db.scalar(select(DocumentChunk)).data_publicacao is None


def test_arquivo_que_nao_existe_avisa(db, versao, tmp_path):
    with pytest.raises(FileNotFoundError):
        persistencia.persistir_jsonl(db, versao.id, tmp_path / "nao_existe.jsonl")


def test_commit_em_lotes_grava_tudo(db, versao, tmp_path):
    itens = [
        trecho(f"editais_normativo:lei:art-{n}:p1", "lei.html")
        for n in range(1, 11)
    ]
    arquivo = escrever_jsonl(tmp_path, "v1_editais_normativo.jsonl", itens)
    resumo = persistencia.persistir_jsonl(db, versao.id, arquivo, tamanho_commit=3)
    assert resumo["chunks_criados"] == 10
    assert len(db.scalars(select(DocumentChunk)).all()) == 10


def test_tamanho_commit_invalido_avisa(db, versao, tmp_path):
    arquivo = escrever_jsonl(tmp_path, "v1_editais_normativo.jsonl", [
        trecho("editais_normativo:lei:art-1:p1", "lei.html"),
    ])
    with pytest.raises(ValueError):
        persistencia.persistir_jsonl(db, versao.id, arquivo, tamanho_commit=0)


# --- título que chega depois: a extração melhorou -------------------------

def test_titulo_vazio_e_preenchido_numa_passada_seguinte(db, versao, tmp_path):
    # Primeiro carregamento: a extração ainda não achava o número do edital.
    arquivo = escrever_jsonl(tmp_path, "sem_titulo.jsonl", [
        trecho("editais_normativo:edital-19:clausula-1:p1", "edital-19.pdf",
               doc_type="edital"),
    ])
    persistencia.persistir_jsonl(db, versao.id, arquivo)
    assert db.scalar(select(Document)).title is None

    # Segundo carregamento, com o JSONL reprocessado: o número apareceu.
    arquivo = escrever_jsonl(tmp_path, "com_titulo.jsonl", [
        trecho("editais_normativo:edital-19:clausula-1:p1", "edital-19.pdf",
               doc_type="edital", numero_edital="PREGÃO ELETRÔNICO N° 019/2025"),
    ])
    resumo = persistencia.persistir_jsonl(db, versao.id, arquivo)

    assert resumo["titulos_preenchidos"] == 1
    assert resumo["chunks_criados"] == 0, "nao pode duplicar trecho"
    assert db.scalar(select(Document)).title == "PREGÃO ELETRÔNICO N° 019/2025"


def test_titulo_ja_gravado_nao_e_sobrescrito(db, versao, tmp_path):
    arquivo = escrever_jsonl(tmp_path, "v1_editais_normativo.jsonl", [
        trecho("editais_normativo:lei-14133:art-1:p1", "lei-14133.html",
               numero_norma="Lei 14.133"),
    ])
    persistencia.persistir_jsonl(db, versao.id, arquivo)

    documento = db.scalar(select(Document))
    documento.title = "Lei 14.133 (corrigido à mão)"
    db.commit()

    resumo = persistencia.persistir_jsonl(db, versao.id, arquivo)

    assert resumo["titulos_preenchidos"] == 0
    assert db.scalar(select(Document)).title == "Lei 14.133 (corrigido à mão)"
