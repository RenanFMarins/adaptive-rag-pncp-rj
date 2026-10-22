
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

Regras gerais de roteamento:
- Use route "structured" para contagens, totais, médias, máximos, mínimos e listas de registros.
- Use route "rag" para perguntas sobre conteúdo de editais, contratos, normas e documentos.
- Use route "hybrid" somente quando a pergunta exigir dados estruturados e evidência documental.
- Use route "catalog" somente para perguntar se um arquivo está listado, disponível, pendente/processado ou para pedir URL/link de download.
- Na rota "catalog", use intent "lookup", entity "documento", bases ["agregada"], operations vazias e needs_document_retrieval false.
- Nunca use "catalog" para responder ao conteúdo de um edital.
- Se a pergunta pedir valor, modalidade, órgão, data ou outro dado do registro e também pedir explicação baseada em edital, termo de referência, contrato ou anexo, use route "hybrid", com bases incluindo "estruturada" e "agregada".
- Não transforme uma pergunta quantitativa em RAG apenas porque existem documentos relacionados ao assunto.

Regras de operações estruturadas:
- Termos como "quantos", "quantidade" e "número de" exigem a operação "count".
- Termos como "valor total", "soma" e "quanto foi gasto" exigem a operação "sum" e um aggregation_field de valor.
- A palavra "valor", isoladamente, não indica uma operação de soma.
- Perguntas como "Qual é o valor do contrato?" solicitam o valor de um contrato individual. Use intent "lookup" e operations ["list"], nunca "sum".
- Quando a pergunta solicitar um contrato individual sem identificadores suficientes, não invente filtros nem transforme a consulta em agregação.
- A identificação de um contrato insuficientemente especificado deverá ser esclarecida antes da execução.
- Para consultas individuais, use aggregation_field null, pois não existe operação de agregação.
- Termos como "maior", "menor", "máximo" e "mínimo" exigem a operação agregada correspondente ou ordenação adequada.
- Termos como "top", "ranking", "maiores" e "menores" exigem "list" e "order_by".
- Use limit quando a pergunta indicar uma quantidade.
- Quando a pergunta pedir resultados "por" um campo, como "por modalidade" ou "por município", use "group_by" com esse campo e inclua a operação "group_by".
- Para "qual modalidade/órgão/município possui mais contratações", use operations ["count", "group_by", "order_by"], agrupe pelo campo solicitado, ordene por {{"field": "count", "direction": "desc"}} e use limit 1.
- Para valores "acima de", "mais de" ou "superior a" X, use filters.valor_minimo=X.
- Para valores "abaixo de", "menos de" ou "inferior a" X, use filters.valor_maximo=X.
- Quando a pergunta disser "valor estimado", use campo_valor="valor_estimado"; caso contrário, use "valor_global".
- Nunca use filters.valor_estimado.
- Para sum, avg, min ou max, informe aggregation_field.
- Quando operations for somente ["list"], aggregation_field DEVE ser null.
- O valor "lookup" é válido apenas em intent. Nunca use "lookup" em operations.

Regras de entidades e documentos:
- Para route "rag", use intent "documental", entity "documento", operations como lista vazia e needs_document_retrieval true.
- Para consultar um contrato ou contratação específico, use intent "lookup" e operations ["list"].
- Em perguntas documentais sobre contratos ou contratações, tipo_entidade pode indicar a origem do documento ("contrato" ou "contratacao"), mas entity continua "documento".
- "Contratação" e "contrato" não são modalidades.
- Só preencha modalidade quando a pergunta citar uma modalidade concreta, como "Pregão", "Dispensa" ou "Concorrência".
- Para perguntas sobre documentos do PNCP, use a base "agregada".
- Use "normativa" quando a pergunta pedir conteúdo de leis, decretos ou normas.
- Uma pergunta sobre atribuições previstas em decreto deve ser tratada como consulta documental à base "normativa".
- Não invente identificadores de documentos, números de controle PNCP ou tipos documentais não informados.

