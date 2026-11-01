# Auditoria dos 14 contratos acima de R$ 1 bilhão

## Resultado

Os 14 contratos foram conferidos contra seus payloads RAW e contra as
contratações-pai disponíveis:

| Classe | Contratos | Interpretação |
| --- | ---: | --- |
| `valorGlobal` mais de 10× acima do `valorInicial` | 5 | forte inconsistência interna na origem |
| `valorGlobal` mais de 10× acima do maior valor da contratação-pai | 3 | possível escala/unidade incorreta na origem |
| campos internamente consistentes | 6 | não há contradição interna; não equivale a confirmação externa |

O maior registro informa `valorGlobal=R$ 457.322.461.390,80` e
`valorInicial=R$ 58.754.997,00`, razão aproximada de 7.783,55. Essa divergência
explica por que o valor não deve ser apresentado ao usuário sem aviso de
qualidade.

## Proveniência e unidade

- 14/14 ativos RAW foram localizados;
- 14/14 hashes coincidem;
- 14/14 `valorGlobal` normalizados correspondem exatamente ao valor decimal da
  RAW multiplicado por 100;
- 14/14 `valorInicial` seguem a mesma conversão;
- não existe versão RAW alternativa com `valorGlobal` corrigido;
- os 14 payloads não possuem um campo de moeda adicional.

Portanto, não houve erro de centavos na normalização. Os campos monetários do
PNCP foram tratados como reais e armazenados em centavos inteiros, conforme o
contrato de dados do projeto. A inconsistência já existe nos valores recebidos.

## Decisão

1. preservar os valores e a RAW;
2. marcar os oito casos contraditórios para revisão de origem;
3. não corrigir por divisão arbitrária por 10, 100 ou 1.000;
4. exibir aviso de qualidade em rankings, máximos e somas que incluam esses
   contratos;
5. tratar os seis restantes como internamente consistentes, não como valores
   externamente homologados.

Comando reproduzível, somente leitura:

```bash
.venv/bin/python scripts/audit_billion_contracts.py
```

O relatório agregado é gravado em `/tmp/pncp_billion_contracts_audit.json`.
