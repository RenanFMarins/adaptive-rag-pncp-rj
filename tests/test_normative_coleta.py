"""
Testes da coleta da base normativa (app/modules/normative/services.py).

Rodam sem internet: usam arquivos pequenos criados na hora, numa pasta
temporária (tmp_path), e nunca baixam nada.

    pytest tests/test_normative_coleta.py -v
"""

import hashlib

from app.modules.normative import services


# --- detectar_tipo: reconhece o arquivo pelo conteúdo ----------------------

def test_reconhece_pdf():
    assert services.detectar_tipo(b"%PDF-1.7 ...") == "pdf"


def test_reconhece_html():
    assert services.detectar_tipo(b"<html><body>Lei</body></html>") == "html"


def test_erro_do_pncp_nao_e_documento():
    # É assim que o PNCP responde quando falha (erro 422)
    erro = b'{"status":"422","error":"422 UNPROCESSABLE_ENTITY"}'
    assert services.detectar_tipo(erro) is None


# --- nome_do_arquivo: o mesmo link sempre gera o mesmo nome ----------------

def test_nome_de_edital_do_pncp():
    url = "https://pncp.gov.br/pncp-api/v1/orgaos/42498600000171/compras/2025/921/arquivos/1"
    assert services.nome_do_arquivo(url) == "pncp_42498600000171_2025_921_arq1"


def test_nome_da_lei_do_planalto():
    url = "https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2021/lei/l14133.htm"
    assert services.nome_do_arquivo(url) == "planalto_l14133"


# --- idempotência: arquivo que já existe não é baixado de novo -------------

def test_arquivo_ja_baixado_e_encontrado(tmp_path):
    (tmp_path / "planalto_l14133.html").write_text("<html></html>")
    assert services.ja_baixado(tmp_path, "planalto_l14133") is not None


def test_arquivo_que_nao_existe_nao_e_encontrado(tmp_path):
    assert services.ja_baixado(tmp_path, "planalto_l14133") is None


# --- decretos baixados à mão: o sha256 precisa bater com o manifesto -------

def _bloco_local(pasta_manual, conteudo, sha256):
    (pasta_manual / "decreto-teste.pdf").write_bytes(conteudo)
    return {
        "pasta": str(pasta_manual) + "/",
        "arquivos": [{"arquivo": "decreto-teste.pdf", "sha256": sha256,
                      "origem": "https://exemplo.gov.br/decreto-teste"}],
    }


def test_decreto_com_hash_certo_e_copiado(tmp_path):
    manual, destino = tmp_path / "manual", tmp_path / "raw"
    manual.mkdir(); destino.mkdir()
    conteudo = b"%PDF-1.4 decreto de teste"
    bloco = _bloco_local(manual, conteudo, hashlib.sha256(conteudo).hexdigest())

    registros = services.coletar_arquivos_locais(bloco, destino)

    assert registros[0]["status"] == "ok"
    assert (destino / "decreto-teste.pdf").exists()


def test_decreto_com_hash_diferente_vira_falha(tmp_path):
    manual, destino = tmp_path / "manual", tmp_path / "raw"
    manual.mkdir(); destino.mkdir()
    bloco = _bloco_local(manual, b"%PDF-1.4 decreto alterado", "0" * 64)

    registros = services.coletar_arquivos_locais(bloco, destino)

    assert registros[0]["status"] == "falhou"
    assert not (destino / "decreto-teste.pdf").exists()
