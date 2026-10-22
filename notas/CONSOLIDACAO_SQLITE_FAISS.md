# Diagnóstico e preparação da consolidação PNCP + normativa

## Estado vigente — publicado localmente, 22/10/2026

A segunda aprovação do usuário foi executada. Somente
`RAG_FAISS_INDEX_DIR` no `.env` foi alterado de `data/index/faiss/v1` para
`data/index/faiss/staging/consolidacao_pncp_normativa_20261022_122148_66171c9c`.
A configuração ativa foi validada em processos novos, sem caminho manual no
serviço RAG: 67.276 vetores, sendo 66.482 PNCP e 794 normativos, sem órfãos,
duplicados ou inconsistências. Passaram os testes de leitura para PNCP, lei,
decreto e edital, com RRF e fontes/citações conferidos e sem gerar embeddings.

Nenhum serviço foi reiniciado, pois não havia serviço RAG ativo identificado.
Bancos e índices permaneceram intactos; 574 arquivos protegidos foram
verificados por SHA-256. Não houve deploy remoto, migração, commit ou push.
A primeira tentativa teve um erro de importação no utilitário de validação;
o rollback automático restaurou v1 e foi confirmado. A execução corrigida
passou, deixando o estado final **publicado localmente**.

Relatório vigente e rollback:
`notas/PUBLICACAO_FAISS_CONSOLIDADO_20261022.md` e
`notas/PUBLICACAO_FAISS_CONSOLIDADO_20261022.json`.
As restrições de “somente staging, aguardando segunda aprovação” nas seções
abaixo pertencem ao histórico, anterior à autorização de publicação.

---

## Histórico — criação e validação antes da publicação local

## Resultado vigente — staging real criado e validado, 22/10/2026

Execução autorizada limitada ao staging concluída, sem migração SQLite,
publicação, deploy ou reinício de serviços. Nenhuma configuração ativa foi
alterada. Esta seção substitui o estado de “somente dry-run” preservado abaixo.

**Índice consolidado:**

```text
F:\ecoa_projetos\rag-grande-desafio-grupo03-contratacoes-publicas\data\index\faiss\staging\consolidacao_pncp_normativa_20261022_122148_66171c9c
```

**Auditoria detalhada:**
`notas/consolidacao_staging_20261022_122148_66171c9c.json`.
Status final: `validated_staging_only`. O relatório contém inventário completo
com SHA-256, manifests, estado, mapas de IDs, auditoria de cobertura da aplicação,
resultados das consultas reais e histórico das verificações.

### Construção e auditoria em disco

O diretório exclusivo foi criado por `src.consolidacao.consolidate()`, com o
banco principal aberto em `mode=ro` e `query_only=ON`. **Não foi chamado
`migrate()`, `run(...execute=True)` nem a CLI `--executar`.** Os 13 documentos
e 794 chunks normativos do destino foram somente lidos e reutilizados, sem
sincronizar título, data ou corpus. Os mapas de IDs foram novamente conferidos
contra a origem e o destino antes da escrita do índice.

Snapshots consistentes dos dois SQLite foram gerados pela API de backup em
diretório temporário e removidos ao concluir. Não houve escrita SQL nos bancos
originais nem necessidade de restaurá-los.

O staging contém a cópia completa do índice PNCP gerenciado, sua base de
65.362 vetores, os 67 checkpoints anteriores (1.120 vetores) e um novo
checkpoint de 794 vetores normativos: `cp-00000068-fc74b39f`. Seu manifesto tem
SHA-256 `5b3fcf7acef86c41730821209db898b8f2a277f1703917fce920526786a81c9f`.
Mapas de IDs e hashes de conteúdo foram gerados junto do shard e referenciados
pelo estado gravado atomicamente. Os checkpoints normativos originais não
foram injetados ou sobrescritos.

| Métrica | Antes: staging/v2 | Novo staging em disco |
|---|---:|---:|
| Vetores PNCP | 66.482 | 66.482, idênticos |
| Vetores normativos | 0 | 794, idênticos à origem |
| Total de vetores | 66.482 | 67.276 |
| Checkpoints ativos | 67 | 68 |
| IDs duplicados | 0 | 0 |
| IDs órfãos | 0 | 0 |
| Inconsistências | 0 | 0 |
| Hashes de conteúdo divergentes | 0 | 0 |
| Documentos/chunks normativos no SQLite | 13 / 794 | 13 / 794, inalterados |
| Documentos/chunks PNCP no SQLite | 1.896 / 99.536 | 1.896 / 99.536, inalterados |

O índice foi recarregado e auditado após a gravação e novamente após os testes
de recuperação. Os 66.482 vetores PNCP foram comparados exatamente, em blocos;
os 794 vetores normativos foram comparados exatamente com o índice normativo.
Modelo `xagi/qwen3-embedding:0.6b-q4_k_m`, dimensão 1024, produto interno e
normalização unitária foram mantidos. Nenhum embedding documental foi gerado.

A normativa ficou com 100% de cobertura: 794 chunks e 13 documentos completos.
O PNCP mantém 66,79% de cobertura: 66.482 de 99.536 chunks. Os 33.054 chunks
PNCP pendentes não foram indexados ou descartados nesta operação.

### Consultas reais pela camada da aplicação

