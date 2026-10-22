# Publicação local controlada do índice FAISS — 22/10/2026

**Status final: publicado localmente.** A configuração ativa seleciona o
índice consolidado aprovado. Não houve deploy na VPS, alteração de
infraestrutura remota, commit ou push.

## Configuração alterada

Somente a chave `RAG_FAISS_INDEX_DIR` do `.env` foi alterada. As demais linhas
foram preservadas byte a byte; `app/core/config.py` não foi modificado.

Anterior:

```text
RAG_FAISS_INDEX_DIR=data/index/faiss/v1
```

Caminho anterior absoluto, preservado para rollback:

```text
F:\ecoa_projetos\rag-grande-desafio-grupo03-contratacoes-publicas\data\index\faiss\v1
```

Novo valor:

```text
RAG_FAISS_INDEX_DIR=data/index/faiss/staging/consolidacao_pncp_normativa_20261022_122148_66171c9c
```

Caminho ativo confirmado em processos novos da aplicação:

```text
F:\ecoa_projetos\rag-grande-desafio-grupo03-contratacoes-publicas\data\index\faiss\staging\consolidacao_pncp_normativa_20261022_122148_66171c9c
```

A aplicação usa Pydantic Settings com `env_file=".env"`. Variáveis do processo
têm precedência sobre esse arquivo. Na inspeção não havia sobreposição de
`RAG_FAISS_INDEX_DIR` no processo, no ambiente de usuário ou no de máquina.
O valor padrão em `app/core/config.py` permanece v1; nesta execução a seleção
efetiva vem do `.env`. A carga posterior do `.env` pelo módulo de LLM não
exigiu alterações adicionais.

## Verificações anteriores à alteração

- Diretório aprovado existente, carregável e com arquivos idênticos aos do
  relatório de aprovação do staging.
- Manifests, checksums, checkpoints, mapas e estado auditados novamente.
- 67.276 vetores: 66.482 PNCP e 794 normativos; zero IDs órfãos, duplicados,
  hashes de conteúdo divergentes ou inconsistências reportadas.
- Compatibilidade mantida: modelo `xagi/qwen3-embedding:0.6b-q4_k_m`, dimensão
  1024, produto interno e vetores normalizados.
- `app.db` correspondente ao índice; ambos os SQLite com integridade `ok` e
  nenhuma violação de chave estrangeira.
- Processos inspecionados por Win32_Process e psutil, incluindo argumentos e
  diretório de trabalho. Foram observados apenas processos transitórios dos
  diagnósticos; nenhum Uvicorn/Streamlit/RAG ativo deste projeto foi encontrado.
  Nenhum serviço de outro projeto foi interrompido.

## Validação depois da alteração

As verificações foram executadas em processo Python novo, iniciado na raiz do
repositório, herdando o ambiente normal e sem atribuir variável FAISS ou
fornecer `cache_dir` ao serviço RAG.

A rotina real `validar_faiss_no_startup()` aprovou o índice selecionado pela
configuração ativa. `carregar_indice_faiss(resolver_caminho_indice_faiss())`
carregou 67.276 vetores. A auditoria de cobertura confirmou 66.482 PNCP,
794 normativos e zero inconsistências.

| Teste de leitura | Resultado |
|---|---|
| PNCP — contratação do lote canônico | 10 resultados, fonte esperada recuperada |
| Lei 14.133/2021 — artigo 86 | 10 resultados, artigo esperado recuperado |
| Decreto RJ 48.817/2023 | 10 resultados, trecho esperado recuperado |
| Edital normativo | 10 resultados, trecho esperado recuperado |
| BM25/FTS5 e FAISS | Contribuição dos dois rankings em cada caso |
| RRF | Fórmula conferida em todos os resultados |
| Citações | IDs, documentos, títulos, URLs e marcadores do contexto conferidos |
| SQLite | Ambos íntegros, FKs válidas e contagens inalteradas |

Para cumprir a restrição de não gerar embeddings, cada consulta utilizou o
texto exato de um chunk existente e reaproveitou seu vetor armazenado como
embedding de consulta. O serviço RAG resolveu o índice exclusivamente pela
configuração ativa. A geração de embeddings foi bloqueada no validador.
Esses testes confirmam a integração e as fontes com o índice ativo; não
constituem avaliação adicional de qualidade semântica para paráfrases. As
consultas livres com embeddings reais já tinham sido testadas na aprovação
do staging, registrada em relatório separado.

Não houve chamada a LLM para gerar respostas nem gravação de consultas ou
histórico. Foram verificados os metadados das fontes e o contexto/prompt
numerado de citações.

**Serviços reiniciados: nenhum.** Não havia serviço ativo a reiniciar. O
lifespan completo de `app.main` não foi executado, pois ele chama
`initialize_database()` e `init_db()`. A validação observacional de startup
FAISS e o serviço RAG foram exercitados diretamente, com SQLite em `mode=ro`
e `query_only`. Não foi iniciado servidor HTTP nem executada migração.

## Rollback automático exercitado

A primeira tentativa atualizou a chave e chamou um validador temporário por
caminho de arquivo. Esse utilitário não tinha a raiz do repositório no caminho
de importação e falhou com `ModuleNotFoundError: No module named 'src'`, antes
de testar a aplicação. O controle restaurou imediatamente o `.env` anterior
byte a byte e confirmou o retorno a v1 com 65.362 vetores.

Após corrigir somente a forma de execução do utilitário — `python -c` a
partir da raiz — a tentativa controlada foi repetida e passou em todas as
verificações. A primeira tentativa, o motivo e a prova do rollback foram
preservados no JSON. O estado final é publicado localmente, não revertido.

Para reverter esta publicação futuramente, restaurar **somente**:

```text
RAG_FAISS_INDEX_DIR=data/index/faiss/v1
```

Confirmar em um processo novo que o caminho ativo voltou a v1 e que carrega
65.362 vetores. Se algum serviço deste projeto estiver ativo nessa ocasião,
identificá-lo antes e reiniciar apenas o serviço afetado. Não é necessário
restaurar banco ou remover qualquer índice.

Comando de confirmação, sem forçar o caminho do índice:

```powershell
.venv/Scripts/python.exe -c "from app.core.config import resolver_caminho_indice_faiss; from src.index import carregar_indice_faiss; p=resolver_caminho_indice_faiss(); print(p); print(carregar_indice_faiss(p).index.ntotal)"
```

## Evidências e preservação

Relatório estruturado:
`notas/PUBLICACAO_FAISS_CONSOLIDADO_20261022.json`.

Ele contém os caminhos anterior e novo, precedência de configuração,
auditoria completa, cobertura por base, resultados individuais dos testes,
metadados de fontes, integridade SQLite, histórico das tentativas e hashes.
Não contém o conteúdo completo do `.env` ou suas credenciais.

Os SHA-256 de **574 arquivos protegidos** permaneceram iguais, incluindo
ambos os bancos, índices v1 e v1_mvp, staging/v2, índice normativo original,
índice consolidado aprovado e `app/core/config.py`. Não houve alteração de
checkpoints/manifests, geração de embeddings, reindexação ou migração SQLite.
O `.env` teve exclusivamente a chave FAISS atualizada. Nenhum banco ou índice
binário foi incluído em commit; não foi realizado commit/push.
