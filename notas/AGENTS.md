# AGENTS.md

## Guia do Codex --- Adaptive RAG para Contratações Públicas do Estado do Rio de Janeiro

Este arquivo contém as instruções obrigatórias para o Codex e outros
agentes de desenvolvimento que trabalhem neste repositório.

O projeto é uma aplicação **FastAPI** organizada por módulos de domínio
e possui um pipeline de **Adaptive Retrieval-Augmented Generation
(Adaptive RAG)**.

O agente deve preservar a arquitetura definida neste documento e nos
documentos existentes em `notes/`.

------------------------------------------------------------------------

# 1. Documentos que devem ser lidos primeiro

Antes de implementar uma funcionalidade relevante, consulte:

``` text
notes/
├── ANALISE_DE_REQUISITOS_CONTRATACOES_PUBLICAS_RJ.md
├── ENGENHARIA_DE_SOFTWARE_CONTRATACOES_PUBLICAS_RJ.md
└── AGENTS.md
```

Também consulte, quando existirem:

``` text
README.md
ARQUITETURA.md
PERSONAS.md
corpus_manifest.yaml
CORPUS_INVENTORY.md
pyproject.toml
requirements.txt
.env.example
```

A Análise de Requisitos define **o que o sistema deve fazer**.

A Engenharia de Software define **como o sistema deve ser organizado**.

Este `AGENTS.md` define **como o Codex deve trabalhar no projeto**.

Não altere requisitos ou arquitetura silenciosamente.

------------------------------------------------------------------------

# 2. Objetivo do sistema

O sistema responde consultas sobre **Contratações Públicas do Estado do
Rio de Janeiro** utilizando evidências provenientes de diferentes
naturezas de base:

``` text
normativa
estruturada
conversacional
agregada
```

O sistema não é um chatbot com busca vetorial simples.

O pipeline esperado é:

``` text
Pergunta
   |
   v
Query Analyzer
   |
   v
Adaptive Router
   |
   v
Filtros
   |
   +------------------+
   |                  |
   v                  v
Dense Retrieval      BM25
   |                  |
   +--------+---------+
            |
            v
           RRF
            |
            v
        Reranking
            |
            v
        Guardrails
            |
            v
         Geração
            |
            v
        Validação
            |
            v
Resposta + Fontes + Histórico
```

Não simplifique esse pipeline para:

``` text
pergunta -> embedding -> LLM
```

sem solicitação explícita e alteração correspondente da arquitetura.

------------------------------------------------------------------------

# 3. Estrutura obrigatória do projeto

A estrutura de referência é:

``` text
contratacoes-rj-rag/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── exceptions.py
│   │   └── logging.py
│   │
│   └── modules/
│       ├── query/
│       │   ├── __init__.py
│       │   ├── model.py
│       │   ├── schemas.py
│       │   ├── services.py
│       │   └── routes.py
│       │
│       ├── rag/
│       │   ├── __init__.py
│       │   ├── model.py
│       │   ├── schemas.py
│       │   ├── services.py
│       │   └── routes.py
│       │
│       ├── corpus/
│       │   ├── __init__.py
│       │   ├── model.py
│       │   ├── schemas.py
│       │   ├── services.py
│       │   └── routes.py
│       │
│       ├── documents/
│       │   ├── __init__.py
│       │   ├── model.py
│       │   ├── schemas.py
│       │   ├── services.py
│       │   └── routes.py
│       │
│       ├── feedback/
│       │   ├── __init__.py
│       │   ├── model.py
│       │   ├── schemas.py
│       │   ├── services.py
│       │   └── routes.py
│       │
│       └── history/
│           ├── __init__.py
│           ├── model.py
│           ├── schemas.py
│           ├── services.py
│           └── routes.py
│
├── src/
│   ├── __init__.py
│   ├── fetch_corpus.py
│   ├── ingest.py
│   ├── index.py
│   ├── router.py
│   ├── retrieve.py
│   ├── generate.py
│   ├── schema.py
│   └── obs.py
│
├── notes/
│   ├── ANALISE_DE_REQUISITOS_CONTRATACOES_PUBLICAS_RJ.md
│   ├── ENGENHARIA_DE_SOFTWARE_CONTRATACOES_PUBLICAS_RJ.md
│   └── AGENTS.md
│
├── data/
│   ├── raw/
│   ├── processed/
│   ├── cache/
│   └── indexes/
│
├── eval/
├── logs/
│
├── tests/
│   ├── fixtures/
│   ├── unit/
│   ├── contract/
│   └── integration/
│
├── corpus_manifest.yaml
├── CORPUS_INVENTORY.md
├── ARQUITETURA.md
├── PERSONAS.md
├── README.md
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
└── pyproject.toml
```