Foram usados `readonly_session()` e
`app.modules.rag.services.recuperar_chunks_ranqueados()` com o argumento
`cache_dir` apontando explicitamente para o novo staging. Os embeddings das
três consultas vieram do serviço real configurado, com o mesmo modelo e
dimensão. Não foram utilizados embeddings fictícios ou vetores de documentos
para simular consultas.

| Consulta | Filtros | Resultado nos dez primeiros |
|---|---|---|
| Especificações da maleta de testes e comissionamento de relés de proteção hexafásica | Base PNCP; controle `00394452000103-1-015448/2026` | 10 evidências; 10 com rank lexical e 10 com rank denso |
| Artigo 86 da Lei 14.133/2021 | Base normativa; documento da Lei | Artigo 86 em primeiro; 5 evidências lexicais e 5 densas |
| Obrigações de fiscalização no Decreto RJ 48.817/2023 | Base normativa; documento do decreto | 10 evidências; 10 com rank lexical e 10 com rank denso |

As três consultas passaram. Para cada resultado, foram conferidos o cálculo
do RRF (`sum(1/(60+rank))`), conteúdo, vínculo chunk/documento, base, título e
URL contra o SQLite. Os contextos numerados `[1]`, `[2]` etc. e os prompts
contêm os IDs e metadados corretos das fontes.

As mesmas consultas, com os mesmos embeddings de consulta e filtros, foram
comparadas com os índices originais correspondentes: staging/v2 para PNCP,
índice normativo para as duas perguntas normativas. IDs, ordem e scores RRF
coincidiram. Os exemplos são consultas com filtros explícitos, não uma
avaliação exaustiva de qualidade para todas as perguntas possíveis.

O carregador normal `carregar_indice_faiss()`, a validação de modelo usada pela
aplicação e o serviço RAG carregaram o novo índice sem alterações de código.
A configuração ativa continua apontando para `data/index/faiss/v1`; o novo
staging **não foi selecionado para produção**. Não foi iniciado servidor.

Escopo das citações: fontes recuperadas, URLs/títulos e contexto/prompt
numerado foram verificados. Não houve geração de resposta com LLM nem
persistência de consultas, respostas ou histórico no SQLite.

### Interrupções e diagnóstico registrados

O teste preliminar de acesso ao serviço de embeddings foi bloqueado pelo
sandbox (`WinError 10013`), antes da criação do staging. A mesma verificação,
com acesso de rede permitido, retornou um embedding válido de 1.024 dimensões.

Na primeira rodada de testes, uma asserção indevida exigiu que ao menos um
mesmo chunk aparecesse simultaneamente nas listas lexical e densa. A operação
foi interrompida para diagnóstico. O FTS5 retornava o artigo 86 em primeiro;
o RRF permite rankings disjuntos. A checagem foi corrigida para validar
contribuição dos dois rankings e a fórmula do RRF, preservando no relatório
a tentativa interrompida e seu traceback. Os testes de leitura então passaram.
Nenhum índice, banco, modelo ou configuração foi alterado para contornar essa
asserção. Não houve falha de integridade dos dados ou dos artefatos.

### Preservação e rollback

Os SHA-256 de **294 arquivos protegidos** foram iguais antes/depois, incluindo
`app.db`, `app_normativa.db`, todos os arquivos de v1, staging/v2, índice
normativo original, `.env` e `app/core/config.py`. Os próprios arquivos do novo
staging também permaneceram idênticos durante os testes de recuperação.

Não há alteração SQLite ou de configuração para desfazer. O rollback desta
etapa é **não selecionar o novo staging**, mantendo a configuração atual em
v1. O diretório novo pode permanecer sem uso para auditoria. Eventual remoção
ou arquivamento deve se limitar ao caminho exclusivo acima, preservando os
índices originais e o relatório. Não restaurar um backup sobre o banco atual:
o banco não foi migrado nesta etapa.

Auditoria somente leitura, reproduzível a partir da raiz:

```powershell
.venv/Scripts/python.exe -m src.base_estruturada.pipelines.pipeline_indexacao_faiss --auditar --indice-dir data/index/faiss/staging/consolidacao_pncp_normativa_20261022_122148_66171c9c
```

Publicação, alteração de `rag_faiss_index_dir`, deploy e reinício dependem da
segunda aprovação explícita e não foram executados.

---

## Histórico — correção e dry-run anteriores à criação do staging

## Resultado vigente — fluxo corrigido e dry-run aprovado, 22/10/2026

Esta seção substitui os bloqueios descritos nas seções históricas abaixo.
O fluxo de `src/consolidacao.py` foi corrigido e o dry-run completo retornou
**código 0, status `ready`, estratégia A**. Nenhuma consolidação real foi
executada. Bancos, índices originais e configuração permaneceram intactos.

### Correção implementada

A migração procura primeiro documentos normativos pela identidade estável
`base_id + source_file`, independentemente do nome local da versão de corpus.
Quando existe um único documento equivalente, reutiliza seu ID. Não cria outra
versão nem outro documento só porque a origem usa `normativo-v1` e o destino
usa `pncp-2026-08`. Títulos, datas de criação e vínculos de corpus do destino
são preservados; diferenças são explicitadas em
`migration.preserved_document_differences`.

Os demais metadados documentais continuam sendo validados estritamente.
Identidades ambíguas, metadados incompatíveis ou relacionamentos conflitantes
bloqueiam a transação. Para chunks, a comparação continua estrita por
`chunk_id`, conteúdo e metadados, depois de remapear `document_id` para o
documento existente. Não foi removida a verificação dos relacionamentos.

