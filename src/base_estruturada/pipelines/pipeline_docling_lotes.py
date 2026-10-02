"""Extracao Docling por lotes, preparada para execucao no Google Colab.

O modulo nao baixa nada do PNCP e nao altera os manifestos originais. Ele
trabalha em duas etapas:

1. ``gerar_fila_docling`` transforma os manifestos em uma fila portavel;
2. ``executar_docling_por_lotes`` processa a fila em microlotes e persiste um
   checkpoint depois de cada microlote.

Os arquivos de entrada podem ficar temporariamente em ``/content``. Os
Markdowns, a fila e o checkpoint devem ficar em uma pasta persistente (Drive
ou projeto local), para ser possivel retomar uma sessao interrompida.
"""

from __future__ import annotations

import importlib.metadata
import os
import platform
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

from src.base_estruturada.pncp.repository import salvar_json


SCHEMA_FILA = "fila_docling_pncp_v1"
SCHEMA_ESTADO = "estado_docling_pncp_v1"


def _agora() -> str:
    return datetime.now(timezone.utc).isoformat()


def _nome_seguro(texto: str) -> str:
    texto = re.sub(r'[<>:"/\\|?*]', "-", texto).strip()
    return (texto or "sem_nome")[:140]


def _caminho_relativo_documentos(caminho: str | Path) -> str:
    """Remove a parte local ate ``data/documents`` de um caminho.

    A fila nao pode guardar ``C:\\Users\\...`` porque esse caminho nao existe
    no Colab. O ZIP enviado ao Colab deve conter ``original/`` e ``expanded/``
    na raiz; por isso o caminho retornado comeca por uma dessas pastas.
    """

    texto = str(caminho).replace("\\", "/")
    marcador = "/data/documents/"
    indice = texto.lower().find(marcador)
    if indice >= 0:
        return texto[indice + len(marcador):]

    texto = texto.removeprefix("data/documents/")
    return texto.lstrip("/")


def _iterar_pdfs_manifesto(
    manifesto: list[dict[str, Any]],
    origem: str,
) -> Iterator[dict[str, Any]]:
    """Produz PDFs diretos e PDFs que foram expandidos de pacotes."""

    vistos: set[tuple[str, int | None, str, str]] = set()

    for entidade in manifesto:
        if not isinstance(entidade, dict):
            continue

        controle = str(entidade.get("numeroControlePNCP") or "")
        if not controle:
            continue

        for documento in entidade.get("documentos") or []:
            if not isinstance(documento, dict):
                continue

            sequencial = documento.get("sequencialDocumento")
            fontes: list[tuple[str, str]] = []

            download = documento.get("download") or {}
            caminho_download = str(download.get("caminho") or "")
            if (
                download.get("formato") == "PDF"
                and caminho_download.lower().endswith(".pdf")
            ):
                fontes.append(("pdf_original", caminho_download))

            extracao = documento.get("extracao") or {}
            for caminho in extracao.get("arquivos") or []:
                caminho_texto = str(caminho)
                if caminho_texto.lower().endswith(".pdf"):
                    fontes.append(("pdf_expandido_de_zip", caminho_texto))

            for tipo_fonte, caminho in sorted(fontes, key=lambda item: item[1].lower()):
                relativo = _caminho_relativo_documentos(caminho)
                chave = (controle, sequencial, tipo_fonte, relativo)
                if chave in vistos:
                    continue
                vistos.add(chave)
                yield {
                    "origem": origem,
                    "numeroControlePNCP": controle,
                    "sequencialDocumento": sequencial,
                    "tipoDocumento": documento.get("tipoDocumentoNome"),
                    "tituloDocumento": documento.get("titulo"),
                    "urlFontePncp": documento.get("url") or documento.get("uri"),
                    "tipoFonte": tipo_fonte,
                    "caminhoFonteRelativo": relativo,
                }


def gerar_fila_docling(
    periodo: str,
    manifestos: dict[str, list[dict[str, Any]]],
    caminho_fila: Path,
) -> dict[str, Any]:
    """Gera uma fila deterministica e portavel, sem editar manifestos."""

    documentos: list[dict[str, Any]] = []
    for origem in ("contratos", "contratacoes"):
        manifesto = manifestos.get(origem, [])
        if not isinstance(manifesto, list):
            continue
        documentos.extend(_iterar_pdfs_manifesto(manifesto, origem))

    documentos.sort(
        key=lambda item: (
            item["origem"],
            item["numeroControlePNCP"],
            str(item.get("sequencialDocumento") or ""),
            item["caminhoFonteRelativo"],
        )
    )

    for documento in documentos:
        # A chave usa a identidade do documento, nao sua posicao na fila.
        # Assim, inserir PDFs em execucoes futuras nao desloca checkpoints.
        documento["idProcessamento"] = "|".join(
            (
                periodo,
                str(documento["origem"]),
                str(documento["numeroControlePNCP"]),
                str(documento.get("sequencialDocumento") or "sem_sequencial"),
                str(documento["tipoFonte"]),
                str(documento["caminhoFonteRelativo"]),
            )
        )

    fila = {
        "schemaVersion": SCHEMA_FILA,
        "periodo": periodo,
        "geradoEm": _agora(),
        "orientacaoEntrada": (
            "Envie ao Colab um ZIP cuja raiz contenha as pastas original/ "
            "e expanded/ de data/documents."
        ),
        "quantidadeDocumentos": len(documentos),
        "documentos": documentos,
    }
    salvar_json(caminho_fila, fila)
    return fila


