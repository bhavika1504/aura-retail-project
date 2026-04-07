from inventory.pricing_strategy import PricingStrategy, PricingContext

class StandardPricing(PricingStrategy):
   
    def calculate_price(self, base_price: float, context: PricingContext) -> float:
        return round(base_price, 2)

    def get_name(self) -> str:
        return "StandardPricing"


class DiscountPricing(PricingStrategy):

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
   
    _ESSENTIAL_MULTIPLIER: float = 1.0
    _NON_ESSENTIAL_MULTIPLIER: float = 1.5

    def calculate_price(self, base_price: float, context: PricingContext) -> float:
       
        multiplier = self._ESSENTIAL_MULTIPLIER  
        return round(base_price * multiplier, 2)

    def get_name(self) -> str:
        return "EmergencyPricing"