Não reorganize essa estrutura inteira sem necessidade.

------------------------------------------------------------------------

# 4. Regra obrigatória para módulos

Todo módulo de domínio em:

``` text
app/modules/
```

deve seguir o padrão:

``` text
<modulo>/
├── __init__.py
├── model.py
├── schemas.py
├── services.py
└── routes.py
```

O fluxo padrão é:

``` text
HTTP
 ↓
routes.py
 ↓
schemas.py
 ↓
services.py
 ↓
model.py / src / integrações
 ↓
schemas.py
 ↓
HTTP
```

------------------------------------------------------------------------

# 5. `model.py`

Use `model.py` para entidades persistentes do módulo.

Quando SQLAlchemy estiver sendo utilizado, coloque os modelos ORM aqui.

Exemplo conceitual:

``` python
class QueryModel(Base):
    __tablename__ = "queries"

    ...
```

Não coloque endpoints FastAPI em `model.py`.

Não coloque toda a lógica do RAG em models.

------------------------------------------------------------------------

# 6. `schemas.py`

Use `schemas.py` para contratos Pydantic.

Exemplos:

``` text
QueryRequest
QueryResponse
QueryFilters
FeedbackCreate
FeedbackResponse
HistoryResponse
RAGRequest
RAGResponse
```

Schemas devem definir claramente:

-   entrada;
-   saída;
-   tipos;
-   campos opcionais;
-   validações.

Os schemas de endpoints devem ser declarados no FastAPI para que
apareçam corretamente no Swagger.

------------------------------------------------------------------------

# 7. `services.py`

Toda regra de negócio relevante deve ficar em `services.py` ou em
componentes especializados de `src/`.

A route deve chamar o service.

Evite:

``` python
@router.post("/ask")
async def ask(...):
    # 200 linhas de lógica RAG aqui
```

Prefira:

``` python
@router.post("/ask")
async def ask(request: RAGRequest):
    return await rag_service.ask(request)
```

O service coordena a operação.

------------------------------------------------------------------------

# 8. `routes.py`

Use `routes.py` exclusivamente para a camada HTTP.

Responsabilidades:

``` text
receber request
validar schema
chamar service
declarar response_model
declarar status HTTP
retornar response
```

Utilize:

``` python
APIRouter
```

com `prefix` e `tags`.

Exemplo:

``` python
router = APIRouter(
    prefix="/rag",
    tags=["RAG"],
)
```

------------------------------------------------------------------------

# 9. `app/main.py`

`app/main.py` é o ponto de entrada da API.

Ele deve:

-   criar `FastAPI`;
-   configurar metadados OpenAPI;
-   registrar routers;
-   registrar handlers globais;
-   disponibilizar `/health`;
-   manter Swagger habilitado.

Estrutura esperada:

``` python
app = FastAPI(
    title="Contratações Públicas RJ - Adaptive RAG API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)
```

Registrar os routers por:

``` python
app.include_router(...)
```

Não crie várias instâncias FastAPI independentes para cada módulo.

------------------------------------------------------------------------

# 10. Swagger é parte da arquitetura

A API deve permanecer utilizável pelo Swagger.

Após iniciar:

``` bash
python -m uvicorn app.main:app --reload
```

espera-se:

``` text
API:
http://127.0.0.1:8000

Swagger:
http://127.0.0.1:8000/docs

OpenAPI:
http://127.0.0.1:8000/openapi.json

ReDoc:
http://127.0.0.1:8000/redoc
```

Ao criar endpoint novo:

-   use `response_model`;
-   use schemas Pydantic;
-   defina `summary` quando útil;
-   defina `tags`;
-   defina códigos HTTP;
-   mantenha exemplos/documentação quando agregarem valor.

------------------------------------------------------------------------

# 11. Tags do Swagger

Organize os endpoints preferencialmente nas tags:

``` text
Health
Queries
RAG
Corpus
Documents
Feedback
History
```

Não coloque todos os endpoints em uma única tag genérica.

------------------------------------------------------------------------

# 12. Módulo `query`

Local:

``` text
app/modules/query/
```

Responsável pela consulta e seu ciclo de vida.

Pode conter:

``` text
QueryModel
QueryRequest
QueryResponse
QueryFilters
QueryService
query routes
```

O módulo `query` não deve duplicar internamente todo o pipeline RAG.

------------------------------------------------------------------------

# 13. Módulo `rag`

Local:

``` text
app/modules/rag/
```

É a camada de aplicação responsável por coordenar o Adaptive RAG.

Fluxo conceitual do service:

``` text
RAGService
   |
   +--> Query Analyzer
   +--> Adaptive Router
   +--> Retriever
   +--> RRF
   +--> Reranker
   +--> Guardrails
   +--> Generator
   +--> Validator
```

Não implemente todos esses algoritmos diretamente em `routes.py`.

------------------------------------------------------------------------

# 14. Módulo `corpus`

Local:

``` text
app/modules/corpus/
```

Responsável pela visão da aplicação sobre:

``` text
versões
inventário
estado do corpus
metadados
```

A coleta e atualização técnica do corpus permanecem em:

``` text
src/fetch_corpus.py
```

------------------------------------------------------------------------

# 15. Módulo `documents`

Local:

``` text
app/modules/documents/
```

Representa documentos/chunks/fontes quando a aplicação precisar
manipulá-los ou consultá-los.

Metadados essenciais de chunk:

``` text
source_file
doc_type
chunk_id
sensitivity
base_id
```

------------------------------------------------------------------------

# 16. Módulo `feedback`

Local:

``` text
app/modules/feedback/
```

Responsável por registrar avaliações do usuário.

Campos conceituais:

``` text
feedback_id
query_id
rating
comment
created_at
```

------------------------------------------------------------------------

# 17. Módulo `history`

Local:

``` text
app/modules/history/
```

Responsável por histórico de consultas e respostas.

Não misture regras de feedback com histórico apenas por utilizarem a
mesma consulta.

------------------------------------------------------------------------

# 18. Separação entre `app/` e `src/`

A regra é:

``` text
app/
    camada da aplicação/API/domínio

src/
    componentes técnicos do pipeline RAG
```

Exemplo:

``` text
app/modules/rag/services.py
```

pode orquestrar:

``` text
src/router.py
src/retrieve.py
src/generate.py
src/obs.py
```

Mas:

``` text
src/retrieve.py
```

não deve importar uma route FastAPI.

------------------------------------------------------------------------

# 19. `src/fetch_corpus.py`

Responsável pela aquisição e versionamento do corpus.

Operações previstas:

``` bash
python -m src.fetch_corpus fetch --manifest corpus_manifest.yaml
python -m src.fetch_corpus update --manifest corpus_manifest.yaml
python -m src.fetch_corpus inventory --version v1
```

Requisitos:

-   idempotência;
-   retomada;
-   rate limit;
-   registro de falhas;
-   hashes;
-   seleção determinística;
-   versionamento imutável.

------------------------------------------------------------------------

# 20. `src/ingest.py`

Responsável por:

``` text
carregar
normalizar
classificar sensibilidade
extrair metadados
chunkear
```

Saída:

``` text
DocumentChunk[]
```

Não aceite chunk sem:

``` text
source_file
doc_type
chunk_id
sensitivity
base_id
```

------------------------------------------------------------------------

# 21. `src/index.py`

Responsável por:

``` text
embeddings
cache
índice vetorial
BM25
persistência
carregamento
```

Não gere novamente embeddings idênticos sem necessidade.

Persistir índices em:

``` text
data/indexes/
```

ou caminho equivalente definido na configuração.

