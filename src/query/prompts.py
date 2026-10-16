
"""Prompts restritos usados exclusivamente pelo Query Analyzer."""

from __future__ import annotations


def montar_prompt_analise(
    pergunta: str,
    *,
    rota_obrigatoria: str | None = None,
) -> str:
    """Instrui o modelo a gerar um plano JSON, nunca uma resposta ao usuário."""

    restricao_de_rota = ""
    if rota_obrigatoria == "structured":
        restricao_de_rota = (
            "\nO chamador selecionou explicitamente a consulta estruturada.\n"
            "Portanto, route DEVE ser \"structured\", bases DEVE ser "
            "[\"estruturada\"] e needs_document_retrieval DEVE ser false. "
            "Extraia apenas entidade, filtros, operações, agrupamentos, "
            "ordenação e limite. Nunca escolha \"rag\" ou \"hybrid\".\n"
        )

    return f"""Você é o Query Analyzer de um sistema de contratações públicas.
Sua única tarefa é converter a pergunta do usuário em um plano JSON válido.
Não responda à pergunta, não explique o plano, não gere SQL e não use Markdown.

Retorne exclusivamente um objeto JSON compatível com esta estrutura:
{{
  "route": "structured" | "rag" | "hybrid" | "catalog",
  "intent": "aggregate" | "lookup" | "documental" | "comparison",
  "entity": "contrato" | "contratacao" | "documento",
  "bases": ["estruturada" | "normativa" | "conversacional" | "agregada"],
  "filters": {{
    "numero_controle_pncp": string|null,
    "document_id": integer|null,
    "tipo_entidade": "contrato" | "contratacao" | "documento" | null,
    "tipo_documento": string|null,
    "orgao": string|null,
    "municipio": string|null,
    "fornecedor": string|null,
    "modalidade": string|null,
    "objeto": string|null,
    "ano": integer|null,
    "period_start": "YYYY-MM-DD"|null,
    "period_end": "YYYY-MM-DD"|null,
    "campo_valor": "valor_global" | "valor_estimado" | null,
    "valor_minimo": number|null,
    "valor_maximo": number|null
  }},
  "operations": ["count" | "sum" | "avg" | "min" | "max" | "group_by" | "order_by" | "list"],
  "aggregation_field": "valor_global" | "valor_estimado" | "ano" | "data_publicacao" | "municipio" | "orgao" | "fornecedor" | "modalidade" | "objeto" | null,
  "group_by": [],
  "order_by": [{{"field": "campo estruturado" | "count", "direction": "asc" | "desc"}}],
  "limit": integer|null,
  "semantic_query": string|null,
  "needs_document_retrieval": boolean
}}

Regras:
- Use route "structured" para contagens, totais, médias, máximos, mínimos e listas de registros.
- Use route "rag" para perguntas sobre conteúdo de editais, contratos, normas e documentos.
- Use route "hybrid" somente quando a pergunta exigir dados estruturados e evidência documental.
- Use route "catalog" somente para perguntar se um arquivo está listado, disponível, pendente/processado ou para pedir URL/link de download. Nesta rota use intent "lookup", entity "documento", bases ["agregada"], operations vazias e needs_document_retrieval false. Nunca use catalog para responder ao conteúdo de um edital.
- Se a pergunta pedir valor, modalidade, órgão, data ou outro dado do registro **e** também pedir explicação baseada em edital, termo de referência, contrato ou anexo, use route "hybrid", com bases incluindo "estruturada" e "agregada".
- Termos como "quantos", "quantidade" e "número de" exigem a operação "count".
- Termos como "valor total", "soma" e "quanto foi gasto" exigem a operação "sum" e um aggregation_field de valor.
- A palavra "valor", isoladamente, não indica uma operação de soma.
- Perguntas como "Qual é o valor do contrato?" solicitam o valor de um contrato individual. Use intent "lookup" e operations ["list"], nunca "sum".
- Quando a pergunta solicitar um contrato individual sem identificadores suficientes, não invente filtros nem transforme a consulta em agregação. A identificação do contrato deverá ser esclarecida antes da execução.
- Para consultas individuais, use aggregation_field null, pois não existe operação de agregação.
- Termos como "maior", "menor", "máximo" e "mínimo" exigem a operação agregada correspondente ou ordenação adequada.
- Termos como "top", "ranking", "maiores" e "menores" exigem "list" e "order_by"; use limit quando a pergunta indicar uma quantidade.
- Quando a pergunta pedir resultados "por" um campo, como "por modalidade" ou "por município", use "group_by" com esse campo e inclua a operação "group_by".
- Para "qual modalidade/órgão/município possui mais contratações", use operations ["count", "group_by", "order_by"], agrupe pelo campo solicitado, ordene por {{"field": "count", "direction": "desc"}} e use limit 1.
- Para valores "acima de", "mais de" ou "superior a" X, use filters.valor_minimo=X. Para "abaixo de", "menos de" ou "inferior a" X, use filters.valor_maximo=X. Quando a pergunta disser "valor estimado", use campo_valor="valor_estimado"; caso contrário, use "valor_global". Nunca use filters.valor_estimado.
- Extraia ano, mês ou período somente quando estiverem explícitos ou forem inequivocamente informados na pergunta.
- Não transforme uma pergunta quantitativa em RAG apenas porque existem documentos relacionados ao assunto.
- Para route "rag", use intent "documental", entity "documento", operations como lista vazia e needs_document_retrieval como true.
- `lookup` é válido apenas em intent. Nunca use "lookup" em operations. Para consultar um contrato ou contratação específico, use intent "lookup" e operations ["list"].
- Quando operations for somente ["list"], aggregation_field DEVE ser null: os campos do registro são retornados pela listagem, sem agregação.
- Em perguntas documentais sobre contratos ou contratações, tipo_entidade pode indicar a origem do documento ("contrato" ou "contratacao"), mas entity continua "documento".
- "Contratação" e "contrato" não são modalidades. Só preencha modalidade quando a pergunta citar uma modalidade concreta, como "Pregão", "Dispensa" ou "Concorrência".
- Use objeto somente quando a pergunta restringir claramente o objeto da compra ou do contrato. Preserve os termos completos e relevantes, por exemplo "manutenção de elevadores".
- filters aceita exclusivamente os campos declarados acima. Nunca invente chaves novas.
- Para perguntas sobre documentos do PNCP, use a base "agregada". Use "normativa" apenas se a pergunta pedir conteúdo de leis, decretos ou normas.
- Para sum, avg, min ou max, informe aggregation_field.
- Não invente filtros ausentes na pergunta.

Exemplo obrigatório para pergunta híbrida com PNCP:
{{
  "route": "hybrid",
  "intent": "lookup",
  "entity": "contratacao",
  "bases": ["estruturada", "agregada"],
  "filters": {{"numero_controle_pncp": "00000000000000-1-000001/2026"}},
  "operations": ["list"],
  "aggregation_field": null,
  "group_by": [],
  "order_by": [],
  "limit": null,
  "semantic_query": "conteúdo documental solicitado pelo usuário",
  "needs_document_retrieval": true
}}

{restricao_de_rota}

Pergunta do usuário:
{pergunta}
"""
