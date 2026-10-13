"""Console local para validar a API do RAG sem substituir Swagger ou FastAPI.

O token fica apenas em ``st.session_state``: não é gravado no projeto, banco
ou arquivo de configuração. A tela chama a API HTTP real, validando também
autenticação e os contratos de resposta dos endpoints.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import requests
import streamlit as st


RAIZ_PROJETO = Path(__file__).resolve().parents[1]
ARQUIVO_CASOS = RAIZ_PROJETO / "tests" / "fixtures" / "query_cases.json"
URL_API_PADRAO = "http://127.0.0.1:8000"


def _casos_fixos() -> list[dict[str, Any]]:
    if not ARQUIVO_CASOS.is_file():
        return []
    conteudo = json.loads(ARQUIVO_CASOS.read_text(encoding="utf-8"))
    return conteudo.get("cases", []) if isinstance(conteudo, dict) else []


def _chamar_api(
    metodo: str,
    url: str,
    *,
    token: str,
    params: dict[str, Any] | None = None,
    corpo: dict[str, Any] | None = None,
) -> tuple[int | None, dict[str, Any] | str]:
    headers = {"Authorization": f"Bearer {token}"} if token.strip() else {}
    try:
        resposta = requests.request(
            metodo, url, headers=headers, params=params, json=corpo, timeout=120
        )
    except requests.RequestException as exc:
        return None, f"Não foi possível alcançar a API: {exc}"
    try:
        return resposta.status_code, resposta.json()
    except ValueError:
        return resposta.status_code, resposta.text


def _exibir_status(status: int | None, conteudo: dict[str, Any] | str) -> None:
    if status is None:
        st.error(str(conteudo))
    elif status == 401:
        st.warning("Token ausente, inválido ou expirado. Cole um token novo na barra lateral.")
    elif status >= 400:
        st.error(f"A API retornou HTTP {status}.")
    else:
        st.success(f"HTTP {status}")


def _exibir_resultado_ask(conteudo: dict[str, Any] | str) -> None:
    if not isinstance(conteudo, dict):
        st.code(str(conteudo))
        return
    if conteudo.get("answer"):
        st.subheader("Resposta")
        st.write(conteudo["answer"])
    abas = st.tabs(["Rota e análise", "SQL", "Fontes", "Catálogo", "Bruto"])
    with abas[0]:
        st.json({chave: conteudo.get(chave) for chave in ("route", "analysis", "plan")})
    with abas[1]:
        st.json(conteudo.get("structured_result"))
    with abas[2]:
        st.json(conteudo.get("sources", []))
    with abas[3]:
        externos = conteudo.get("external_documents", [])
        if externos:
            st.info("Arquivos listados no PNCP, ainda sem chunks processados.")
        st.json(externos)
    with abas[4]:
        st.json(conteudo)


def main() -> None:
    st.set_page_config(page_title="Console RAG PNCP", page_icon="🔎", layout="wide")
    st.title("Console de validação — RAG PNCP")
    st.caption("Cliente da FastAPI; não baixa documentos, não altera o banco e não salva token.")

    with st.sidebar:
        st.header("Conexão")
        url_api = st.text_input("URL da API", value=URL_API_PADRAO).rstrip("/")
        token = st.text_input(
            "Access token", type="password", help="Fica somente nesta sessão do Streamlit."
        )
        if st.button("Limpar token"):
            st.session_state.clear()
            st.rerun()
        st.caption("Inicie a FastAPI em outro terminal antes de consultar.")

    aba_pergunta, aba_catalogo, aba_casos, aba_historico = st.tabs(
        ["Perguntar", "Catálogo PNCP", "Casos de teste", "Histórico"]
    )

    with aba_pergunta:
        pergunta = st.text_area(
            "Pergunta", placeholder="Ex.: Quantas contratações existem por modalidade em 2026?"
        )
        top_k = st.slider("Top K documental", min_value=1, max_value=20, value=5)
        if st.button("Executar /query/ask", type="primary", disabled=not pergunta.strip()):
            with st.spinner("Aguardando a API..."):
                status, conteudo = _chamar_api(
                    "POST", f"{url_api}/query/ask", token=token,
                    corpo={"pergunta": pergunta.strip(), "top_k": top_k},
                )
            _exibir_status(status, conteudo)
            if status is not None and status < 400:
                _exibir_resultado_ask(conteudo)
            st.session_state.setdefault("historico", []).insert(
                0, {"pergunta": pergunta.strip(), "status": status, "resposta": conteudo}
            )

    with aba_catalogo:
        st.caption("Consulta local; não chama PNCP nem Ecoa.")
        controle = st.text_input("Número de controle PNCP", key="catalogo_controle")
        colunas = st.columns(3)
        tipo_entidade = colunas[0].selectbox("Tipo de entidade", ["", "contrato", "contratacao"])
        tipo_documento = colunas[1].text_input("Tipo de documento")
        titulo = colunas[2].text_input("Título contém")
        if st.button("Consultar /query/catalog/documents"):
            parametros = {
                chave: valor for chave, valor in {
                    "numero_controle_pncp": controle.strip(),
                    "tipo_entidade": tipo_entidade,
                    "tipo_documento": tipo_documento.strip(),
                    "titulo": titulo.strip(),
                }.items() if valor
            }
            if not parametros:
                st.warning("Informe ao menos um filtro.")
            else:
                status, conteudo = _chamar_api(
                    "GET", f"{url_api}/query/catalog/documents", token=token,
                    params=parametros,
                )
                _exibir_status(status, conteudo)
                st.json(conteudo)

    with aba_casos:
        st.caption("Casos versionados para validar o Query Analyzer e o Router.")
        for caso in _casos_fixos():
            with st.expander(f"{caso['id']} · {caso['expected']['route']}"):
                st.write(caso["question"])
                st.json(caso["expected"])
                st.caption(caso.get("note", ""))

    with aba_historico:
        historico = st.session_state.get("historico", [])
        if not historico:
            st.caption("Nenhuma chamada realizada nesta sessão.")
        for item in historico:
            with st.expander(f"HTTP {item['status']} · {item['pergunta']}"):
                st.json(item["resposta"])


if __name__ == "__main__":
    main()