------------------------------------------------------------------------

# 22. `src/router.py`

Responsável por:

``` text
Query Analyzer
Adaptive Router
```

O Query Analyzer deve extrair, quando possível:

``` text
intent
semantic_query
evidence_types
filters
subqueries
```

Exemplo:

``` json
{
  "intent": "buscar_contratos",
  "semantic_query": "licenciamento de software",
  "evidence_types": ["estruturada"],
  "filters": {
    "uf": "RJ",
    "ano": 2025,
    "valor_minimo": 500000
  }
}
```

------------------------------------------------------------------------

# 23. Não confundir filtros com busca semântica

Se a pergunta contém:

``` text
RJ
2025
acima de R$ 500 mil
```

não transforme tudo apenas em texto para embedding.

Extraia:

``` text
uf = RJ
ano = 2025
valor_minimo = 500000
```

e use a descrição do objeto como consulta semântica.

------------------------------------------------------------------------

# 24. Adaptive Router

Rotas:

``` text
normativa
estruturada
conversacional
agregada
```

Exemplos:

``` text
Lei / regra / participação
    -> normativa

contrato / fornecedor / valor
    -> estruturada

ata / comunicação
    -> conversacional

média / comparação / indicador
    -> agregada ou agregada + estruturada
```

Não roteie apenas por palavra-chave.

Uma pergunta pode exigir mais de uma rota.

------------------------------------------------------------------------

# 25. Perguntas compostas

Exemplo:

``` text
Sou MEI, posso participar de pregão eletrônico?
Tem algum aberto para material de escritório?
```

O sistema deve poder decompor em:

``` text
subquery 1
 -> normativa

subquery 2
 -> estruturada
```

Não force as duas perguntas para a mesma base.

------------------------------------------------------------------------

# 26. `src/retrieve.py`

Responsável por:

``` text
filtros
Dense Retrieval
BM25
RRF
reranking
```

Fluxo:

``` text
RoutingDecision
       |
       v
Metadata Filters
       |
       +----------------+
       |                |
       v                v
     Dense             BM25
       |                |
       +-------+--------+
               |
               v
              RRF
               |
               v
            Rerank
```

------------------------------------------------------------------------

# 27. Dense Retrieval

Use embeddings para busca semântica.

Adequado para:

``` text
descrição do objeto
conceitos
formulações semanticamente equivalentes
```

Não utilize Dense Retrieval como substituto universal de filtros exatos.

------------------------------------------------------------------------

# 28. BM25

Use BM25 para correspondência lexical.

Especialmente importante para:

``` text
CNPJ
número de contrato
número de edital
nomes
identificadores
expressões exatas
```

Não remova BM25 por existir busca vetorial.

------------------------------------------------------------------------

# 29. RRF

A fusão deve ser feita em código.

Forma conceitual:

``` text
score(d) = Σ 1 / (k + rank(d))
```

RRF deve:

-   ser determinístico;
-   possuir teste unitário;
-   trabalhar com IDs estáveis de chunks;
-   não depender de LLM.

Não peça ao modelo generativo para combinar rankings.

------------------------------------------------------------------------

# 30. Reranking

Aplique reranking somente sobre candidatos previamente selecionados.

Não envie todo o corpus ao reranker.

O modelo deve ser configurável.

------------------------------------------------------------------------

# 31. `src/generate.py`

Responsável por:

``` text
contexto
prompt
chamada ao LLM
resposta fundamentada
citações
```

O modelo deve responder utilizando as evidências fornecidas.

Não invente fonte.

Não apresente evidência inexistente.

------------------------------------------------------------------------

# 32. Guardrails

Guardrails devem ocorrer antes da geração.

Classificações:

``` text
publico
interno
restrito
```

Permitido:

``` text
valor do contrato
nome da empresa
CNPJ de pessoa jurídica
objeto contratado
```

Mascarar:

``` text
CPF
telefone pessoal
e-mail pessoal
```

Bloquear:

``` text
dados bancários
credenciais
dados restritos
```

Não envie dado restrito ao LLM para removê-lo depois.

------------------------------------------------------------------------

# 33. Acusações jurídicas

