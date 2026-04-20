from typing import Any, Dict, Optional
from hardware.dispenser_hardware import DispenserHardware, SpiralDispenser
from hardware.optional_modules import HardwareModule
from hardware.payment_processor import PaymentProcessor
from hardware.failure_chain import RetryHandler, RecalibrationHandler, TechnicianAlertHandler


class HardwareManager:
    """
    Coordinates hardware subsystems.  Subsystems communicate
    with hardware only through here — never directly.
    """

    def __init__(self) -> None:
        self._dispenser: DispenserHardware = SpiralDispenser()
        self._payment: Optional[PaymentProcessor] = None
        self._modules: Dict[str, HardwareModule] = {}
        self._failure_chain = self._build_failure_chain()
        
    @staticmethod
    def _build_failure_chain() -> RetryHandler:
        """
        PATTERN: Chain of Responsibility
        RetryHandler → RecalibrationHandler → TechnicianAlertHandler
        """
        retry = RetryHandler()
        recal = RecalibrationHandler()
        tech  = TechnicianAlertHandler()
        retry.set_next(recal).set_next(tech)
        return retry

    # ----------------------------------------------------------
    # Dispenser management
    # ----------------------------------------------------------
    def set_dispenser(self, dispenser: DispenserHardware) -> None:
        """Hot-swap the dispenser at runtime (Path B constraint)."""
        old = type(self._dispenser).__name__
        self._dispenser = dispenser
        print(f"[HardwareManager] Dispenser swapped: {old} → {type(dispenser).__name__}")

    def dispense_product(self, product_id: str, qty: int) -> bool:
        """
        Attempt to dispense; on failure invoke the Chain of Responsibility.
        """
        success = self._dispenser.dispense(product_id, qty)
        if not success:
            failure: Dict[str, Any] = {
                "component": type(self._dispenser).__name__,
                "hardware_ref": self._dispenser,
                "product_id": product_id,
                "retry_count": 0,
                "error": "Dispense operation failed",
            }
            success = self._failure_chain.handle_failure(failure)
        return success

    # ----------------------------------------------------------
    # Payment
    # ----------------------------------------------------------
    def set_payment_processor(self, processor: PaymentProcessor) -> None:
        self._payment = processor
        print(f"[HardwareManager] Payment provider set: {processor.get_provider_name()}")

    def process_payment(self, amount: float, reference: str) -> bool:
        if self._payment is None:
            raise RuntimeError("[HardwareManager] No payment processor configured.")
        return self._payment.charge(amount, reference)

    def process_refund(self, amount: float, reference: str) -> bool:
        if self._payment is None:
            return False
        return self._payment.refund(amount, reference)

    # ----------------------------------------------------------
    # Optional modules (dynamic attach / detach)
    # ----------------------------------------------------------
    def attach_module(self, name: str, module: HardwareModule) -> bool:
        """Dynamically attach an optional hardware module."""
        if module.initialize():
            self._modules[name] = module
            print(f"[HardwareManager] Module attached: '{name}'")
            return True
        return False

    def detach_module(self, name: str) -> None:
        if name in self._modules:
            self._modules[name].shutdown()
            del self._modules[name]
            print(f"[HardwareManager] Module detached: '{name}'")

    def is_module_available(self, name: str) -> bool:
        return name in self._modules

    def get_module(self, name: str) -> Optional[HardwareModule]:
        return self._modules.get(name)

    # ----------------------------------------------------------
    # Diagnostics
    # ----------------------------------------------------------
    def get_hardware_report(self) -> Dict[str, Any]:
        return {
            "dispenser_type": type(self._dispenser).__name__,
            "dispenser_status": self._dispenser.get_status(),
            "payment_provider": (self._payment.get_provider_name()
                                 if self._payment else "None"),
            "modules": {name: m.get_status() for name, m in self._modules.items()},
        }

