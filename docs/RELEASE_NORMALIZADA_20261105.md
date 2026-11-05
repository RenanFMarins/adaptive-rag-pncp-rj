# Release da base normalizada sanitizada — 05/11/2026

## Escopo

Esta release substitui o snapshot público de 20/10/2026. O núcleo estruturado
mantém a cobertura até 19/10/2026 e incorpora a ampliação das atas para 2.116
pares órgão–unidade, consultados em 8.464 alvos entre 01/01/2023 e
31/10/2026.

| Item | Valor |
| --- | --- |
| Tag | `base-normalizada-pncp-rj-20261105-v1` |
| URL | <https://github.com/RenanFMarins/adaptive-rag-pncp-rj/releases/tag/base-normalizada-pncp-rj-20261105-v1> |
| Banco sanitizado | `pncp_rj_normalized_public_20261105.sqlite.gz` |
| Tamanho compactado | 510.390.154 bytes |
| SHA-256 compactado | `87e7bbffb8aea76bf77d6b041a3effad30f0b8ef66b56133796d9e554321d2ef` |
| SHA-256 descompactado | `10a98cb950fb296907ba599ea7b1dc0b484332d4d3d0bca875eee07e2d3f2c01` |
| SHA-256 da base privada de origem | `7314325346891f6ce93cb6d25467dbfc9ab4c1350850980734416b2e88ca563b` |
| Política de sanitização | `pncp-public-v1` |

## Contagens principais

| Entidade | Registros |
| --- | ---: |
| Contratações | 180.419 |
| Itens de contratação | 557.211 |
| Resultados homologados | 417.675 |
| Contratos | 151.898 |
| Empenhos | 1.900 |
| Atas de registro de preços | 82.713 |
| PCAs | 567 |
| Itens de PCA | 228.469 |

## Sanitização

A mesma chave privada da release anterior foi reutilizada para manter
pseudônimos estáveis. A chave não integra o banco, o manifesto, o Git ou os
anexos da release. Foram protegidos:

- 6.446 fornecedores;
- 13.071 resultados homologados;
- 6.075 contratos;
- 57 empenhos;
- 6.446 chaves de linhagem.

## Validações

- `PRAGMA integrity_check = ok`;
- zero violações de chave estrangeira;
- zero identificadores diretos de PF/PE nas relações protegidas;
- zero entidades com mais de uma linhagem atual;
- `gzip -t` aprovado;
- hashes do banco e do pacote conferidos;
- anexos remotos confirmados com estado `uploaded`;
- restauração integral pela internet aprovada em diretório temporário;
- 874 testes e 124 subtestes aprovados;
- lint e build do React aprovados com Node 22.22.0.

As 2.166 linhas de `normalization_issue` representam 1.083 alertas distintos
observados em duas execuções. A repetição preserva a auditoria por execução
e não duplica entidades normalizadas.

## Limitações

- `COMPLETE` significa completo em relação ao snapshot, não a todo o PNCP;
- atas e empenhos permanecem com cobertura `PARTIAL`;
- a ausência de registro não comprova inexistência na fonte;
- `pca_contratacao_link` permanece vazia por falta de evidência oficial.
