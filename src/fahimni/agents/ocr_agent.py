"""OCR agent for scanned documents, handwritten notes, and whiteboard captures."""

from fahimni.services.ai_service import AIService


class OCRAgent:
    """Agent that extracts and indexes text from image inputs."""

    def __init__(self, ai_service: AIService | None = None) -> None:
        self._ai = ai_service or AIService()

    def process_image(self, course_id: str, image_bytes: bytes, filename: str) -> dict[str, object]:
        return self._ai.ingest_ocr_image(course_id=course_id, image_bytes=image_bytes, filename=filename)