def _carregar_estado(
    caminho_estado: Path,
    periodo: str,
    perfil: str,
) -> dict[str, Any]:
    if caminho_estado.is_file():
        import json

        with caminho_estado.open("r", encoding="utf-8") as arquivo:
            estado = json.load(arquivo)
        if isinstance(estado, dict) and estado.get("schemaVersion") == SCHEMA_ESTADO:
            return estado

    return {
        "schemaVersion": SCHEMA_ESTADO,
        "periodo": periodo,
        "perfil": perfil,
        "criadoEm": _agora(),
        "ambiente": _informacoes_ambiente(),
        "documentos": {},
    }


def _informacoes_ambiente() -> dict[str, Any]:
    """Registra o ambiente automaticamente; nao exige acao manual."""

    ambiente: dict[str, Any] = {
        "python": sys.version.split()[0],
        "sistema": platform.platform(),
    }
    for pacote in ("docling", "torch"):
        try:
            ambiente[pacote] = importlib.metadata.version(pacote)
        except importlib.metadata.PackageNotFoundError:
            ambiente[pacote] = None

    try:
        import torch

        ambiente["cudaDisponivel"] = torch.cuda.is_available()
        if torch.cuda.is_available():
            ambiente["gpu"] = torch.cuda.get_device_name(0)
    except ImportError:
        ambiente["cudaDisponivel"] = False

    return ambiente


def _criar_conversor_docling(
    perfil: str,
    artifacts_path: Path | None,
):
    """Cria uma unica instancia do Docling para toda a execucao."""

    try:
        from docling.datamodel.accelerator_options import (
            AcceleratorDevice,
            AcceleratorOptions,
        )
        from docling.datamodel.base_models import InputFormat
        from docling.datamodel.pipeline_options import (
            PdfPipelineOptions,
            TableFormerMode,
        )
        from docling.document_converter import DocumentConverter, PdfFormatOption
    except ImportError as exc:
        raise RuntimeError(
            "Docling nao esta instalado. No Colab, execute primeiro "
            "`pip install -r requirements-colab.txt`."
        ) from exc

    opcoes = PdfPipelineOptions()
    opcoes.accelerator_options = AcceleratorOptions(
        device=AcceleratorDevice.CUDA,
        num_threads=min(4, os.cpu_count() or 4),
    )

    if perfil == "digital_rapido":
        # Perfil futuro: so use quando houver certeza de que o PDF tem texto.
        opcoes.do_ocr = False
        opcoes.do_table_structure = True
        opcoes.table_structure_options.mode = TableFormerMode.FAST
        opcoes.do_code_enrichment = False
        opcoes.do_formula_enrichment = False
        opcoes.generate_page_images = False
        opcoes.generate_picture_images = False
    elif perfil != "qualidade":
        raise ValueError("perfil deve ser 'qualidade' ou 'digital_rapido'.")

    if artifacts_path is not None and artifacts_path.is_dir():
        opcoes.artifacts_path = artifacts_path.resolve()

    return DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=opcoes)
        }
    )


def _destino_markdown(pasta_saida: Path, documento: dict[str, Any]) -> Path:
    nome_fonte = Path(documento["caminhoFonteRelativo"]).stem
    return (
        pasta_saida
        / str(documento["origem"])
        / _nome_seguro(str(documento["numeroControlePNCP"]))
        / f"{documento['tipoFonte']}__{_nome_seguro(nome_fonte)}.md"
    )


def _relativo_portavel(caminho: Path, raiz: Path) -> str:
    try:
        return caminho.resolve().relative_to(raiz.resolve()).as_posix()
    except ValueError:
        return str(caminho)


def _microlotes(itens: list[dict[str, Any]], tamanho: int) -> Iterator[list[dict[str, Any]]]:
    for inicio in range(0, len(itens), tamanho):
        yield itens[inicio: inicio + tamanho]