Só documentos efetivamente ausentes exigem criação de versão de corpus.
Se apenas alguns chunks estiverem ausentes de um documento já presente, eles
serão associados ao documento existente. Não há sincronização automática de
títulos, datas ou versões. Quando não há mudanças e o FTS5/triggers já estão
presentes, o índice lexical não é reconstruído desnecessariamente.

O mapa produzido é validado antes de integrar vetores: cada `chunk_id` do
índice normativo precisa corresponder ao ID SQL e ao documento de destino
declarados. Os IDs textuais FAISS são mantidos; nunca são substituídos pelos
IDs inteiros SQLite. O mesmo mapa é passado à consolidação futura, garantindo
que a associação aprovada no plano seja a utilizada na preparação do staging.

### Resultado do dry-run com os bancos atualizados

SQLite utilizado:
`F:\ecoa_projetos\rag-grande-desafio-grupo03-contratacoes-publicas\app.db`.
Origem: `app_normativa.db`. Índice PNCP selecionado explicitamente:
`data/index/faiss/staging/v2`. Índice normativo:
`indice/faiss_normativo_794`.

| Métrica | Antes | Depois no dry-run |
|---|---:|---:|
| Versões de corpus no destino | 1 | 1 |
| Documentos PNCP | 1.896 | 1.896 |
| Chunks PNCP | 99.536 | 99.536 |
| Documentos normativos | 13 | 13 |
| Chunks normativos | 794 | 794 |
| Novas versões/documentos/chunks | — | 0 / 0 / 0 |
| Documentos/chunks normativos reutilizados | — | 13 / 794 |
| Vetores PNCP | 66.482 | 66.482, preservados exatamente |
| Vetores normativos no índice PNCP | 0 | 794 previstos em memória |
| Total FAISS | 66.482 | 67.276 previstos em memória |
| IDs duplicados | 0 | 0 |
| IDs órfãos | 0 | 0 |

Mapas confirmados: documentos da origem 1–13 para destino 1.897–1.909;
chunks da origem 1–794 para destino 99.537–100.330. O mapa completo está em
`normative_chunk_mapping` e os mapas SQL em `migration.id_maps` do novo JSON.

O dry-run agora inclui a simulação vetorial: clona o FAISS em memória,
reaproveita somente os vetores normativos ausentes e verifica a preservação
exata dos vetores PNCP e normativos. Nenhum staging, checkpoint ou manifesto
novo é persistido nessa modalidade. O resultado real permanece com 66.482
vetores até uma execução autorizada; 67.276 é o total validado da simulação.

Modelos, dimensão 1024, produto interno, normalização e hashes continuam
compatíveis. Nenhum embedding novo foi gerado. Os 33.054 chunks PNCP ainda
sem vetores continuam pendentes, sem impedir o acréscimo da normativa.

Na reexecução, IDs vetoriais já presentes só são reutilizados se seus vetores
forem exatamente iguais. O plano conta zero novos vetores quando a normativa
já está no índice de entrada. Um staging existente não é sobrescrito.

### Testes e preservação

Comando executado:

```powershell
.venv/Scripts/python.exe -m pytest tests/integration/test_consolidacao.py tests/integration/test_hybrid_retrieval.py tests/integration/test_incremental_faiss_index.py tests/unit/test_retrieve_filters.py -q -p no:cacheprovider
```

**62 testes e 23 subtestes passaram**, incluindo 19 testes de consolidação.
Os novos testes cobrem: normativa integralmente presente sob outro corpus;
preservação do título, timestamp e corpus locais; mapas de IDs existentes;
reexecução SQLite sem inserções; dry-run sem alterar os arquivos de entrada;
consolidação/reconsolidação exclusivamente em índices temporários sem novos
vetores duplicados; rejeição de mapeamento SQL incorreto e de identidades
ambíguas; bloqueio de metadados de chunk conflitantes; carga parcial somente
dos chunks ausentes. A igualdade dos vetores PNCP e dos metadados pré-existentes
foi verificada nos testes e no dry-run.

Os SHA-256 de **299 arquivos protegidos** foram iguais antes/depois do dry-run,
incluindo ambos os bancos, índices originais, `.env` e `app/core/config.py`.
`app.db` já estava diferente da versão antiga rastreada pelo Git por causa da
atualização realizada pelo usuário; a verificação desta execução usa hashes
imediatamente anteriores e posteriores, não presume igualdade com o Git.

Arquivos alterados nesta correção: `src/consolidacao.py`,
`tests/integration/test_consolidacao.py` e este relatório. Resultado atual em
`notas/consolidacao_dry_run_corrigido.json`, com caminhos absolutos no comando,
código de saída, contagens, mapas, diferenças preservadas e hashes dos arquivos.
Os JSONs anteriores foram mantidos como histórico.

### Reprodução e condição para execução real

```powershell
.venv/Scripts/python.exe -m src.consolidacao --dry-run --origem app_normativa.db --destino app.db --pncp data/index/faiss/staging/v2 --normativo indice/faiss_normativo_794 --relatorio notas/consolidacao_proxima_simulacao.json
```

O arquivo de relatório deve ser novo. A reprodução não modifica os bancos
originais ou índices. O dry-run aprovado não autoriza a execução real.

