# Adaptive RAG PNCP/RJ

[![Licença MIT](https://img.shields.io/badge/licen%C3%A7a-MIT-176b5b.svg)](LICENSE)

Sistema de consulta em linguagem natural sobre contratações públicas do Estado do Rio de Janeiro. O projeto combina consultas estruturadas em SQLite com recuperação documental, roteamento adaptativo e geração de respostas fundamentadas.

Desenvolvido pelo Time 03 no Grande Desafio de IA Generativa da Residência TIC/PUC-Rio/Instituto ECOA.

## Demonstração

🎬 **[Assistir ao vídeo de demonstração (8min21s)](https://github.com/RenanFMarins/adaptive-rag-pncp-rj/releases/download/demonstracao-adaptive-rag-2026-10-27-v1/video02.mp4)**

[Página da Release](https://github.com/RenanFMarins/adaptive-rag-pncp-rj/releases/tag/demonstracao-adaptive-rag-2026-10-27-v1) · [Documentação técnica completa](docs/GUIA_TECNICO_COMPLETO.md) · [Arquitetura](ARQUITETURA.md)

## O que o sistema faz

- recebe perguntas em linguagem natural por uma API FastAPI ou interface React;
- classifica a pergunta e seleciona as rotas `structured`, `rag`, `hybrid` ou `catalog`;
- consulta contratações, contratos, itens, resultados homologados, atas e PCAs;
- combina busca lexical BM25/FTS5 e busca vetorial FAISS quando os índices estão disponíveis;
- preserva dados RAW, versões, checkpoints e auditoria da ingestão incremental;
- mantém a base normalizada em modo somente leitura durante as consultas;
- minimiza conteúdo sensível nos logs e retorna erros controlados quando o FAISS está indisponível.

## Arquitetura resumida

```text
PNCP/API + documentos
        │
        ▼
Ingestão RAW e incremental
        │
        ▼
Base normalizada SQLite
        │
        ├── Structured/SQL Tool
        ├── BM25/FTS5
        └── FAISS
                │
                ▼
Guardrail → Analyzer → Planner → Executor → Resposta
                │
                ▼
          FastAPI + React
```

## Cobertura da base normalizada

Inventário validado em outubro de 2026:

| Entidade | Registros |
| --- | ---: |
| Contratações | 180.419 |
| Itens de contratação | 557.211 |
| Resultados homologados | 417.675 |
| Contratos | 151.898 |
| Empenhos | 1.900 |
| Atas de registro de preços | 80.761 |
| PCAs | 567 |
| Itens de PCA | 228.469 |

Consulte [CORPUS_INVENTORY.md](CORPUS_INVENTORY.md) para o inventário detalhado e as limitações conhecidas.

## Início rápido

### 1. Clonar e criar o ambiente Python

```bash
git clone https://github.com/RenanFMarins/adaptive-rag-pncp-rj.git
cd adaptive-rag-pncp-rj
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt -r requirements-dev.txt
```

No PowerShell, ative o ambiente com:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 2. Configurar variáveis de ambiente

```bash
cp .env.example .env
```

Preencha ao menos `JWT_SECRET_KEY`. Para utilizar somente a OpenAI, ajuste no `.env`:

```env
LLM_PRIMARY_PROVIDER=openai
LLM_FALLBACK_PROVIDER=none
OPENAI_API_KEY=sua_chave_local
EMBEDDING_PROVIDER=openai
```

Nunca envie o arquivo `.env` ao GitHub.

### 3. Preparar os bancos

O projeto utiliza dois bancos com finalidades diferentes:

| Banco | Finalidade | Como obter |
| --- | --- | --- |
| `app.db` | autenticação, histórico e metadados da aplicação | `python -m app.init_db` |
| `data/normalized/pncp_rj_normalized.db` | consultas estruturadas do PNCP/RJ | gerar pela pipeline ou restaurar um snapshot publicado |

Bancos, dados coletados e índices não são versionados no Git. A base
normalizada sanitizada pode ser instalada diretamente da
[release de 20/10/2026](https://github.com/RenanFMarins/adaptive-rag-pncp-rj/releases/tag/base-normalizada-pncp-rj-20261020-v1):

```bash
python -m scripts.restore_normalized_release
```

O restaurador confere tamanho, SHA-256, manifesto, contagens, integridade e
chaves estrangeiras antes de publicar o SQLite no destino. Ele recusa
sobrescrever um banco existente e também interrompe antes do download pesado
se não houver espaço livre seguro. Consulte o
[guia de restauração](docs/RESTAURACAO_BASE_NORMALIZADA.md) e
[data/README.md](data/README.md) para opções adicionais.

### 4. Iniciar o backend

```bash
python -m uvicorn app.main:app --reload
```

- API: <http://127.0.0.1:8000>
- Swagger: <http://127.0.0.1:8000/docs>
- ReDoc: <http://127.0.0.1:8000/redoc>
- Saúde: <http://127.0.0.1:8000/health>
- Prontidão e capacidades: <http://127.0.0.1:8000/ready>

O histórico técnico autenticado fica em `/history`, com retenção limitada e
sem perguntas ou respostas brutas. Consulte a
[política de histórico privado](docs/HISTORICO_PRIVADO.md).

### 5. Iniciar o frontend React

Requer Node.js 22 ou superior.

```bash
cd frontend/react-console
npm ci
npm run dev
```

Abra <http://127.0.0.1:5173>. Em desenvolvimento, o Vite encaminha `/auth` e `/query` para a API na porta 8000.

Na mesma conversa, o React envia apenas a última análise estruturada validada
para permitir acompanhamentos seguros, como `E somente os estaduais?`. O texto
completo do histórico não é reenviado. **Nova consulta** e o logout descartam
esse contexto.

### 6. Executar os testes

```bash
python -m pytest -q
```

Em pull requests, o GitHub Actions executa a suíte Python offline e valida o
lint e o build do frontend React. As dependências enxutas desse ambiente ficam
em `requirements-ci.txt`; OCR/Docling e chamadas a serviços externos não fazem
parte da CI.

## O que funciona sem os artefatos opcionais

| Recurso | Requisito |
| --- | --- |
| Autenticação e Swagger | `app.db` inicializado |
| Consultas estruturadas | base normalizada configurada |
| Busca lexical | corpus carregado no FTS5 |
| Busca vetorial | índice FAISS compatível |
| Rotas RAG/Hybrid | corpus, índice e provedor LLM configurados |

Se o FAISS estiver ausente, as rotas estruturadas continuam disponíveis e as rotas que dependem do índice retornam indisponibilidade controlada, sem expor caminhos internos.

## Estrutura do repositório

```text
app/                    API, autenticação e serviços da aplicação
src/                    ingestão, normalização, consulta e RAG
frontend/react-console/ interface web React + Vite
tests/                  testes unitários e de integração
migrations/             migrações SQLite versionadas
config/                 políticas e inventários de escopo
scripts/                automações e verificadores
docs/                   guias, decisões e relatórios técnicos
data/README.md          convenções para dados locais
```

## Documentação

- [Guia técnico completo](docs/GUIA_TECNICO_COMPLETO.md)
- [Arquitetura](ARQUITETURA.md)
- [Ingestão incremental](INGESTAO_INCREMENTAL.md)
- [Inventário do corpus](CORPUS_INVENTORY.md)
- [Cenários do desafio](GRANDE_DESAFIO_CENARIOS.md)
- [Backlog](BACKLOG.md)
- [Acompanhamento da equipe](acompanhamento/ACOMPANHAMENTO_GERAL.md)

## Limitações conhecidas

- o índice FAISS operacional publicado é um piloto e não representa toda a cobertura documental;
- `pca_contratacao_link` permanece vazio porque a API não fornece uma chave confiável para associar planejamento e execução;
- a cobertura de atas é parcial e depende do inventário de órgãos e unidades coletados;
- snapshots de dados são distribuídos fora do histórico Git para evitar repositórios gigantes e exposição indevida.

## Segurança e governança

- segredos devem existir somente no `.env` local;
- bancos, logs, dados RAW e índices gerados são ignorados pelo Git;
- a base normalizada é aberta em modo somente leitura pela API;
- o workflow de governança bloqueia novos artefatos proibidos em pull requests;
- logs operacionais preservam correlação e métricas sem persistir perguntas ou respostas completas por padrão.

## Licença e atribuição

O software e a documentação autoral do projeto são distribuídos sob a
[licença MIT](LICENSE). Dados e documentos provenientes do PNCP ou de outros
publicadores continuam sujeitos à sua origem e aos termos aplicáveis; a MIT
não relicencia conteúdo de terceiros. Consulte [NOTICE.md](NOTICE.md).

## Equipe

Time 03 — Luiz Felipe Antunes, Ana Karina, Luciano Oliveira, Marcio da Costa, Ester da Silva, Alisson Lima e Renan Freitas.

Este repositório pessoal preserva o histórico do trabalho colaborativo desenvolvido no [repositório original do grupo](https://github.com/grande-desafio-ia-rag-03/rag-grande-desafio-grupo03-contratacoes-publicas).
