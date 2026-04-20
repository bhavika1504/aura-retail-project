# =============================================================
# core/aura_kiosk.py  — Devam Tanna (202512010)
#
# Abstract base for every kiosk type.
# Concrete subclasses (PharmacyKiosk, FoodKiosk, etc.) only
# override get_kiosk_type() and validate_purchase() —
# everything else is provided here.
# =============================================================
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict

from inventory.inventory import Inventory
from hardware.hardware_manager import HardwareManager
from core.kiosk_mode_manager import KioskModeManager
from transaction.command_invoker import CommandInvoker
from transaction.transaction_memento import TransactionCaretaker


class AuraKiosk(ABC):
    """
    Abstract kiosk entity.

    Holds references to every subsystem required for operation:
      _inventory       → stock data + derived available stock
      _hardware        → dispenser, payment, optional modules
      _mode_manager    → current state + pricing strategy
      _invoker         → command executor + history
      _caretaker       → memento store for atomic rollback

    Subclasses must implement:
      get_kiosk_type()        → "PharmacyKiosk" etc.
      validate_purchase()     → kiosk-specific pre-purchase rules
    """

    def __init__(
        self,
        kiosk_id: str,
        location: str,
        inventory: Inventory,
        hardware_manager: HardwareManager,
        mode_manager: KioskModeManager,
        command_invoker: CommandInvoker,
        caretaker: TransactionCaretaker,
    ) -> None:
        self._kiosk_id = kiosk_id
        self._location = location
        self._inventory = inventory
        self._hardware = hardware_manager
        self._mode_manager = mode_manager
        self._invoker = command_invoker
        self._caretaker = caretaker

    # ----------------------------------------------------------
    # Properties (read-only access for KioskInterface / facade)
    # ----------------------------------------------------------
    @property
    def kiosk_id(self) -> str:
        return self._kiosk_id

    @property
    def location(self) -> str:
        return self._location

    @property
    def inventory(self) -> Inventory:
        return self._inventory

    @property
    def hardware(self) -> HardwareManager:
        return self._hardware

    @property
    def mode_manager(self) -> KioskModeManager:
        return self._mode_manager

    @property
    def invoker(self) -> CommandInvoker:
        return self._invoker

    @property
    def caretaker(self) -> TransactionCaretaker:
        return self._caretaker

    # ----------------------------------------------------------
    # Abstract interface (subclass responsibility)
    # ----------------------------------------------------------
    @abstractmethod
    def get_kiosk_type(self) -> str:
        """Return a human-readable type label."""

    @abstractmethod
    def validate_purchase(self, product_id: str, qty: int, user_id: str) -> bool:
        """
        Kiosk-specific pre-purchase validation.
        Called by KioskInterface BEFORE creating a PurchaseCommand.
        Examples:
          PharmacyKiosk — prescription check for controlled substances
          FoodKiosk     — verify refrigeration module is online
          EmergencyKiosk— delegate to EmergencyState qty limit
        """

    # ----------------------------------------------------------
    # Operational status (derived attribute — computed live)
    # ----------------------------------------------------------
    def get_operational_status(self) -> Dict[str, Any]:
        """
        Derived operational status of the kiosk.
        Combines mode, hardware, and configuration into one report.
        """
        return {
            "kiosk_id": self._kiosk_id,
            "type": self.get_kiosk_type(),
            "location": self._location,
            "mode": self._mode_manager.get_current_mode(),
            "pricing": self._mode_manager.get_pricing_strategy().get_name(),
            "hardware": self._hardware.get_hardware_report(),
            "mode_constraints": self._mode_manager.handle_diagnostics(),
        }

    # ----------------------------------------------------------
    # Dunder
    # ----------------------------------------------------------
    def __repr__(self) -> str:
        return (
            f"{self.get_kiosk_type()}("
            f"id={self._kiosk_id!r}, "
            f"location={self._location!r}, "
            f"mode={self._mode_manager.get_current_mode()}"
            f")"
        )
