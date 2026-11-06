# PNCP/RJ — Fase 11: scheduler incremental de contratações

Data: 2026-11-06

## 1. Objetivo

Automatizar o planejamento das janelas fechadas da cobertura composta de
contratações, preservando as 14 modalidades, a sobreposição de dois dias e a
retomada por estado persistido.

Esta fase não instalou nem ativou serviços e não escreveu no banco operacional.

## 2. Componentes

- `plan_contracting_schedule()` lê o watermark composto e monta as janelas em
  ordem cronológica;
- `execute_contracting_schedule()` executa somente planos sem bloqueios;
- `src.fetch_incremental_schedule` oferece simulação por padrão e exige
  confirmação redundante para escrita;
- os modelos systemd preparam execução diária e recuperação após falha, mas
  permanecem desativados.

## 3. Regras de segurança

- o último dia automático é ontem em `America/Sao_Paulo`;
- a data inicial da ativação precisa ser informada explicitamente;
- o modo padrão é somente leitura;
- a execução exige `--execute`, confirmação exata do banco e log absoluto;
- bancos em `/tmp` são recusados no modo operacional;
- existe espera mínima de 30 segundos entre shards e entre dias;
- qualquer janela ou execução ativa bloqueia o plano;
- uma nova tentativa recalcula `RUN`, `RESUME`, `REPROCESS` e `SKIP` a partir
  do SQLite, sem depender do journal do serviço.

## 4. Simulação somente leitura

O banco operacional informou watermark composto em
`2026-10-19T23:59:59.999999`. O planejamento até 21/10/2026 retornou:

```text
ready: true
janelas: 18, 19, 20 e 21/10/2026
REPROCESS: 28 shards
RUN: 28 shards
execuções: 0
```

Os dias 18 e 19 representam a sobreposição confirmada. Os dias 20 e 21 são
novas janelas. A simulação não acessou a API e não modificou o banco.

## 5. Validação

- 15 testes dos módulos diretamente alterados aprovados;
- suíte completa: 900 testes, 36 ignorados e 130 subtestes aprovados;
- unidade e timer aceitos pelo `systemd-analyze verify`;
- avisos exibidos pelo verificador pertencem a unidades do sistema local, não
  aos modelos do projeto.

## 6. Limite desta fase

O scheduler cobre a sequência temporal das contratações e suas modalidades.
O encadeamento automático das execuções-pai para itens, resultados e empenhos
continua pendente e deve ser implementado separadamente antes de qualquer
ativação recorrente completa.
