"""
Módulo de Verificação de Guardrails e Regras de Escopo.
Intercepta perguntas fora do escopo do RAG (como recomendações comerciais - P3.3).
"""

from src.prompts import SYSTEM_PROMPT_BASE

# Termos que indicam solicitação de recomendação comercial ou escolha de empresa
TERMOS_RECUSA_COMERCIAL = [
    "qual empresa devo contratar",
    "qual empresa contratar",
    "me indique uma empresa",
    "me recomende uma empresa",
    "qual o melhor fornecedor para contratar",
    "qual marca devo comprar",
    "indique um fornecedor",
]

MENSAGEM_RECUSA_PADRAO = (
    "Como assistente de dados públicos do Estado do Rio de Janeiro, não posso "
    "recomendar ou indicar empresas/fornecedores específicos. Posso apenas "
    "fornecer dados históricos de contratações, licitações ativas e estatísticas do setor público."
)

def verificar_guardrails_pergunta(pergunta: str) -> tuple[bool, str | None]:
    """
    Verifica se a pergunta viola algum guardrail de escopo antes de acionar a LLM.
    
    Retorna:
        tuple[bool, str | None]: 
            - (True, mensagem_de_recusa) se a pergunta for bloqueada.
            - (False, None) se a pergunta for válida e puder prosseguir.
    """
    pergunta_lower = pergunta.lower().strip()
    
    for termo in TERMOS_RECUSA_COMERCIAL:
        if termo in pergunta_lower:
            return True, MENSAGEM_RECUSA_PADRAO
            
    return False, None