#  -----------------------------------------------------------------------------------------
#  (C) Copyright IBM Corp. 2024.
#  https://opensource.org/licenses/BSD-3-Clause
#  -----------------------------------------------------------------------------------------

from typing import Literal, Sequence, Any

from langchain.text_splitter import TextSplitter
from langchain_core.documents import Document

from .base_chunker import BaseChunker


__all__ = [
    "LangChainChunker",
]


class LangChainChunker(BaseChunker[Document]):
    """
    Wrapper for LangChain TextSplitter.

    :param method: describes type of the TextSplitter as the main instance performing chunking, defaults to "recursive"
    :type method: Literal["recursive", "character", "token"], optional

    :param chunk_size: maximum size of a single chunk that is returned, defaults to 4000
    :type chunk_size: int, optional

    :param chunk_overlap: overlap in characters between chunks, defaults to 200
    :type chunk_overlap: int, optional

    :param encoding_name: encoding used in the TokenTextSplitter, defaults to "gpt2"
    :type encoding_name: str, optional

    :param model_name: model used in the TokenTextSplitter
    :type model_name: str, optional
    """

    supported_methods = ("recursive", "character", "token")

    def __init__(
        self,
        method: Literal["recursive", "character", "token"] = "recursive",
        chunk_size: int = 4000,
        chunk_overlap: int = 200,
        encoding_name: str = "gpt2",
        model_name: str | None = None,
        **kwargs: Any,
    ) -> None:
        self.method = method
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.encoding_name = encoding_name
        self.model_name = model_name
        self.separators = kwargs.pop("separators", ["\n\n", "(?<=\. )", "\n", " ", ""])
        self._text_splitter = self._get_text_splitter()

    def __eq__(self, other: object) -> bool:
        if isinstance(other, LangChainChunker):
            return self.to_dict() == other.to_dict()
        else:
            return NotImplemented

    def _get_text_splitter(self) -> TextSplitter:
        """Create instance of TextSplitter based on the settings."""

        text_splitter: TextSplitter

        match self.method:
            case "recursive":
                from langchain.text_splitter import RecursiveCharacterTextSplitter

                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=self.chunk_size,
                    chunk_overlap=self.chunk_overlap,
                    separators=self.separators,
                    length_function=len,
                )

            case "character":
                from langchain.text_splitter import CharacterTextSplitter

                text_splitter = CharacterTextSplitter(
                    chunk_size=self.chunk_size,
                    chunk_overlap=self.chunk_overlap,
                )

            case "token":
                from langchain.text_splitter import TokenTextSplitter

                text_splitter = TokenTextSplitter(
                    chunk_size=self.chunk_size,
                    chunk_overlap=self.chunk_overlap,
                    encoding_name=self.encoding_name,
                    model_name=self.model_name,
                )

            case _:
                raise ValueError(
                    "Chunker method '{}' is not supported. Use one of {}".format(
                        self.method, self.supported_methods
                    )
                )

        return text_splitter

    def to_dict(self) -> dict[str, Any]:
        """
        Return dict that can be used to recreate instance of the LangChainChunker.
        """
        params = (
            "method",
            "chunk_size",
            "chunk_overlap",
            "encoding_name",
            "model_name",
        )

        ret = {k: v for k, v in self.__dict__.items() if k in params}

        return ret

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "LangChainChunker":
        """Create instance from the dictionary"""

        return cls(**d)

    def split_documents(self, documents: Sequence[Document]) -> list[Document]:
        """
        Split series of documents into smaller parts based on the provided
        chunker settings.

        :param documents: sequence of elements that contain context in the format of text
        :type documents: Sequence[ChunkType]

        :return: list of documents splitter into smaller ones, having less content
        :rtype: list[ChunkType]
        """
        return self._text_splitter.split_documents(documents)
