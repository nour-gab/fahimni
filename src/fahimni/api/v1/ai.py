"""AI router endpoints for RAG, hybrid search, OCR, tutoring, and analytics."""

from dataclasses import asdict

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status

from fahimni.agents.orchestrator_agent import OrchestratorAgent
from fahimni.core.dependencies import get_current_user, require_role
from fahimni.models.user import User, UserRole
from fahimni.schemas.ai import (
    AnalyticsRequest,
    AnswerCorrectionRequest,
    AskRequest,
    ExamGeneratorRequest,
    LearningPathRequest,
    MultiAgentRequest,
    SearchRequest,
    TeacherAssistRequest,
)
from fahimni.services.ai_service import AIService

router = APIRouter(prefix="/ai", tags=["ai"])
_ai_service = AIService()


def get_ai_service() -> AIService:
    """Dependency provider for AI service to enable test overrides."""
    return _ai_service


@router.post("/rag/ask")
async def rag_ask(
    payload: AskRequest,
    _: User = Depends(get_current_user),
    ai: AIService = Depends(get_ai_service),
) -> dict[str, object]:
    try:
        return ai.answer_with_rag(payload.course_id, payload.question, payload.task_hint)
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc


@router.post("/search/hybrid")
async def hybrid_search(
    payload: SearchRequest,
    _: User = Depends(get_current_user),
    ai: AIService = Depends(get_ai_service),
) -> dict[str, object]:
    hits = ai.hybrid_search(course_id=payload.course_id, query=payload.query, k=payload.k)
    return {"results": [asdict(hit) for hit in hits]}


@router.post("/upload/pdf")
async def upload_pdf(
    course_id: str,
    file: UploadFile = File(...),
    _: User = Depends(require_role(UserRole.PROFESSOR, UserRole.ADMIN)),
    ai: AIService = Depends(get_ai_service),
) -> dict[str, object]:
    data = await file.read()
    try:
        chunks = ai.ingest_pdf_bytes(course_id=course_id, file_bytes=data, filename=file.filename or "pdf")
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    return {"chunks_indexed": chunks, "filename": file.filename}


@router.post("/upload/ocr")
async def upload_ocr(
    course_id: str,
    file: UploadFile = File(...),
    _: User = Depends(require_role(UserRole.PROFESSOR, UserRole.ADMIN)),
    ai: AIService = Depends(get_ai_service),
) -> dict[str, object]:
    data = await file.read()
    try:
        return ai.ingest_ocr_image(course_id=course_id, image_bytes=data, filename=file.filename or "image")
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc


@router.post("/teacher/analyze")
async def teacher_analyze(
    payload: TeacherAssistRequest,
    _: User = Depends(require_role(UserRole.PROFESSOR, UserRole.ADMIN)),
    ai: AIService = Depends(get_ai_service),
) -> dict[str, object]:
    return ai.teacher_upload_assistant(course_id=payload.course_id, uploaded_text=payload.content)


@router.post("/agents/orchestrate")
async def orchestrate_agents(
    payload: MultiAgentRequest,
    _: User = Depends(get_current_user),
    ai: AIService = Depends(get_ai_service),
) -> dict[str, object]:
    orchestrator = OrchestratorAgent(ai)
    return orchestrator.run(course_id=payload.course_id, prompt=payload.prompt, student_id=payload.student_id)


@router.post("/learning-path")
async def learning_path(
    payload: LearningPathRequest,
    _: User = Depends(get_current_user),
    ai: AIService = Depends(get_ai_service),
) -> dict[str, object]:
    return ai.generate_learning_path(
        weak_topics=payload.weak_topics,
        study_minutes_per_day=payload.study_minutes_per_day,
        horizon_days=payload.horizon_days,
    )


@router.post("/quiz/exam-generator")
async def exam_generator(
    payload: ExamGeneratorRequest,
    _: User = Depends(require_role(UserRole.PROFESSOR, UserRole.ADMIN)),
    ai: AIService = Depends(get_ai_service),
) -> dict[str, str]:
    return {
        "exam": ai.generate_exam(
            course_id=payload.course_id,
            topic=payload.topic,
            question_count=payload.question_count,
        )
    }


@router.post("/answers/evaluate")
async def evaluate_answer(
    payload: AnswerCorrectionRequest,
    _: User = Depends(get_current_user),
    ai: AIService = Depends(get_ai_service),
) -> dict[str, object]:
    return ai.evaluate_student_answer(
        reference=payload.reference_answer,
        student_answer=payload.student_answer,
    )


@router.post("/analytics")
async def analytics(
    payload: AnalyticsRequest,
    _: User = Depends(require_role(UserRole.PROFESSOR, UserRole.ADMIN)),
    ai: AIService = Depends(get_ai_service),
) -> dict[str, object]:
    return ai.learning_analytics(payload.records)
