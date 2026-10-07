from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.index import carregar_indice_faiss, indexar_chunks_incrementalmente


class IncrementalFaissIndexTests(unittest.TestCase):
    def test_segunda_execucao_embeda_somente_chunk_novo(self):
        chamadas: list[str] = []

        def embedding(texto: str) -> list[float]:
            chamadas.append(texto)
            return [1.0, 0.0] if "alpha" in texto else [0.0, 1.0]

        with TemporaryDirectory() as pasta:
            diretorio = Path(pasta)
            _, primeiro = indexar_chunks_incrementalmente(
                [("c1", "alpha"), ("c2", "beta")],
                embedding,
                diretorio,
                tamanho_lote=1,
                modelo_embedding="fake-v1",
                origem="lote_001",
            )
            _, segundo = indexar_chunks_incrementalmente(
                [("c1", "alpha"), ("c2", "beta"), ("c3", "beta novo")],
                embedding,
                diretorio,
                tamanho_lote=1,
                modelo_embedding="fake-v1",
                origem="lote_002",
            )
            indice = carregar_indice_faiss(diretorio)

        self.assertEqual(primeiro.novos, 2)
        self.assertEqual(segundo.ja_indexados, 2)
        self.assertEqual(segundo.novos, 1)
        self.assertEqual(chamadas, ["alpha", "beta", "beta novo"])
        self.assertEqual(indice.chunk_ids, ["c1", "c2", "c3"])
        self.assertEqual(indice.search([0.0, 1.0], top_k=1)[0][0], "c2")


if __name__ == "__main__":
    unittest.main()
