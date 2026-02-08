from typing import List

from fastapi import APIRouter, HTTPException, Query

from app.dependencies import evaluation_service
from app.models.schemas import EvaluationRequest, EvaluationResult

router = APIRouter(prefix="/api/evaluation", tags=["evaluation"])


@router.post("/run", response_model=EvaluationResult)
async def run_evaluation(request: EvaluationRequest):
    """프롬프트 평가 실행"""
    try:
        return evaluation_service.evaluate(request)
    except Exception as exc:  # pylint: disable=broad-except
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/recent", response_model=List[EvaluationResult])
async def recent_evaluations(limit: int = Query(10, ge=1, le=50)):
    """최근 평가 결과 조회"""
    try:
        return evaluation_service.recent_evaluations(limit=limit)
    except Exception as exc:  # pylint: disable=broad-except
        raise HTTPException(status_code=500, detail=str(exc)) from exc
