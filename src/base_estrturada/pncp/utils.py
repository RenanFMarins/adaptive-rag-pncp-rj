from urllib.parse import urlsplit, urlunsplit, urlparse
from pathlib import Path
import re
from typing import Any


TIPOS_PRIORITARIOS = {
    "Edital",
    "Termo de Referência",
    "Estudo Técnico Preliminar",
    "Minuta do Contrato",
    "Contrato",
    "Termo Aditivo",
    "Termo de Apostilamento",
    "Ata de Registro de Preços",
    "Termo de Rescisão",
    "Relatório Final de Contrato",
    "Documento de Formalização da Demanda",
    "Mapa de Riscos",
    "Termo/Ato de Homologação",
    "Aviso de Contratação Direta",
    "Ato que autoriza a Contratação Direta",
}


def url_pura(url: str) -> str:
    """
    Remove formatos Markdown e limpa portas numéricas inválidas (como :46790)
    das URLs retornadas pela API do PNCP para evitar erros de timeout.
    """
    if not url:
        return ""

    url = url.strip()

    # 1. Trata se a URL vier encapsulada em formato Markdown [Texto](http://...)
    if url.startswith("[") and "](" in url and url.endswith(")"):
        url = url.rsplit("](", 1)[1][:-1]

    # 2. Desestrutura a URL para remover a porta do host
    partes = urlsplit(url)
    if not partes.hostname:
        return url

    # Reconstroi a URL sem a porta (partes.hostname ignora a porta automaticamente)
    url_limpa = urlunsplit((
        partes.scheme,
        partes.hostname,  # <-- Remove a porta de forma nativa e segura
        partes.path,
        partes.query,
        partes.fragment
    ))

    return url_limpa


def nome_seguro(texto: str) -> str:
    return re.sub(r'[<>:"/\\|?*]', "-", texto)


def extensao_por_content_type(
        content_type: str,
        url: str
) -> str:
    content_type = content_type.lower().split(";")[0].strip()

    extensoes = {
        "application/pdf": ".pdf",
        "application/zip": ".zip",
        "application/x-rar-compressed": ".rar",
        "application/vnd.rar": ".rar",
        "application/msword": ".doc",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
        "application/vnd.oasis.opendocument.text": ".odt",
        "image/jpeg": ".jpg",
        "image/png": ".png",
    }

    if content_type in extensoes:
        return extensoes[content_type]

    extensao_url = Path(urlparse(url).path).suffix

    if extensao_url:
        return extensao_url.lower()

    return ".bin"


def obter_tipo_documento(
    documento: dict[str, Any],
    tipos_por_id: dict[int, str],
) -> str | None:
    """
    Obtém o tipo do documento considerando as diferentes
    estruturas retornadas pelo PNCP.
    """

    # Algumas respostas já trazem o nome do tipo
    tipo_nome = documento.get("tipoDocumentoNome")
    print("=============")
    print(tipo_nome)
    print("=============")
    if tipo_nome:
        return str(tipo_nome).strip()

    # Outras podem trazer somente o ID
    tipo_id = documento.get("tipoDocumentoId")

    if tipo_id is not None:
        return tipos_por_id.get(int(tipo_id))

    return None


def deve_baixar_documento(
    documento: dict[str, Any],
    tipos_por_id: dict[int, str],
) -> bool:

    tipo = obter_tipo_documento(
        documento,
        tipos_por_id
    )

    if not tipo:
        return False

    return tipo in TIPOS_PRIORITARIOS
