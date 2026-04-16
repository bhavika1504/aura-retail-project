# -----------------------------------------------------------
# PATTERN: State (Context) + Strategy (host)
#
# Holds the CURRENT state (KioskState) and CURRENT pricing
# strategy (PricingStrategy).  Both are swappable at runtime.
#
# On every state transition it:
#   1. Logs the old → new mode change.
#   2. Publishes ModeChangedEvent via EventBus.
#   3. If entering EMERGENCY, also activates EmergencyPricing
#      and publishes EmergencyModeActivated.
# --------------------------------------------------------------
from __future__ import annotations
from typing import TYPE_CHECKING

from core.kiosk_states import KioskState, ActiveState
from inventory.pricing_strategy import PricingContext, PricingStrategy
from inventory.pricing_strategies import StandardPricing, EmergencyPricing

if TYPE_CHECKING:
    pass


class KioskModeManager:
    """
    PATTERN: State (Context)

    External callers (KioskInterface, AuraKiosk) delegate all
    mode-dependent decisions here.  They never inspect the state
    object directly — they just call handle_purchase() etc.

    Also doubles as the Strategy host: holds _pricing and exposes
    switch_pricing_strategy() for runtime swaps.
    """

    def __init__(self, kiosk_id: str) -> None:
        self._kiosk_id = kiosk_id
        self._state: KioskState = ActiveState()
        self._pricing: PricingStrategy = StandardPricing()

    # State management (PATTERN: State)

    def set_state(self, new_state: KioskState) -> None:
        from events.event_bus import EventBus
        from events.events import ModeChangedEvent, EmergencyModeActivated

        old_name = self._state.get_mode_name()
        new_name = new_state.get_mode_name()
        self._state = new_state

        print(f"[ModeManager:{self._kiosk_id}] {old_name} → {new_name}")

        EventBus().publish(ModeChangedEvent(
            source=self._kiosk_id,
            kiosk_id=self._kiosk_id,
            old_mode=old_name,
            new_mode=new_name,
        ))

        # Auto-activate emergency pricing on emergency transition
        if new_name == "EMERGENCY":
            self._pricing = EmergencyPricing()
            EventBus().publish(EmergencyModeActivated(
                source=self._kiosk_id,
                kiosk_id=self._kiosk_id,
                reason="System entered emergency lockdown.",
            ))
        elif old_name == "EMERGENCY" and new_name == "ACTIVE":
            # Restore standard pricing when leaving emergency
            self._pricing = StandardPricing()
            print(f"[ModeManager:{self._kiosk_id}] Pricing restored to StandardPricing.")

    def get_current_mode(self) -> str:
        return self._state.get_mode_name()

    # Delegated state behaviours
    def handle_purchase(self, product_id: str, qty: int) -> bool:
        return self._state.handle_purchase(self, product_id, qty)

    def handle_restock(self) -> bool:
        return self._state.handle_restock(self)

    def handle_diagnostics(self) -> dict:
        return self._state.handle_diagnostics(self)

    # Pricing management (PATTERN: Strategy)
    def switch_pricing_strategy(self, strategy: PricingStrategy) -> None:
        old = self._pricing.get_name()
        self._pricing = strategy
        print(f"[ModeManager:{self._kiosk_id}] Pricing: {old} → {strategy.get_name()}")

    def get_pricing_strategy(self) -> PricingStrategy:
        return self._pricing

    def get_pricing_context(self) -> PricingContext:
        return PricingContext(mode=self.get_current_mode().lower())