O sistema não deve concluir automaticamente:

``` text
"esse contrato é fraude"
```

ou equivalentes.

Pode apresentar dados públicos, inconsistências encontradas de forma
objetiva e suas fontes.

Não transforme o modelo em julgador jurídico.

------------------------------------------------------------------------

# 34. Falta de evidência

Quando o corpus não sustentar a resposta:

``` text
não inventar
não preencher com conhecimento geral silenciosamente
não fabricar fonte
```

Retorne indicação de evidência insuficiente.

------------------------------------------------------------------------

# 35. Schemas do RAG

Prefira contratos Pydantic.

Exemplo conceitual:

``` python
class QueryFilters(BaseModel):
    uf: str | None = None
    municipio: str | None = None
    ano: int | None = None
    valor_minimo: float | None = None
    valor_maximo: float | None = None
    modalidade: str | None = None
    fornecedor: str | None = None


class SourceReference(BaseModel):
    base_id: str
    source_file: str
    chunk_id: str
    source_url: str | None = None


class RAGResponse(BaseModel):
    query_id: str
    run_id: str
    answer: str
    routes: list[str]
    sources_used: list[SourceReference]
    is_refusal: bool = False
```

Antes de criar schema duplicado, procure se já existe contrato
equivalente.

------------------------------------------------------------------------

# 36. Persistência

Se SQLAlchemy estiver configurado, mantenha entidades persistentes nos
respectivos `model.py`.

Entidades conceituais:

``` text
Query
Response
ResponseSource
Feedback
PipelineEvent
```

Não introduza banco novo ou ORM diferente sem necessidade.

------------------------------------------------------------------------

# 37. Banco e migrations

Se o projeto utilizar Alembic:

-   alteração em model persistente deve ser acompanhada da migration
    necessária;
-   não apague migrations existentes para "resolver" conflito;
-   não recrie o banco como solução padrão;
-   preserve dados sempre que possível.

------------------------------------------------------------------------

# 38. Observabilidade

Toda consulta deve possuir:

``` text
query_id
run_id
```

O mesmo `run_id` deve acompanhar as etapas do pipeline.

Logs:

``` text
logs/pipeline-AAAA-MM-DD.jsonl
```

Estágios padronizados:

``` text
query_analysis
roteamento
retrieval_denso
retrieval_bm25
fusao_rrf
rerank
geracao
validacao
feedback
```

Não invente sinônimos para esses nomes em diferentes módulos.

------------------------------------------------------------------------

# 39. Campos de log

Registre, quando aplicável:

``` text
ts
run_id
query_id
stage
status
latency_ms
input
output
tokens
model
extra
```

Evite registrar segredos ou conteúdo sensível integralmente.

------------------------------------------------------------------------

# 40. Tokens

Chamadas de modelo devem registrar:

``` text
prompt
completion
total
```

Exemplo:

``` json
{
  "prompt": 900,
  "completion": 180,
  "total": 1080
}
```

Consumo de tokens faz parte da avaliação técnica.

------------------------------------------------------------------------

# 41. Modelos e configuração

Configurações devem ficar centralizadas em:

``` text
app/core/config.py
```

ou equivalente já existente.

Referências do desafio:

``` text
OLLAMA_URL=http://ecoa-llm.duckdns.org:11434/v1
GENERATION_MODEL=qcwind/qwen3-8b-instruct-Q4-K-M
EMBEDDING_MODEL=xagi/qwen3-embedding:0.6b-q4_k_m
```

O reranker deve permanecer configurável.

Não espalhe URLs e nomes de modelo pelo código.

------------------------------------------------------------------------

# 42. Segredos

Nunca escreva no código:

``` python
API_KEY = "..."
PASSWORD = "..."
```

Use ambiente/configuração.

Nunca faça commit de:

``` text
.env
credenciais
tokens
senhas
```

------------------------------------------------------------------------

# 43. Corpus manifest

`corpus_manifest.yaml` é a fonte de verdade da composição do corpus.

Não substitua o manifesto por downloads manuais não reproduzíveis.

O mesmo manifesto deve permitir reconstrução determinística tanto quanto
a fonte externa permitir.

