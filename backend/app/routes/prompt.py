from fastapi import APIRouter, HTTPException

from app.dependencies import prompt_improver
from app.models.schemas import PromptHistoryResponse, PromptImproveRequest, PromptImproveResponse

router = APIRouter(prefix="/api/prompts", tags=["prompts"])


@router.get("/history", response_model=PromptHistoryResponse)
async def get_history():
    try:
        return prompt_improver.history()
    except Exception as exc:  # pylint: disable=broad-except
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/improve", response_model=PromptImproveResponse)
async def improve_prompt(request: PromptImproveRequest):
    try:
        return prompt_improver.improve(request)
    except Exception as exc:  # pylint: disable=broad-except
        raise HTTPException(status_code=500, detail=str(exc)) from exc