**Não há bloqueio técnico encontrado para o reaproveitamento neste estado.**
Permanece necessária a autorização do usuário para preparar um staging real.
Uma execução posterior deve refazer as validações e backups consistentes antes
da escrita, auditar os manifests/checkpoints persistidos e testar recuperação
híbrida/citações no staging. Publicação, mudança de configuração e reinício
de serviços permanecem separados. As verificações atuais não incluem geração
de respostas com LLM nem publicação de novos artefatos FAISS reais.

---

## Histórico — reavaliação anterior à correção do fluxo

## Estado atualizado — app.db restaurado pelo usuário, 22/10/2026

Esta seção substitui as conclusões operacionais do diagnóstico inicial
preservado abaixo. Nesta reavaliação só foram executados diagnósticos, dry-run
em cópias temporárias e simulação vetorial em memória. Nenhum banco, índice,
configuração ou código de migração foi alterado.

**Conclusão:** o bloqueio dos 66.482 IDs PNCP órfãos foi resolvido no banco
atualizado. Os 794 vetores normativos podem ser reaproveitados. Entretanto,
**o dry-run da CLI `src.consolidacao.py` ainda falha**, agora por uma diferença
de identidade de corpus/vínculo documental no tratamento de registros já
existentes. Não executar `--executar` como está.

### Caminhos confirmados nesta execução

SQLite efetivamente utilizado, tanto na auditoria refeita quanto no dry-run:

```text
F:\ecoa_projetos\rag-grande-desafio-grupo03-contratacoes-publicas\app.db
```

`settings.database_url` resolveu para `sqlite:///./app.db`, com o diretório de
trabalho na raiz deste projeto. Não há ambiguidade de caminho nesta execução.
É possível confirmar o ambiente desta reexecução; não há registro de conexão
do comando que o usuário executou anteriormente para comprovar seu caminho
histórico de forma independente.

Origem normativa:
`F:\ecoa_projetos\rag-grande-desafio-grupo03-contratacoes-publicas\app_normativa.db`.

Índice PNCP auditado explicitamente:
`F:\ecoa_projetos\rag-grande-desafio-grupo03-contratacoes-publicas\data\index\faiss\staging\v2`.

Índice normativo auditado:
`F:\ecoa_projetos\rag-grande-desafio-grupo03-contratacoes-publicas\indice\faiss_normativo_794`.

A configuração efetiva da aplicação continua apontando para
`data/index/faiss/v1`. Auditar staging/v2 com caminho explícito não o coloca
em produção. A configuração foi apenas lida.

### Contagens verificadas no banco atualizado

| Métrica | Estado real atual | Simulação vetorial somente em memória |
|---|---:|---:|
| Documentos PNCP | 1.896 | inalterados |
| Chunks PNCP | 99.536 | inalterados |
| Vetores PNCP no staging/v2 | 66.482 | 66.482, idênticos |
| Chunks PNCP ainda sem vetores | 33.054 | inalterados |
| Documentos normativos | 13 | inalterados |
| Chunks normativos | 794 | inalterados |
| Vetores normativos no staging/v2 | 0 | 794 anexados em memória |
| Vetores totais | 66.482 | 67.276 |
| IDs duplicados no conjunto FAISS | 0 | 0 |
| IDs órfãos no conjunto FAISS | 0 | 0 |
| Inconsistências dos artefatos auditados | 0 | nenhum artefato novo persistido |

Os 33.054 chunks PNCP pendentes representam cobertura parcial do índice,
não IDs órfãos. Não precisam ser reindexados para acrescentar a normativa.
Ambos os SQLite passaram em `integrity_check` e `foreign_key_check`.

### Correspondência PNCP: confirmada

A CLI existente `pipeline_indexacao_faiss --auditar` reproduziu os resultados
informados pelo usuário: 66.482 vetores, todos ligados ao SQLite atualizado,
zero IDs duplicados/órfãos, zero conteúdos alterados com hash histórico e
nenhuma inconsistência. Há 1.327 documentos PNCP completos, 1 parcial e
568 sem vetores.

Além da igualdade de IDs, foram comparados os conteúdos dos 66.482 chunks
indexados do SQLite com os JSONLs canônicos: **66.482 correspondências,
zero conteúdos divergentes e zero diferenças no recálculo do chunk_id**.
Distribuição por arquivo:

| Lote JSONL | Chunks presentes no FAISS |
|---|---:|
| chunks_2026_08_lote_001.jsonl | 26.287 |
| chunks_2026_08_lote_002.jsonl | 20.925 |
| chunks_2026_08_lote_003.jsonl | 19.270 |
| chunks_2026_08_lote_004.jsonl | 0 |

Os 1.120 hashes de conteúdo dos checkpoints PNCP conferem com o banco.
Os 65.362 vetores legados não possuem hash histórico individual de conteúdo;
compará-los por IDs recalculados e conteúdo SQLite/JSONL aumenta a evidência
de procedência, mas não cria uma prova retrospectiva da entrada do serviço
de embeddings. Os manifests, checksums dos arquivos e mapas passaram na
auditoria atual.

### Comparação normativa: 794 conteúdos idênticos, diferenças documentais

Os 794 `chunk_id` textuais são exatamente os mesmos nos dois bancos: nenhum
ausente e nenhum adicional. Os 794 conteúdos e seus SHA-256 são idênticos.
Todos os metadados das linhas `document_chunks` também são idênticos,
exceto `id` e `document_id`, que são chaves internas de cada banco.

Mapeamentos verificados, não gravados:

- Documentos de origem 1–13 correspondem aos documentos de destino 1.897–1.909,
  pela chave `base_id + source_file`.
- Chunks de origem 1–794 correspondem aos chunks de destino 99.537–100.330,
  pelo `chunk_id` textual, preservando o documento correspondente.
- O mapa completo, com SHA-256 de cada conteúdo, está no novo JSON de auditoria.

Nos documentos, `source_file`, `source_url`, `base_id`, `doc_type` e
`sensitivity` coincidem. Foram encontradas diferenças reais:

1. Os 13 documentos têm datas de criação locais diferentes: destino
   `2026-10-12 21:00:35`; origem `2026-10-21 21:17:25`. São timestamps de
   persistência, não divergências de texto ou data de publicação.
2. Um documento, associado a 27 chunks, tem título diferente:
   `editais_normativo|pncp_42498600000171_2025_6553_arq1.pdf`.
   Na origem: `PREGÃO ELETRÔNICO N° 019/2025`; no destino:
   `pncp_42498600000171_2025_6553_arq1.pdf`. Essa diferença afeta apresentação
   de citações e filtros pelo título, não o conteúdo do embedding.
3. Embora `corpus_version_id=1` em ambos, o registro referenciado é diferente:
   origem `normativo-v1`; destino `pncp-2026-08`. IDs numéricos iguais em bancos
   diferentes não comprovam identidade de corpus.

Nenhum desses campos foi sincronizado, sobrescrito ou renumerado.

### Resultado do dry-run da CLI: bloqueio no fluxo de migração

O comando existente foi reexecutado com caminhos explícitos e retornou
código **1**, com:

```text
ValueError: Conteúdo/metadados conflitantes: document_chunks
{'chunk_id': 'editais_normativo:decreto-48760-2023-pca:preambulo:p1'}
```

Motivo verificado no código: `migrate()` primeiro procura/cria o corpus pela
coluna `version`. A origem usa `normativo-v1`, ausente no destino. Na cópia
temporária, o fluxo passa a preparar outros documentos nessa versão, porque
sua chave inclui `corpus_version_id`. Quando encontra o chunk já existente
pela chave global `chunk_id`, o `document_id` esperado é diferente do vínculo
atual. A comparação estrita de `put()` então recusa a operação.

**Essa mensagem não significa que o texto ou hash do chunk divergiu.** O
conflito ocorre no relacionamento que o plano de migração tentaria criar.
Alterar apenas a comparação do chunk, ignorando `document_id`, seria inseguro:
poderia deixar documentos duplicados e uma versão vazia no plano.

A migração falha dentro da transação e faz rollback da cópia temporária. O
banco real é aberto somente para leitura no dry-run. Como a exceção ocorre
antes da etapa final que salva `--relatorio`, o arquivo
`consolidacao_dry_run_atualizado.json` não foi gerado pela CLI. Para registrar
essa falha sem ocultá-la, comando, código de saída e traceback foram
capturados em `script_dry_run` do novo JSON.

### Reaproveitamento vetorial: aprovado nos diagnósticos

`validate_pair()` passou usando os dois índices e o banco atualizado.
Modelo de ambos: `xagi/qwen3-embedding:0.6b-q4_k_m`; dimensão 1024;
produto interno; vetores normalizados e sem inconsistências.
Os 794 hashes do índice normativo conferem tanto com a origem quanto com
o destino. Os IDs normativos não se sobrepõem aos 66.482 IDs PNCP.

Foi clonado o FAISS em memória e anexados os 794 vetores existentes:

- Total de 67.276 vetores, sem IDs duplicados ou órfãos.
- Todos os vetores PNCP preservados exatamente, comparados em blocos.
- Todos os vetores normativos preservados exatamente.
- Nenhum embedding novo e nenhum arquivo de índice ou staging criado.

O FAISS usa uma lista ordenada de `chunk_id` textuais, não os IDs SQL. Assim,
os IDs textuais podem ser mantidos sem transformação; os mapas SQL servem
para confirmar os relacionamentos. Não se deve substituir o mapa FAISS por
IDs 99.537–100.330. Cada vetor precisa continuar pareado com seu `chunk_id`
original e ser resolvido pelo SQLite do destino.

### Bloqueios e próximo passo proposto

**Não há bloqueio de correspondência banco/FAISS ou de compatibilidade de
embeddings. Há um bloqueio operacional na CLI que acopla migração SQLite e
consolidação vetorial.** A normativa já está persistida, portanto o plano
correto para esta situação deve prever zero novos documentos e zero novos
chunks no SQLite, preservando seus vínculos atuais.

Antes de autorizar uma execução completa pelo script, será necessário
preparar e testar um fluxo que consolide os índices sem repetir a migração
SQLite, ou uma revisão da migração que reconheça explicitamente a normativa
pré-existente e valide seus vínculos antes de produzir o plano. O código não
foi alterado nesta etapa, conforme o escopo de apenas diagnóstico/dry-run.

O título divergente deve ser preservado no destino nesta operação; eventual
enriquecimento com o título da origem deve ser uma alteração separada e
autorizada. Também não é necessário mover documentos para outra versão de
corpus para permitir a consolidação vetorial.

Depois da autorização e da preparação desse fluxo: gerar backups SQLite
consistentes; copiar integralmente o PNCP gerenciado para staging exclusivo;
anexar os vetores normativos por API FAISS; gerar o checkpoint e atualizar
o estado atomicamente; auditar os 67.276 IDs e os hashes; comparar os vetores
PNCP; testar a recuperação híbrida e as citações. Publicação e mudança de
configuração continuam sendo etapas separadas. Nenhuma delas foi executada.

