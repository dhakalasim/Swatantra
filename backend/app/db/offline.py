import json
import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path
import asyncio
import aiohttp


class OfflineSyncManager:
    """Manages offline-first synchronization between SQLite and PostgreSQL"""
    
    def __init__(self, sqlite_path: str, postgresql_url: Optional[str] = None):
        self.sqlite_path = sqlite_path
        self.postgresql_url = postgresql_url
        self.sync_queue_db = Path(sqlite_path).parent / "sync_queue.db"
        self._init_sync_queue()
    
    def _init_sync_queue(self):
        """Initialize sync queue database"""
        conn = sqlite3.connect(self.sync_queue_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sync_queue (
                id INTEGER PRIMARY KEY,
                operation_type TEXT NOT NULL,
                table_name TEXT NOT NULL,
                record_id INTEGER,
                data TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                synced BOOLEAN DEFAULT 0,
                synced_at DATETIME
            )
        """)
        
        conn.commit()
        conn.close()
    
    def add_to_sync_queue(
        self, 
        operation_type: str,  # insert, update, delete
        table_name: str,
        record_id: Optional[int],
        data: Optional[Dict[str, Any]] = None
    ):
        """Add an operation to the sync queue"""
        conn = sqlite3.connect(self.sync_queue_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO sync_queue (operation_type, table_name, record_id, data)
            VALUES (?, ?, ?, ?)
        """, (operation_type, table_name, record_id, json.dumps(data) if data else None))
        
        conn.commit()
        conn.close()
    
    def get_pending_syncs(self) -> List[Dict[str, Any]]:
        """Get all pending sync operations"""
        conn = sqlite3.connect(self.sync_queue_db)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM sync_queue WHERE synced = 0 ORDER BY timestamp ASC
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    async def sync_to_cloud(self, api_endpoint: str, auth_token: Optional[str] = None) -> Dict[str, Any]:
        """Sync pending operations to cloud PostgreSQL"""
        pending_syncs = self.get_pending_syncs()
        
        if not pending_syncs:
            return {"status": "success", "synced_count": 0}
        
        results = {
            "status": "success",
            "synced_count": 0,
            "failed_count": 0,
            "errors": []
        }
        
        headers = {}
        if auth_token:
            headers["Authorization"] = f"Bearer {auth_token}"
        
        async with aiohttp.ClientSession() as session:
            for sync_op in pending_syncs:
                try:
                    method = "POST" if sync_op["operation_type"] == "insert" else "PUT"
                    endpoint = f"{api_endpoint}/api/sync/{sync_op['table_name']}"
                    
                    payload = {
                        "operation_type": sync_op["operation_type"],
                        "record_id": sync_op["record_id"],
                        "data": json.loads(sync_op["data"]) if sync_op["data"] else None
                    }
                    
                    async with session.request(method, endpoint, json=payload, headers=headers) as resp:
                        if resp.status in [200, 201]:
                            self._mark_as_synced(sync_op["id"])
                            results["synced_count"] += 1
                        else:
                            results["failed_count"] += 1
                            results["errors"].append(f"Failed to sync {sync_op['table_name']}: {resp.status}")
                
                except Exception as e:
                    results["failed_count"] += 1
                    results["errors"].append(f"Sync error for {sync_op['table_name']}: {str(e)}")
        
        return results
    
    def _mark_as_synced(self, sync_id: int):
        """Mark a sync operation as synced"""
        conn = sqlite3.connect(self.sync_queue_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE sync_queue SET synced = 1, synced_at = CURRENT_TIMESTAMP WHERE id = ?
        """, (sync_id,))
        
        conn.commit()
        conn.close()
    
    def get_sync_status(self) -> Dict[str, Any]:
        """Get current sync status"""
        conn = sqlite3.connect(self.sync_queue_db)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM sync_queue WHERE synced = 0")
        pending = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM sync_queue WHERE synced = 1")
        synced = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "pending_count": pending,
            "synced_count": synced,
            "total_count": pending + synced,
            "last_sync": self._get_last_sync_time()
        }
    
    def _get_last_sync_time(self) -> Optional[str]:
        """Get timestamp of last sync"""
        conn = sqlite3.connect(self.sync_queue_db)
        cursor = conn.cursor()
        
        cursor.execute("SELECT MAX(synced_at) FROM sync_queue WHERE synced = 1")
        result = cursor.fetchone()[0]
        
        conn.close()
        return result
    
    def clear_synced_records(self, days_old: int = 30):
        """Clear old synced records from sync queue"""
        conn = sqlite3.connect(self.sync_queue_db)
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM sync_queue 
            WHERE synced = 1 AND synced_at < datetime('now', '-' || ? || ' days')
        """, (days_old,))
        
        conn.commit()
        conn.close()


# Singleton instance
_offline_sync_manager: Optional[OfflineSyncManager] = None


def get_offline_sync_manager(sqlite_path: str) -> OfflineSyncManager:
    """Get or create offline sync manager instance"""
    global _offline_sync_manager
    if _offline_sync_manager is None:
        _offline_sync_manager = OfflineSyncManager(sqlite_path)
    return _offline_sync_manager
