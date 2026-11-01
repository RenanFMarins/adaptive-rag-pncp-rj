# Benchmark comparativo: BM25 × FAISS × RRF

Data da medição: 01/11/2026.

## Objetivo e contrato

Esta medição compara os três recuperadores com as mesmas condições:

- corpus `normativo-v1`, com 13 documentos e 794 chunks;
- sete perguntas factuais de `eval/questions.json`;
- os mesmos prefixos de chunks esperados, revisados previamente;
- cortes `k = 1, 3, 5, 10`;
- 50 candidatos por recuperador e RRF com constante 60;
- SQLite aberto somente para leitura;
- FAISS `openai:text-embedding-3-small:d1024`, com 849 vetores e nenhuma
  inconsistência.

O benchmark está implementado em `eval/benchmark_hybrid.py`. O BM25 e o FAISS
produzem rankings independentes; o RRF combina as duas listas sem comparar os
scores heterogêneos diretamente.

## Resultado agregado

| Métrica | BM25 | FAISS | RRF |
| --- | ---: | ---: | ---: |
| Hit@1 | 57,14% | 28,57% | 42,86% |
| Hit@3 | 71,43% | 57,14% | 42,86% |
| Hit@5 | 71,43% | 57,14% | **85,71%** |
| Hit@10 | 85,71% | 71,43% | **100,00%** |
| Prefix Recall@5 | 51,19% | 40,95% | **57,62%** |
| Prefix Recall@10 | 57,62% | 48,10% | **65,95%** |
| MRR | **0,652381** | 0,459799 | 0,559524 |
| Latência média | **10,9 ms** | 483,2 ms | 494,2 ms |

O RRF ampliou a cobertura em `top 5` e `top 10`, incluindo ao menos uma fonte
esperada para todas as sete perguntas até a décima posição. Por outro lado,
BM25 manteve o melhor MRR e os melhores resultados nos primeiros três lugares.
O FAISS isolado não superou o BM25 neste conjunto.

Isso não demonstra que busca lexical seja universalmente superior. O conjunto
tem somente sete perguntas e julgamentos parciais, com forte correspondência
entre termos jurídicos da pergunta e do texto. O resultado recomenda manter a
recuperação híbrida, revisar a ordenação final e ampliar os julgamentos antes
de ajustar pesos ou trocar modelos.

## Diagnóstico por pergunta

`RR` é o inverso da posição da primeira fonte esperada. `Hit@10` indica se
ao menos uma fonte esperada apareceu nas dez primeiras posições.

| Pergunta | RR BM25 | RR FAISS | RR RRF | Hit@10 BM25 | Hit@10 FAISS | Hit@10 RRF |
| --- | ---: | ---: | ---: | :---: | :---: | :---: |
| N1 | 0,166667 | **0,500000** | 0,250000 | sim | sim | sim |
| N2 | 0,066667 | 0,142857 | **0,250000** | não | sim | sim |
| N3 | **1,000000** | 0,500000 | **1,000000** | sim | sim | sim |
| N4 | **1,000000** | 0,032258 | 0,166667 | sim | não | sim |
| N5 | **1,000000** | **1,000000** | **1,000000** | sim | sim | sim |
| N6 | **0,333333** | 0,043478 | 0,250000 | sim | não | sim |
| N7 | **1,000000** | **1,000000** | **1,000000** | sim | sim | sim |

O maior ganho híbrido ocorreu em N2: BM25 não encontrou a fonte esperada no
top 10, enquanto FAISS e RRF a encontraram. N4 e N6 mostram o comportamento
oposto: o componente lexical recuperou a fonte e compensou o ranking denso no
RRF.

## Reprodução

Com `app.db`, o índice homologado e a chave de embeddings configurados apenas
no `.env` local:

```bash
python3 -m eval.benchmark_hybrid \
  --database-url sqlite:///./app.db \
  --index-dir data/index/faiss/staging/openai-v2 \
  --questions eval/questions.json \
  --top-k 1 3 5 10 \
  --candidate-k 50 \
  --rrf-k 60 \
  --output /tmp/pncp-bm25-faiss-rrf.json
```

Identidade do índice usado:

```text
estado SHA-256: 48b3dc7b501bd1eb2504a386baddd6a969f4bcbfb223e66c5a5799f3d649b2c1
modelo: openai:text-embedding-3-small:d1024
vetores: 849
```

O relatório completo permanece em `/tmp` por padrão e não inclui perguntas
ou respostas de usuários. Cada execução realiza sete embeddings de consulta;
não reconstrói o índice e não chama o modelo de geração.

## Limitações e próximo passo

- prefixos esperados são julgamentos parciais, não uma lista exaustiva de
  todos os chunks relevantes;
- latência FAISS inclui a chamada remota de embedding e varia com a rede;
- RRF foi medido com a constante 60, sem ajuste orientado ao resultado;
- sete perguntas não sustentam conclusão estatística ampla;
- qualidade da recuperação não equivale à fidelidade da resposta final.

A próxima tarefa é revisar manualmente uma amostra de respostas e citações,
principalmente N1, N2, N4 e N6, sem calibrar o sistema usando o próprio conjunto
de avaliação como se fosse dado de treino.
