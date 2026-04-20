# =============================================================
# main.py  — Simulation Entry Point (all team members)
# =============================================================
# Run:  python main.py
#
# Demonstrates four scenarios required by Path A spec:
#   Scenario 1 — Normal food kiosk purchases + discount pricing
#   Scenario 2 — Emergency kiosk with purchase limits
#   Scenario 3 — Pharmacy with mode transitions
#   Scenario 4 — Hardware failure → Chain of Responsibility
# =============================================================
import random
random.seed(42)   # reproducible demo output

from core.kiosk_factory import (
    PharmacyKioskFactory, FoodKioskFactory, EmergencyKioskFactory,
)
from interface.kiosk_interface import KioskInterface
from events.event_bus import EventBus
from events.events import (
    LowStockEvent, HardwareFailureEvent, EmergencyModeActivated,
    TransactionRollbackEvent, ModeChangedEvent,
)
from registry.central_registry import CentralRegistry
from inventory.pricing_strategies import DiscountPricing, EmergencyPricing
from hardware.dispenser_hardware import SpiralDispenser


# =============================================================
# OBSERVER SUBSCRIBERS — city-wide monitoring setup
# (Each team member registers their own events here)
# =============================================================

def setup_event_subscribers() -> None:
    """
    PATTERN: Observer — register all city-monitoring handlers.
    Publishers never know these handlers exist.
    """
    bus = EventBus()

    # Charmi — inventory events
    bus.subscribe(LowStockEvent, lambda e: print(
        f"\n🔔 [SupplyChain]  LOW STOCK ALERT: '{e.product_id}' "
        f"→ only {e.current_qty} units left at kiosk '{e.source}'"
    ))

    # Bhavika — hardware events
    bus.subscribe(HardwareFailureEvent, lambda e: print(
        f"\n🔔 [Maintenance]  HARDWARE FAULT: component='{e.component}' "
        f"after {e.failure_count} retries — technician dispatched."
    ))

    # Kajal — transaction events
    bus.subscribe(TransactionRollbackEvent, lambda e: print(
        f"\n🔔 [TxnMonitor]   ROLLBACK: txn='{e.transaction_id}' "
        f"reason='{e.reason}'"
    ))

    # Devam — mode events
    bus.subscribe(EmergencyModeActivated, lambda e: print(
        f"\n🚨 [CityMonitor]  EMERGENCY ACTIVATED: kiosk='{e.kiosk_id}' "
        f"→ {e.reason}"
    ))
    bus.subscribe(ModeChangedEvent, lambda e: print(
        f"\n🔔 [CityMonitor]  MODE CHANGE: kiosk='{e.kiosk_id}' "
        f"'{e.old_mode}' → '{e.new_mode}'"
    ))


# =============================================================
# SCENARIO 1 — Food Kiosk: Normal purchases + Strategy swap
# =============================================================

def scenario_1_food_kiosk_normal_and_discount() -> None:
    header("SCENARIO 1 — Food Kiosk: Normal Purchases + Discount Pricing")

    ui = KioskInterface(FoodKioskFactory().create_kiosk("FK-01", "Central Metro Station"))
    ui.run_diagnostics()

    print("\n--- Purchase water (standard pricing) ---")
    info = ui.get_stock_info("FOOD003")
    print(f"  Live stock info: {info}")
    ui.purchase_item("FOOD003", qty=2, user_id="USR-101")

    print("\n--- Purchase cold coffee (checks refrigeration) ---")
    ui.purchase_item("FOOD002", qty=1, user_id="USR-102")

    print("\n--- Switch to 15 % DiscountPricing at runtime (Strategy pattern) ---")
    ui._kiosk.mode_manager.switch_pricing_strategy(DiscountPricing(discount_rate=0.15))
    info = ui.get_stock_info("FOOD001")
    print(f"  Live price after discount: {info['live_price']} (was {info['base_price']})")
    ui.purchase_item("FOOD001", qty=1, user_id="USR-103")

    print("\n--- Undo last purchase ---")
    ui.undo_last_command()

    print("\n--- Transaction history ---")
    for entry in ui.get_transaction_history():
        print(f"  • {entry}")


# =============================================================
# SCENARIO 2 — Emergency Kiosk: Limits + Event Broadcast
# =============================================================