### Comandos de leitura reproduzidos

Executar a partir da raiz do projeto:

```powershell
.venv/Scripts/python.exe -c "from app.core.config import settings; from app.core.database.connection import database_path; print(settings.database_url); print(database_path(settings.database_url))"

.venv/Scripts/python.exe -m src.base_estruturada.pipelines.pipeline_indexacao_faiss --auditar --indice-dir data/index/faiss/staging/v2

.venv/Scripts/python.exe -m src.consolidacao --dry-run --origem app_normativa.db --destino app.db --pncp data/index/faiss/staging/v2 --normativo indice/faiss_normativo_794
```

O último comando permanece bloqueado pela diferença descrita acima. Não
confundir sua falha com a validação vetorial, que passou independentemente.

Evidências atuais em `notas/consolidacao_verificacao_atualizada.json`:
caminhos absolutos, contagens, integridade SQLite, comparação documental,
mapas completos de IDs, inventários FAISS, comparação PNCP/JSONL, simulação
em memória e saída do dry-run. Os SHA-256 de **299 arquivos** (incluindo bancos,
índices, configuração e `.env`) foram iguais antes/depois dessa reexecução.
O JSON anterior `consolidacao_auditoria.json` é histórico e não foi sobrescrito.

As verificações executadas nesta etapa não incluem publicação de manifests
novos nem teste de respostas com LLM. A simulação em memória não equivale a
um staging persistido e auditado. Os resultados antigos de 56 testes e 23
subtestes na seção histórica não representam uma nova execução nesta etapa.

---

## Histórico — diagnóstico inicial com o app.db antigo

As contagens e os comandos de execução abaixo pertencem ao diagnóstico
anterior à atualização do banco pelo usuário. Não usar suas conclusões ou o
exemplo `--executar` como aprovação para executar no estado atual.

Data: 22/10/2026. Escopo executado: leitura dos dados reais, implementação,
testes temporários e dry-run. Nenhuma migração real, consolidação real,
publicação, mudança de configuração ou reinício de serviço foi executado.
Na última execução da CLI, SHA-256 de 298 arquivos (bancos, configuração e
artefatos dos índices originais) permaneceu idêntico antes/depois. O resultado
e os hashes estão em `preservation_check` no JSON de auditoria.

O detalhamento reproduzível está em `consolidacao_auditoria.json`: schemas
completos, índices SQL, constraints, FKs, triggers, contagens, mapas de IDs da
simulação, inventário de todos os arquivos FAISS com SHA-256 e evidências locais.

## Resultado que impede a consolidação real

O `app.db` contém apenas **2 documentos e 55 chunks PNCP**, além de **12.070
registros raw_asset**. Nenhum dos IDs textuais desses 55 chunks consta dos
índices PNCP encontrados. O índice mais recente tem **66.482 vetores sem
correspondência no banco principal**. Não é seguro publicar uma combinação
dessas fontes. O `app.db.backup` também tem 2 documentos, 55 chunks e 12.070
raw_asset; sua contagem não resolve a divergência e ele não foi restaurado.

Não se deve eliminar vetores órfãos, fabricar chunks, remapear por posição ou
reindexar o PNCP para ocultar esse problema. Primeiro é necessário localizar
o SQLite/corpus correspondente aos 66.482 IDs e reconciliá-lo preservando
conteúdos e metadados, em uma etapa adicional revisável.

## Bancos e migração simulada

Ambos os bancos passaram em `PRAGMA integrity_check` e
`PRAGMA foreign_key_check`. A origem possui 13 documentos e 794 chunks,
todos de `editais_normativo`. O destino não possui normativa.

As colisões de IDs inteiros são reais: 1 versão de corpus, 2 documentos e 55
chunks. Os IDs SQL foram remapeados na cópia; `chunk_id`, usado pelo FAISS,
permanece textual e estável. A versão normativa é distinta da versão PNCP.

Chaves verificadas: `corpus_versions.version`, documento identificado pela
versão de corpus + base + source_file, e `document_chunks.chunk_id` único.
O documento normativo segue `<base_id>|<arquivo>`, conforme
`app/modules/normative/persistencia.py`. Ambiguidades, chaves legadas,
conteúdo divergente e relações adicionais populadas bloqueiam a operação.
Não há relações de resposta/citação populadas na origem a transportar.

O schema do destino é anterior ao atual: falta `documents.title`; também
faltam FTS5 e seus triggers. A migração adiciona a coluna nullable sem mudar
valores existentes, transporta os títulos e prepara FTS5 e triggers na
mesma transação. Campos adicionais desconhecidos não são descartados.

O script não chama `init_db` nem importa sessões globais para abrir os bancos
reais. A origem é aberta com `mode=ro`. Antes da migração são criados snapshots
dos dois bancos por `sqlite3.Connection.backup`. No dry-run esses backups e a
cópia de trabalho ficam em diretório temporário. Na execução futura, os
backups persistentes ficam separados da cópia de trabalho e nunca são migrados.
Uma impressão digital do destino detecta mudanças desde o backup sob lock de
escrita. Falhas SQL fazem rollback, inclusive de DDL e FTS5.

## Índices encontrados e compatibilidade

