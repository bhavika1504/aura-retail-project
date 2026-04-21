
from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class Product:
    """
    Represents a single stocked product.

    Fields
    ------
    product_id      : Unique identifier (e.g. "MED001")
    name            : Display name
    base_price      : Price before strategy adjustment (₹)
    quantity        : Physical units in the kiosk
    reserved        : Units locked by in-flight transactions
    hw_faulted      : Units blocked due to hardware fault
    requires_refrigeration : Needs RefrigerationUnit to be sold
    is_essential    : Capped quantity during emergency mode
    category        : "otc" | "prescription" | "food" | "general"
    """
    product_id: str
    name: str
    base_price: float
    quantity: int = 0
    reserved: int = 0
    hw_faulted: int = 0
    requires_refrigeration: bool = False
    is_essential: bool = False
    category: str = "general"

    
    # Serialisation helpers (used by PersistenceManager)
  
    def to_dict(self) -> Dict[str, Any]:
        return {
            "product_id": self.product_id,
            "name": self.name,
            "base_price": self.base_price,
            "quantity": self.quantity,
            "reserved": self.reserved,
            "hw_faulted": self.hw_faulted,
            "requires_refrigeration": self.requires_refrigeration,
            "is_essential": self.is_essential,
            "category": self.category,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Product":
        return cls(**data)

    def __repr__(self) -> str:
        return (f"Product({self.product_id!r}, qty={self.quantity}, "
                f"reserved={self.reserved}, faulted={self.hw_faulted})")
