# CORPUS_INVENTORY

**Time 03 · Contratações Públicas do Estado do Rio de Janeiro**

Este documento registra **o que entrou de fato no corpus**, versão por versão.
O que deve entrar está declarado no [`corpus_manifest.yaml`](corpus_manifest.yaml).

| | |
| --- | --- |
| **Versão corrente** | `v1` |
| **Coleta da v1** | 21 a 23/09/2026 |
| **Como reproduzir** | `python -m app.modules.normative.services fetch --manifest corpus_manifest.yaml --versao v1` |
| **Nova versão + diff** | `python -m app.modules.normative.services update --manifest corpus_manifest.yaml` |
| **Inventário legível** | `python -m app.modules.normative.services inventory --versao v1` |
| **Onde ficam os arquivos** | `data/raw/v1/<base_id>/` (não versionado no Git) |
| **Registros por arquivo** | `data/inventory/v1_<base_id>.json` (versionado) |

---

## 1. Totais da versão v1

| | |
| --- | --- |
| **Arquivos coletados** | 13 |
| **Bytes** | 8.916.113 (8,5 MB) |
| **Falhas** | 0 |
| **Bases concluídas** | 1 de 4 |

---

## 2. Por base

| base_id | Natureza | Arquivos | Formatos | Bytes | volume_alvo | Divergência | Falhas |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `editais_normativo` | normativa | 13 | 12 pdf, 1 html | 8.916.113 | 13 | 0 | 0 |
| `contratos_estruturado` | estruturada | — | — | — | 1200 | — | — |
| `atas_conversacional` | conversacional | — | — | — | 20 | — | — |
| `pca_agregada` | agregada | — | — | — | a definir | — | — |

> As três últimas bases ainda não foram coletadas pelo script de coleta. Os
> responsáveis por cada base preenchem a própria linha quando a coleta rodar.

---

## 3. Detalhe da base normativa (`editais_normativo`)

**Fontes:** Lei 14.133/2021 (Planalto), 7 decretos estaduais do RJ e 5 editais de
órgãos do RJ publicados no PNCP, ano-base 2025.

**Coletado em:** 21 a 23/09/2026 · **Divergência em relação ao `volume_alvo`:** 0

### 3.1 Lei e editais (baixados por URL)

| Arquivo | Documento | Bytes | sha256 (início) |
| --- | --- | --- | --- |
| `planalto_l14133.html` | Lei 14.133/2021 (texto compilado) | 649.705 | `1cbcced00ae8` |
| `pncp_42498600000171_2025_926_arq1.pdf` | Edital · equipamentos (Fundação Saúde RJ) | 560.992 | `1062573c7c4e` |
| `pncp_11867889000125_2025_48_arq1.pdf` | Edital · materiais de saúde (Bom Jardim/RJ) | 2.289.291 | `531d0ca7d804` |
| `pncp_42498600000171_2025_4831_arq9.pdf` | Edital · material de escritório (PMERJ) | 498.281 | `0ab17df0e23b` |
| `pncp_42498600000171_2025_6553_arq1.pdf` | Edital · licenciamento de software (PRODERJ) | 1.023.700 | `0edc5df50abd` |
| `pncp_42498600000171_2025_921_arq1.pdf` | Edital · medicamentos (Fundação Saúde RJ) | 1.934.918 | `47f75b817267` |

### 3.2 Decretos estaduais (baixados manualmente, com autorização do professor)

O site de origem bloqueia download automático (HTTP 403). Os arquivos estão
versionados em `data/manual/editais_normativo/` e o `sha256` de cada um está
declarado no manifesto, o que garante a reprodutibilidade.

| Arquivo | Norma | Bytes | sha256 (início) |
| --- | --- | --- | --- |
| `decreto-48760-2023-pca.pdf` | Decreto RJ 48.760/2023 · Plano de Contratações Anual | 290.216 | `66802a832cac` |
| `decreto-49129-2024-altera-pca.pdf` | Decreto RJ 49.129/2024 · altera o 48.760 | 168.712 | `4f40867f0c03` |
| `decreto-48778-2023-menor-preco.pdf` | Decreto RJ 48.778/2023 · menor preço / maior desconto | 282.257 | `1dd02eac1ed6` |
| `decreto-48816-2023-fase-preparatoria.pdf` | Decreto RJ 48.816/2023 · fase preparatória | 394.175 | `0aafdd4c0f0d` |
| `decreto-48817-2023-gestao-fiscalizacao.pdf` | Decreto RJ 48.817/2023 · gestão e fiscalização | 301.772 | `afceff2fac64` |
| `decreto-48820-2023-contratacao-direta.pdf` | Decreto RJ 48.820/2023 · contratação direta | 236.120 | `b8fe3f78d349` |
| `decreto-48843-2023-registro-de-precos.pdf` | Decreto RJ 48.843/2023 · registro de preços | 285.974 | `668ba5f4f42d` |

### 3.3 Falhas