| Diretório | Vetores | Atualização declarada UTC | Auditoria de artefatos | Órfãos no app.db |
|---|---:|---|---|---:|
| data/index/faiss/v1_mvp | 100 | 06/10/2026 19:46:33 | íntegro | 100 |
| data/index/faiss/v1 | 65.362 | 12/10/2026 12:11:00 | íntegro | 65.362 |
| data/index/faiss/staging/v2 | 66.482 | 14/10/2026 23:35:50 | íntegro | 66.482 |
| indice/faiss_normativo_794 | 794 | 19/10/2026 20:26:36 | íntegro | 0 na origem normativa |

`staging/v2` foi identificado após auditar os candidatos, não por presumir
que estava disponível. Ele contém uma base de 65.362 vetores e 67 checkpoints
ativos, somando 1.120 vetores adicionais. A base interna não é outra versão
independente. Os índices v1 e v1_mvp são legados; a normativa tem 3 checkpoints
(10, 500 e 284 vetores), sem base legada. O loader deve receber a raiz
`indice/faiss_normativo_794`, e não sua subpasta `checkpoints`.

Todos declaram `xagi/qwen3-embedding:0.6b-q4_k_m`, dimensão 1024. Os shards
reais usam produto interno e vetores unitários; normas medidas aproximadamente
entre 0,99999988 e 1,00000012. Não há IDs duplicados ou inconsistências de
manifest/checksum detectadas. Os 794 IDs normativos correspondem exatamente
aos chunks de origem; seus 794 hashes SHA-256 de conteúdo também correspondem.
Os vetores legados PNCP não possuem hashes de conteúdo individuais; não é
possível verificar seu conteúdo contra o banco atual. A identidade declarada
do modelo não prova a revisão histórica do servidor, ausente nos manifests.

## Estratégia implementada

**A: reaproveitar os vetores existentes**, condicionada à reconciliação do
banco PNCP. É compatível com os artefatos observados, evita 794 chamadas de
embedding e não gera novamente os vetores PNCP. O custo é leitura, cópia de
artefatos e auditoria local; não foi medido tempo de consolidação real.

`consolidate` valida IDs, conteúdo normativo, modelo, dimensões, métrica e
normalização. Copia um índice gerenciado completo ou prepara base legada
usando `src.index.preparar_staging`. Reconstrói um novo shard pela API FAISS;
não concatena binários ou injeta checkpoints isolados. Sobreposições de IDs
só são aceitas se os vetores forem idênticos. Confere IDs e vetores PNCP
byte a byte, audita o resultado e disponibiliza apenas um novo staging por
rename no mesmo filesystem. O ponteiro de checkpoints usa a escrita atômica
existente. Origens e configuração de produção permanecem separadas.

O destino não pode coincidir, conter ou estar dentro das origens. Staging
existente nunca é sobrescrito; a CLI escolhe um sufixo exclusivo. Falha antes
do rename pode deixar uma pasta temporária oculta para inspeção. Falha SQL
após criar staging pode deixar um staging sem migração correspondente:
nunca utilizá-lo sem nova auditoria. Não existe transação distribuída entre
SQLite e filesystem; o script prepara artefatos offline, sem publicação.

**B: reindexar apenas a normativa** se o modelo, hashes, dimensões ou métrica
não puderem ser comprovados. O pipeline existente
`src.base_estruturada.pipelines.pipeline_indexacao_faiss` já seleciona
`--base-id editais_normativo`, exclui IDs indexados e grava checkpoints.
Deve operar contra o banco migrado e um novo staging derivado do PNCP;
`preparar_staging` atual só aceita base legada, portanto não usá-lo diretamente
para copiar staging/v2 gerenciado. Essa estratégia exige até 794 novos
embeddings e mantém os vetores PNCP. Não resolve o bloqueio dos 66.482 órfãos;
não foi executada nem necessária neste diagnóstico.

## Contagens antes/depois

“Depois” abaixo é a simulação SQLite; a consolidação FAISS foi bloqueada.
Os arquivos reais mantêm todas as contagens anteriores.

| Métrica | Antes (destino/índice PNCP selecionado) | Depois (dry-run) |
|---|---:|---:|
| Documentos PNCP | 2 | 2 |
| Chunks PNCP | 55 | 55 |
| Vetores PNCP | 66.482 | sem consolidação; original intacto |
| Documentos normativos no destino | 0 | 13 |
| Chunks normativos no destino | 0 | 794 |
| Vetores normativos no índice PNCP | 0 | sem consolidação |
| Total de vetores FAISS selecionado | 66.482 | sem consolidação |
| IDs duplicados FAISS | 0 | sem alteração |
| IDs órfãos PNCP | 66.482 | 66.482; bloqueante |
| Inconsistências de artefatos FAISS | 0 | 0 nos originais |
| Chaves estrangeiras inválidas | 0 | 0 |

O total aritmético esperado de uma combinação seria 67.276 vetores, mas
**esse índice não foi criado nem validado com os dados reais**. Os 55 chunks
PNCP atuais também não têm vetores nesses índices. Contagens de vetores PNCP
acima são atribuídas pela procedência do índice, não por associação SQLite,
que está ausente.

`raw_asset` preservado: 2.024 contratações, 4.804 itens, 1.378 contratos,
195 PCA e 3.669 resultados de itens. Essas linhas não são chunks FAISS.

## RAG e perguntas propostas

