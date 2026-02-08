"""SQLite database helper."""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable


class Database:
    """Lightweight SQLite wrapper with automatic schema + legacy import."""

    def __init__(self, db_path: Path | str = Path("./data/app.db")) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self._ensure_schema()
        self._bootstrap_from_files()

    def _ensure_schema(self) -> None:
        cur = self.conn.cursor()
        cur.executescript(
            """
            CREATE TABLE IF NOT EXISTS prompts (
                id TEXT PRIMARY KEY,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                score REAL,
                notes TEXT
            );

            CREATE TABLE IF NOT EXISTS prompt_meta (
                key TEXT PRIMARY KEY,
                value TEXT
            );

            CREATE TABLE IF NOT EXISTS evaluations (
                id TEXT PRIMARY KEY,
                prompt_version TEXT,
                preference_alignment REAL,
                guideline_adherence REAL,
                overall REAL,
                notes TEXT,
                metadata TEXT,
                system_prompt TEXT,
                user_message TEXT,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS evaluation_guidelines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                evaluation_id TEXT NOT NULL,
                guideline TEXT NOT NULL,
                followed INTEGER NOT NULL,
                explanation TEXT,
                evidence TEXT,
                FOREIGN KEY (evaluation_id) REFERENCES evaluations(id) ON DELETE CASCADE
            );
            """
        )
        self.conn.commit()

    def query(self, sql: str, params: Iterable[Any] | None = None) -> list[sqlite3.Row]:
        cur = self.conn.cursor()
        cur.execute(sql, params or [])
        return cur.fetchall()

    def execute(self, sql: str, params: Iterable[Any] | None = None) -> None:
        cur = self.conn.cursor()
        cur.execute(sql, params or [])
        self.conn.commit()

    def executemany(self, sql: str, params_seq: Iterable[Iterable[Any]]) -> None:
        cur = self.conn.cursor()
        cur.executemany(sql, params_seq)
        self.conn.commit()

    def _bootstrap_from_files(self) -> None:
        prompts_empty = not self.query("SELECT 1 FROM prompts LIMIT 1")
        system_path = Path("./data/system_prompts")
        if prompts_empty and system_path.exists():
            versions = sorted(system_path.glob("version_*.json"))
            records: list[tuple[Any, ...]] = []
            for file in versions:
                data = json.loads(file.read_text())
                records.append(
                    (
                        data["id"],
                        data["content"],
                        data.get("created_at"),
                        data.get("score"),
                        data.get("notes"),
                    )
                )
            if records:
                self.executemany(
                    "INSERT OR IGNORE INTO prompts (id, content, created_at, score, notes) VALUES (?, ?, ?, ?, ?)",
                    records,
                )
                current_file = system_path / "current.json"
                current_id = "version_0001"
                if current_file.exists():
                    current_id = json.loads(current_file.read_text()).get("current_version", current_id)
                self.execute(
                    "INSERT OR REPLACE INTO prompt_meta (key, value) VALUES ('current_version', ?)",
                    (current_id,),
                )

        evaluations_empty = not self.query("SELECT 1 FROM evaluations LIMIT 1")
        eval_file = Path("./data/evaluations.jsonl")
        if evaluations_empty and eval_file.exists():
            with eval_file.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    payload = json.loads(line)
                    result = payload["result"]
                    request = payload["request"]
                    self.execute(
                        """
                        INSERT OR REPLACE INTO evaluations (
                            id, prompt_version, preference_alignment, guideline_adherence,
                            overall, notes, metadata, system_prompt, user_message, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            result["evaluation_id"],
                            result.get("prompt_version"),
                            result["scores"]["preference_alignment"],
                            result["scores"]["guideline_adherence"],
                            result["scores"]["overall"],
                            result.get("notes"),
                            json.dumps(result.get("metadata")) if result.get("metadata") is not None else None,
                            request.get("system_prompt"),
                            request.get("user_message"),
                            payload.get("timestamp", datetime.utcnow().isoformat()),
                        ),
                    )
                    guidelines = result.get("guideline_results") or []
                    params = [
                        (
                            result["evaluation_id"],
                            item["guideline"],
                            1 if item["followed"] else 0,
                            item.get("explanation"),
                            item.get("evidence"),
                        )
                        for item in guidelines
                    ]
                    if params:
                        self.executemany(
                            """
                            INSERT INTO evaluation_guidelines (
                                evaluation_id, guideline, followed, explanation, evidence
                            ) VALUES (?, ?, ?, ?, ?)
                            """,
                            params,
                        )


db = Database()
