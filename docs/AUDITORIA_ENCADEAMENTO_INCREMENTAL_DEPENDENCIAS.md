# Auditoria do encadeamento incremental de dependências

Data: 2026-11-06

## Objetivo

Definir como encadear com segurança:

```text
contratação -> itens -> resultados homologados
contrato -> empenhos
```

A auditoria foi somente leitura. Nenhuma coleta, migration ou alteração no
banco operacional foi executada.

## Estado atual

- cada modalidade de contratação possui um job e uma janela independentes;
- os recursos dependentes recebem hoje um único `parent_run_id`;
- a descoberta considera apenas versões RAW `NEW` ou `UPDATED` criadas pela
  execução-pai;
- entidades `UNCHANGED` continuam cobertas pela fila
  `sync_reconciliation_target` depois de registradas;
- itens e resultados usam cadência de um dia e horizonte de 365 dias;
- empenhos usam cadência de sete dias e horizonte de 730 dias.

## Riscos encontrados

### 1. Os 14 pais convergem para um filho

Uma janela diária de contratações produz até 14 execuções-pai. Executar o
mesmo job de itens uma vez para cada pai gera conflito, pois o job dependente
possui uma única janela para aquela data. O correto é agregar as descobertas
dos 14 pais antes de abrir a janela filha.

### 2. Lacuna entre a conclusão do pai e o registro do filho

Se o processo terminar depois de confirmar o pai e antes de registrar os alvos
filhos, o reprocessamento do pai pode retornar somente `UNCHANGED`. Como ele
não cria outra versão RAW, os alvos ainda não registrados podem deixar de ser
descobertos. O journal do systemd não resolve essa lacuna transacional.

### 3. Bootstrap da fila histórica

A fila de reconciliação cobre apenas alvos que já foram registrados. Antes da
ativação recorrente, é necessário cadastrar de modo idempotente os pais atuais
da RAW que ainda estão dentro dos horizontes operacionais. Sem isso, o
scheduler acompanha mudanças novas, mas não garante revisita aos pais
históricos elegíveis.

### 4. Controle de carga

Uma reconciliação pode selecionar muitos alvos. O executor precisa impor
limite por lote, espera entre requisições e retomada persistente antes de ser
ligado ao timer diário.

## Desenho seguro proposto

1. Criar um despacho persistente pai-filho, por migration aditiva, com estado
   `PENDING`, `RUNNING`, `COMPLETED` ou `FAILED`.
2. Registrar o despacho no mesmo fluxo que confirma a janela-pai, ou manter
   evidência suficiente para reconstruí-lo deterministicamente.
3. Agregar todos os `run_id` confirmados da cobertura diária antes de criar a
   janela de itens.
4. Manter um job filho estável por recurso e escopo, preservando a fila de
   reconciliação entre janelas.
5. Executar resultados somente depois da conclusão confirmada dos itens.
6. Aplicar a mesma regra a contratos e empenhos.
7. Criar um comando separado de bootstrap, com simulação somente leitura,
   contagem prevista e escrita apenas mediante confirmação explícita.
8. Adicionar limites de lote, intervalo mínimo e retomada por alvo.

## Critérios de aceitação

- nenhuma modalidade concluída fica sem despacho filho;
- uma interrupção em qualquer ponto pode ser retomada sem redescoberta
  manual;
- os 14 pais alimentam uma única janela de itens sem conflito;
- `UNCHANGED` não remove nem duplica alvos da reconciliação;
- o bootstrap é idempotente e apresenta contagens antes de escrever;
- falhas de um alvo não avançam indevidamente sua reconciliação;
- o banco oficial só recebe a migration depois de validação em cópia,
  `integrity_check`, `foreign_key_check` e comparação de contagens.

## Decisão

O encadeamento automático não deve ser ativado apenas com chamadas
sequenciais em memória. A próxima implementação precisa começar pelo despacho
persistente e pelo plano de bootstrap; até lá, o timer do scheduler permanece
como modelo desativado.
