# Restauração da base normalizada sanitizada

Este procedimento instala o snapshot público da base normalizada sem colocar
arquivos SQLite no histórico Git.

## Release padrão

- repositório: `RenanFMarins/adaptive-rag-pncp-rj`;
- tag: `base-normalizada-pncp-rj-20261020-v1`;
- destino: `data/normalized/pncp_rj_normalized.db`;
- cobertura principal: PNCP/RJ até 19/10/2026;
- atas e empenhos possuem cobertura parcial declarada no manifesto.

O snapshot protege identificadores e nomes de fornecedores PF/PE por
pseudonimização. A chave privada não integra a release.

## Instalação pela internet

Na raiz do clone:

```bash
python -m scripts.restore_normalized_release
```

O diretório de destino precisa ter aproximadamente 3,4 GB livres para manter
o arquivo compactado, a base em validação e uma margem de segurança. O script
verifica o espaço antes de baixar o anexo principal.

## Instalação a partir de anexos locais

Baixe na mesma pasta:

- `pncp_rj_normalized_public_20261020.sqlite.gz`;
- `release_manifest.json`;
- `SHA256SUMS.txt`.

Depois execute:

```bash
python -m scripts.restore_normalized_release \
  --source-directory /caminho/para/os/anexos
```

## Substituição controlada

Por padrão, um destino existente é preservado. Para substituí-lo:

```bash
python -m scripts.restore_normalized_release --force
```

Mesmo com `--force`, a base atual só é substituída por `os.replace` depois de
o novo arquivo passar por todas as validações. Falhas de rede, checksum,
descompactação ou SQLite não alteram o destino existente.

## Validações executadas

1. tag e nomes seguros no manifesto;
2. tamanho e SHA-256 do arquivo compactado;
3. SHA-256 da base descompactada;
4. presença das tabelas normalizadas obrigatórias;
5. `PRAGMA integrity_check`;
6. `PRAGMA foreign_key_check`;
7. contagens de cada tabela contra o manifesto;
8. versão da política e fingerprint da sanitização.

O script não baixa RAW, não executa migrations e não grava na base durante
a validação.
