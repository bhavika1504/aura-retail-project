from events.event_bus import EventBus
from events.events import ModeChangedEvent, EmergencyModeActivated
from inventory.pricing_strategies import StandardPricing, DiscountPricing, EmergencyPricing
from inventory.pricing_strategy import PricingContext
from core.kiosk_states import ActiveState, MaintenanceState, EmergencyState
from core.kiosk_mode_manager import KioskModeManager



print("\n========= OBSERVER SUBSCRIBER ============")

bus = EventBus()

bus.subscribe(ModeChangedEvent,
    lambda e: print(f"[City Monitor] Mode changed: {e.old_mode} → {e.new_mode}"))
bus.subscribe(EmergencyModeActivated,
    lambda e: print(f"[City Monitor] EMERGENCY on kiosk {e.kiosk_id}"))
bus.publish(ModeChangedEvent(
    kiosk_id="KIOSK-01",
    old_mode="ACTIVE",
    new_mode="MAINTENANCE"
))
bus.publish(EmergencyModeActivated(
    reason="System Failure",
    kiosk_id="KIOSK-01"
))

# ===================== STATE PATTERN =====================
print("\n=====------- STATE PATTERN ----------=====")

manager = KioskModeManager("KIOSK-01")

print(f"Current mode: {manager.get_current_mode()}")

manager.set_state(MaintenanceState())
print(f"Purchase in maintenance: {manager.handle_purchase('MED001', 1)}")

manager.set_state(EmergencyState())
print(f"Buy 5 units in emergency: {manager.handle_purchase('MED001', 5)}")
print(f"Buy 1 unit in emergency:  {manager.handle_purchase('MED001', 1)}")


# ===================== STRATEGY PATTERN =====================
print("\n=====-------- STRATEGY PATTERN ---------=====")

ctx = PricingContext(mode="active")

for strategy in [StandardPricing(), DiscountPricing(0.20), EmergencyPricing()]:
    manager.switch_pricing_strategy(strategy)
    price = manager.get_pricing_strategy().calculate_price(100.0, ctx)
    print(f"{strategy.get_name()}: Rs.100 → Rs.{price}")
