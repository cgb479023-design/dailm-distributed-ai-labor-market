import json
import os
import sqlite3
import time
from typing import Any, Dict, Optional


class JobStore:
    def __init__(self, db_path: str = "mission_logs/state.db"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS rfp_jobs (
                job_id TEXT PRIMARY KEY,
                status TEXT,
                ui_status TEXT,
                backend_status TEXT,
                progress INTEGER,
                error_json TEXT,
                telemetry_json TEXT,
                blueprint_json TEXT,
                source_hash TEXT,
                project_id TEXT,
                created_at REAL,
                updated_at REAL
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS ui_packages (
                ui_package_id TEXT PRIMARY KEY,
                job_id TEXT,
                status TEXT,
                download_url TEXT,
                checksum TEXT,
                build_meta_json TEXT,
                created_at REAL
            )
            """
        )
        conn.commit()
        conn.close()

    def create_job(self, job_id: str, source_hash: str, project_id: str) -> None:
        now = time.time()
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute(
            """
            INSERT OR REPLACE INTO rfp_jobs
            (job_id, status, ui_status, backend_status, progress, error_json, telemetry_json, blueprint_json, source_hash, project_id, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                job_id,
                "queued",
                "ok",
                "partial",
                0,
                None,
                None,
                None,
                source_hash,
                project_id,
                now,
                now,
            ),
        )
        conn.commit()
        conn.close()

    def update_job(
        self,
        job_id: str,
        status: Optional[str] = None,
        ui_status: Optional[str] = None,
        backend_status: Optional[str] = None,
        progress: Optional[int] = None,
        error: Optional[Dict[str, Any]] = None,
        telemetry: Optional[Dict[str, Any]] = None,
        blueprint: Optional[Dict[str, Any]] = None,
    ) -> None:
        fields = []
        values = []
        if status is not None:
            fields.append("status = ?")
            values.append(status)
        if ui_status is not None:
            fields.append("ui_status = ?")
            values.append(ui_status)
        if backend_status is not None:
            fields.append("backend_status = ?")
            values.append(backend_status)
        if progress is not None:
            fields.append("progress = ?")
            values.append(progress)
        if error is not None:
            fields.append("error_json = ?")
            values.append(json.dumps(error, ensure_ascii=False))
        if telemetry is not None:
            fields.append("telemetry_json = ?")
            values.append(json.dumps(telemetry, ensure_ascii=False))
        if blueprint is not None:
            fields.append("blueprint_json = ?")
            values.append(json.dumps(blueprint, ensure_ascii=False))

        fields.append("updated_at = ?")
        values.append(time.time())

        values.append(job_id)
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute(
            f"UPDATE rfp_jobs SET {', '.join(fields)} WHERE job_id = ?",
            values,
        )
        conn.commit()
        conn.close()

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute(
            """
            SELECT job_id, status, ui_status, backend_status, progress, error_json, telemetry_json, blueprint_json, source_hash, project_id
            FROM rfp_jobs WHERE job_id = ?
            """,
            (job_id,),
        )
        row = cur.fetchone()
        conn.close()
        if not row:
            return None
        return {
            "job_id": row[0],
            "status": row[1],
            "ui_status": row[2],
            "backend_status": row[3],
            "progress": row[4],
            "error": json.loads(row[5]) if row[5] else None,
            "telemetry": json.loads(row[6]) if row[6] else None,
            "blueprint": json.loads(row[7]) if row[7] else None,
            "source_hash": row[8],
            "project_id": row[9],
        }

    def create_ui_package(
        self,
        ui_package_id: str,
        job_id: str,
        status: str,
        download_url: Optional[str],
        checksum: Optional[str],
        build_meta: Optional[Dict[str, Any]],
    ) -> None:
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute(
            """
            INSERT OR REPLACE INTO ui_packages
            (ui_package_id, job_id, status, download_url, checksum, build_meta_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ui_package_id,
                job_id,
                status,
                download_url,
                checksum,
                json.dumps(build_meta or {}, ensure_ascii=False),
                time.time(),
            ),
        )
        conn.commit()
        conn.close()

    def update_ui_package(
        self,
        ui_package_id: str,
        status: Optional[str] = None,
        download_url: Optional[str] = None,
        checksum: Optional[str] = None,
        build_meta: Optional[Dict[str, Any]] = None,
    ) -> None:
        fields = []
        values = []
        if status is not None:
            fields.append("status = ?")
            values.append(status)
        if download_url is not None:
            fields.append("download_url = ?")
            values.append(download_url)
        if checksum is not None:
            fields.append("checksum = ?")
            values.append(checksum)
        if build_meta is not None:
            fields.append("build_meta_json = ?")
            values.append(json.dumps(build_meta, ensure_ascii=False))

        values.append(ui_package_id)
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute(
            f"UPDATE ui_packages SET {', '.join(fields)} WHERE ui_package_id = ?",
            values,
        )
        conn.commit()
        conn.close()

    def get_ui_package(self, ui_package_id: str) -> Optional[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute(
            """
            SELECT ui_package_id, job_id, status, download_url, checksum, build_meta_json
            FROM ui_packages WHERE ui_package_id = ?
            """,
            (ui_package_id,),
        )
        row = cur.fetchone()
        conn.close()
        if not row:
            return None
        return {
            "ui_package_id": row[0],
            "job_id": row[1],
            "status": row[2],
            "download_url": row[3],
            "checksum": row[4],
            "build_meta": json.loads(row[5]) if row[5] else {},
        }
