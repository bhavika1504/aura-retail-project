import random
import time
from abc import ABC, abstractmethod


class DispenserHardware(ABC):
    """
    Abstract dispenser interface.
    Business logic only depends on this contract —
    never on SpiralDispenser or RoboticArmDispenser directly.
    """

    @abstractmethod
    def dispense(self, product_id: str, qty: int) -> bool:
        """Attempt to physically dispense qty units. Returns True on success."""

    @abstractmethod
    def recalibrate(self) -> bool:
        """Run the hardware self-calibration routine. Returns True on success."""

    @abstractmethod
    def get_status(self) -> str:
        """Return a one-word status: "OK" | "FAULT" | "CALIBRATING"."""


class SpiralDispenser(DispenserHardware):
    """
    Spiral-coil vending mechanism.
    Simulates occasional jams (configurable failure_rate).
    """

    def __init__(self, failure_rate: float = 0.1) -> None:
        self._failure_rate = failure_rate
        self._calibrated: bool = True

    def dispense(self, product_id: str, qty: int) -> bool:
        if not self._calibrated:
            print("[SpiralDispenser] Cannot dispense — not calibrated.")
            return False
        # DISABLED RANDOM FAILURE FOR STABLE DEMO
        # if random.random() < self._failure_rate:
        #     self._calibrated = False
        #     print(f"[SpiralDispenser] Jam detected while dispensing {product_id}.")
        #     return False
        print(f"[SpiralDispenser] Dispensed {qty} x {product_id}")
        time.sleep(0.05)  
        return True

    def recalibrate(self) -> bool:
        print("[SpiralDispenser] Recalibrating coil motor…")
        time.sleep(0.05)
        self._calibrated = True
        print("[SpiralDispenser] Recalibration complete.")
        return True

    def get_status(self) -> str:
        return "OK" if self._calibrated else "FAULT"


class RoboticArmDispenser(DispenserHardware):
    """
    Robotic-arm dispenser — more precise, lower failure rate.
    Used in hospital / emergency kiosks that need careful handling.
    """

    def __init__(self, failure_rate: float = 0.05) -> None:
        self._failure_rate = failure_rate
        self._operational: bool = True

    def dispense(self, product_id: str, qty: int) -> bool:
        # DISABLED RANDOM FAILURE FOR STABLE DEMO
        # if random.random() < self._failure_rate:
        #     self._operational = False
        #     print(f"[RoboticArmDispenser] Arm fault — {product_id} not dispensed.")
        #     return False
        print(f"[RoboticArmDispenser] Arm dispensed {qty} x {product_id}")
        time.sleep(0.08)
        return True

    def recalibrate(self) -> bool:
        print("[RoboticArmDispenser] Running arm-calibration sequence…")
        time.sleep(0.05)
        self._operational = True
        print("[RoboticArmDispenser] Arm ready.")
        return True

    def get_status(self) -> str:
        return "OK" if self._operational else "FAULT"
