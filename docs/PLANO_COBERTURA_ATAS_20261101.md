# Plano de ampliação da cobertura de atas

## Diagnóstico

A coleta ampla anterior de atas resolveu seus alvos a partir das contratações
do primeiro trimestre de 2023. Esse recorte possui 233 pares distintos de
órgão–unidade. A RAW foi depois ampliada e o inventário congelado do RJ passou
a conter 2.116 pares, distribuídos por 617 CNPJs.

As 80.761 atas existentes antes desta ampliação resultavam de duas estratégias:

- busca por vigência nas 233 unidades iniciais;
- complementação direta pelas contratações SRP conhecidas.

Esse desenho é útil, mas não comprova que todas as 2.116 unidades tenham sido
consultadas em todas as janelas. Por isso a cobertura permanece `PARTIAL`.

## Nova fonte

A fonte `pncp_atas_rj_inventario_2023_ate_2026_10_31` usa diretamente o
inventário versionado `config/pncp_rj_scope_inventory.json`. Antes da coleta,
o carregador valida:

1. o `inventory_id` recalculado;
2. o `inventory_id` do plano de cobertura de atas;
3. a quantidade declarada de membros;
4. CNPJ, unidade e UF de cada alvo;
5. ausência de mistura entre inventário congelado e fontes RAW dinâmicas.

O período de 01/01/2023 a 31/10/2026 é dividido automaticamente por ano.
Assim, o plano possui 2.116 unidades × 4 janelas anuais = **8.464 alvos-base**,
com paginação interna quando uma unidade retorna mais de 500 atas.

A fonte tem identidade e checkpoint próprios. Reexecutá-la não depende do
checkpoint antigo e não cria duplicatas de entidade, pois a identidade canônica
da ata continua sendo `numeroControlePNCPAta`.

## Piloto operacional

Em 02/11/2026 foi executado um piloto isolado em `/tmp`, sem modificar a RAW
oficial. Seis alvos-base cobriram respostas reais HTTP `200` e `204`, com 17
registros observados, 14 novos, 3 inalterados e nenhuma falha.

O ensaio inicial com oito workers e intervalo de 0,5 segundo provocou respostas
HTTP `429`. A primeira execução oficial mostrou que 1 segundo ainda poderia ser
limitado após rajadas anteriores. Por isso a fonte oficial adota uma política
ainda mais conservadora:

- uma execução por vez (`max_concurrency: 1`);
- intervalo mínimo de 2 segundos entre chamadas;
- cinco retries com espera progressiva.

Essa configuração privilegia integridade e retomada em vez de velocidade.

## Execução operacional

Antes de executar, deve-se confirmar que nenhum coletor escreve no SQLite e
criar um backup íntegro ou uma cópia operacional. O comando de retomada é:

```bash
python3 -u -m src.fetch_corpus update \
  --source pncp_atas_rj_inventario_2023_ate_2026_10_31 \
  --database-url sqlite:///./data/debug/pncp_contracts_2023_t1_all.db
```

O uso de `update` permite retomar pelo checkpoint dessa fonte. A conclusão da
coleta comprovará cobertura relativa ao inventário e ao período declarados,
mas ainda não autoriza alegar cobertura universal de todo o PNCP.

## Resultado final

A coleta oficial foi concluída em 02/11/2026. Três interrupções de comunicação
foram registradas e retomadas pelo checkpoint; a execução final terminou com:

- checkpoint `SUCCESS` em **8.464 de 8.464 alvos-base**;
- 2.116 pares órgão–unidade cobertos nas quatro janelas anuais;
- 142.555 observações recebidas ao somar as execuções retomadas;
- 1.952 novas entidades, 44.952 atualizações e 95.651 observações
  inalteradas;
- nenhuma falha pendente ao final.

Em 05/11/2026, a normalização incremental materializou **82.713 atas**:
1.952 inseridas, 44.952 atualizadas e 35.809 inalteradas em relação ao
snapshot normalizado anterior. A execução não rejeitou registros, o
`PRAGMA integrity_check` retornou `ok`, o `foreign_key_check` não encontrou
violações e não existem relacionamentos órfãos.

A cobertura continua classificada como `PARTIAL`: o resultado comprova a
consulta completa do inventário congelado e do período de 01/01/2023 a
31/10/2026, não de todos os órgãos e atas que possam existir no PNCP.
