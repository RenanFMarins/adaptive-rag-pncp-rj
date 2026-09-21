"""
Coleta da base normativa (editais_normativo).

Lê o bloco `editais_normativo` do corpus_manifest.yaml, grava os documentos em
data/raw/<versao>/editais_normativo/ e os registros da coleta em
data/inventory/<versao>_editais_normativo.json, seguindo as regras do
enunciado (item 2.3):

- idempotente: arquivo já baixado não é baixado de novo;
- retomável: se a coleta cair no meio, rodar de novo continua de onde parou;
- respeita o rate_limit_seg do manifesto;
- registra falhas sem abortar: um link com problema vira status "falhou".

Uso:
    python -m app.modules.normative.services --manifest corpus_manifest.yaml --versao v1
"""

import argparse
import hashlib
import json
import shutil
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import requests
import truststore
import yaml

# Os sites do governo (Planalto, PNCP) usam certificados da ICP-Brasil, que o
# Python não reconhece sozinho (dá SSLError). O truststore faz o Python usar os
# certificados do Windows, que já confiam na ICP-Brasil.
truststore.inject_into_ssl()

BASE_ID = "editais_normativo"
TENTATIVAS = 3              # o PNCP às vezes responde 422 e funciona segundos depois
ESPERA_ENTRE_TENTATIVAS = 5  # segundos

sessao = requests.Session()
# O Planalto não responde se o programa não se identificar como navegador.
sessao.headers.update({"User-Agent": "Mozilla/5.0 (compatible; rag-grande-desafio-grupo03)"})


# ---------------------------------------------------------------------------
# Funções auxiliares
# ---------------------------------------------------------------------------

def agora():
    """Data e hora atual com fuso, no formato usado no inventário."""
    return datetime.now().astimezone().isoformat(timespec="seconds")


def sha256_de(conteudo: bytes) -> str:
    """Impressão digital do arquivo: muda se qualquer byte mudar."""
    return hashlib.sha256(conteudo).hexdigest()


def detectar_tipo(conteudo: bytes) -> str | None:
    """
    Descobre o tipo pelo começo do arquivo, e não pelo que o site diz.
    Isso pega os casos que já vimos: a página de erro do PNCP (JSON) e a
    "verificação de segurança" do Senado (HTML no lugar do PDF).
    """
    inicio = conteudo[:1024].lstrip().lower()
    if inicio.startswith(b"%pdf"):
        return "pdf"
    if inicio.startswith(b"pk"):
        return "zip"
    if inicio.startswith(b"<!doctype html") or inicio.startswith(b"<html"):
        return "html"
    return None


def nome_do_arquivo(url: str) -> str:
    """
    Gera um nome fixo para cada URL (sem extensão), para a coleta saber se o
    arquivo já foi baixado. O mesmo link sempre gera o mesmo nome.

    PNCP:     .../orgaos/<cnpj>/compras/<ano>/<seq>/arquivos/<n>  -> pncp_<cnpj>_<ano>_<seq>_arq<n>
    Planalto: .../lei/l14133.htm                                 -> planalto_l14133
    """
    partes = urlparse(url).path.strip("/").split("/")
    if "pncp.gov.br" in url and "orgaos" in partes:
        i = partes.index("orgaos")
        cnpj, ano, seq, n = partes[i + 1], partes[i + 3], partes[i + 4], partes[i + 6]
        return f"pncp_{cnpj}_{ano}_{seq}_arq{n}"
    if "planalto.gov.br" in url:
        return "planalto_" + Path(partes[-1]).stem
    # Qualquer outro site: usa o final do caminho
    return Path(partes[-1]).stem or "documento"


def ja_baixado(pasta: Path, nome: str) -> Path | None:
    """Idempotência: procura o arquivo com qualquer extensão."""
    encontrados = list(pasta.glob(nome + ".*"))
    return encontrados[0] if encontrados else None


def baixar_com_retentativa(url: str) -> bytes:
    """
    Baixa a URL tentando de novo quando dá erro. Se todas as tentativas
    falharem, levanta exceção com o último erro (quem chama decide o que fazer).
    """
    ultimo_erro = None
    for tentativa in range(1, TENTATIVAS + 1):
        try:
            resposta = sessao.get(url, timeout=120)
            if resposta.status_code == 200:
                return resposta.content
            ultimo_erro = f"HTTP {resposta.status_code}"
        except requests.RequestException as erro:
            ultimo_erro = type(erro).__name__
        if tentativa < TENTATIVAS:
            time.sleep(ESPERA_ENTRE_TENTATIVAS)
    raise RuntimeError(f"{ultimo_erro} após {TENTATIVAS} tentativas")


def registro(caminho, tipo, conteudo, origem, status="ok", erro=None):
    """Uma linha do inventário, no formato do enunciado."""
    return {
        "path": str(caminho).replace("\\", "/") if caminho else None,
        "base_id": BASE_ID,
        "tipo": tipo,
        "bytes": len(conteudo) if conteudo else 0,
        "sha256": sha256_de(conteudo) if conteudo else None,
        "origem": origem,
        "coletado_em": agora(),
        "status": status,
        "erro": erro,
    }