------------------------------------------------------------------------

# 44. Versionamento do corpus

Versões devem ser imutáveis.

Exemplo:

``` text
data/raw/
├── v1/
├── v2/
└── v3/
```

`update` cria nova versão.

Não sobrescreva `v1`.

------------------------------------------------------------------------

# 45. Chunking

A estratégia deve respeitar a natureza da base.

Normativa:

``` text
capítulo
seção
artigo
cláusula
```

Estruturada:

``` text
registro de contratação
```

Conversacional:

``` text
blocos que preservem sequência e contexto
```

Agregada:

``` text
indicador + unidade + período + recorte
```

Não aplique cegamente o mesmo chunking a todas as bases.

------------------------------------------------------------------------

# 46. Cálculos numéricos

Para:

``` text
média
total
contagem
máximo
mínimo
comparação
```

prefira cálculo determinístico em código quando os dados estiverem
disponíveis.

Fluxo:

``` text
recuperar registros
 -> calcular
 -> fornecer resultado/evidência
 -> gerar explicação
```

Não use o LLM como calculadora de grandes conjuntos de registros.

------------------------------------------------------------------------

# 47. Cache de embeddings

Embeddings devem ser reutilizados.

Chave recomendada conceitualmente:

``` text
hash(conteúdo + modelo)
```

Se conteúdo e modelo não mudaram, não chame novamente o endpoint.

------------------------------------------------------------------------

# 48. Índices persistentes

Os índices devem poder ser salvos e carregados.

Evite:

``` text
iniciar API
 -> gerar embeddings de tudo
 -> reconstruir índices sempre
```

Prefira:

``` text
iniciar API
 -> carregar índices existentes
```

quando válidos.

------------------------------------------------------------------------

# 49. Testes

Estrutura:

``` text
tests/
├── fixtures/
├── unit/
├── contract/
└── integration/
```

O Codex deve adicionar ou ajustar testes quando alterar comportamento
relevante.

------------------------------------------------------------------------

# 50. Testes unitários

Não devem depender de LLM ou internet.

Prioridades:

``` text
RRF
normalização de filtros
schemas
chunking
mascaramento
manifesto
serialização
```

------------------------------------------------------------------------

# 51. Testes de contrato

Devem verificar invariantes.

Todo chunk deve possuir:

``` text
source_file
doc_type
chunk_id
sensitivity
base_id
```

Também verificar:

``` text
RAGResponse
SourceReference
rotas
sensibilidade
recusas
```

------------------------------------------------------------------------

# 52. Testes de integração

Devem testar fluxos como:

``` text
FastAPI
 -> route
 -> service
 -> RAG
 -> response
```

Utilize `TestClient` ou ferramenta já adotada no projeto.

------------------------------------------------------------------------

# 53. Testes com LLM

Marque:

``` python
@pytest.mark.llm
```

Testes dependentes de LLM não devem rodar na suíte offline padrão.

------------------------------------------------------------------------

# 54. Fixtures

Use:

``` text
tests/fixtures/
```

para um corpus pequeno representando:

``` text
normativa
estruturada
conversacional
agregada
```

Não use todo o corpus real em testes unitários.

------------------------------------------------------------------------

# 55. Swagger e testes

Sempre que criar ou alterar endpoint, verifique:

``` text
/docs
```

Confirme:

-   endpoint aparece;
-   tag correta;
-   request schema correto;
-   response schema correto;
-   status correto;
-   descrição compreensível.

Swagger é teste manual/documentação, não substituto dos testes
automatizados.

------------------------------------------------------------------------

# 56. Tratamento de erros

Prefira exceções específicas.

Possíveis categorias:

``` text
CorpusError
SourceUnavailableError
ManifestValidationError
IndexNotFoundError
QueryAnalysisError
RetrievalError
ModelUnavailableError
ResponseValidationError
SecurityPolicyError
```

Evite:

``` python
try:
    ...
except Exception:
    pass
```

Nunca esconda silenciosamente falha crítica.

------------------------------------------------------------------------

# 57. `app/core/exceptions.py`

Centralize exceções compartilhadas quando fizer sentido.

