#  -----------------------------------------------------------------------------------------
#  (C) Copyright IBM Corp. 2024.
#  https://opensource.org/licenses/BSD-3-Clause
#  -----------------------------------------------------------------------------------------

from ibm_watsonx_ai.foundation_models.extensions.rag.vector_stores.langchain_vector_store_adapter import (
    LangChainVectorStoreAdapter,
)
from ibm_watsonx_ai.wml_client_error import MissingExtension

try:
    from langchain_milvus import Milvus
except ImportError:
    raise MissingExtension("langchain_milvus")


class MilvusLangchainAdapter(LangChainVectorStoreAdapter):

    def __init__(self, vector_store: Milvus) -> None:
        super().__init__(vector_store)

    def get_client(self) -> Milvus:
        return super().get_client()

    def clear(self) -> None:
        ids = self.get_client().get_pks("pk != ''")
        if ids:
            self.delete(ids)

    def count(self) -> int:
        ids = self.get_client().get_pks("pk != ''")
        return len(ids)
