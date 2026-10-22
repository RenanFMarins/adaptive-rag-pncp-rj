"""Aplica correção pontual de ranking ao src/retrieve.py; cria backup e valida sintaxe."""
import ast
from pathlib import Path
import re
import shutil

path = Path('src/retrieve.py')
if not path.is_file():
    raise SystemExit('Execute na raiz do projeto: src/retrieve.py não encontrado.')
original = path.read_text(encoding='utf-8-sig')
lines = original.splitlines(keepends=True)
tree = ast.parse(original)
funcs = {n.name: n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
required = ('_relevancia_textual', '_buscar_no_documento', 'retrieve_hibrido')
if any(x not in funcs for x in required):
    raise SystemExit('Estrutura do retrieve.py diferente da esperada; nenhuma alteração realizada.')

new_relevancia = '''def _relevancia_textual(pergunta: str, conteudo: str) -> float:
    """Pontuação contextual, sem depender de artigos ou decretos específicos."""
    import unicodedata

    def norm(s: str) -> str:
        s = unicodedata.normalize("NFKD", s or "")
        return "".join(c for c in s if not unicodedata.combining(c)).lower()

    equivalencias = {
        "fiscais": "fiscal", "fiscalizacao": "fiscal",
        "atribuicoes": "competencia", "atribuicao": "competencia",
        "competencias": "competencia", "compete": "competencia",
        "responsabilidades": "competencia", "responsabilidade": "competencia",
        "deveres": "competencia", "dever": "competencia",
    }
    ignorar = {
        "quais", "qual", "como", "que", "dos", "das", "nos", "nas",
        "sao", "previstas", "previstos", "sobre", "para", "pela", "pelo",
        "contrato", "contratos", "decreto", "estadual", "lei", "numero", "rj",
        "art", "ano", "no", "na", "do", "da", "de", "em", "uma", "um",
    }
    pergunta_limpa = re.sub(
        r"\\b(?:lei|decreto)(?:\\s+(?:estadual|federal|municipal|rj))*"
        r"\\s+(?:n[º°o.]*)?\\s*\\d{1,3}(?:\\.\\d{3})*(?:/\\d{4})?",
        " ", norm(pergunta),
    )
    def palavras(s: str) -> set[str]:
        return {equivalencias.get(t, t) for t in re.findall(r"[a-z]{3,}", s)}

    termos = palavras(pergunta_limpa) - ignorar
    if not termos:
        return 0.0
    texto = norm(conteudo)
    corpo = palavras(texto)
    cabecalho = re.sub(r"^\\s*(?:\\[)?art\\.?\\s*\\d+[^a-z]*", "", texto)
    cabecalho = cabecalho[:260]
    inicio = palavras(cabecalho)
    comuns = termos & corpo
    score = sum(2.0 if len(t) >= 6 else 1.0 for t in comuns)
    score += 5.0 * len(termos & inicio)
    if "competencia" in termos and "competencia" in inicio:
        score += 8.0
    return score
'''
new_busca = '''def _buscar_no_documento(
    db: Session,
    pergunta: str,
    documento_id: int,
    allowed_chunk_ids: set[str] | None,
    limite: int,
) -> list[tuple[str, float]]:
    """Busca local sem escrita; ordena todos os chunks elegíveis por relevância."""
    if limite <= 0:
        return []
    consulta = (
        select(DocumentChunk)
        .where(DocumentChunk.document_id == documento_id)
        .order_by(DocumentChunk.id)
    )
    if allowed_chunk_ids is not None:
        consulta = consulta.where(DocumentChunk.chunk_id.in_(allowed_chunk_ids))
    candidatos = list(db.scalars(consulta))
    pontuados = [
        (chunk, _relevancia_textual(pergunta, chunk.content or ""))
        for chunk in candidatos
    ]
    pontuados = [(chunk, score) for chunk, score in pontuados if score > 0]
    pontuados.sort(key=lambda item: (-item[1], item[0].id))
    return [(chunk.chunk_id, score) for chunk, score in pontuados[:limite]]
'''

# Atualiza a ordenação normativa para comparar relevância textual antes do rank local.
node = funcs['retrieve_hibrido']
segment = ''.join(lines[node.lineno-1:node.end_lineno])
pattern = r'''int\(item\[0\] in local_ranks\),\s*-local_ranks\.get\(item\[0\],\s*10\*\*9\),\s*item\[1\],'''
replacement = '''_relevancia_textual(pergunta, chunks[item[0]].content or ""),
                            int(item[0] in local_ranks),
                            item[1],'''
segment2, count = re.subn(pattern, replacement, segment)
if count != 1:
    raise SystemExit('Não encontrei o bloco exato de ordenação normativa; nenhuma alteração realizada.')

edits = [
    (funcs['_relevancia_textual'], new_relevancia),
    (funcs['_buscar_no_documento'], new_busca),
    (node, segment2),
]
for fn, new_text in sorted(edits, key=lambda item: item[0].lineno, reverse=True):
    lines[fn.lineno-1:fn.end_lineno] = [new_text.rstrip() + '\n']
updated = ''.join(lines)
ast.parse(updated)
backup = path.with_suffix('.py.bak_reranking')
shutil.copy2(path, backup)
path.write_text(updated, encoding='utf-8')
print('Correção aplicada:', path)
print('Backup:', backup)
print('Sintaxe validada. Execute: python .\\teste_identificar_norma.py')
