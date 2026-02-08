"""Evaluation service for prompt compliance scoring."""
from __future__ import annotations

import json
import uuid
from dataclasses import dataclass
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.db import db
from app.models.schemas import (
    EvaluationRequest,
    EvaluationResult,
    EvaluationScores,
    GuidelineCompliance,
    MatchedReference,
)
from app.services.compliance_checker import ComplianceChecker
from app.services.prompt_improver import PromptImproverService


@dataclass
class _ReferenceRecord:
    reference_id: Optional[int]
    chosen: str
    rejected: str

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "_ReferenceRecord":
        return cls(
            reference_id=data.get("id"),
            chosen=data.get("chosen", ""),
            rejected=data.get("rejected", ""),
        )


class EvaluationService:
    def __init__(
        self,
        compliance_checker: ComplianceChecker,
        dataset_path: Path | str = Path("./data/hh_rlhf_samples.jsonl"),
        prompt_improver: Optional[PromptImproverService] = None,
    ) -> None:
        self.compliance_checker = compliance_checker
        self.dataset_path = Path(dataset_path)
        self.prompt_improver = prompt_improver
        self._dataset_cache: List[_ReferenceRecord] = []
        self._dataset_mtime: Optional[float] = None
        self._ensure_dataset_loaded()

    def evaluate(self, request: EvaluationRequest) -> EvaluationResult:
        reference = self._match_reference(request.user_message)
        preference_score, matched_reference = self._score_preference_alignment(
            model_response=request.model_response,
            reference=reference,
        )

        guideline_results: Optional[List[GuidelineCompliance]] = None
        guideline_score = 1.0
        if request.guidelines:
            analysis = self.compliance_checker.analyze_compliance(
                system_prompt_guidelines=request.guidelines,
                user_message=request.user_message,
                assistant_response=request.model_response,
                llm_provider=request.llm_provider,
                model_name=request.model_name,
            )
            guideline_results = analysis.guideline_results
            guideline_score = analysis.overall_score / 100 if analysis else 1.0

        overall_score = (preference_score + guideline_score) / 2
        evaluation_id = str(uuid.uuid4())
        result = EvaluationResult(
            evaluation_id=evaluation_id,
            prompt_version=request.prompt_version,
            scores=EvaluationScores(
                preference_alignment=round(preference_score, 4),
                guideline_adherence=round(guideline_score, 4),
                overall=round(overall_score, 4),
            ),
            matched_reference=matched_reference,
            guideline_results=guideline_results,
            metadata=request.metadata,
            notes=self._build_notes(reference is None, request.guidelines),
        )

        self._persist_evaluation(result, request)
        return result

    def recent_evaluations(self, limit: int = 10) -> List[EvaluationResult]:
        rows = db.query(
            "SELECT * FROM evaluations ORDER BY datetime(created_at) DESC LIMIT ?",
            (limit,),
        )
        results: List[EvaluationResult] = []
        for row in rows:
            guidelines = db.query(
                "SELECT guideline, followed, explanation, evidence FROM evaluation_guidelines WHERE evaluation_id=?",
                (row["id"],),
            )
            guideline_objs = [
                GuidelineCompliance(
                    guideline=g["guideline"],
                    followed=bool(g["followed"]),
                    explanation=g["explanation"] or "",
                    evidence=g["evidence"],
                )
                for g in guidelines
            ] or None
            metadata = json.loads(row["metadata"]) if row["metadata"] else None
            results.append(
                EvaluationResult(
                    evaluation_id=row["id"],
                    prompt_version=row["prompt_version"],
                    scores=EvaluationScores(
                        preference_alignment=row["preference_alignment"],
                        guideline_adherence=row["guideline_adherence"],
                        overall=row["overall"],
                    ),
                    matched_reference=None,
                    guideline_results=guideline_objs,
                    notes=row["notes"],
                    metadata=metadata,
                )
            )
        return results

    def _ensure_dataset_loaded(self) -> None:
        if not self.dataset_path.exists():
            self._dataset_cache = []
            self._dataset_mtime = None
            return
        mtime = self.dataset_path.stat().st_mtime
        if self._dataset_mtime and self._dataset_mtime == mtime:
            return
        self._dataset_cache = []
        with self.dataset_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                except json.JSONDecodeError:
                    continue
                self._dataset_cache.append(_ReferenceRecord.from_dict(data))
        self._dataset_mtime = mtime

    def _match_reference(self, user_message: str) -> Optional[_ReferenceRecord]:
        self._ensure_dataset_loaded()
        if not self._dataset_cache:
            return None
        target = f"Human: {user_message.strip()}"
        best_record = None
        best_score = -1.0
        for record in self._dataset_cache:
            score = self._similarity(target, record.chosen)
            if score > best_score:
                best_score = score
                best_record = record
        return best_record

    def _score_preference_alignment(
        self,
        model_response: str,
        reference: Optional[_ReferenceRecord],
    ) -> tuple[float, Optional[MatchedReference]]:
        if not reference:
            return 0.5, None
        sim_chosen = self._similarity(model_response, reference.chosen)
        sim_rejected = self._similarity(model_response, reference.rejected)
        total = sim_chosen + sim_rejected
        preference_score = sim_chosen / total if total else 0.5
        matched = MatchedReference(
            reference_id=reference.reference_id,
            similarity_to_chosen=round(sim_chosen, 4),
            similarity_to_rejected=round(sim_rejected, 4),
            chosen_preview=reference.chosen[:280],
            rejected_preview=reference.rejected[:280],
        )
        return preference_score, matched

    def _similarity(self, a: str, b: str) -> float:
        return SequenceMatcher(None, a or "", b or "").ratio()

    def _build_notes(self, no_reference: bool, guidelines: Optional[List[str]]) -> Optional[str]:
        notes: List[str] = []
        if no_reference:
            notes.append("Reference dataset unavailable or empty")
        if not guidelines:
            notes.append("Guideline adherence skipped (no guidelines provided)")
        return "; ".join(notes) if notes else None

    def _persist_evaluation(self, result: EvaluationResult, request: EvaluationRequest) -> None:
        db.execute(
            """
            INSERT INTO evaluations (
                id, prompt_version, preference_alignment, guideline_adherence,
                overall, notes, metadata, system_prompt, user_message, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                result.evaluation_id,
                result.prompt_version,
                result.scores.preference_alignment,
                result.scores.guideline_adherence,
                result.scores.overall,
                result.notes,
                json.dumps(result.metadata) if result.metadata is not None else None,
                request.system_prompt,
                request.user_message,
                datetime.utcnow().isoformat(),
            ),
        )
        if result.guideline_results:
            params = [
                (
                    result.evaluation_id,
                    item.guideline,
                    1 if item.followed else 0,
                    item.explanation,
                    item.evidence,
                )
                for item in result.guideline_results
            ]
            db.executemany(
                """
                INSERT INTO evaluation_guidelines (
                    evaluation_id, guideline, followed, explanation, evidence
                ) VALUES (?, ?, ?, ?, ?)
                """,
                params,
            )
        if self.prompt_improver:
            recent = self.recent_evaluations(limit=50)
            self.prompt_improver.record_evaluations(recent)
