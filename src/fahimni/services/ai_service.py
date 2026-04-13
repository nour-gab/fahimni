"""LangChain AI service for RAG, hybrid search, OCR, and learning intelligence."""

from __future__ import annotations

import io
import logging
import re
import uuid
from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from fahimni.core.config import settings

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class SearchHit:
    """Unified search result item for hybrid retrieval."""

    text: str
    source: str
    score: float
    page: int = 1
    highlight: str = ""


class AIService:
    """Production-oriented AI workflow service for course learning assistants."""

    def __init__(self) -> None:
        self._initialized = False
        self._embeddings: Any = None
        self._llm: Any = None

    def _initialize_runtime(self) -> None:
        if self._initialized:
            return

        try:
            from langchain_community.embeddings import FastEmbedEmbeddings
            from langchain_community.llms import HuggingFaceEndpoint
        except ImportError as exc:
            raise RuntimeError(
                "Missing AI dependencies. Run 'uv sync' to install LangChain/HuggingFace packages."
            ) from exc

        self._embeddings = FastEmbedEmbeddings(
            model_name=settings.embedding_model_id,
        )
        if not settings.huggingface_api_token:
            raise RuntimeError("HUGGINGFACE_API_TOKEN is required for LLM inference")
        self._llm = HuggingFaceEndpoint(
            repo_id=settings.huggingface_model_id,
            task="text2text-generation",
            max_new_tokens=512,
            temperature=0.1,
            huggingfacehub_api_token=settings.huggingface_api_token,
        )
        self._initialized = True

    def _vector_store(self, course_id: str) -> Any:
        self._initialize_runtime()
        from langchain_chroma import Chroma

        if self._embeddings is None:
            raise RuntimeError("Embeddings runtime unavailable")

        return Chroma(
            collection_name=f"course-{course_id}",
            embedding_function=self._embeddings,
            persist_directory=settings.vector_store_path,
        )

    def _split_text(self, text: str) -> list[str]:
        from langchain_text_splitters import RecursiveCharacterTextSplitter

        splitter = RecursiveCharacterTextSplitter(chunk_size=900, chunk_overlap=180)
        return [chunk for chunk in splitter.split_text(text) if chunk.strip()]

    def ingest_text(self, course_id: str, content: str, source: str) -> int:
        """Chunk, embed, and store raw course text in the vector store."""
        chunks = self._split_text(content)
        if not chunks:
            return 0

        from langchain_core.documents import Document

        docs = [
            Document(
                page_content=chunk,
                metadata={
                    "source": source,
                    "course_id": course_id,
                    "ingested_at": datetime.now(UTC).isoformat(),
                },
            )
            for chunk in chunks
        ]
        ids = [str(uuid.uuid4()) for _ in docs]
        self._vector_store(course_id).add_documents(documents=docs, ids=ids)
        return len(docs)

    def ingest_pdf_bytes(self, course_id: str, file_bytes: bytes, filename: str) -> int:
        """Extract text from PDF, then store chunks in vector database."""
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise RuntimeError("Missing pypdf dependency. Run 'uv sync'.") from exc

        reader = PdfReader(io.BytesIO(file_bytes))
        text = "\n\n".join((page.extract_text() or "") for page in reader.pages)
        return self.ingest_text(course_id=course_id, content=text, source=filename)

    def _configure_tesseract(self) -> None:
        import pytesseract  # type: ignore[import-untyped]

        if settings.tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = settings.tesseract_cmd

    def ingest_ocr_image(self, course_id: str, image_bytes: bytes, filename: str) -> dict[str, object]:
        """OCR image content and store extracted text in the course vector store."""
        try:
            import pytesseract
            from PIL import Image
        except ImportError as exc:
            raise RuntimeError("Missing OCR dependencies. Run 'uv sync'.") from exc

        self._configure_tesseract()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        raw_text = pytesseract.image_to_string(image)
        cleaned = re.sub(r"\s+", " ", raw_text).strip()
        chunks = self.ingest_text(course_id=course_id, content=cleaned, source=filename)

        return {
            "chunks": chunks,
            "detected": self.detect_document_artifacts(cleaned),
        }

    def detect_document_artifacts(self, text: str) -> dict[str, bool]:
        """Best-effort structural signal detection from OCR text."""
        equation_tokens = len(re.findall(r"[=+\-*/^]|\\int|\\sum|\\frac", text))
        table_markers = len(re.findall(r"\b(row|column|table)\b|\|", text.lower()))
        diagram_markers = len(re.findall(r"\b(figure|diagram|flowchart|graph)\b", text.lower()))

        return {
            "equations": equation_tokens >= 3,
            "tables": table_markers >= 2,
            "diagrams": diagram_markers >= 1,
        }

    def hybrid_search(self, course_id: str, query: str, k: int = 5) -> list[SearchHit]:
        """Run semantic + BM25 retrieval and return merged snippets with source refs."""
        vector_store = self._vector_store(course_id)
        semantic_docs = vector_store.similarity_search(query, k=max(k * 3, 8))
        if not semantic_docs:
            return []

        corpus = [doc.page_content for doc in semantic_docs]
        tokenized = [self._tokenize(text) for text in corpus]
        bm25_scores = self._bm25_scores(tokenized, self._tokenize(query))

        hits: list[SearchHit] = []
        for i, doc in enumerate(semantic_docs):
            source = str(doc.metadata.get("source", "unknown"))
            semantic_score = 1.0 / float(i + 1)
            keyword_score = bm25_scores[i]
            score = (0.65 * semantic_score) + (0.35 * keyword_score)
            page_meta = doc.metadata.get("page")
            page = int(page_meta) + 1 if isinstance(page_meta, int) else 1
            hits.append(
                SearchHit(
                    text=doc.page_content,
                    source=source,
                    page=page,
                    score=score,
                    highlight=self._build_highlight(doc.page_content, query),
                )
            )

        hits.sort(key=lambda item: item.score, reverse=True)
        return hits[:k]

    def answer_with_rag(self, course_id: str, question: str, task_hint: str = "") -> dict[str, object]:
        """Answer course questions with grounded context snippets."""
        hits = self.hybrid_search(course_id=course_id, query=question, k=5)
        if not hits:
            return {"answer": "No matching course content found yet.", "sources": []}

        context = "\n\n".join(
            [f"Source: {hit.source}\nSnippet: {hit.text[:1000]}" for hit in hits]
        )
        prompt = (
            "You are a course learning assistant. Answer ONLY from provided context. "
            "If information is missing, say so. Keep answer clear and structured.\n\n"
            f"Task Hint: {task_hint or 'standard QA'}\n"
            f"Question: {question}\n\n"
            f"Context:\n{context}"
        )
        answer = self._generate_text(prompt)
        return {
            "answer": answer,
            "sources": [{"source": hit.source, "score": round(hit.score, 4)} for hit in hits],
        }

    def teacher_upload_assistant(self, course_id: str, uploaded_text: str) -> dict[str, object]:
        """Generate summary, key concepts, and quiz draft from uploaded content."""
        self.ingest_text(course_id=course_id, content=uploaded_text, source="teacher-upload")

        summary = self._generate_text(
            "Summarize this course material for students in 6 concise bullets:\n\n"
            + uploaded_text[:8000]
        )
        concepts = self._extract_key_concepts(uploaded_text)
        quiz = self._generate_text(
            "Create 5 MCQs with 4 options each and include correct answer labels.\n\n"
            + uploaded_text[:8000]
        )
        return {
            "summary": summary,
            "key_concepts": concepts,
            "quiz_draft": quiz,
        }

    def run_multi_agent_workflow(self, course_id: str, question: str, student_id: str) -> dict[str, object]:
        """Coordinate specialized agents for tutoring, quiz, planning, and search."""
        search_hits = self.hybrid_search(course_id=course_id, query=question, k=4)
        tutor = self.answer_with_rag(course_id=course_id, question=question, task_hint="tutor")
        quiz = self._generate_text(f"Generate 3 practice questions about: {question}")
        planner = self.generate_learning_path(
            weak_topics=[question],
            study_minutes_per_day=60,
            horizon_days=5,
        )
        return {
            "student_id": student_id,
            "tutor_agent": tutor,
            "quiz_agent": quiz,
            "search_agent": [hit.__dict__ for hit in search_hits],
            "planner_agent": planner,
        }

    def generate_learning_path(
        self,
        weak_topics: Sequence[str],
        study_minutes_per_day: int,
        horizon_days: int,
    ) -> dict[str, object]:
        """Create adaptive study plan based on weak areas and time budget."""
        if not weak_topics:
            weak_topics = ["general revision"]

        plan: list[dict[str, str]] = []
        for day in range(1, horizon_days + 1):
            topic = weak_topics[(day - 1) % len(weak_topics)]
            plan.append(
                {
                    "day": str(day),
                    "focus": topic,
                    "duration_minutes": str(study_minutes_per_day),
                    "difficulty": "medium" if day < horizon_days else "hard",
                }
            )
        return {"plan": plan}

    def generate_exam(self, course_id: str, topic: str, question_count: int) -> str:
        """Create exam-style items from course context and target topic."""
        rag = self.answer_with_rag(course_id=course_id, question=f"Important points about {topic}")
        context = str(rag["answer"])
        return self._generate_text(
            f"Create {question_count} exam-style questions based on:\n{context}\n"
            "Include a mix of MCQ and open-ended questions."
        )

    def evaluate_student_answer(self, reference: str, student_answer: str) -> dict[str, object]:
        """Grade free-text answer with rationale and improvement guidance."""
        prompt = (
            "Compare student answer to reference. Return: score/100, mistakes, and improvements.\n\n"
            f"Reference:\n{reference}\n\nStudent Answer:\n{student_answer}"
        )
        evaluation = self._generate_text(prompt)
        score = self._heuristic_score(reference=reference, student_answer=student_answer)
        return {"score": score, "feedback": evaluation}

    def learning_analytics(self, records: Sequence[dict[str, object]]) -> dict[str, object]:
        """Summarize progress and weak-topic signals from student activity records."""
        if not records:
            return {"progress": 0.0, "weak_topics": [], "insights": "No activity yet"}

        topic_counter: Counter[str] = Counter()
        scores: list[float] = []
        for item in records:
            topic = str(item.get("topic", "unknown"))
            topic_counter[topic] += 1
            score_value = item.get("score")
            if isinstance(score_value, (int, float)):
                scores.append(float(score_value))

        weak_topics = [topic for topic, _ in topic_counter.most_common(3)]
        avg_score = sum(scores) / len(scores) if scores else 0.0
        return {
            "progress": round(avg_score, 2),
            "weak_topics": weak_topics,
            "insights": "Focus next sessions on top weak topics with adaptive quizzes.",
        }

    def answer_with_context(self, course_id: str, question: str) -> str:
        """Backward-compatible method used by existing code paths."""
        return str(self.answer_with_rag(course_id=course_id, question=question)["answer"])

    def _generate_text(self, prompt: str) -> str:
        self._initialize_runtime()
        if self._llm is None:
            raise RuntimeError("LLM runtime unavailable")
        return str(self._llm.invoke(prompt))

    def _extract_key_concepts(self, text: str) -> list[str]:
        words = re.findall(r"[A-Za-z][A-Za-z\-]{3,}", text)
        stop = {
            "this",
            "that",
            "with",
            "from",
            "have",
            "were",
            "their",
            "about",
            "there",
            "which",
            "chapter",
            "lesson",
            "course",
        }
        filtered = [word.lower() for word in words if word.lower() not in stop]
        top = Counter(filtered).most_common(12)
        return [word for word, _ in top]

    def _heuristic_score(self, reference: str, student_answer: str) -> int:
        ref = set(self._tokenize(reference))
        student = set(self._tokenize(student_answer))
        if not ref:
            return 0
        overlap = len(ref.intersection(student)) / max(len(ref), 1)
        return int(round(overlap * 100))

    @staticmethod
    def _tokenize(text: str) -> list[str]:
        return re.findall(r"[A-Za-z0-9_]+", text.lower())

    def _build_highlight(self, text: str, query: str, max_len: int = 220) -> str:
        normalized = re.sub(r"\s+", " ", text).strip()
        if len(normalized) <= max_len:
            return normalized

        for token in self._tokenize(query):
            match = re.search(re.escape(token), normalized, flags=re.IGNORECASE)
            if match is None:
                continue
            half = max_len // 2
            start = max(match.start() - half, 0)
            end = min(start + max_len, len(normalized))
            if start > 0:
                return "..." + normalized[start:end].strip()
            return normalized[start:end].strip()

        return normalized[:max_len].rstrip() + "..."

    @staticmethod
    def _bm25_scores(corpus_tokens: list[list[str]], query_tokens: list[str]) -> list[float]:
        try:
            from rank_bm25 import BM25Okapi  # type: ignore[import-untyped]
        except ImportError as exc:
            raise RuntimeError("Missing rank-bm25 dependency. Run 'uv sync'.") from exc

        bm25 = BM25Okapi(corpus_tokens)
        raw_scores = bm25.get_scores(query_tokens)
        if len(raw_scores) == 0:
            return []

        max_score = float(max(raw_scores)) or 1.0
        return [float(score) / max_score for score in raw_scores]
