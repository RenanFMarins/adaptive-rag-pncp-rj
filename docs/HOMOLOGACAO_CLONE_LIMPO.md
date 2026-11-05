# Homologação em clone limpo

Execução inicial realizada em **01/11/2026** contra o commit
`895ffd98ad48153d2a5386a4d303f109d69348ff` da branch `main` do repositório
pessoal. A restauração integral foi revalidada pela internet em **05/11/2026**
contra a release `base-normalizada-pncp-rj-20261105-v1`.

## Escopo

O ensaio utilizou um clone filtrado e isolado. O diretório de desenvolvimento
original e seus bancos operacionais não foram alterados. O clone não continha
`.env`, `app.db` ou arquivos SQLite versionados.

## Resultado

| Verificação | Resultado |
| --- | --- |
| Clone da `main` pessoal | aprovado |
| Ausência de bancos e segredos versionados | aprovado |
| Suíte Python | 844 aprovados, 36 ignorados e 124 subtestes aprovados |
| `npm ci` com Node.js 22.22.0 | aprovado |
| Lint do React | aprovado |
| Build de produção do React | aprovado |
| Auditoria de dependências de produção | 0 vulnerabilidades conhecidas |
| Inicialização da API sem base e sem FAISS | aprovado em modo degradado seguro |
| Restauração integral da base normalizada | aprovada em 05/11/2026 |

As dependências Python do ensaio local foram executadas pelo ambiente virtual
já homologado, para não duplicar pacotes no disco quase cheio. A instalação
Python do zero continua coberta pelo workflow de CI em runner descartável.

## Comportamento da API sem artefatos de dados

A API foi iniciada com caminhos sintéticos dentro do clone, sem chaves reais.
O comportamento observado foi:

- `GET /health`: HTTP 200 com `{"status":"ok"}`;
- `GET /ready`: HTTP 503 com a base normalizada e o índice vetorial marcados
  como indisponíveis;
- `GET /`: HTTP 200;
- nenhuma rota indisponível expôs traceback, segredo ou caminho local na
  resposta HTTP.

Esse resultado confirma que a ausência dos artefatos não impede a inicialização
e é representada corretamente pelo contrato de readiness. Ele não homologa as
capacidades `structured`, `rag` ou `hybrid` sem seus respectivos artefatos.

## Bloqueio histórico da restauração completa

O restaurador leu e validou os pequenos arquivos de manifesto e checksums e
interrompeu antes do download do snapshot principal:

```text
disponível=2359836672 bytes
recomendado=3562278866 bytes
```

Faltavam **1.202.442.194 bytes** (aproximadamente 1,12 GiB) para cumprir a
margem de segurança. A recusa é o comportamento esperado: nenhum arquivo
parcial foi publicado e nenhum banco existente foi substituído.

Não foram removidos backups ou dados do usuário para liberar espaço. Esse
bloqueio foi resolvido posteriormente com a liberação segura de espaço e a
publicação do snapshot de 05/11/2026.

## Revalidação integral de 05/11/2026

O restaurador foi executado sem `--source-directory`, obrigando o download
real dos três anexos publicados no GitHub. O destino ficou em um diretório
temporário isolado e foi removido automaticamente ao final.

| Verificação | Resultado |
| --- | --- |
| Download de `SHA256SUMS.txt` e manifesto | aprovado |
| Download do pacote de 510.390.154 bytes | aprovado |
| SHA-256 compactado | aprovado |
| Descompactação para 2.138.464.256 bytes | aprovada |
| SHA-256 descompactado | aprovado |
| Contagens do manifesto | aprovadas |
| `PRAGMA integrity_check` | `ok` |
| `PRAGMA foreign_key_check` | zero violações |
| Política e fingerprint da sanitização | aprovados |

O ensaio confirma que um clone sem bancos versionados consegue instalar o
snapshot público somente com o código e acesso à release. A cópia temporária
de 2,14 GB foi descartada depois da validação; os bancos operacionais locais
não foram modificados.

## Reprodução

Em um clone novo com ao menos 3,6 GB livres:

```bash
cp .env.example .env
python -m scripts.restore_normalized_release
python -m app.init_db
python -m uvicorn app.main:app
```

Em outro terminal:

```bash
curl -i http://127.0.0.1:8000/health
curl -i http://127.0.0.1:8000/ready
```

O critério final de aceite é `normalized_database: ready`, seguido de uma
consulta estruturada sintética e da inicialização do frontend com `npm ci` e
`npm run dev` usando Node.js 22.13 ou superior.