# ---------------------------------------------------------------------------
# Coleta
# ---------------------------------------------------------------------------

def carregar_bloco_normativo(caminho_manifesto: str) -> dict:
    """Lê o manifesto e devolve só o bloco da base normativa."""
    with open(caminho_manifesto, encoding="utf-8") as f:
        manifesto = yaml.safe_load(f)
    for base in manifesto["bases"]:
        if base["base_id"] == BASE_ID:
            return base
    raise ValueError(f"Base {BASE_ID} não encontrada no manifesto")


def coletar_urls(urls, pasta, rate_limit):
    """Parte 1: documentos baixados por URL (Lei 14.133 e editais do PNCP)."""
    registros = []
    for url in urls:
        nome = nome_do_arquivo(url)

        existente = ja_baixado(pasta, nome)
        if existente:
            conteudo = existente.read_bytes()
            print(f"  [já existe] {existente.name}")
            registros.append(registro(existente, existente.suffix[1:], conteudo, url))
            continue

        try:
            conteudo = baixar_com_retentativa(url)
        except RuntimeError as erro:
            print(f"  [FALHOU]    {url} -> {erro}")
            registros.append(registro(None, None, None, url, "falhou", str(erro)))
            time.sleep(rate_limit)
            continue

        tipo = detectar_tipo(conteudo)
        if tipo not in ("pdf", "html", "zip"):
            # Veio uma página de erro ou algo inesperado: não salva como documento
            print(f"  [FALHOU]    {url} -> conteúdo não é PDF/HTML/ZIP")
            registros.append(registro(None, None, None, url, "falhou",
                                      "conteúdo inesperado (não é PDF/HTML/ZIP)"))
        else:
            destino = pasta / f"{nome}.{tipo}"
            destino.write_bytes(conteudo)
            print(f"  [baixado]   {destino.name} ({len(conteudo):,} bytes)")
            registros.append(registro(destino, tipo, conteudo, url))

        time.sleep(rate_limit)  # respeita o site entre um download e outro
    return registros


def coletar_arquivos_locais(bloco, pasta):
    """
    Parte 2: decretos baixados à mão (data/manual/...). Copia para a versão
    e confere o sha256 anotado no manifesto. Hash diferente vira falha.
    """
    registros = []
    if not bloco:
        return registros
    origem_pasta = Path(bloco["pasta"])
    for item in bloco["arquivos"]:
        origem = origem_pasta / item["arquivo"]
        if not origem.exists():
            print(f"  [FALHOU]    {origem} não encontrado")
            registros.append(registro(None, None, None, item["origem"], "falhou", "arquivo local não encontrado"))
            continue

        conteudo = origem.read_bytes()
        if sha256_de(conteudo) != item["sha256"].lower():
            print(f"  [FALHOU]    {origem.name}: sha256 diferente do manifesto")
            registros.append(registro(None, None, None, item["origem"], "falhou", "sha256 diferente do manifesto"))
            continue

        destino = pasta / item["arquivo"]
        if not destino.exists():
            shutil.copy2(origem, destino)
            print(f"  [copiado]   {destino.name}")
        else:
            print(f"  [já existe] {destino.name}")
        registros.append(registro(destino, detectar_tipo(conteudo), conteudo, item["origem"]))
    return registros


def coletar(caminho_manifesto="corpus_manifest.yaml", versao="v1", raiz="data/raw"):
    """Coleta completa da base normativa. Devolve a lista de registros."""
    base = carregar_bloco_normativo(caminho_manifesto)
    acesso = base["acesso"]
    pasta = Path(raiz) / versao / BASE_ID
    pasta.mkdir(parents=True, exist_ok=True)

    print(f"Coletando {BASE_ID} em {pasta}")
    registros = coletar_urls(acesso.get("urls", []), pasta, acesso.get("rate_limit_seg", 1.0))
    registros += coletar_arquivos_locais(acesso.get("arquivos_locais"), pasta)

    ok = sum(r["status"] == "ok" for r in registros)
    falhas = len(registros) - ok
    print(f"Resumo: {ok} ok, {falhas} falhas | volume_alvo {base['volume_alvo']} "
          f"| divergência {base['volume_alvo'] - ok}")

    # Guarda os registros para quem monta o inventário (data/inventory/)
    pasta_inventario = Path("data/inventory")
    pasta_inventario.mkdir(parents=True, exist_ok=True)
    saida = pasta_inventario / f"{versao}_{BASE_ID}.json"
    saida.write_text(json.dumps(registros, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Registros salvos em {saida}")
    return registros


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Coleta da base normativa")
    parser.add_argument("--manifest", default="corpus_manifest.yaml")
    parser.add_argument("--versao", default="v1")
    parser.add_argument("--raiz", default="data/raw")
    args = parser.parse_args()
    coletar(args.manifest, args.versao, args.raiz)
