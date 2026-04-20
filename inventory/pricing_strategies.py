# =============================================================
# inventory/pricing_strategies.py  — Charmi Bhayani (202512028)
# PATTERN: Strategy (concrete implementations)
#
# Three strategies that can be swapped at runtime by
# KioskModeManager.switch_pricing_strategy().
#
#   StandardPricing   → no adjustment (default)
#   DiscountPricing   → percentage discount, premium bonus
#   EmergencyPricing  → essentials capped at base; no gouging
# =============================================================
from inventory.pricing_strategy import PricingStrategy, PricingContext


class StandardPricing(PricingStrategy):
    """
    PATTERN: Strategy — Default retail pricing.
    Returns base_price with no adjustment.
    Active during ACTIVE and POWER_SAVING modes.
    """

    def calculate_price(self, base_price: float, context: PricingContext) -> float:
        return round(base_price, 2)

    def get_name(self) -> str:
        return "StandardPricing"


class DiscountPricing(PricingStrategy):
    """
    PATTERN: Strategy — Discount pricing for loyalty / low-demand periods.

    Parameters
    ----------
    discount_rate : base discount  (default 10 %)
    premium_bonus : extra discount for premium users (default 5 %)
    """

    def __init__(self, discount_rate: float = 0.10, premium_bonus: float = 0.05):
        self._discount_rate = discount_rate
        self._premium_bonus = premium_bonus

    def calculate_price(self, base_price: float, context: PricingContext) -> float:
        rate = self._discount_rate
        if context.user_tier == "premium":
            rate += self._premium_bonus
        return round(base_price * (1.0 - rate), 2)

    def get_name(self) -> str:
        return f"DiscountPricing({int(self._discount_rate * 100)}%)"


class EmergencyPricing(PricingStrategy):
    """
    PATTERN: Strategy — Emergency mode pricing.

    Policy (city council mandate):
      - Essential items  → sold at exactly base price (no markup).
      - Non-essentials   → 50 % surcharge to discourage bulk buying.

    Activated automatically when KioskModeManager enters EmergencyState.
    """
    _ESSENTIAL_MULTIPLIER: float = 1.0
    _NON_ESSENTIAL_MULTIPLIER: float = 1.5

    def calculate_price(self, base_price: float, context: PricingContext) -> float:
        # context.mode == "emergency" implies essential-cap rule
        multiplier = self._ESSENTIAL_MULTIPLIER   # default: cap at base
        return round(base_price * multiplier, 2)

    def get_name(self) -> str:
        return "EmergencyPricing"
