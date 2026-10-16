
from llm_ecoa import client, GENERATION_MODEL
from openai import (
    APITimeoutError,
    APIConnectionError,
    APIStatusError,
)

print("Iniciando teste da API ECOA...")

try:
    resposta = client.with_options(
        timeout=20,
        max_retries=0,
    ).chat.completions.create(
        model=GENERATION_MODEL,
        messages=[
            {
                "role": "user",
                "content": "Responda apenas OK."
            }
        ],
        max_tokens=20,
    )

    print("API funcionando!")
    print("Resposta:", resposta.choices[0].message.content)

except APITimeoutError:
    print("TIMEOUT: a API não respondeu dentro do prazo.")

except APIConnectionError as erro:
    print("ERRO DE CONEXÃO:", erro)

except APIStatusError as erro:
    print("ERRO HTTP:", erro.status_code)
    print("Detalhes:", erro.response.text[:500])

except Exception as erro:
    print("ERRO INESPERADO:", type(erro).__name__, erro)
