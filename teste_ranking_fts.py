
import re
import sqlite3

from src.fts import preparar_consulta_fts5

pergunta = (
    "Quais são as responsabilidades do fiscal de contrato "
    "previstas na Lei nº 14.133/2021?"
)

termos = re.findall(r"[^\W_]+", pergunta.lower(), flags=re.UNICODE)

consulta_antiga = " OR ".join(f'"{termo}"' for termo in termos)
consulta_nova = preparar_consulta_fts5(pergunta)

alvo = 99937

conexao = sqlite3.connect("app.db")

try:
    for nome, consulta in [
        ("ANTES", consulta_antiga),
        ("DEPOIS", consulta_nova),
    ]:
        cursor = conexao.execute(
            """
            SELECT rowid
            FROM document_chunks_fts
            WHERE document_chunks_fts MATCH ?
            ORDER BY bm25(document_chunks_fts)
            LIMIT 2000
            """,
            (consulta,),
        )

        posicao = next(
            (
                indice
                for indice, (rowid,) in enumerate(cursor, start=1)
                if rowid == alvo
            ),
            None,
        )

        print(f"{nome}: {posicao or 'fora do Top 2000'}")
finally:
    conexao.close()
