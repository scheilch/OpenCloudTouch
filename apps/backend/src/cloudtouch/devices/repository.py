"""
Database models and repository for device management
Uses aiosqlite for async SQLite operations
"""

import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, List, Optional

import aiosqlite

logger = logging.getLogger(__name__)


class Device:
    """Device model."""

    def __init__(
        self,
        device_id: str,
        ip: str,
        name: str,
        model: str,
        mac_address: str,
        firmware_version: str,
        schema_version: Optional[str] = None,
        last_seen: Optional[datetime] = None,
        id: Optional[int] = None,
    ):
        self.id = id
        self.device_id = device_id
        self.ip = ip
        self.name = name
        self.model = model
        self.mac_address = mac_address
        self.firmware_version = firmware_version
        self.schema_version = schema_version or self._extract_schema_version(
            firmware_version
        )
        self.last_seen = last_seen or datetime.now(UTC)

    @staticmethod
    def _extract_schema_version(firmware_version: str) -> str:
        """
        Extract schema version from firmware version.

        For SoundTouch, schema version is derived from firmware major.minor.patch.
        Example: "28.0.3.46454 epdbuild..." -> "28.0.3"
        """
        if not firmware_version:
            return "unknown"

        # Extract first 3 version components (major.minor.patch)
        parts = firmware_version.split()[0].split(".")
        if len(parts) >= 3:
            return ".".join(parts[:3])
        return firmware_version.split()[0] if firmware_version else "unknown"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "id": self.id,
            "device_id": self.device_id,
            "ip": self.ip,
            "name": self.name,
            "model": self.model,
            "mac_address": self.mac_address,
            "firmware_version": self.firmware_version,
            "schema_version": self.schema_version,
            "last_seen": self.last_seen.isoformat() if self.last_seen else None,
        }


class DeviceRepository:
    """Repository for device persistence."""

    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self._db: Optional[aiosqlite.Connection] = None

    async def initialize(self) -> None:
        """Initialize database and create tables."""
        # Ensure directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self._db = await aiosqlite.connect(str(self.db_path))

        await self._db.execute(
            """
            CREATE TABLE IF NOT EXISTS devices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT UNIQUE NOT NULL,
                ip TEXT NOT NULL,
                name TEXT NOT NULL,
                model TEXT NOT NULL,
                mac_address TEXT NOT NULL,
                firmware_version TEXT NOT NULL,
                schema_version TEXT,
                last_seen TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Migration: Add schema_version column if it doesn't exist
        try:
            await self._db.execute("SELECT schema_version FROM devices LIMIT 1")
        except aiosqlite.OperationalError:
            logger.info("Migrating devices table: Adding schema_version column")
            await self._db.execute(
                """
                ALTER TABLE devices ADD COLUMN schema_version TEXT
            """
            )
            await self._db.commit()

        await self._db.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_device_id ON devices(device_id)
        """
        )

        await self._db.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_ip ON devices(ip)
        """
        )

        await self._db.commit()
        logger.info(f"Database initialized: {self.db_path}")

    async def close(self) -> None:
        """Close database connection."""
        if self._db:
            await self._db.close()
            self._db = None

    async def upsert(self, device: Device) -> Device:
        """
        Insert or update device.

        Args:
            device: Device to upsert

        Returns:
            Device with updated id
        """
        if not self._db:
            raise RuntimeError("Database not initialized")

        cursor = await self._db.execute(
            """
            INSERT INTO devices (device_id, ip, name, model, mac_address, firmware_version, schema_version, last_seen)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(device_id) DO UPDATE SET
                ip = excluded.ip,
                name = excluded.name,
                model = excluded.model,
                firmware_version = excluded.firmware_version,
                schema_version = excluded.schema_version,
                last_seen = excluded.last_seen,
                updated_at = CURRENT_TIMESTAMP
            RETURNING id
        """,
            (
                device.device_id,
                device.ip,
                device.name,
                device.model,
                device.mac_address,
                device.firmware_version,
                device.schema_version,
                device.last_seen,
            ),
        )

        row = await cursor.fetchone()
        device.id = row[0] if row else None

        await self._db.commit()
        logger.debug(f"Upserted device: {device.name} ({device.device_id})")

        return device

    async def get_all(self) -> List[Device]:
        """Get all devices."""
        if not self._db:
            raise RuntimeError("Database not initialized")

        cursor = await self._db.execute(
            """
            SELECT id, device_id, ip, name, model, mac_address, firmware_version, schema_version, last_seen
            FROM devices
            ORDER BY last_seen DESC
        """
        )

        rows = await cursor.fetchall()

        devices = [
            Device(
                id=row[0],
                device_id=row[1],
                ip=row[2],
                name=row[3],
                model=row[4],
                mac_address=row[5],
                firmware_version=row[6],
                schema_version=row[7],
                last_seen=datetime.fromisoformat(row[8]) if row[8] else None,
            )
            for row in rows
        ]

        return devices

    async def get_by_device_id(self, device_id: str) -> Optional[Device]:
        """Get device by device_id."""
        if not self._db:
            raise RuntimeError("Database not initialized")

        cursor = await self._db.execute(
            """
            SELECT id, device_id, ip, name, model, mac_address, firmware_version, schema_version, last_seen
            FROM devices
            WHERE device_id = ?
        """,
            (device_id,),
        )

        row = await cursor.fetchone()

        if not row:
            return None

        return Device(
            id=row[0],
            device_id=row[1],
            ip=row[2],
            name=row[3],
            model=row[4],
            mac_address=row[5],
            firmware_version=row[6],
            schema_version=row[7],
            last_seen=datetime.fromisoformat(row[8]) if row[8] else None,
        )

    async def delete_all(self) -> int:
        """Delete all devices from database. Returns number of deleted rows."""
        if not self._db:
            raise RuntimeError("Database not initialized")

        cursor = await self._db.execute("DELETE FROM devices")
        await self._db.commit()

        deleted_count = cursor.rowcount
        logger.debug(f"Deleted all devices from database: {deleted_count} rows")

        return deleted_count
