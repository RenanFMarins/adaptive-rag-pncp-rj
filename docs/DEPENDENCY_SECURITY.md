# Segurança das dependências

## Política do frontend

A instalação do frontend deve ser reproduzível a partir do
`frontend/react-console/package-lock.json`. O workflow de qualidade executa
dois controles complementares:

1. `npm audit --omit=dev --audit-level=moderate` bloqueia vulnerabilidades de
   severidade moderada ou superior nas dependências que integram a aplicação
   entregue ao usuário.
2. `npm audit --audit-level=high` bloqueia vulnerabilidades altas ou críticas
   inclusive nas ferramentas de desenvolvimento.

Não deve ser usado `npm audit fix --force` sem revisão, porque o comando pode
trocar versões principais, remover pacotes necessários ou produzir uma árvore
incompatível.

## Exceção temporária — 31/10/2026

A auditoria realizada com Node.js 22 encontrou:

- **dependências de produção:** nenhuma vulnerabilidade conhecida;
- **árvore completa:** 12 ocorrências moderadas, todas na cadeia de ferramentas
  de lint que passa por ESLint/TypeScript ESLint e `minimatch` 10.x;
- **vulnerabilidades altas ou críticas:** nenhuma.

Essa cadeia é usada durante desenvolvimento e CI e não integra o bundle React
de produção. Na data da auditoria, as versões mais recentes compatíveis de
ESLint e TypeScript ESLint ainda dependiam de `minimatch` 10.x. Uma atualização
forçada ou um `override` para a versão principal 11 poderia quebrar contratos
dessas ferramentas e, por isso, não foi aplicado.

O risco moderado de tooling é aceito temporariamente, com estas salvaguardas:

- entradas de glob da CI são definidas pelo próprio repositório;
- produção permanece bloqueada a partir da severidade moderada;
- toda a árvore permanece bloqueada para severidades alta e crítica;
- a exceção deve ser revista quando ESLint/TypeScript ESLint suportarem uma
  versão corrigida de `minimatch` (11.0.1 ou posterior) sem override forçado.

## Como reproduzir a auditoria

Execute dentro de `frontend/react-console`, usando Node.js 22:

```bash
npm ci
npm audit --registry=https://registry.npmjs.org --omit=dev --audit-level=moderate
npm audit --registry=https://registry.npmjs.org --audit-level=high
npm run lint
npm run build
```

Uma falha em qualquer controle deve ser investigada antes de atualizar o
arquivo de lock. Exceções futuras precisam informar data, dependência, alcance,
impacto, salvaguardas e condição de encerramento.
