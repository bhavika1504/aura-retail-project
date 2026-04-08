
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class PricingContext:
    mode: str = "active"          
    demand_level: float = 1.0     
    user_tier: str = "standard"   

class PricingStrategy(ABC):
    
    @abstractmethod
    def calculate_price(self, base_price: float, context: PricingContext) -> float:
        pass
       

    @abstractmethod
    def get_name(self) -> str:
        pass