`src/index.py` carrega legado ou checkpoints e valida seus manifests.
`src/retrieve.py` consulta FAISS, FTS5/BM25 e faz RRF por `chunk_id`, carregando
texto e metadados do SQLite. IDs órfãos são ignorados pelo retriever, portanto
o índice PNCP atual não entrega evidências densas a partir deste banco.
`app/modules/rag/services.py` resolve o diretório via
`app/core/config.py:rag_faiss_index_dir`, admitindo caminho explícito para teste.
Nada nessa configuração foi alterado.

Os filtros lógicos já distinguem `pncp_rj_estruturada` e `editais_normativo`.
Filtros de entidade usam `Document.doc_type`; `tipo_documento` faz busca no
título, não igualdade de doc_type. Isso deve ser considerado ao validar
consultas normativas. O retriever fornece ID do documento, tipo, base, título
e URL; os campos `tituloDocumento` e `urlFontePncp` são consumidos pela geração,
inclusive para normativa apesar do nome do campo. Não foi alterado o contrato
de citações, nem removido reranking/guardrails/validação.

As quatro perguntas propostas foram usadas nos testes de recuperação híbrida
temporários com embeddings determinísticos, filtros por base, ambos os rankings
e metadados de fonte. São testes de integração mecânica com corpus sintético,
não prova de resposta factual ou qualidade semântica do modelo real.

Na cópia dos dados reais foi executado SQL/FTS5, com evidências e URLs no JSON:

- Dispensa em 2026: **0 registros no recorte `anoCompra=2026` e modalidade
  contendo “dispensa”**. Não significa ausência nacional nem ausência de
  publicações em 2026 de compras de outro ano.
- Dez maiores valores: ranking determinístico de `raw_asset/contratacao`,
  última versão local por identidade, sem filtro de ano. As dez linhas estão
  no JSON. O maior valor armazenado é R$ 4.596.237.649,92, identificador
  `00394494000136-1-000039/2023`; trata-se de valor do corpus, sem verificação
  externa de sua correção. Não confundir `valorTotalEstimado` com valor de
  contrato ou valor homologado.
- Artigo 86: evidência exata presente em
  `editais_normativo:planalto_l14133:86:p1`, com texto integral e fonte na
  seção `article86_exact` do JSON. A pesquisa exata evita confundir com art. 186.
- Fiscalização: FTS5 retorna trechos normativos reais e suas fontes; o JSON
  registra os candidatos. Recuperar candidatos não demonstra que todas as
  obrigações foram identificadas.

Não houve chamada a LLM nem geração de resposta jurídica. A validação de
respostas fundamentadas e da recuperação semântica real das duas bases
permanece pendente da reconciliação PNCP e de execução autorizada posterior.

## Testes e reprodução

Arquivos criados: `src/consolidacao.py`,
`tests/integration/test_consolidacao.py`, este relatório e
`notas/consolidacao_auditoria.json`. Sem dependências novas.

```powershell
.venv/Scripts/python.exe -m src.consolidacao --dry-run
```

Resultado observado: simulação insere 1 versão, 13 documentos e 794 chunks.
A CLI retorna código **2** para consolidação bloqueada; não é uma migração
parcial do banco real. `--relatorio <arquivo-novo.json>` grava o diagnóstico
sem sobrescrever relatório já existente. `--pncp <diretorio>` permite seleção
explícita; omitido, audita os candidatos e escolhe o íntegro mais recente.

```powershell
.venv/Scripts/python.exe -m pytest tests/integration/test_consolidacao.py tests/integration/test_hybrid_retrieval.py tests/integration/test_incremental_faiss_index.py tests/unit/test_retrieve_filters.py -q -p no:cacheprovider
```

Resultado: **56 testes e 23 subtestes passaram**. Cobertura nova: preservação
PNCP, remapeamento, idempotência, rollback por conflito, coluna de título,
integridade FK/FTS5, vetores normativos, vetores PNCP idênticos, ausência de
órfãos/duplicados, manifests, incompatibilidade de modelo, hashes divergentes,
relações não suportadas, fontes/filtros no RRF e backups intactos. `--executar`
foi exercitado exclusivamente em bancos e índices temporários.

## Execução futura e rollback

Não executar agora. Após reconciliar o banco/índice e obter a autorização
solicitada no enunciado, refazer o dry-run até não haver bloqueios e usar:

```powershell
.venv/Scripts/python.exe -m src.consolidacao --executar --backup-dir backups/consolidacao_NOVO --staging data/index/faiss/staging/consolidacao_pncp_normativa --relatorio notas/consolidacao_execucao_NOVO.json
```

Esse comando prepara staging e migra SQLite, mas não publica o índice nem
altera `rag_faiss_index_dir`. Com os dados atuais ele recusa a execução antes
de escrever no banco principal. A aceitação em produção é etapa separada.

Durante uma migração, erro causa rollback da transação SQLite. Depois de uma
migração concluída, rollback integral exige janela sem escritores, preservação
de outro snapshot do estado atual e restauração de `backups/.../target.db`
pela API de backup SQLite, seguida de integrity_check/FK check. Não restaurar
por cima de um banco com novas gravações sem conciliá-las. Não copiar apenas
o arquivo principal quando houver WAL ativo. A origem normativa não precisa
de restauração, pois é somente leitura. Como os índices originais não são
alterados e não há publicação automática, o rollback do staging é simplesmente
não selecioná-lo; arquivá-lo para auditoria. Nenhuma restauração foi executada.
