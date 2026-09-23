"""
Testes do processamento da base normativa (app/modules/ingest/services.py).

Rodam sem internet e em segundos: usam um documento de exemplo pequeno,
guardado em tests/fixtures/lei_trecho.html, e não dependem de data/raw/.

    pytest tests/test_ingest_normativa.py -v
"""

from pathlib import Path

import pytest

from app.modules.ingest import services

FIXTURE = Path(__file__).parent / "fixtures" / "lei_trecho.html"


@pytest.fixture(scope="module")
def chunks():
    """Processa o documento de exemplo uma vez e reaproveita nos testes."""
    return services.gerar_chunks(FIXTURE)


# --- 1. Metadados obrigatórios -------------------------------------------

def test_todo_chunk_tem_metadado_obrigatorio(chunks):
    obrigatorios = {"source_file", "doc_type", "chunk_id", "sensitivity", "base_id"}
    for c in chunks:
        faltando = obrigatorios - set(c["metadata"])
        assert not faltando, f"{c['metadata'].get('chunk_id')} sem: {faltando}"


def test_sensibilidade_definida_na_ingestao(chunks):
    # A classificação é feita agora, e não na hora de responder
    assert all(c["metadata"]["sensitivity"] == "publico" for c in chunks)


def test_chunk_id_nao_se_repete(chunks):
    ids = [c["metadata"]["chunk_id"] for c in chunks]
    assert len(ids) == len(set(ids))


# --- 2. O artigo não é cortado ao meio -----------------------------------

def _artigo(chunks, nome):
    return [c for c in chunks if c["metadata"].get("artigo") == nome]


def test_artigo_fica_com_seus_paragrafos_e_incisos(chunks):
    art1 = _artigo(chunks, "Art. 1")
    assert len(art1) == 1, "o Art. 1 deveria estar em um chunk só"

    texto = art1[0]["texto"]
    assert texto.startswith("Art. 1")
    for trecho in ["§ 1", "I - a administração direta", "II - as autarquias", "§ 2"]:
        assert trecho in texto, f"faltou no chunk do Art. 1: {trecho}"


def test_citacao_no_inicio_da_linha_nao_vira_artigo_novo(chunks):
    # No texto, "Art. 2º desta Lei" é uma citação dentro do § 2º do Art. 1º.
    # Ela não pode abrir um chunk novo, senão o artigo é partido ao meio.
    assert "Art. 2º desta Lei aos casos omissos" in _artigo(chunks, "Art. 1")[0]["texto"]


def test_artigos_na_ordem_e_sem_faltar(chunks):
    artigos = [c["metadata"]["artigo"] for c in chunks if c["metadata"].get("artigo", "").startswith("Art.")]
    assert artigos == ["Art. 1", "Art. 2", "Art. 3"]


# --- 3. Acentuação (HTML do Planalto é cp1252) ---------------------------

def test_acentos_saem_corretos(chunks):
    texto = " ".join(c["texto"] for c in chunks)
    assert "licitação" in texto
    assert "vigência" in texto
    assert "�" not in texto, "apareceu caractere quebrado: leia o HTML como cp1252"


# --- 4. Texto revogado (riscado) não entra no corpus ---------------------

def test_texto_riscado_nao_entra(chunks):
    texto = " ".join(c["texto"] for c in chunks)
    assert "REDACAO ANTIGA REVOGADA" not in texto


def test_versao_vigente_do_artigo_entra(chunks):
    # O mesmo Art. 2º tem uma redação riscada (antiga) e a vigente.
    # Só a vigente pode aparecer.
    assert "O prazo de vigência do contrato será de 12 (doze) meses" in _artigo(chunks, "Art. 2")[0]["texto"]
