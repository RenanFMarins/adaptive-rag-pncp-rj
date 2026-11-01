# Revisão manual de respostas e citações — 01/11/2026

## Objetivo e proteções

Esta revisão avaliou quatro perguntas normativas públicas do benchmark
(`N1`, `N2`, `N4` e `N6`) contra o corpus operacional de 13 documentos e 794
chunks normativos. O fluxo usou o FAISS OpenAI v2, recuperação híbrida,
`top_k=10` e geração com o provedor configurado.

O SQLite foi aberto somente para leitura, a geração foi executada com
`persistir=False` e os eventos de auditoria minimizados foram direcionados a
`/tmp`. Nenhum banco, índice ou log operacional foi modificado. As perguntas
são sintéticas e públicas; este documento não reproduz respostas integrais.

Uma citação numericamente válida não garante que a afirmação esteja apoiada
pela fonte. Por isso, a avaliação combinou verificação estrutural e leitura
humana do texto recuperado.

## Diagnóstico inicial

| Caso | Tema | Parecer | Motivo principal |
| --- | --- | --- | --- |
| N1 | ME/EPP em licitações | aprovada com ressalvas | núcleo legal apoiado, mas condições de editais específicos foram apresentadas perto de regras gerais |
| N2 | dispensa por valor | necessita correção | a resposta desviou para emergência e habilitação; o art. 75 esperado não apareceu diretamente entre as evidências finais |
| N4 | vigência contratual | necessita correção | misturou prazo de um edital específico e vigência de ata com o regime geral dos contratos |
| N6 | modalidades e pregão | aprovada | modalidades, uso do pregão e exceções foram sustentados pelos arts. 6º, 28 e 29 da Lei 14.133/2021 |

Resultado inicial: uma resposta aprovada, uma aprovada com ressalvas e duas
que necessitavam correção.

## Correção e revalidação

Foram aplicadas duas correções pequenas e auditáveis:

1. consultas explicitamente normativas e jurídicas gerais passaram a priorizar
   leis e decretos, preservando o score RRF original; consultas a edital ou
   documento concreto não usam essa reordenação;
2. o gerador passou a separar regra geral de exemplo de edital, respeitar o
   recorte causal da pergunta e distinguir contrato de ata.

A continuidade de seção também traz a primeira parte de um artigo quando uma
continuação relevante é ranqueada. Isso fez o início do art. 75 acompanhar a
continuação recuperada, sem alterar o índice nem recalcular seus scores.

| Caso | Parecer após correção | Evidência da melhoria |
| --- | --- | --- |
| N1 | aprovada | resposta usa Lei art. 4º e decretos gerais; não generaliza vedação de edital específico |
| N2 | aprovada com ressalva formal | limita-se às hipóteses de baixo valor e apresenta R$ 100 mil/R$ 50 mil; a citação ao final da lista sustenta ambos os itens, mas poderia ser repetida em cada item |
| N4 | aprovada | usa arts. 105, 111 e 113 e não apresenta vigência de ata como prazo contratual |
| N6 | aprovada | permaneceu correta, sem regressão semântica |

A amostra foi aprovada quanto à fidelidade factual. O alerta estrutural de N2
é conservador e foi mantido visível: não existe citação fora do intervalo nem
afirmação sem fonte material, mas o marcador compartilhado no fim da lista não
atende à preferência de uma citação repetida por item.

## Achados por caso

### N1 — microempresas e empresas de pequeno porte

O tratamento favorecido, a preferência no desempate, a contratação exclusiva
quando aplicável e os limites do art. 4º da Lei 14.133/2021 estavam presentes
nas fontes. Entretanto, restrições de consórcio e sanções vieram de editais
concretos. Elas não devem ser generalizadas como regra universal sem indicar
que dependem do instrumento convocatório e do caso.

### N2 — dispensa em razão do valor

O Decreto estadual 48.820/2023 recuperado distingue as hipóteses dos incisos I
e II do art. 75. A resposta fez bem ao não inventar valores monetários ausentes
da evidência, mas acrescentou emergência/calamidade, que não responde ao recorte
"por causa do valor". Também usou o art. 70 e regra de habilitação do Decreto
48.778/2023, que tratam de documentação dispensável, e não do fundamento
material da contratação direta. A recuperação final deveria priorizar o art. 75
da Lei 14.133/2021.

### N4 — vigência de contrato administrativo

A conclusão de que não existe um prazo único está correta. Os arts. 105, 111 e
113 da Lei 14.133/2021 apoiam, respectivamente, a previsão no edital e a
disponibilidade orçamentária, a prorrogação automática de contratos por escopo
e o limite do serviço associado. Porém, "12 meses" veio de uma contratação
específica e não deve ser chamado de contrato padrão. O prazo de uma ata de
registro de preços, art. 84, também não é prazo do contrato dela decorrente.

### N6 — modalidades e uso do pregão

A enumeração das modalidades foi apoiada pelo art. 28; o conceito de pregão,
pelo art. 6º; e seu uso obrigatório para bens e serviços comuns, com as exceções
cabíveis, pelo art. 29. A referência complementar ao sistema de registro de
preços foi compatível com o Decreto estadual 48.843/2023. Não foi identificada
afirmação material sem apoio.

## Causas prováveis

1. Perguntas jurídicas gerais podem ranquear editais específicos acima da lei.
2. Similaridade temática não distingue fundamento material de regra processual
   próxima, como dispensa por valor versus dispensa de documentos.
3. A geração combina evidências heterogêneas mesmo quando uma fonte específica
   deveria ser tratada apenas como exemplo.
4. Marcadores corretos validam proveniência formal, mas não o escopo da alegação.

## Correções implementadas e pendência

1. A prioridade de legislação/decretos foi implementada somente no escopo
   jurídico geral e tem testes de não aplicação a editais concretos.
2. As instruções de não generalização e separação de entidades foram
   implementadas e revalidadas com respostas reais.
3. O recorte de dispensa exclusivamente por baixo valor recebeu uma restrição
   contextual próxima à pergunta, eliminando hipóteses de outro fundamento.
4. `eval.review_grounded_answers` passou a detectar citações fora do intervalo,
   fontes não usadas e blocos substantivos sem marcador.
5. Permanece como melhoria de formato repetir a fonte em cada item de uma lista,
   mesmo quando um marcador final sustenta o conjunto.

## Critério para encerrar a tarefa 21

- nenhuma citação fora do intervalo das fontes;
- toda afirmação documental material acompanhada de fonte pertinente;
- nenhuma regra de edital específico generalizada como regra legal;
- nenhuma mistura entre contrato, ata e procedimento;
- N1, N2, N4 e N6 aprovadas em nova execução controlada.

Os cinco critérios foram atendidos semanticamente; a ressalva de formatação de
N2 permanece documentada e não mascara o resultado do verificador estrutural.
