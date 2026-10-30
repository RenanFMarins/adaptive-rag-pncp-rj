# Console React do Adaptive RAG PNCP/RJ

Interface web para cadastro, autenticação e envio de perguntas à API FastAPI do projeto.

## Requisitos

- Node.js 22 ou superior;
- backend executando em `http://127.0.0.1:8000`.

## Desenvolvimento

```bash
npm ci
npm run dev
```

Abra `http://127.0.0.1:5173`.

O servidor Vite encaminha as rotas `/auth` e `/query` para a API local. Para utilizar outra URL, defina `VITE_API_URL` em um arquivo `.env.local` desta pasta.

## Verificações

```bash
npm run lint
npm run build
```

O diretório `dist/` é gerado pelo build e não deve ser versionado.
