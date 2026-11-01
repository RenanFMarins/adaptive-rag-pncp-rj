# Histórico privado de consultas

O endpoint principal registra um histórico técnico mínimo para que cada pessoa
possa auditar a própria atividade sem persistir o conteúdo da conversa.

## Dados armazenados

- identificador interno do evento e do usuário;
- rota e entidade selecionadas pelo Analyzer;
- status técnico da execução;
- tamanho da pergunta, sem o texto;
- quantidade de resultados;
- criação e expiração.

Não são armazenados nessa tabela perguntas, respostas, prompts, saídas brutas
do modelo, JWTs, credenciais ou cabeçalhos. O conteúdo visível do chat continua
somente na sessão da interface.

## Isolamento e retenção

Todas as operações exigem autenticação. A API sempre filtra pelo `user_id` do
token e responde com `404` quando alguém tenta excluir um evento que não lhe
pertence. O identificador do usuário não é devolvido no payload público.

A retenção padrão é de 30 dias. Ela pode ser configurada por
`QUERY_HISTORY_RETENTION_DAYS`, entre 1 e 365 dias. Registros vencidos são
apagados durante novas gravações e listagens.

## Rotas

```text
GET    /history             lista os eventos do usuário autenticado
DELETE /history/{event_id}  remove um evento próprio
DELETE /history             remove todos os eventos próprios
```

As tabelas legadas `queries` e `responses` podem conter conteúdo integral de
execuções documentais antigas, mas não possuem vínculo confiável com usuário.
Por isso, elas não são expostas por essas rotas. Uma futura política para esses
registros exige migração e descarte controlados, sem inferir propriedade.