def executar_docling_por_lotes(
    fila: dict[str, Any],
    caminho_estado: Path,
    caminho_relatorio: Path,
    raiz_documentos: Path,
    pasta_saida: Path,
    raiz_projeto_portavel: Path,
    tamanho_microlote: int = 50,
    limite_documentos: int | None = 1_000,
    perfil: str = "qualidade",
    artifacts_path: Path | None = None,
    reprocessar_erros: bool = False,
) -> dict[str, int]:
    """Converte pendentes em microlotes e salva estado apos cada um.

    ``limite_documentos`` e' o lote logico da execucao. Por exemplo, 1.000
    documentos podem ser processados em vinte microlotes de 50, com vinte
    pontos de retomada.
    """

    if tamanho_microlote <= 0:
        raise ValueError("tamanho_microlote deve ser maior que zero.")
    documentos = fila.get("documentos")
    periodo = str(fila.get("periodo") or "sem_periodo")
    if not isinstance(documentos, list):
        raise RuntimeError("A fila nao contem a lista 'documentos'.")

    estado = _carregar_estado(caminho_estado, periodo, perfil)
    registros_estado = estado.setdefault("documentos", {})

    pendentes: list[dict[str, Any]] = []
    for documento in documentos:
        if not isinstance(documento, dict):
            continue
        anterior = registros_estado.get(documento.get("idProcessamento"), {})
        status = anterior.get("status")
        if status == "concluido":
            continue
        if status == "erro" and not reprocessar_erros:
            continue
        pendentes.append(documento)

    if limite_documentos is not None:
        pendentes = pendentes[:limite_documentos]

    resumo = {
        "selecionados": len(pendentes),
        "concluidos": 0,
        "erros": 0,
        "arquivosNaoEncontrados": 0,
        "microlotes": 0,
    }
    if not pendentes:
        estado["atualizadoEm"] = _agora()
        salvar_json(caminho_estado, estado)
        salvar_json(caminho_relatorio, {"resumo": resumo, "geradoEm": _agora()})
        return resumo

    conversor = _criar_conversor_docling(perfil, artifacts_path)

    for numero_lote, microlote in enumerate(_microlotes(pendentes, tamanho_microlote), start=1):
        existentes: list[tuple[dict[str, Any], Path]] = []
        for documento in microlote:
            caminho = raiz_documentos / documento["caminhoFonteRelativo"]
            if not caminho.is_file():
                registros_estado[documento["idProcessamento"]] = {
                    **documento,
                    "status": "erro",
                    "erro": "arquivo_nao_encontrado_no_lote",
                    "atualizadoEm": _agora(),
                }
                resumo["arquivosNaoEncontrados"] += 1
                resumo["erros"] += 1
            else:
                existentes.append((documento, caminho))

        if existentes:
            inicio = time.perf_counter()
            resultados = conversor.convert_all(
                [caminho for _, caminho in existentes],
                raises_on_error=False,
            )

            for (documento, _), resultado in zip(existentes, resultados):
                inicio_documento = time.perf_counter()
                try:
                    if resultado.document is None:
                        raise RuntimeError(str(getattr(resultado, "status", "sem documento")))
                    markdown = resultado.document.export_to_markdown()
                    destino = _destino_markdown(pasta_saida, documento)
                    destino.parent.mkdir(parents=True, exist_ok=True)
                    destino.write_text(markdown, encoding="utf-8")
                    registros_estado[documento["idProcessamento"]] = {
                        **documento,
                        "status": "concluido",
                        "caminhoMarkdown": _relativo_portavel(destino, raiz_projeto_portavel),
                        "quantidadeCaracteres": len(markdown.strip()),
                        "atualizadoEm": _agora(),
                        # A conversao ocorre em lote; este tempo mede apenas
                        # exportacao/gravação deste item, nao a inferencia GPU.
                        "tempoPersistenciaSegundos": round(time.perf_counter() - inicio_documento, 2),
                    }
                    resumo["concluidos"] += 1
                except Exception as exc:
                    registros_estado[documento["idProcessamento"]] = {
                        **documento,
                        "status": "erro",
                        "erro": f"{type(exc).__name__}: {exc}",
                        "atualizadoEm": _agora(),
                    }
                    resumo["erros"] += 1

            tempo_lote = round(time.perf_counter() - inicio, 2)
        else:
            tempo_lote = 0.0

        resumo["microlotes"] += 1
        estado["atualizadoEm"] = _agora()
        estado["ultimoMicrolote"] = {
            "numero": numero_lote,
            "documentos": len(microlote),
            "tempoSegundos": tempo_lote,
        }
        estado["resumoParcial"] = resumo.copy()
        # Este e' o checkpoint de retomada: e' salvo apos cada microlote.
        salvar_json(caminho_estado, estado)
        print(
            f"Microlote {numero_lote} | documentos={len(microlote)} | "
            f"concluidos={resumo['concluidos']} | erros={resumo['erros']}"
        )

    relatorio = {
        "schemaVersion": "relatorio_extracao_docling_v1",
        "geradoEm": _agora(),
        "periodo": periodo,
        "perfil": perfil,
        "ambiente": estado.get("ambiente"),
        "resumo": resumo,
    }
    salvar_json(caminho_relatorio, relatorio)
    return resumo
