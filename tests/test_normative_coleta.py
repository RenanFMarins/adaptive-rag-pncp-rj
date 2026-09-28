"""
Testes da coleta da base normativa (app/modules/normative/services.py).

Rodam sem internet: usam arquivos pequenos criados na hora, numa pasta
temporária (tmp_path), e nunca baixam nada.

    pytest tests/test_normative_coleta.py -v
"""

import hashlib
import json

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


# --- versionamento: qual é a próxima versão -------------------------------

def test_primeira_versao_e_v1(tmp_path):
    assert services.proxima_versao(tmp_path) == "v1"


def test_proxima_versao_vem_depois_da_ultima(tmp_path):
    for nome in ["v1", "v2", "outra_pasta"]:
        (tmp_path / nome).mkdir()
    assert services.versoes_existentes(tmp_path) == ["v1", "v2"]
    assert services.proxima_versao(tmp_path) == "v3"


# --- hash do conteúdo: ignora o que muda a cada download ------------------

def test_script_do_html_nao_muda_o_hash_do_conteudo():
    # O Planalto gera um script de segurança diferente a cada acesso.
    # O documento é o mesmo, então o hash do conteúdo não pode mudar.
    a = b"<html><script>token=111</script><p>Art. 1.</p></html>"
    b = b"<html><script>token=999</script><p>Art. 1.</p></html>"
    assert services.sha256_do_conteudo(a, "html") == services.sha256_do_conteudo(b, "html")
    assert services.sha256_de(a) != services.sha256_de(b)


def test_mudanca_real_no_texto_muda_o_hash_do_conteudo():
    a = b"<html><p>Art. 1. Texto original.</p></html>"
    b = b"<html><p>Art. 1. Texto alterado.</p></html>"
    assert services.sha256_do_conteudo(a, "html") != services.sha256_do_conteudo(b, "html")


# --- diff entre versões ---------------------------------------------------

def _inventario(tmp_path, versao, registros, monkeypatch):
    monkeypatch.setattr(services, "PASTA_INVENTARIO", tmp_path)
    caminho = tmp_path / f"{versao}_{services.BASE_ID}.json"
    caminho.write_text(json.dumps(registros, ensure_ascii=False), encoding="utf-8")


def test_diff_classifica_entrou_saiu_mudou_e_identico(tmp_path, monkeypatch):
    def reg(origem, nome, h):
        return {"path": f"data/raw/v1/{nome}", "origem": origem, "sha256": h,
                "sha256_conteudo": h, "status": "ok", "bytes": 10, "tipo": "pdf"}

    v1 = [reg("u/identico", "a.pdf", "aaa"), reg("u/mudou", "b.pdf", "bbb"), reg("u/saiu", "c.pdf", "ccc")]
    v2 = [reg("u/identico", "a.pdf", "aaa"), reg("u/mudou", "b.pdf", "zzz"), reg("u/entrou", "d.pdf", "ddd")]
    _inventario(tmp_path, "v1", v1, monkeypatch)
    _inventario(tmp_path, "v2", v2, monkeypatch)

    texto = services.gerar_diff("v1", "v2").read_text(encoding="utf-8")

    assert "| Entraram | 1 |" in texto
    assert "| Saíram | 1 |" in texto
    assert "| Mudaram de conteúdo | 1 |" in texto
    assert "| Permaneceram idênticos | 1 |" in texto


def test_inventario_legivel_traz_totais(tmp_path, monkeypatch):
    registros = [{"path": "data/raw/v1/a.pdf", "origem": "u/a", "sha256": "a" * 64,
                  "sha256_conteudo": "a" * 64, "status": "ok", "bytes": 1000, "tipo": "pdf",
                  "coletado_em": "2026-09-25T10:00:00-03:00"}]
    _inventario(tmp_path, "v1", registros, monkeypatch)

    texto = services.escrever_inventario("v1").read_text(encoding="utf-8")

    assert "| Arquivos | 1 |" in texto
    assert "| Falhas | 0 |" in texto
    assert "Nenhuma." in texto

# --- inventário JSON no formato do enunciado -----------------------------

def test_inventario_json_tem_o_envelope_do_enunciado(tmp_path, monkeypatch):
    registros = [
        {"path": "data/raw/v1/a.pdf", "origem": "u/a", "sha256": "a" * 64,
         "sha256_conteudo": "a" * 64, "status": "ok", "bytes": 1000,
         "tipo": "pdf", "coletado_em": "2026-09-28T10:00:00-03:00"},
        {"path": None, "origem": "u/b", "sha256": None, "sha256_conteudo": None,
         "status": "falhou", "bytes": 0, "tipo": None, "erro": "HTTP 404",
         "coletado_em": "2026-09-28T10:00:01-03:00"},
    ]
    _inventario(tmp_path, "v1", registros, monkeypatch)

    manifesto = tmp_path / "manifesto.yaml"
    manifesto.write_text(
        "scenario_id: contratacoes-rj\n"
        "bases:\n"
        f"  - base_id: {services.BASE_ID}\n"
        "    natureza: normativa\n"
        "    volume_alvo: 2\n", encoding="utf-8")

    caminho = services.inventario_json("v1", str(manifesto))
    dados = json.loads(caminho.read_text(encoding="utf-8"))

    assert dados["scenario_id"] == "contratacoes-rj"
    assert dados["version"] == "v1"
    assert dados["manifest_hash"].startswith("sha256:")
    assert dados["totais"] == {"arquivos": 1, "bytes": 1000, "falhas": 1}
    assert dados["por_base"][0]["natureza"] == "normativa"
    assert dados["por_base"][0]["divergencia_alvo"] == 1
    assert dados["falhas"][0]["erro"] == "HTTP 404"


def test_base_ainda_nao_coletada_nao_aparece_no_inventario(tmp_path, monkeypatch):
    # Cada base entra sozinha quando a coleta dela rodar: ninguém espera ninguém.
    _inventario(tmp_path, "v1", [], monkeypatch)

    manifesto = tmp_path / "manifesto.yaml"
    manifesto.write_text(
        "scenario_id: contratacoes-rj\n"
        "bases:\n"
        f"  - base_id: {services.BASE_ID}\n"
        "    natureza: normativa\n"
        "    volume_alvo: 13\n"
        "  - base_id: contratos_estruturado\n"
        "    natureza: estruturada\n"
        "    volume_alvo: 1200\n", encoding="utf-8")

    dados = json.loads(services.inventario_json("v1", str(manifesto))
                       .read_text(encoding="utf-8"))

    assert [b["base_id"] for b in dados["por_base"]] == [services.BASE_ID]