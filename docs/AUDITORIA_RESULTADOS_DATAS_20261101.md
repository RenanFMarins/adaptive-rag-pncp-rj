# Auditoria dos 72 resultados com datas suspeitas

## Escopo e segurança

A auditoria comparou `resultado_item` na base normalizada com o ativo RAW
corrente e com todas as versões da mesma identidade canônica. Os dois bancos
foram abertos com `mode=ro`. Nenhum payload, data, checkpoint ou status foi
reescrito.

Comando reproduzível:

```bash
.venv/bin/python scripts/audit_suspect_result_dates.py
```

O relatório agregado é gravado por padrão em
`/tmp/pncp_suspect_result_dates_audit.json`; payloads completos, fornecedores e
valores financeiros não são copiados.

## Resultado

| Classificação | Registros | Contratações | Interpretação |
| --- | ---: | ---: | --- |
| data anterior à publicação | 59 | 59 | `dataResultado` precede a própria publicação da contratação |
| data posterior à referência | 10 | 1 | dez itens da mesma contratação informam `2027-04-30` |
| ano mais de dez anos à frente | 3 | 1 | três itens informam `2202-12-29`, forte indício de erro de digitação |
| **Total** | **72** | **61** | todos permanecem `SUSPECT_DATE` |

Distribuição por órgão:

- 52 registros do Município de Macaé, todos com datas de 2024 em
  contratações publicadas em 2026;
- 10 do Município de São José do Vale do Rio Preto, todos em `2027-04-30`;
- 4 do Consórcio de Saúde Pública do Noroeste, sendo três em `2202-12-29`;
- 6 registros antigos isolados, distribuídos entre seis outros órgãos.

## Conferência da linhagem

| Verificação | Resultado |
| --- | ---: |
| ativo RAW corrente localizado | 72/72 |
| data normalizada idêntica a `payload.dataResultado` | 72/72 |
| hash corrente idêntico ao hash RAW | 72/72 |
| identidade pai/item/resultado idêntica | 72/72 |
| entidades com mais de uma versão RAW | 0/72 |
| entidades com data alternativa em outra versão | 0/72 |

As 72 linhas vieram das fontes de resultado por item: 64 da coleta histórica
ampla e 8 da janela complementar de setembro/outubro de 2026. Todos os
resultados estavam com situação `Informado`.

## Conclusão

A anomalia é de dado de origem: o normalizador preservou fielmente o valor
recebido do PNCP e marcou `SUSPECT_DATE`. Não há evidência de erro de parsing,
junção, identidade, hash ou versionamento.

Consequências operacionais:

1. manter as linhas e a RAW sem correção especulativa;
2. continuar excluindo `SUSPECT_DATE` de indicadores temporais confiáveis;
3. não substituir datas por publicação, inclusão ou atualização;
4. em uma reconciliação futura, aceitar uma correção somente se o PNCP
   publicar nova versão do resultado;
5. exibir aviso de qualidade quando uma consulta retornar uma dessas linhas.
