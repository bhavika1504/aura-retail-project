from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Event:
    """Base class for all system events."""
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = ""


@dataclass
class LowStockEvent(Event):
    """Published by Inventory when available stock ≤ threshold."""
    product_id: str = ""
    current_qty: int = 0
    threshold: int = 5


@dataclass
class HardwareFailureEvent(Event):
    """Published by TechnicianAlertHandler when failure chain is exhausted."""
    component: str = ""
    error_message: str = ""
    failure_count: int = 1


@dataclass
class EmergencyModeActivated(Event):
    """Published by KioskModeManager on transition to EmergencyState."""
    reason: str = ""
    kiosk_id: str = ""


@dataclass
class TransactionRollbackEvent(Event):
    """Published by PurchaseCommand when dispense fails mid-transaction."""
    transaction_id: str = ""
    reason: str = ""


@dataclass
class ModeChangedEvent(Event):
    """Published by KioskModeManager on every state transition."""
    kiosk_id: str = ""
    old_mode: str = ""
    new_mode: str = ""