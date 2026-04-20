
from typing import Dict, Optional
from inventory.product import Product


class Inventory:
   
    LOW_STOCK_THRESHOLD: int = 5

    def __init__(self, kiosk_id: str) -> None:
        self._kiosk_id = kiosk_id
        self._products: Dict[str, Product] = {}

    # Catalogue management

    def add_product(self, product: Product) -> None:
        self._products[product.product_id] = product

    def get_product(self, product_id: str) -> Optional[Product]:
        return self._products.get(product_id)

    def all_products(self) -> Dict[str, Product]:
        return dict(self._products)

    # DERIVED ATTRIBUTE: available stock
    def get_available_stock(self, product_id: str) -> int:
       
        p = self._products.get(product_id)
        if p is None:
            return 0
        return max(0, p.quantity - p.reserved - p.hw_faulted)

    # ----------------------------------------------------------
    # Transaction lifecycle helpers
    # ----------------------------------------------------------
    def reserve_stock(self, product_id: str, qty: int) -> bool:
       
        p = self._products.get(product_id)
        if p is None or self.get_available_stock(product_id) < qty:
            return False
        p.reserved += qty
        self._check_low_stock(p)
        return True

    def release_reservation(self, product_id: str, qty: int) -> None:
        p = self._products.get(product_id)
        if p:
            p.reserved = max(0, p.reserved - qty)

    def commit_transaction(self, product_id: str, qty: int) -> bool:
       
        p = self._products.get(product_id)
        if p is None:
            return False
        p.reserved = max(0, p.reserved - qty)
        p.quantity = max(0, p.quantity - qty)
        self._check_low_stock(p)
        return True

    
    # Restock
    def restock(self, product_id: str, qty: int) -> None:
        p = self._products.get(product_id)
        if p:
            p.quantity += qty
            print(f"[Inventory] Restocked '{p.name}' +{qty} → total {p.quantity}")

   
    # Hardware fault tracking (impacts derived attribute)
    def mark_hw_faulted(self, product_id: str, qty: int) -> None:
        
        p = self._products.get(product_id)
        if p:
            p.hw_faulted = min(p.quantity, p.hw_faulted + qty)
            print(f"[Inventory] HW fault: {qty}x '{p.name}' marked unavailable.")

    def clear_hw_fault(self, product_id: str) -> None:
        """Clear hardware fault flag after recalibration."""
        p = self._products.get(product_id)
        if p:
            p.hw_faulted = 0
            print(f"[Inventory] HW fault cleared for '{p.name}'.")


    # Low-stock event (Observer integration)

    def _check_low_stock(self, product: Product) -> None:
        from events.event_bus import EventBus
        from events.events import LowStockEvent
        avail = self.get_available_stock(product.product_id)
        if avail <= self.LOW_STOCK_THRESHOLD:
            EventBus().publish(LowStockEvent(
                source=self._kiosk_id,
                product_id=product.product_id,
                current_qty=avail,
                threshold=self.LOW_STOCK_THRESHOLD,
            ))
