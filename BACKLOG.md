# Roadmap priorizado do Adaptive RAG PNCP/RJ

Atualizado em **31/10/2026** para refletir o estado real do repositório
pessoal. As estimativas indicam tempo de trabalho, não tempo de espera de APIs.

## Critérios

- **P0 — imediato:** bloqueia apresentação, segurança ou reprodutibilidade.
- **P1 — alto:** amplia uma capacidade central já demonstrável.
- **P2 — médio:** melhora cobertura, qualidade ou operação.
- **P3 — evolução:** desejável, mas não bloqueia a entrega atual.
- `[x]` concluído; `[ ]` pendente; `[~]` cobertura parcial ou piloto.

## P0 — menor tempo e maior prioridade

| Ordem | Tarefa | Estimativa | Estado | Critério de conclusão |
| ---: | --- | ---: | :---: | --- |
| 1 | Reorganizar o README de apresentação | 10–20 min | [x] | PR de documentação integrado |
| 2 | Criar `main` estável no repositório pessoal | 20–40 min | [x] | `main` publicada e definida como padrão |
| 3 | Atualizar este roadmap com o estado real | 30–60 min | [x] | tarefas concluídas e pendentes separadas |
| 4 | Escolher e adicionar uma licença | 15–30 min | [ ] | `LICENSE` compatível com os dados e o código |
| 5 | Expor `/health` e `/ready` sem dados sensíveis | 1–2 h | [x] | saúde da API e dependências verificáveis |
| 6 | Criar CI de Python e React | 1–2 h | [ ] | testes, lint e build executados em PRs |
| 7 | Revisar o PR amplo de limpeza do repositório | 1–2 h | [ ] | clone limpo validado antes de integrar o PR #1 |

## P1 — reprodutibilidade dos dados

| Ordem | Tarefa | Estimativa | Estado | Critério de conclusão |
| ---: | --- | ---: | :---: | --- |
| 8 | Gerar snapshot sanitizado da base normalizada | 2–4 h | [ ] | sem usuários, tokens, logs ou segredos |
| 9 | Compactar, dividir se necessário e gerar SHA-256 | 1–2 h | [ ] | artefatos verificáveis e dentro dos limites do GitHub |
| 10 | Publicar release versionada da base | 1 h | [ ] | release com cobertura, data e limitações documentadas |
| 11 | Criar script de download e restauração | 2–4 h | [ ] | instalação reproduzível sem versionar SQLite |
| 12 | Homologar em clone limpo | 2–4 h | [ ] | API, base normalizada e interface iniciam do zero |

## P1 — experiência conversacional

| Ordem | Tarefa | Estimativa | Estado | Critério de conclusão |
| ---: | --- | ---: | :---: | --- |
| 13 | Enviar contexto nas perguntas seguintes do React | 3–6 h | [ ] | conversa preserva filtros e entidade anterior |
| 14 | Exibir fontes, cobertura e limitações na interface | 2–4 h | [ ] | usuário distingue dado estruturado, documental e parcial |
| 15 | Publicar rotas de histórico com privacidade H1 | 4–8 h | [ ] | histórico autenticado e com retenção definida |
| 16 | Publicar rotas e interface de feedback | 4–8 h | [ ] | avaliação vinculada a `query_id`, sem payload sensível |

## P1 — RAG documental

| Ordem | Tarefa | Estimativa | Estado | Critério de conclusão |
| ---: | --- | ---: | :---: | --- |
| 17 | Importar o catálogo documental operacional | 4–8 h | [ ] | catálogo deixa de ter zero entradas |
| 18 | Integrar os 794 chunks normativos ao fluxo operacional | 1–2 dias | [~] | proveniência e versão preservadas |
| 19 | Regerar FAISS com um modelo de embedding compatível | 1 dia | [~] | índice deixa de ser apenas o piloto de 55 chunks |
| 20 | Comparar BM25, FAISS e RRF no mesmo benchmark | 1–2 dias | [ ] | métricas e conjunto de perguntas idênticos |
| 21 | Revisar respostas e citações manualmente | 4–8 h | [ ] | amostra aprovada e erros documentados |

## P2 — qualidade e cobertura dos dados

| Ordem | Tarefa | Estimativa | Estado | Critério de conclusão |
| ---: | --- | ---: | :---: | --- |
| 22 | Auditar 72 resultados com datas suspeitas | 2–4 h | [ ] | anomalias classificadas sem reescrever a RAW |
| 23 | Auditar anos anômalos de contratos e atas | 2–4 h | [ ] | origem e impacto documentados |
| 24 | Auditar 14 contratos acima de R$ 1 bilhão | 2–4 h | [ ] | valor, unidade e proveniência conferidos |
| 25 | Gerar relatório automático de qualidade e cobertura | 1 dia | [ ] | relatório reproduzível por snapshot |
| 26 | Ampliar a cobertura parcial de atas | 1–3 dias | [~] | inventário e janelas de coleta atualizados |
| 27 | Recuperar as quatro lacunas conhecidas de empenhos | 2–4 h | [~] | lacunas resolvidas ou justificadas |

## P2 — ingestão incremental completa

O incremental de `contratacao` está operacional. Os demais recursos possuem
componentes e testes, mas ainda precisam de ativação online controlada.

| Ordem | Recurso | Estimativa | Estado |
| ---: | --- | ---: | :---: |
| 28 | Contratos | 1–2 dias | [ ] |
| 29 | PCA | 1 dia | [ ] |
| 30 | Atas | 1–2 dias | [ ] |
| 31 | Itens de contratação | 1 dia | [ ] |
| 32 | Resultados homologados | 1–2 dias | [ ] |
| 33 | Empenhos | 1–2 dias | [ ] |
| 34 | Automação, alertas e retomada | 1–2 dias | [ ] |

## P3 — evoluções opcionais ou de maior risco

- [ ] Integrar a trilha sintética de e-mails da base conversacional.
- [ ] Adicionar Docker/Compose e estratégia de deploy.
- [ ] Avaliar reranker por cross-encoder com estudo de ablação.
- [ ] Reescrever o histórico Git para expurgar binários antigos somente com
  plano de coordenação, backup e aviso aos colaboradores.
- [ ] Relacionar PCA e contratação somente quando houver evidência oficial;
  `pca_contratacao_link` deve permanecer vazia enquanto isso não existir.

## Entregas já consolidadas

- [x] RAW versionada com identidade canônica, observações e checkpoints.
- [x] Normalização de órgãos, unidades, fornecedores, contratações,
  itens, resultados, contratos, empenhos, atas, PCAs e itens de PCA.
- [x] Base normalizada consumida em modo somente leitura.
- [x] SQL Tool, Analyzer, Planner, Adaptive Executor, API e interfaces.
- [x] Autenticação, minimização de logs (H1) e indisponibilidade segura
  do FAISS (H2).
- [x] Corpus normativo com 13 documentos e 794 chunks.
- [x] Testes automatizados: 816 aprovados, 35 ignorados e 118 subtestes na
  última auditoria completa.

As contagens e coberturas detalhadas ficam em
[`CORPUS_INVENTORY.md`](CORPUS_INVENTORY.md). A palavra `COMPLETE` nesse
inventário significa completo em relação ao snapshot do projeto, não a todo o
universo histórico do PNCP.