Handlers HTTP globais podem ser registrados no FastAPI.

Não repita a mesma conversão de exceção para HTTP em dezenas de routes.

------------------------------------------------------------------------

# 58. Código Python

Preferências:

``` text
Python moderno
type hints
Pydantic
funções pequenas
nomes claros
responsabilidade única
baixo acoplamento
alta coesão
```

Evite abstrações excessivas sem benefício concreto.

------------------------------------------------------------------------

# 59. Imports

Organize preferencialmente:

``` python
# standard library

# third-party

# local application
```

Evite imports circulares.

------------------------------------------------------------------------

# 60. Funções e classes

Antes de criar classe nova, pergunte:

``` text
qual responsabilidade ela possui?
já existe componente responsável?
isso pertence a app ou src?
```

Não crie classes apenas para aumentar abstração.

------------------------------------------------------------------------

# 61. Dependências

Antes de adicionar pacote:

1.  consulte `requirements.txt`;
2.  consulte `pyproject.toml`;
3.  procure implementação já existente;
4.  confirme necessidade;
5.  adicione a dependência no arquivo correto.

Não invente bibliotecas ou APIs.

------------------------------------------------------------------------

# 62. Não criar código fictício

Antes de chamar:

``` python
some_service.do_something()
```

confirme que:

``` text
some_service existe
do_something existe
assinatura é compatível
```

Se precisar, implemente explicitamente.

Não deixe referências quebradas para "completar depois" sem sinalização.

------------------------------------------------------------------------

# 63. Leia antes de editar

Antes de alterar um arquivo:

1.  leia o arquivo;
2.  identifique dependências;
3.  procure testes;
4.  procure schemas relacionados;
5.  procure chamadas existentes;
6.  só então edite.

Não substitua um arquivo inteiro sem entender o conteúdo existente.

------------------------------------------------------------------------

# 64. Política de mudança mínima

Para bugs:

``` text
reproduzir
 -> localizar causa
 -> corrigir menor superfície possível
 -> testar
```

Não faça refatoração ampla não solicitada junto com correção pequena.

------------------------------------------------------------------------

# 65. Preserve código funcional

Não reescreva módulos funcionais apenas por preferência de estilo.

Uma arquitetura "mais bonita" não justifica quebrar comportamento
existente.

------------------------------------------------------------------------

# 66. Não apagar funcionalidades

Antes de remover:

``` text
endpoint
schema
model
service
campo
função
arquivo
```

procure usos no projeto.

Se houver dependências, atualize-as de forma consistente.

------------------------------------------------------------------------

# 67. Git

Não versionar normalmente:

``` text
.env
.venv/
__pycache__/
.pytest_cache/
data/raw/
data/cache/
data/indexes/
logs/
*.pyc
```

Preservar no Git:

``` text
código
testes
fixtures
manifesto
inventários
documentação
.env.example
```

------------------------------------------------------------------------

# 68. Não executar comandos destrutivos sem necessidade

Evite automaticamente:

``` text
git reset --hard
git clean -fd
drop database
rm -rf
apagar migrations
```

Não destrua alterações locais para resolver um problema.

------------------------------------------------------------------------

# 69. Personas como casos de referência

## Marina

Pergunta típica:

``` text
Qual foi o valor médio por quilo de arroz contratado
por municípios do RJ em 2025 e em quais modalidades?
```

Esperado:

``` text
agregada + estruturada
filtros RJ/2025/arroz
cálculo determinístico quando aplicável
fontes
```

## Rodrigo

Pergunta típica:

``` text
Quais contratos de licenciamento de software foram
assinados por órgãos estaduais do RJ acima de
R$ 500 mil em 2025 e quem foram os fornecedores?
```

Esperado:

``` text
semantic_query = licenciamento de software
uf = RJ
ano = 2025
valor_minimo = 500000
rota = estruturada
```

## Cláudia

Pergunta típica:

``` text
Sou MEI, posso participar de pregão eletrônico?
Tem algum aberto para material de escritório?
```

Esperado:

``` text
normativa
+
estruturada
```

------------------------------------------------------------------------

# 70. Avaliação do RAG

Ao implementar avaliação, mantenha métricas separadas quando possível:

