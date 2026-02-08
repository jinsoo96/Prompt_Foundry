"""SQLite-backed prompt storage."""
from __future__ import annotations

from datetime import datetime
from typing import List

from app.db import db
from app.models.schemas import PromptVersion


class PromptStore:
    def __init__(self) -> None:
        self.db = db

    def list_versions(self) -> List[PromptVersion]:
        rows = self.db.query("SELECT id, content, created_at, score, notes FROM prompts ORDER BY created_at")
        return [self._row_to_version(row) for row in rows]

    def get_current(self) -> PromptVersion:
        row = self.db.query("SELECT value FROM prompt_meta WHERE key='current_version'")
        current_id = row[0]["value"] if row else None
        if not current_id:
            raise ValueError("current_version not set")
        return self.get_version(current_id)

    def get_version(self, version_id: str) -> PromptVersion:
        rows = self.db.query(
            "SELECT id, content, created_at, score, notes FROM prompts WHERE id=?",
            (version_id,),
        )
        if not rows:
            raise ValueError(f"Prompt version {version_id} not found")
        return self._row_to_version(rows[0])

    def save_new_version(self, content: str, notes: str | None = None, score: float | None = None) -> PromptVersion:
        version_id = datetime.utcnow().strftime("version_%Y%m%d%H%M%S")
        created_at = datetime.utcnow().isoformat()
        self.db.execute(
            "INSERT INTO prompts (id, content, created_at, score, notes) VALUES (?, ?, ?, ?, ?)",
            (version_id, content, created_at, score, notes),
        )
        self._set_current(version_id)
        return PromptVersion(id=version_id, content=content, created_at=created_at, score=score, notes=notes)

    def update_version(self, version: PromptVersion) -> None:
        self.db.execute(
            "UPDATE prompts SET content=?, score=?, notes=? WHERE id=?",
            (version.content, version.score, version.notes, version.id),
        )

    def _set_current(self, version_id: str) -> None:
        self.db.execute(
            "INSERT OR REPLACE INTO prompt_meta (key, value) VALUES ('current_version', ?)",
            (version_id,),
        )

    def _row_to_version(self, row) -> PromptVersion:
        return PromptVersion(
            id=row["id"],
            content=row["content"],
            created_at=row["created_at"],
            score=row["score"],
            notes=row["notes"],
        )
