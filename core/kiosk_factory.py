# =============================================================
# core/kiosk_factory.py  — Devam Tanna (202512010)
# PATTERN: Abstract Factory
#
# Problem: Each kiosk type requires a DIFFERENT compatible set of:
#   Dispenser, PaymentProcessor, Inventory seed, Optional Modules,
#   and initial KioskState.
#
# Solution: One abstract factory per kiosk type.
#   KioskFactory         — abstract base
#   PharmacyKioskFactory — creates pharmacy-specific setup
#   FoodKioskFactory     — creates food-kiosk-specific setup
#   EmergencyKioskFactory— creates emergency-kiosk setup
#
# Each factory also registers the new kiosk in CentralRegistry.
# =============================================================
from abc import ABC, abstractmethod

from inventory.inventory import Inventory
from inventory.product import Product
from inventory.persistence_manager import PersistenceManager
from hardware.hardware_manager import HardwareManager
from hardware.dispenser_hardware import SpiralDispenser, RoboticArmDispenser
from hardware.payment_processor import CardPaymentAdapter, UPIAdapter, WalletAdapter
from hardware.optional_modules import RefrigerationUnit, SolarPowerMonitor
from core.kiosk_mode_manager import KioskModeManager
from core.kiosk_states import EmergencyState
from core.kiosk_types import PharmacyKiosk, FoodKiosk, EmergencyReliefKiosk
from transaction.command_invoker import CommandInvoker
from transaction.transaction_memento import TransactionCaretaker
from registry.central_registry import CentralRegistry


# =============================================================
# ABSTRACT FACTORY
# =============================================================

class KioskFactory(ABC):
    """
    PATTERN: Abstract Factory — base

    Subclasses implement create_kiosk() and return a fully
    wired AuraKiosk with compatible components.
    """

    @abstractmethod
    def create_kiosk(self, kiosk_id: str, location: str): ...

    # ----------------------------------------------------------
    # Shared wiring helper (used by all factories)
    # ----------------------------------------------------------
    @staticmethod
    def _make_base(kiosk_id: str):
        """
        Build the subsystems shared by every kiosk type.
        Returns (inventory, hardware, mode_manager, invoker, caretaker).
        """
        inventory     = Inventory(kiosk_id)
        hardware      = HardwareManager()
        mode_manager  = KioskModeManager(kiosk_id)
        pm            = PersistenceManager()
        invoker       = CommandInvoker(pm)
        caretaker     = TransactionCaretaker()
        return inventory, hardware, mode_manager, invoker, caretaker


# =============================================================
# CONCRETE FACTORIES
# =============================================================

class PharmacyKioskFactory(KioskFactory):
    """
    PATTERN: Abstract Factory — Pharmacy product

    Compatible component set
    ------------------------
    Dispenser     : RoboticArmDispenser (precise, low failure rate)
    Payment       : CardPaymentAdapter  (hospital billing)
    Modules       : none by default
    Seed products : OTC + prescription medicines
    Initial mode  : ACTIVE
    """

    def create_kiosk(self, kiosk_id: str, location: str) -> PharmacyKiosk:
        inv, hw, mode, invoker, caretaker = self._make_base(kiosk_id)

        # Compatible dispenser + payment for pharmacy
        hw.set_dispenser(RoboticArmDispenser(failure_rate=0.05))
        hw.set_payment_processor(CardPaymentAdapter())

        # Seed catalogue
        inv.add_product(Product(
            "MED001", "Paracetamol 500mg", base_price=15.0, quantity=50,
            category="otc", is_essential=True,
        ))
        inv.add_product(Product(
            "MED002", "Amoxicillin 250mg", base_price=85.0, quantity=20,
            category="prescription",
        ))
        inv.add_product(Product(
            "MED003", "Insulin Vial 10ml", base_price=320.0, quantity=10,
            category="controlled_substance", requires_refrigeration=True,
        ))

        kiosk = PharmacyKiosk(kiosk_id, location, inv, hw, mode, invoker, caretaker)
        CentralRegistry().register_kiosk(kiosk_id, kiosk)
        return kiosk


# =============================================================

class FoodKioskFactory(KioskFactory):
    """
    PATTERN: Abstract Factory — Food product

    Compatible component set
    ------------------------
    Dispenser     : SpiralDispenser     (standard coil mechanism)
    Payment       : UPIAdapter          (metro tap-to-pay)
    Modules       : RefrigerationUnit   (cold drinks, dairy)
    Seed products : snacks, beverages, cold items
    Initial mode  : ACTIVE
    """

    def create_kiosk(self, kiosk_id: str, location: str) -> FoodKiosk:
        inv, hw, mode, invoker, caretaker = self._make_base(kiosk_id)

        hw.set_dispenser(SpiralDispenser(failure_rate=0.1))
        hw.set_payment_processor(UPIAdapter())
        hw.attach_module("refrigeration", RefrigerationUnit(target_temp=4.0))

        inv.add_product(Product(
            "FOOD001", "Sandwich", base_price=45.0, quantity=30, is_essential=True,
        ))
        inv.add_product(Product(
            "FOOD002", "Cold Coffee", base_price=60.0, quantity=20,
            requires_refrigeration=True,
        ))
        inv.add_product(Product(
            "FOOD003", "Water Bottle 1L", base_price=20.0, quantity=100,
            is_essential=True,
        ))
        inv.add_product(Product(
            "FOOD004", "Milk 200ml", base_price=18.0, quantity=40,
            requires_refrigeration=True, is_essential=True,
        ))

        kiosk = FoodKiosk(kiosk_id, location, inv, hw, mode, invoker, caretaker)
        CentralRegistry().register_kiosk(kiosk_id, kiosk)
        return kiosk


# =============================================================

class EmergencyKioskFactory(KioskFactory):
    """
    PATTERN: Abstract Factory — Emergency Relief product

    Compatible component set
    ------------------------
    Dispenser     : RoboticArmDispenser (reliable in field)
    Payment       : UPIAdapter + WalletAdapter (offline-capable)
    Modules       : SolarPowerMonitor  (disaster-zone power)
    Seed products : water, food kits, first-aid
    Initial mode  : EMERGENCY (pre-activated)
    """

    def create_kiosk(self, kiosk_id: str, location: str) -> EmergencyReliefKiosk:
        inv, hw, mode, invoker, caretaker = self._make_base(kiosk_id)

        hw.set_dispenser(RoboticArmDispenser(failure_rate=0.05))
        hw.set_payment_processor(UPIAdapter())
        hw.attach_module("solar", SolarPowerMonitor())

        # Start in emergency lockdown immediately
        mode.set_state(EmergencyState())

        inv.add_product(Product(
            "EM001", "Water Bottle 500ml", base_price=10.0, quantity=200,
            is_essential=True,
        ))
        inv.add_product(Product(
            "EM002", "Emergency Food Kit", base_price=150.0, quantity=50,
            is_essential=True,
        ))
        inv.add_product(Product(
            "EM003", "First Aid Kit", base_price=200.0, quantity=30,
            is_essential=True,
        ))
        inv.add_product(Product(
            "EM004", "Thermal Blanket", base_price=120.0, quantity=40,
            is_essential=True,
        ))

        kiosk = EmergencyReliefKiosk(kiosk_id, location, inv, hw, mode, invoker, caretaker)
        CentralRegistry().register_kiosk(kiosk_id, kiosk)
        return kiosk
