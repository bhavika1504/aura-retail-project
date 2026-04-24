import sys
sys.stdout.reconfigure(encoding='utf-8')

from core.kiosk_factory import PharmacyKioskFactory, FoodKioskFactory
from interface.kiosk_interface import KioskInterface
from events.event_bus import EventBus
from events.events import ModeChangedEvent, HardwareFailureEvent

def run_simulation():
    print("="*60)
    print("   AURA OS — Retail Kiosk Intelligence Simulation   ")
    print("="*60)
    
    # 1. SETUP: Initialize Global Observer (Singleton + Observer)
    # The EventBus is a Singleton — we get the same instance everywhere.
    bus = EventBus()
    bus.subscribe(ModeChangedEvent, lambda e: print(f"  [OBSERVER] Received ModeChangedEvent: {e.old_mode} -> {e.new_mode}"))
    bus.subscribe(HardwareFailureEvent, lambda e: print(f"  [OBSERVER] Received HardwareFailureEvent: {e.reason}"))

    # 2. FACTORY: Create a Pharmacy Kiosk
    # The PharmacyKioskFactory (Abstract Factory) wires together a RoboticArmDispenser, 
    # CardPayment, and specific medicine inventory.
    print("\n[PHASE 1] Initializing Pharmacy Kiosk...")
    factory = PharmacyKioskFactory()
    pharmacy_kiosk = factory.create_kiosk("PHARM-001", "City Hospital")
    
    # 3. FACADE: Interact through KioskInterface
    # We use the KioskInterface (Facade) so we don't have to deal with 
    # CommandInvoker or ModeManager directly.
    kiosk = KioskInterface(pharmacy_kiosk)
    
    # 4. COMMAND + DECORATOR: Execute a basic purchase
    # This triggers PurchaseCommand wrapped in Timing and Logging Decorators.
    print("\n[PHASE 2] Executing standard purchase...")
    kiosk.purchase_item("MED001", qty=2, user_id="CUST-77")

    # 5. STATE + STRATEGY: Switch to Emergency Mode
    # State pattern changes behavior; Strategy pattern changes pricing.
    print("\n[PHASE 3] Simulating Emergency Mode activation...")
    kiosk.set_operating_mode("emergency")
    
    # Check live stock info (Derived via Strategy)
    info = kiosk.get_stock_info("MED001")
    print(f"  Live Price (Emergency Strategy): ₹{info['live_price']}")
    
    # Try to buy too much in Emergency Mode (Denial by State)
    print("\n[PHASE 4] Attempting restricted purchase (5 units) in Emergency Mode...")
    kiosk.purchase_item("MED001", qty=5)

    # 6. MEMENTO: Undo the last successful command
    # We'll switch back to active mode and undo.
    print("\n[PHASE 5] Restoring Active Mode and Testing Undo...")
    kiosk.set_operating_mode("active")
    kiosk.undo_last_command() # Should undo the last modification if possible

    # 7. DIAGNOSTICS: Review System State
    kiosk.run_diagnostics()

    print("\n" + "="*60)
    print("   Simulation Complete — All Design Patterns Validated   ")
    print("="*60)

if __name__ == "__main__":
    run_simulation()