``` text
routing accuracy
retrieval recall
context relevance
answer relevance
groundedness
citation relevance
consistency
latência
tokens
```

Não trate apenas a resposta final como diagnóstico completo do pipeline.

------------------------------------------------------------------------

# 71. Ablation

Quando solicitado avaliar a arquitetura híbrida, comparar:

``` text
Dense
BM25
Dense + BM25
Dense + BM25 + RRF
Dense + BM25 + RRF + Rerank
```

Registre resultados em `eval/`.

------------------------------------------------------------------------

# 72. Ordem recomendada para novas implementações

Ao construir o projeto do zero ou uma área nova, siga preferencialmente:

``` text
1. schemas
2. model, se houver persistência
3. service
4. route
5. registro no main.py
6. teste
7. Swagger
8. documentação
```

Para componentes RAG:

``` text
1. contrato/schema
2. implementação em src
3. teste unitário
4. integração no service
5. observabilidade
6. teste de integração
```

------------------------------------------------------------------------

# 73. Checklist para endpoint novo

Antes de considerar pronto:

``` text
[ ] módulo correto?
[ ] schema request?
[ ] schema response?
[ ] service?
[ ] route?
[ ] APIRouter?
[ ] prefix correto?
[ ] tag Swagger?
[ ] response_model?
[ ] status HTTP?
[ ] router registrado no main.py?
[ ] tratamento de erro?
[ ] teste?
[ ] aparece em /docs?
```

------------------------------------------------------------------------

# 74. Checklist para componente RAG

``` text
[ ] responsabilidade definida?
[ ] contrato de entrada?
[ ] contrato de saída?
[ ] teste offline quando possível?
[ ] log com run_id?
[ ] tratamento de erro?
[ ] sem dado restrito?
[ ] sem chamadas redundantes ao LLM?
[ ] configuração centralizada?
[ ] integração preserva o pipeline?
```

------------------------------------------------------------------------

# 75. Definition of Done

Uma tarefa só está concluída quando:

``` text
[ ] requisito atendido
[ ] arquitetura respeitada
[ ] model/schema/service/route respeitados quando aplicável
[ ] app/main.py atualizado quando necessário
[ ] Swagger funcionando
[ ] testes relevantes passando
[ ] tratamento de erros presente
[ ] observabilidade presente quando aplicável
[ ] segurança preservada
[ ] nenhuma fonte inventada
[ ] nenhum segredo incluído
[ ] documentação atualizada quando necessário
[ ] nenhuma alteração não relacionada introduzida
```

------------------------------------------------------------------------

# 76. Como o Codex deve responder ao implementar

Ao finalizar uma tarefa de código, informe de forma objetiva:

``` text
1. o que foi alterado;
2. quais arquivos foram alterados/criados;
3. quais testes foram executados;
4. resultado dos testes;
5. como testar pelo Swagger, quando aplicável;
6. pendências reais, se existirem.
```

Não declare que algo foi testado se o comando não foi executado.

Não declare que o Swagger funciona se a aplicação não pôde ser iniciada
ou validada.

------------------------------------------------------------------------

# 77. Regra final

Prioridades do projeto:

``` text
correção
>
rastreabilidade
>
segurança
>
testabilidade
>
aderência aos requisitos
>
simplicidade
>
performance
>
conveniência
```

Sempre prefira código determinístico para:

``` text
filtros
cálculos
RRF
validação
segurança
persistência
```

Utilize LLM onde ele realmente agrega valor:

``` text
interpretação da linguagem
análise semântica
roteamento adaptativo quando necessário
síntese fundamentada
```

O objetivo é construir um sistema Adaptive RAG que possa ser:

``` text
explicado
testado
medido
auditado
mantido
```

e que permaneça organizado como uma aplicação FastAPI modular:

``` text
app/main.py
      |
      v
app/modules/
      |
      +--> model.py
      +--> schemas.py
      +--> services.py
      +--> routes.py
```

com documentação e teste manual disponíveis pelo Swagger em:

``` text
/docs
```

e com o núcleo técnico do RAG mantido desacoplado em:

``` text
src/
```
