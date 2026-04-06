"""Claude and ChromaDB orchestration service for academic assistant flows."""

import logging
from collections.abc import Sequence

import anthropic
import chromadb

from fahimni.core.config import settings

logger = logging.getLogger(__name__)


class AIService:
    """Thin service wrapper over Anthropic and ChromaDB clients."""

    def __init__(self) -> None:
        self._anthropic = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self._chroma = chromadb.HttpClient(host=settings.chroma_host, port=settings.chroma_port)

    def get_or_create_course_collection(self, course_id: str) -> chromadb.Collection:
        return self._chroma.get_or_create_collection(name=f"course-{course_id}")

    def add_course_chunks(self, course_id: str, ids: Sequence[str], docs: Sequence[str]) -> None:
        collection = self.get_or_create_course_collection(course_id)
        collection.add(ids=list(ids), documents=list(docs))

    def answer_with_context(self, course_id: str, question: str) -> str:
        collection = self.get_or_create_course_collection(course_id)
        result = collection.query(query_texts=[question], n_results=4)
        docs = result.get("documents", [[]])[0]
        context = "\n\n".join(docs)

        prompt = (
            "You are an academic assistant for professor-student collaboration. "
            "Use the provided context first and explicitly say when information is missing.\n\n"
            f"Context:\n{context}\n\nQuestion: {question}"
        )

        response = self._anthropic.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=800,
            temperature=0.2,
            messages=[{"role": "user", "content": prompt}],
        )
        first_block = response.content[0]
        text = getattr(first_block, "text", "No response")
        logger.info("Generated Claude answer for course context")
        return text
