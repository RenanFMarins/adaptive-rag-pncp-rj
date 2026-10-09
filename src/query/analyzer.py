from __future__ import annotations

import json
import re

from pydantic import ValidationError

from llm_ecoa import gerar_resposta
from src.query.schemas import QueryAnalysis


ANALYZER_SYSTEM_PROMPT = """
Você é o Query Analyzer de um sistema de perguntas e respostas
sobre Contratações Públicas do Estado do Rio de Janeiro.

Sua função é interpretar a pergunta do usuário e produzir SOMENTE
um JSON válido seguindo exatamente o schema fornecido.

Você NÃO deve:
- responder a pergunta;
- gerar SQL;
- inventar dados;
- inventar valores;
- executar consultas;
- recuperar documentos.

Você deve apenas identificar:
- intenção;
- entidade;
- rota;
- operação;
- campo;
- filtros;
- bases necessárias.

ROTAS POSSÍVEIS:

1. structured
Use quando a pergunta puder ser respondida diretamente pelos
dados estruturados/agregados.

Exemplos:
- quantos contratos existem?
- qual o valor total?
- qual foi o maior contrato?
- qual município teve maior valor?
- quantos contratos ocorreram em determinado período?
- quais são os cinco maiores contratos?

2. rag
Use quando a pergunta depende do conteúdo textual de documentos,
normas, decretos, editais, atas ou e-mails.

Exemplos:
- o que determina o Decreto 48.760?
- quais são as regras previstas na norma?
- o que determinado edital estabelece?

3. hybrid
Use quando a pergunta exige combinar dados estruturados com
informação documental.

Exemplo:
- quais contratos ultrapassaram o limite estabelecido pelo decreto?

INTENÇÕES POSSÍVEIS:

- lookup
- aggregate
- comparison
- ranking
- document_question
- normative_question
- conversational_question
- unknown

ENTIDADES POSSÍVEIS:

- contratos
- contratacoes
- itens_contratacao
- resultados_item
- pca
- documentos
- atas
- emails
- fornecedores
- orgaos
- municipios
- normas
- unknown

OPERAÇÕES ESTRUTURADAS COMUNS:

- COUNT
- SUM
- AVG
- MIN
- MAX
- GROUP_BY
- ORDER_BY
- FILTER

REGRAS IMPORTANTES:

1. Perguntas envolvendo "total", "soma", "quanto foi gasto",
   "valor total" normalmente indicam SUM.

2. Perguntas envolvendo "quantos", "quantidade", "número de"
   normalmente indicam COUNT.

3. Perguntas envolvendo "maior", "menor", "máximo" ou "mínimo"
   normalmente indicam MAX ou MIN.

4. Perguntas envolvendo "maiores", "ranking", "top" normalmente
   indicam ORDER_BY.

5. Perguntas envolvendo período devem extrair ano, mês e/ou
   periodo_inicio/periodo_fim quando possível.

6. Nunca transforme uma pergunta quantitativa em RAG apenas porque
   existem documentos relacionados ao assunto.

7. Para perguntas quantitativas sobre contratos, contratações,
   valores, fornecedores, municípios ou órgãos, prefira structured.

8. Para perguntas sobre o conteúdo de uma norma ou documento,
   prefira rag.

9. Para perguntas que explicitamente combinam números/dados com
   regras ou conteúdo documental, use hybrid.

10. Se não houver informação suficiente para determinar a rota,
    use "unknown" apenas quando realmente necessário.

11. Não invente filtros que não estejam presentes ou claramente
    implícitos na pergunta.

12. A resposta deve ser SOMENTE JSON válido.
"""


def _remover_markdown_json(texto: str) -> str:
    """
    Remove cercas de markdown caso a LLM retorne:

    ```json
    {...}
    ```
    """

    texto = texto.strip()

    texto = re.sub(
        r"^```json\s*",
        "",
        texto,
        flags=re.IGNORECASE,
    )

    texto = re.sub(
        r"^```\s*",
        "",
        texto,
    )

    texto = re.sub(
        r"\s*```$",
        "",
        texto,
    )

    return texto.strip()


def _extrair_json(texto: str) -> str:
    """
    Tenta localizar o primeiro objeto JSON na resposta da LLM.
    """

    texto = _remover_markdown_json(texto)

    inicio = texto.find("{")
    fim = texto.rfind("}")

    if inicio == -1 or fim == -1 or fim <= inicio:
        raise ValueError(
            "O Query Analyzer não retornou um objeto JSON válido."
        )

    return texto[inicio : fim + 1]


def _normalizar_analysis(
    analysis: QueryAnalysis,
    pergunta: str,
) -> QueryAnalysis:
    """
    Garante coerência entre route e flags.
    """

    requires_sql = analysis.route in {"structured", "hybrid"}
    requires_rag = analysis.route in {"rag", "hybrid"}

    return analysis.model_copy(
        update={
            "requires_sql": requires_sql,
            "requires_rag": requires_rag,
            "original_question": pergunta,
        }
    )


def analisar_pergunta(
    pergunta: str,
    llm_fn=gerar_resposta,
) -> QueryAnalysis:
    """
    Analisa uma pergunta e retorna um QueryAnalysis validado.

    Esta função NÃO:
    - executa SQL;
    - consulta o banco;
    - executa RAG;
    - chama FAISS;
    - chama BM25;
    - gera a resposta final.

    Ela somente transforma linguagem natural em um plano
    estruturado que será utilizado posteriormente pelo Router.
    """

    pergunta = pergunta.strip()

    if not pergunta:
        raise ValueError("A pergunta não pode ser vazia.")

    prompt = f"""
{ANALYZER_SYSTEM_PROMPT}

SCHEMA ESPERADO:

{QueryAnalysis.model_json_schema()}

PERGUNTA DO USUÁRIO:

{pergunta}

Retorne somente o JSON correspondente ao QueryAnalysis.
"""

    resposta_llm = llm_fn(prompt)

    try:
        json_text = _extrair_json(resposta_llm)
        dados = json.loads(json_text)

    except json.JSONDecodeError as exc:
        raise ValueError(
            "O Query Analyzer retornou JSON inválido."
        ) from exc

    try:
        analysis = QueryAnalysis.model_validate(dados)

    except ValidationError as exc:
        raise ValueError(
            "A saída do Query Analyzer não respeita o schema definido."
        ) from exc

    return _normalizar_analysis(
        analysis=analysis,
        pergunta=pergunta,
    )


if __name__ == "__main__":
    pergunta = input("Pergunta: ").strip()

    resultado = analisar_pergunta(pergunta)

    print(
        json.dumps(
            resultado.model_dump(
                mode="json",
            ),
            ensure_ascii=False,
            indent=2,
        )
    )