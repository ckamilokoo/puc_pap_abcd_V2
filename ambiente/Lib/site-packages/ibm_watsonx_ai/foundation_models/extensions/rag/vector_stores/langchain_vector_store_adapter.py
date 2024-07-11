#  -----------------------------------------------------------------------------------------
#  (C) Copyright IBM Corp. 2024.
#  https://opensource.org/licenses/BSD-3-Clause
#  -----------------------------------------------------------------------------------------
from ibm_watsonx_ai.wml_client_error import MissingExtension

try:
    from langchain_core.vectorstores import VectorStore as LangChainVectorStore
    from langchain_core.vectorstores import (
        VectorStoreRetriever as LangChainVectorStoreRetriever,
    )
    from langchain_core.documents import Document
except ImportError:
    raise MissingExtension("langchain")

import hashlib
from typing import Any
import logging

from ibm_watsonx_ai.foundation_models.embeddings import BaseEmbeddings
from ibm_watsonx_ai.foundation_models.extensions.rag.utils.utils import verbose_search
from ibm_watsonx_ai.foundation_models.extensions.rag.vector_stores.base_vector_store import (
    BaseVectorStore,
)

logger = logging.getLogger(__name__)


class LangChainVectorStoreAdapter(BaseVectorStore):
    """Adapter for LangChain ``VectorStore`` base class.

    :param vector_store: concrete LangChain vector store object
    :type vector_store: langchain_core.vectorstore.VectorStore
    """

    def __init__(self, vector_store: LangChainVectorStore) -> None:
        super().__init__()
        self._langchain_vector_store: LangChainVectorStore = vector_store

    def get_client(self) -> Any:
        return self._langchain_vector_store

    def set_embeddings(self, embedding_fn: BaseEmbeddings) -> None:
        if hasattr(self._langchain_vector_store, "embedding"):
            self._langchain_vector_store.embedding = embedding_fn
        elif hasattr(self._langchain_vector_store, "_embedding"):
            self._langchain_vector_store._embedding = embedding_fn
        elif hasattr(self._langchain_vector_store, "_embedding_function"):
            self._langchain_vector_store._embedding_function = embedding_fn
        elif hasattr(self._langchain_vector_store, "embedding_function"):
            self._langchain_vector_store.embedding_function = embedding_fn
        else:
            raise AttributeError(
                "Could not set an embedding function for this vector store."
            )

    def add_documents(
        self, content: list[str] | list[dict] | list, **kwargs: Any
    ) -> list[str]:
        ids, docs = self._process_documents(content)
        return self._langchain_vector_store.add_documents(docs, ids=ids, **kwargs)

    async def add_documents_async(
        self, content: list[str] | list[dict] | list, **kwargs: Any
    ) -> list[str]:
        ids, docs = self._process_documents(content)
        return await self._langchain_vector_store.aadd_documents(
            docs, ids=ids, **kwargs
        )

    def search(
        self,
        query: str,
        k: int,
        include_scores: bool = False,
        verbose: bool = False,
        **kwargs: Any,
    ) -> list[Document] | list[tuple[Document, float]]:
        result: list[Document] | list[tuple[Document, float]]
        if include_scores:
            result = self._langchain_vector_store.similarity_search_with_score(
                query, k=k, **kwargs
            )
        else:
            result = self._langchain_vector_store.similarity_search(
                query, k=k, **kwargs
            )

        if verbose:
            verbose_search(query, result)
        return result

    def delete(self, ids: list[str], **kwargs: Any) -> None:
        self._langchain_vector_store.delete(ids, **kwargs)

    def clear(self) -> None:
        raise NotImplementedError(
            "Use concrete wrapper if you need to use this functionality."
        )

    def count(self) -> int:
        raise NotImplementedError(
            "Use concrete wrapper if you need to use this functionality."
        )

    def as_langchain_retriever(self, **kwargs: Any) -> Any:
        return LangChainVectorStoreRetriever(
            vectorstore=self._langchain_vector_store, **kwargs
        )

    def _process_documents(
        self, content: list[str] | list[dict] | list
    ) -> tuple[list[str], list[Document]]:
        """Processes arbitrary list of data to produce two lists: one with unique IDs, one with LangChain documents.
        Handles duplicate documents.

        :param content: arbitrary data
        :type content: list[str] | list[dict] | list

        :return: lists with IDs and docs
        :rtype: tuple[list[str], list[langchain_core.documents.Document]
        """
        docs = self._as_langchain_documents(content)
        if docs:
            # Take only unique ID document. Get two lists, one with ids, one with documents
            return tuple(
                map(  # type: ignore[return-value]
                    list,
                    zip(
                        *{
                            hashlib.sha256(doc.page_content.encode()).hexdigest(): doc
                            for doc in docs
                        }.items()
                    ),
                )
            )
        else:
            return [], []

    def _as_langchain_documents(
        self, content: list[str] | list[dict] | list
    ) -> list[Document]:
        """Creates a LangChain ``Document`` list from list of potentially unstructured data.

        :param content: list of unstructured data to be parsed
        :type content: list[str] | list[dict] | list

        :raises AttributeError: when data does not fit the required schema
        :return: list of LangChain Documents
        :rtype: list[langchain_core.documents.Document]
        """
        result = []
        for doc in content:
            if isinstance(doc, str):
                result.append(Document(page_content=doc))
            elif isinstance(doc, dict):
                content_str: str | None = doc.get("content", None)
                metadata = doc.get("metadata", {})

                if content_str:
                    if isinstance(metadata, dict):
                        result.append(
                            Document(page_content=content_str, metadata=metadata)
                        )
                    else:
                        logger.warning(
                            f"Document: {doc} is incorrect. Metadata needs to be given with 'metadata' attribute and it needs to be a serializable dict. Skipping."
                        )
                        continue
                else:
                    logger.warning(
                        f"Document: {doc} is incorrect. Field 'content' is required"
                    )
                    continue
            else:
                try:
                    result.append(
                        Document(page_content=doc.page_content, metadata=doc.metadata)
                    )
                except AttributeError:
                    logger.warning(
                        f"Document: {doc} is not a dict, nor string, nor LangChain Document-like object. Skipping."
                    )

        return result
