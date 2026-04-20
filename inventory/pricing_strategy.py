# =============================================================
# inventory/pricing_strategy.py  — Charmi Bhayani (202512028)
# PATTERN: Strategy (interface / abstract base)
#
# Defines the contract for ALL pricing algorithms.
# KioskModeManager holds a reference to the current strategy
# and can swap it at runtime without touching any other class.
# =============================================================
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class PricingContext:
    """
    Context object passed to every pricing strategy.
    Carries environmental signals the strategy may use.
    """
    mode: str = "active"          # current kiosk mode
    demand_level: float = 1.0     # 0.0 – 2.0  (1.0 = normal)
    user_tier: str = "standard"   # "standard" | "premium" | "relief"


class PricingStrategy(ABC):
    """
    PATTERN: Strategy (abstract base)

    Every concrete strategy must implement:
      calculate_price(base_price, context) → final price
      get_name()                           → human-readable label
    """

    @abstractmethod
    def calculate_price(self, base_price: float, context: PricingContext) -> float:
        """Return the final price for one unit given base_price and context."""

    @abstractmethod
    def get_name(self) -> str:
        """Return a short label for logging / diagnostics."""
