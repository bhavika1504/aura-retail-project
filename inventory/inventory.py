# =============================================================
# inventory/inventory.py  — Charmi Bhayani (202512028)
#
# Core inventory manager for one kiosk.
#
# KEY DESIGN: getAvailableStock() is a DERIVED ATTRIBUTE —
#   available = quantity - reserved - hw_faulted
# This value is NEVER stored; it is always computed live so
# the system cannot sell items that are reserved or faulted.
# =============================================================
from typing import Dict, Optional
from inventory.product import Product


class Inventory:
    """
    Manages the product catalogue and stock levels for a kiosk.

    Derived attribute contract
    --------------------------
    get_available_stock(pid) → int
      = product.quantity - product.reserved - product.hw_faulted
      (minimum 0 — never negative)

    A purchase is blocked if this value < requested quantity.
    """

    LOW_STOCK_THRESHOLD: int = 5

    def __init__(self, kiosk_id: str) -> None:
        self._kiosk_id = kiosk_id
        self._products: Dict[str, Product] = {}

    # ----------------------------------------------------------
    # Catalogue management
    # ----------------------------------------------------------
    def add_product(self, product: Product) -> None:
        self._products[product.product_id] = product

    def get_product(self, product_id: str) -> Optional[Product]:
        return self._products.get(product_id)

    def all_products(self) -> Dict[str, Product]:
        return dict(self._products)

    # ----------------------------------------------------------
    # DERIVED ATTRIBUTE: available stock
    # ----------------------------------------------------------
    def get_available_stock(self, product_id: str) -> int:
        """
        Derived attribute — computed live, never persisted.
        Prevents overselling when concurrent transactions exist.
        """
        p = self._products.get(product_id)
        if p is None:
            return 0
        return max(0, p.quantity - p.reserved - p.hw_faulted)

    # ----------------------------------------------------------
    # Transaction lifecycle helpers
    # ----------------------------------------------------------
    def reserve_stock(self, product_id: str, qty: int) -> bool:
        """
        Phase 1 of purchase: lock units so concurrent transactions
        cannot sell the same items (prevents overselling).
        Returns False if insufficient available stock.
        """
        p = self._products.get(product_id)
        if p is None or self.get_available_stock(product_id) < qty:
            return False
        p.reserved += qty
        self._check_low_stock(p)
        return True

    def release_reservation(self, product_id: str, qty: int) -> None:
        """
        Called on payment failure or rollback:
        undo the reservation so stock returns to available.
        """
        p = self._products.get(product_id)
        if p:
            p.reserved = max(0, p.reserved - qty)

    def commit_transaction(self, product_id: str, qty: int) -> bool:
        """
        Phase 2 of purchase (after successful dispense):
        deduct qty from physical quantity and release reservation.
        Inventory update happens ONLY when transaction fully succeeds.
        """
        p = self._products.get(product_id)
        if p is None:
            return False
        p.reserved = max(0, p.reserved - qty)
        p.quantity = max(0, p.quantity - qty)
        self._check_low_stock(p)
        return True

    # ----------------------------------------------------------
    # Restock
    # ----------------------------------------------------------
    def restock(self, product_id: str, qty: int) -> None:
        p = self._products.get(product_id)
        if p:
            p.quantity += qty
            print(f"[Inventory] Restocked '{p.name}' +{qty} → total {p.quantity}")

    # ----------------------------------------------------------
    # Hardware fault tracking (impacts derived attribute)
    # ----------------------------------------------------------
    def mark_hw_faulted(self, product_id: str, qty: int) -> None:
        """
        Mark qty units as unavailable due to hardware fault.
        This immediately reduces get_available_stock() result.
        """
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

    # ----------------------------------------------------------
    # Low-stock event (Observer integration)
    # ----------------------------------------------------------
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
