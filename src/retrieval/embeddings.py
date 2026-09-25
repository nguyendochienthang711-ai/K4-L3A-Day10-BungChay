from __future__ import annotations

from functools import lru_cache

import sys
import types
import unittest.mock

# Safe shim for environments where pyarrow.dataset DLL is blocked by Windows AppLocker/WDAC
if "datasets" not in sys.modules:
    try:
        import datasets  # noqa: F401
    except Exception:
        class _DatasetsModule(types.ModuleType):
            def __getattr__(self, name):
                return unittest.mock.MagicMock()

        _m = _DatasetsModule("datasets")
        _m.__version__ = "4.0.0"
        _m.__file__ = "datasets/__init__.py"
        _m.__spec__ = unittest.mock.MagicMock()
        _m.Dataset = unittest.mock.MagicMock
        _m.DatasetDict = unittest.mock.MagicMock
        _m.IterableDataset = unittest.mock.MagicMock
        _m.IterableDatasetDict = unittest.mock.MagicMock
        _m.Value = unittest.mock.MagicMock
        _m.Features = unittest.mock.MagicMock
        sys.modules["datasets"] = _m

from langchain_core.embeddings import Embeddings
from sentence_transformers import SentenceTransformer


@lru_cache(maxsize=4)
def _load_model(model_name: str) -> SentenceTransformer:
    return SentenceTransformer(model_name)


class MiniLMEmbeddings(Embeddings):
    def __init__(self, model_name: str):
        self.model = _load_model(model_name)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()

    def embed_query(self, text: str) -> list[float]:
        embedding = self.model.encode([text], normalize_embeddings=True)
        return embedding[0].tolist()