Nenhuma nesta coleta.

**Observação registrada durante a coleta:** a API do PNCP responde
intermitentemente `HTTP 422` no download dos editais. A coleta tenta 3 vezes com
pausa de 5 segundos antes de marcar como `falhou`, e confere o início do arquivo
(`%PDF` / `<html`) para não salvar uma mensagem de erro como se fosse documento.

### 3.4 Processamento

| | |
| --- | --- |
| **Trechos (chunks) gerados** | 794 |
| **Saída** | `data/processed/v1_editais_normativo.jsonl` |
| **Comando** | `python -m app.modules.ingest.services --versao v1` |
| **Critério** | lei e decretos: 1 artigo por chunk · editais: 1 cláusula por chunk |
| **Conferência** | Lei 14.133 com os artigos 1 a 194 em ordem, mais o Art. 44-A incluído pela Lei 15.210/2025 |
| **Sensibilidade** | CPF e telefone mascarados na ingestão (18 trechos marcados com `dados_pessoais`) |
| **Overlap** | 281 trechos de continuação repetem os 200 caracteres finais da parte anterior (`tem_overlap`) |
| **Limpeza** | Cabeçalho e rodapé de impressão (data/hora, link e número da página) removidos antes da divisão |

> O total foi de 784 para 796 trechos quando o overlap entrou: a cauda de 200
> caracteres ocupa parte do limite de 4.000 de cada trecho, então artigos e
> cláusulas longos passam a ser cortados um pouco mais cedo e alguns geram uma
> parte a mais. Depois, a remoção do cabeçalho e do rodapé de impressão dos
> editais do SEI (125 linhas, todas no edital de 60 páginas) trouxe o total
> para 794: sem esse lixo, alguns trechos deixam de estourar o limite e não se
> dividem mais.

### 3.5 Política de sensibilidade aplicada

A varredura dos 794 trechos encontrou dados pessoais nos editais: 4 CPFs,
2 telefones e 38 ocorrências de e-mail. O número de e-mails subiu de 31 para 38
com a entrada do overlap: alguns caem na região repetida entre uma parte e a
seguinte e são contados nos dois trechos. Não são e-mails novos.

| Dado | Tratamento | Onde |
| --- | --- | --- |
| CPF de pessoa física | **Mascarado** (`[CPF MASCARADO]`) | ingestão |
| Telefone | **Mascarado** (`[TELEFONE MASCARADO]`) | ingestão |
| E-mail | Mantido e **sinalizado** no metadado `dados_pessoais` | ingestão |
| CNPJ, nome de empresa, valores, objeto | Mantidos: públicos por lei | — |

Os e-mails encontrados são de **setores** (`licitacao.bomjardim@`, `saude.bjardim@`),
e não de pessoas físicas. Por isso foram mantidos, mas sinalizados, para o time
decidir se devem ser mascarados também.

### 3.6 Cobertura das perguntas de referência

Conferência de que o corpus responde às perguntas normativas do
[`PERSONAS.md`](PERSONAS.md):

| Tema da pergunta | Trechos encontrados | Onde |
| --- | --- | --- |
| ME/EPP em licitações (P3.1) | 44 | Lei 14.133 (Art. 4, 15, 60, 81) + decretos |
| Vigência / validade da proposta (P1.3) | 7 | Lei 14.133 Art. 90, Dec. 48.816, editais |
| Prazo de vigência de contrato | 39 | Dec. 48.816 e 48.817 |
| Adesão a ata de registro de preços | 12 | Dec. 48.843 (Art. 6 e 32) |
| Dispensa de licitação por valor | 3 | Lei 14.133 Art. 75, Dec. 48.820 |
| Pesquisa de preços | 20 | Dec. 48.816 (Art. 27 a 29) |

---

## 4. Histórico de versões

| Versão | Data | O que mudou |
| --- | --- | --- |
| `v1` | 21 a 23/09/2026 | Primeira coleta da base normativa (13 arquivos, 0 falhas) |
| `v2` | 25/09/2026 | Recoleta para validar o versionamento: nenhum arquivo entrou, saiu ou mudou de conteúdo ([DIFF_v1_v2.md](data/inventory/DIFF_v1_v2.md)) |

> **Sobre as datas.** As datas acima vêm do histórico do repositório (o primeiro
> inventário da `v1` foi comitado em 21/09/2026) e da data de modificação dos
> arquivos em `data/raw/`. O campo `coletado_em` dos JSON em `data/inventory/`
> ficou com a data da última execução do `fetch` sobre arquivos já baixados, e
> não a do download: por isso a `v1` aparece ali com 28/09/2026. Desde a
> correção do `preservar_coletado_em`, uma nova execução mantém a data original
> quando o conteúdo do arquivo não mudou.

> A `v1` permanece como corpus corrente. A `v2` foi gerada com o comando
> `update` para demonstrar que a versão anterior não é sobrescrita e que o diff
> entre versões funciona, requisito do teste de regressão das próximas sprints.
