from fastapi import APIRouter, HTTPException
from app.models.schemas import ComplianceAnalysis
from app.dependencies import compliance_checker

router = APIRouter(prefix="/api/compliance", tags=["compliance"])


@router.get("/{compliance_id}", response_model=ComplianceAnalysis)
async def get_compliance_analysis(compliance_id: str):
    """준수도 분석 결과 조회"""
    try:
        analysis = compliance_checker.get_analysis(compliance_id)

        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")

        return analysis

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
