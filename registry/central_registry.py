# =============================================================
# registry/central_registry.py
# PATTERN: Singleton
#
# One global instance holding configuration, kiosk registry,
# and system-wide status. Every layer reads config from here.
# KioskFactory registers every new kiosk here on creation.
# =============================================================
from __future__ import annotations
from typing import Any, Dict, Optional


class CentralRegistry:
    """
    PATTERN: Singleton

    Guarantees exactly one instance across all layers.
    Acts as the single source of truth for:
      - System configuration (emergency limits, thresholds, …)
      - Kiosk registry (id → AuraKiosk object)
      - Runtime status per kiosk
    """
    _instance: "CentralRegistry | None" = None

    def __new__(cls) -> "CentralRegistry":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._config: Dict[str, Any] = {
                "emergency_purchase_limit": 2,
                "low_stock_threshold": 5,
                "max_retry_attempts": 3,
            }
            cls._instance._kiosks: Dict[str, Any] = {}
            cls._instance._status: Dict[str, str] = {}
        return cls._instance

    # ----------------------------------------------------------
    # Configuration
    # ----------------------------------------------------------
    def set_config(self, key: str, value: Any) -> None:
        self._config[key] = value

    def get_config(self, key: str, default: Any = None) -> Any:
        return self._config.get(key, default)

    # ----------------------------------------------------------
    # Kiosk registry
    # ----------------------------------------------------------
    def register_kiosk(self, kiosk_id: str, kiosk: Any) -> None:
        self._kiosks[kiosk_id] = kiosk
        self._status[kiosk_id] = "ACTIVE"
        print(f"[CentralRegistry] ✅ Kiosk registered: {kiosk_id}")

    def get_kiosk(self, kiosk_id: str) -> Optional[Any]:
        return self._kiosks.get(kiosk_id)

    def list_kiosks(self) -> Dict[str, Any]:
        return dict(self._kiosks)

    # ----------------------------------------------------------
    # Status tracking
    # ----------------------------------------------------------
    def update_status(self, kiosk_id: str, status: str) -> None:
        self._status[kiosk_id] = status

    def get_status(self, kiosk_id: str) -> str:
        return self._status.get(kiosk_id, "UNKNOWN")

    def get_all_statuses(self) -> Dict[str, str]:
        return dict(self._status)