Regras de filtros:
- filters aceita exclusivamente os campos declarados no schema.
- Nunca invente chaves novas.
- Extraia ano, mês ou período somente quando estiverem explícitos ou forem inequivocamente informados na pergunta.
- Use objeto somente quando a pergunta restringir claramente o objeto da compra ou do contrato.
- Preserve os termos completos e relevantes do objeto, por exemplo "manutenção de elevadores".
- Não invente filtros ausentes na pergunta.
- Não transforme automaticamente palavras da pergunta em filtros quando elas representam apenas o assunto pesquisado.
- Não utilize filtros excessivamente restritivos que não estejam claramente justificados pela pergunta.

Regras de distinção entre órgão, município e jurisdição:
- Diferencie obrigatoriamente órgão público, localização geográfica e jurisdição normativa.
- Preencha filters.orgao somente quando a pergunta identificar explicitamente um órgão ou entidade pública.
- Exemplos de órgãos ou entidades: "Secretaria de Estado de Saúde", "Fundação Saúde", "Ministério da Educação" e "Tribunal de Contas do Estado do Rio de Janeiro".
- Não considere nomes de estados, isoladamente, como nomes de órgãos públicos.
- Expressões como "Estado do Rio de Janeiro", "legislação estadual do Rio de Janeiro", "normas do RJ", "decretos estaduais do RJ" e "legislação fluminense" indicam jurisdição, não órgão público.
- Quando "Rio de Janeiro" indicar apenas a jurisdição estadual, filters.orgao DEVE ser null.
- Não preencha filters.municipio quando a pergunta mencionar apenas um estado.
- A expressão "Estado do Rio de Janeiro" não significa automaticamente "Município do Rio de Janeiro".
- Preencha filters.municipio somente quando a pergunta identificar claramente um município como restrição geográfica da consulta.
- A presença de uma cidade no nome de um órgão não significa, por si só, que a pergunta está filtrando pelo município.
- Em perguntas sobre competências, atribuições ou obrigações previstas em legislação, não invente filtros de órgão, município ou objeto.
- A jurisdição de uma norma deve ser preservada no contexto semântico da consulta quando não houver um campo específico de jurisdição no schema.
- Não invente um campo "jurisdicao", pois ele não existe no schema atual.
- Não descarte nomes de estados ou referências geográficas da semantic_query quando forem importantes para identificar a legislação solicitada.

Exemplos obrigatórios de interpretação geográfica:

Pergunta: "Quais são as atribuições dos fiscais de contrato na legislação estadual do Rio de Janeiro?"
Interpretação:
- route = "rag"
- intent = "documental"
- entity = "documento"
- bases = ["normativa"]
- filters.orgao = null
- filters.municipio = null
- semantic_query = "atribuições dos fiscais de contrato na legislação estadual do Rio de Janeiro"
- needs_document_retrieval = true

Pergunta: "Quais obrigações contratuais são previstas nos documentos da Secretaria de Estado de Saúde?"
Interpretação:
- route = "rag"
- intent = "documental"
- entity = "documento"
- filters.orgao = "Secretaria de Estado de Saúde"
- Não atribua automaticamente um município.

Pergunta: "Quantas contratações foram realizadas no município de Niterói em 2026?"
Interpretação:
- route = "structured"
- intent = "aggregate"
- filters.municipio = "Niterói"
- filters.ano = 2026
- operations = ["count"]
- Não confunda município com órgão.

Regras de recuperação semântica:
- Para perguntas documentais, semantic_query deve representar o conteúdo que o usuário deseja encontrar.
- Preserve nomes de leis, decretos, artigos e números normativos quando informados.
- Não invente um número de decreto quando o usuário não o mencionar.
- Se a pergunta solicitar atribuições dos fiscais técnicos e administrativos, preserve esses termos na semantic_query.
- Não substitua o assunto específico por uma expressão excessivamente genérica.
- Não use filtros de metadados para representar conceitos que pertencem à pesquisa semântica.
- A escolha de bases e filtros deve respeitar o conteúdo explícito da pergunta.

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
