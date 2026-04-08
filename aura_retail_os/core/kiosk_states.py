
# States
# ----------------------------------------------------------------
# ActiveState       → normal operation, all features enabled
# PowerSavingState  → screen dim, wakes on purchase request
# MaintenanceState  → purchases blocked, restock allowed
# EmergencyState    → purchase qty capped (city mandate: max 2)
# ------------------------------------------------------------------
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Dict, Any

if TYPE_CHECKING:
    from core.kiosk_mode_manager import KioskModeManager


class KioskState(ABC):
    """
    PATTERN: State — Abstract base

    Each concrete state implements three behaviours:
      handle_purchase()   → approve or reject, return bool
      handle_restock()    → approve or reject, return bool
      handle_diagnostics()→ return mode-specific status dict
      get_mode_name()     → short string label
    """

    @abstractmethod
    def handle_purchase(
        self, manager: "KioskModeManager", product_id: str, qty: int
    ) -> bool: ...

    @abstractmethod
    def handle_restock(self, manager: "KioskModeManager") -> bool: ...

    @abstractmethod
    def handle_diagnostics(self, manager: "KioskModeManager") -> Dict[str, Any]: ...

    @abstractmethod
    def get_mode_name(self) -> str: ...



class ActiveState(KioskState):
    """
    PATTERN: State — Normal operating mode.
    All operations are permitted.
    """

    def handle_purchase(self, manager, product_id, qty) -> bool:
        return True   # no restrictions

    def handle_restock(self, manager) -> bool:
        return True

    def handle_diagnostics(self, manager) -> Dict[str, Any]:
        return {
            "mode": "ACTIVE",
            "purchases": "allowed",
            "restock": "allowed",
        }

    def get_mode_name(self) -> str:
        return "ACTIVE"


class PowerSavingState(KioskState):
    """
    PATTERN: State — Screen and motor power reduced.
    A purchase request automatically wakes the kiosk to ACTIVE.
    """

    def handle_purchase(self, manager, product_id, qty) -> bool:
        print("[PowerSavingState] ⚡ Purchase request — waking to ACTIVE mode.")
        manager.set_state(ActiveState())
        return True   # allow after wake

    def handle_restock(self, manager) -> bool:
        print("[PowerSavingState] Waking for restock…")
        manager.set_state(ActiveState())
        return True

    def handle_diagnostics(self, manager) -> Dict[str, Any]:
        return {
            "mode": "POWER_SAVING",
            "purchases": "allowed (wake-on-demand)",
            "restock": "allowed (wake-on-demand)",
        }

    def get_mode_name(self) -> str:
        return "POWER_SAVING"


class MaintenanceState(KioskState):
    """
    PATTERN: State — Technician on-site maintenance.
    Purchases are blocked; restocking is allowed.
    """

    def handle_purchase(self, manager, product_id, qty) -> bool:
        print("[MaintenanceState] ❌ Kiosk under maintenance — purchases suspended.")
        return False

    def handle_restock(self, manager) -> bool:
        print("[MaintenanceState] ✅ Restock approved during maintenance window.")
        return True

    def handle_diagnostics(self, manager) -> Dict[str, Any]:
        return {
            "mode": "MAINTENANCE",
            "purchases": "BLOCKED",
            "restock": "allowed",
            "note": "Service technician window active",
        }

    def get_mode_name(self) -> str:
        return "MAINTENANCE"


class EmergencyState(KioskState):
    """
    PATTERN: State — City emergency lockdown mode.

    System constraint (city council mandate):
      A single transaction may NOT purchase more than
      EMERGENCY_LIMIT units of any essential item.

    EmergencyPricing is activated by KioskModeManager
    automatically on transition into this state.
    """

    EMERGENCY_LIMIT: int = 2

    def handle_purchase(self, manager, product_id, qty) -> bool:
        if qty > self.EMERGENCY_LIMIT:
            print(
                f"[EmergencyState] ❌ Purchase of {qty} units denied. "
                f"Emergency limit is {self.EMERGENCY_LIMIT} per transaction."
            )
            return False
        print(
            f"[EmergencyState] ⚠️  Emergency purchase approved "
            f"({qty}/{self.EMERGENCY_LIMIT} units)."
        )
        return True

    def handle_restock(self, manager) -> bool:
        print("[EmergencyState] ✅ Emergency restock approved.")
        return True

    def handle_diagnostics(self, manager) -> Dict[str, Any]:
        return {
            "mode": "EMERGENCY",
            "purchases": f"limited to {self.EMERGENCY_LIMIT} units/transaction",
            "restock": "allowed",
            "pricing": "EmergencyPricing active",
        }

    def get_mode_name(self) -> str:
        return "EMERGENCY"
