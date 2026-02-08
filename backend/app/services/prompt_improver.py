"""Prompt improvement service (prototype)."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional, TYPE_CHECKING

from openai import OpenAI

from app.models.schemas import (
    EvaluationRequest,
    EvaluationResult,
    PromptHistoryResponse,
    PromptImproveRequest,
    PromptImproveResponse,
    PromptVersion,
    ReEvaluationResult,
)
from app.services.prompt_store import PromptStore

if TYPE_CHECKING:
    from app.services.evaluation_service import EvaluationService


class PromptImproverService:
    """Generates new prompt versions based on evaluation signals (prototype)."""

    def __init__(self, store: PromptStore, evaluation_service: "EvaluationService") -> None:
        self.store = store
        self.evaluation_service = evaluation_service
        self.last_evaluations: List[EvaluationResult] = []
        self.scenarios = json.loads((Path("./app/config/scenarios.json")).read_text())

    def history(self) -> PromptHistoryResponse:
        versions = self.store.list_versions()
        current = self.store.get_current().id if versions else None
        return PromptHistoryResponse(current_version=current, versions=versions)

    def record_evaluations(self, evaluations: List[EvaluationResult]) -> None:
        self.last_evaluations = evaluations[-50:]

    def improve(self, request: PromptImproveRequest) -> PromptImproveResponse:
        previous = self.store.get_current()
        rationale = request.rationale or self._derive_rationale()
        new_content = self._generate_new_prompt(previous.content, rationale)
        notes = f"Auto-generated on {datetime.utcnow().isoformat()} | reason: {rationale}"
        new_version = self.store.save_new_version(content=new_content, notes=notes)

        reevaluation = None
        if request.run_reevaluation:
            reevaluation = self._run_reevaluation(new_version)

        return PromptImproveResponse(
            new_version=new_version,
            previous_version=previous,
            message="새 프롬프트 버전을 생성했습니다",
            reevaluation=reevaluation,
        )

    def _run_reevaluation(self, version: PromptVersion) -> ReEvaluationResult:
        scenarios = self.scenarios.get("compliance", [])
        results: List[EvaluationResult] = []
        for scenario in scenarios:
            evaluation = self.evaluation_service.evaluate(
                EvaluationRequest(
                    system_prompt=version.content,
                    user_message=scenario["user_message"],
                    model_response=scenario["model_response"],
                    prompt_version=version.id,
                    guidelines=scenario["guidelines"],
                )
            )
            results.append(evaluation)
        summary = f"총 {len(results)}건 재평가 완료"
        return ReEvaluationResult(evaluations=results, summary=summary)

    def _derive_rationale(self) -> str:
        if not self.last_evaluations:
            return "평가 데이터 없음"
        for evaluation in reversed(self.last_evaluations):
            if evaluation.guideline_results:
                violated = [g.guideline for g in evaluation.guideline_results if not g.followed]
                if violated:
                    return f"최근 위반: {', '.join(violated[:3])}"
        return "최근 평가 안정적"

    def _generate_new_prompt(self, current_prompt: str, rationale: str) -> str:
        client = OpenAI()
        system = "You rewrite system prompts to improve compliance."
        user = f"현재 프롬프트:\n{current_prompt}\n\n개선 사유: {rationale}\n\n개선된 프롬프트를 제공하세요."
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
                temperature=0.2,
            )
            return response.choices[0].message.content.strip()
        except Exception:
            additions = "\n\n# Auto-adjustments\n- " + rationale
            if "# Auto-adjustments" in current_prompt:
                return current_prompt + f"\n- {rationale}"
            return current_prompt + additions