def scenario_2_emergency_kiosk() -> None:
    header("SCENARIO 2 — Emergency Kiosk: Purchase Limits + Emergency Pricing")

    ui = KioskInterface(EmergencyKioskFactory().create_kiosk("EK-01", "Flood Zone A"))
    ui.run_diagnostics()

    print("\n--- Attempt to buy 5 water bottles (exceeds emergency limit of 2) ---")
    ui.purchase_item("EM001", qty=5, user_id="REF-001")   # blocked

    print("\n--- Buy 2 water bottles (within limit) ---")
    ui.purchase_item("EM001", qty=2, user_id="REF-001")   # approved

    print("\n--- Buy emergency food kit ---")
    ui.purchase_item("EM002", qty=1, user_id="REF-002")

    print("\n--- Buy first aid kit ---")
    ui.purchase_item("EM003", qty=2, user_id="REF-003")

    print("\n--- Stock info after purchases ---")
    for pid in ["EM001", "EM002", "EM003"]:
        info = ui.get_stock_info(pid)
        print(f"  {info['name']}: {info['available']} available @ ₹{info['live_price']}")


# =============================================================
# SCENARIO 3 — Pharmacy: Mode Transitions (State pattern)
# =============================================================

def scenario_3_pharmacy_mode_transitions() -> None:
    header("SCENARIO 3 — Pharmacy Kiosk: Mode Transitions")

    ui = KioskInterface(PharmacyKioskFactory().create_kiosk("PK-01", "City Hospital Wing B"))

    print("\n--- Normal purchase in ACTIVE mode ---")
    ui.purchase_item("MED001", qty=1, user_id="PAT-001")

    print("\n--- Enter POWER_SAVING mode —purchase auto-wakes kiosk ---")
    ui.set_operating_mode("power_saving")
    ui.purchase_item("MED001", qty=2, user_id="PAT-002")  # wakes → ACTIVE

    print("\n--- Enter MAINTENANCE mode ---")
    ui.set_operating_mode("maintenance")
    ui.purchase_item("MED001", qty=1, user_id="PAT-003")   # blocked
    ui.restock_inventory("MED001", qty=20)                  # allowed in maintenance

    print("\n--- Return to ACTIVE ---")
    ui.set_operating_mode("active")
    ui.purchase_item("MED002", qty=1, user_id="PAT-004")   # prescription

    print("\n--- Trigger EMERGENCY mode on pharmacy ---")
    ui.set_operating_mode("emergency")
    ui.purchase_item("MED001", qty=3, user_id="PAT-005")   # exceeds limit
    ui.purchase_item("MED001", qty=1, user_id="PAT-005")   # within limit

    ui.run_diagnostics()


# =============================================================
# SCENARIO 4 — Hardware Failure: Chain of Responsibility
# =============================================================

def scenario_4_hardware_failure_chain() -> None:
    header("SCENARIO 4 — Hardware Failure → Chain of Responsibility")

    kiosk = FoodKioskFactory().create_kiosk("FK-02", "Airport Terminal 3")

    print("\n--- Install a ALWAYS-FAILING dispenser to simulate fault ---")
    kiosk.hardware.set_dispenser(SpiralDispenser(failure_rate=1.0))

    ui = KioskInterface(kiosk)

    print("\n--- Attempt purchase — should trigger Retry → Recalibration → Technician ---")
    ui.purchase_item("FOOD001", qty=1, user_id="USR-999")

    print("\n--- Hardware report after failure chain ---")
    report = kiosk.hardware.get_hardware_report()
    for k, v in report.items():
        print(f"  {k}: {v}")

    print("\n--- Hot-swap to a reliable dispenser (Path B: hardware replacement) ---")
    from hardware.dispenser_hardware import RoboticArmDispenser
    kiosk.hardware.set_dispenser(RoboticArmDispenser(failure_rate=0.0))

    print("\n--- Purchase succeeds after swap ---")
    ui.purchase_item("FOOD001", qty=1, user_id="USR-999")


# =============================================================
# BONUS: Central Registry overview
# =============================================================

def show_central_registry() -> None:
    header("CENTRAL REGISTRY — All Registered Kiosks")
    reg = CentralRegistry()
    kiosks = reg.list_kiosks()
    if not kiosks:
        print("  (empty)")
        return
    for kid, kiosk in kiosks.items():
        print(f"  [{kid}]  {kiosk}  status={reg.get_status(kid)}")


# =============================================================
# Helpers
# =============================================================

def header(title: str) -> None:
    bar = "═" * 65
    print(f"\n{bar}")
    print(f"  {title}")
    print(bar)


# =============================================================
# Entry point
# =============================================================

if __name__ == "__main__":
    setup_event_subscribers()

    scenario_1_food_kiosk_normal_and_discount()
    scenario_2_emergency_kiosk()
    scenario_3_pharmacy_mode_transitions()
    scenario_4_hardware_failure_chain()

    show_central_registry()

    print("\n\n✅  Aura Retail OS simulation complete.")
