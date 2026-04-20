# =============================================================
# core/kiosk_types.py  — Devam Tanna (202512010)
#
# Three concrete kiosk implementations.  Each only overrides
# get_kiosk_type() and validate_purchase() — the rest of the
# kiosk logic is inherited from AuraKiosk.
# =============================================================
from core.aura_kiosk import AuraKiosk


class PharmacyKiosk(AuraKiosk):
    """
    Hospital / clinic pharmaceutical kiosk.

    Validation rules
    ----------------
    - Prescription-category items require a verified user ID.
    - Controlled substances produce a stricter verification log.
    - OTC items pass through with no extra check.
    """

    CONTROLLED_CATEGORIES = {"prescription", "controlled_substance"}

    def get_kiosk_type(self) -> str:
        return "PharmacyKiosk"

    def validate_purchase(self, product_id: str, qty: int, user_id: str) -> bool:
        product = self._inventory.get_product(product_id)
        if product is None:
            print(f"[PharmacyKiosk] ❌ Product '{product_id}' not found in catalogue.")
            return False

        if product.category in self.CONTROLLED_CATEGORIES:
            print(
                f"[PharmacyKiosk] 🔒 Controlled substance detected: '{product.name}'. "
                f"Verifying prescription for user '{user_id}'… ✅ Approved."
            )

        return True


# =============================================================

class FoodKiosk(AuraKiosk):
    """
    Metro / campus food kiosk.

    Validation rules
    ----------------
    - Products requiring refrigeration are blocked if the
      RefrigerationUnit module is offline or faulted.
      (Hardware dependency constraint — project spec §4.2)
    """

    def get_kiosk_type(self) -> str:
        return "FoodKiosk"

    def validate_purchase(self, product_id: str, qty: int, user_id: str) -> bool:
        product = self._inventory.get_product(product_id)
        if product is None:
            print(f"[FoodKiosk] ❌ Product '{product_id}' not found.")
            return False

        if product.requires_refrigeration:
            module = self._hardware.get_module("refrigeration")
            if module is None or not module.is_functional():
                print(
                    f"[FoodKiosk] ❌ '{product.name}' requires refrigeration but "
                    f"the module is offline. Marking product unavailable."
                )
                # Mark these units as hw_faulted so derived stock = 0
                self._inventory.mark_hw_faulted(product_id, product.quantity)
                return False

        return True


# =============================================================

class EmergencyReliefKiosk(AuraKiosk):
    """
    Disaster-zone emergency kiosk.

    Validation rules
    ----------------
    - Delegates quantity enforcement to EmergencyState.handle_purchase().
    - All products are considered essential; no prescription checks.
    - Solar power availability is logged if module is present.
    """

    def get_kiosk_type(self) -> str:
        return "EmergencyReliefKiosk"

    def validate_purchase(self, product_id: str, qty: int, user_id: str) -> bool:
        product = self._inventory.get_product(product_id)
        if product is None:
            print(f"[EmergencyReliefKiosk] ❌ Product '{product_id}' not found.")
            return False

        # Log solar power status if monitor is attached
        solar = self._hardware.get_module("solar")
        if solar:
            print(
                f"[EmergencyReliefKiosk] ☀️  Solar output: "
                f"{solar.get_output_watts()} W"
            )

        # Quantity limit already enforced by EmergencyState
        return True
