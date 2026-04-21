from abc import ABC, abstractmethod
from typing import Any, Dict


class HardwareModule(ABC):
    """
    HardwareManager stores these by name and queries them through
    this interface — it never imports the concrete classes.
    """

    @abstractmethod
    def initialize(self) -> bool:
        """power-on sequence. Returns True on success."""

    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Return a status dict for monitoring."""

    @abstractmethod
    def shutdown(self) -> None:
        """Graceful power-off."""


class RefrigerationUnit(HardwareModule):
    """
    FoodKiosk checks is_functional() before allowing sale
    of any Product with requires_refrigeration = True.
    """

    def __init__(self, target_temp: float = 4.0) -> None:
        self._target_temp = target_temp
        self._current_temp: float = target_temp
        self._active: bool = False

    def initialize(self) -> bool:
        self._active = True
        self._current_temp = self._target_temp
        print(f"[RefrigerationUnit] Initialized at {self._target_temp} °C")
        return True

    def is_functional(self) -> bool:
        """True when running and temperature within 2 °C of target."""
        return self._active and abs(self._current_temp - self._target_temp) < 2.0

    def simulate_fault(self) -> None:
        """For simulation: raise temperature to trigger fault."""
        self._current_temp = self._target_temp + 10
        print("[RefrigerationUnit] Fault: temperature out of range!")

    def get_status(self) -> Dict[str, Any]:
        return {
            "module": "RefrigerationUnit",
            "active": self._active,
            "target_temp_c": self._target_temp,
            "current_temp_c": self._current_temp,
            "functional": self.is_functional(),
        }

    def shutdown(self) -> None:
        self._active = False
        print("[RefrigerationUnit] Shutdown.")


class SolarPowerMonitor(HardwareModule):
    """
    Emergency kiosks in disaster zones use solar — this module
    tracks output wattage and can trigger power-saving mode.
    """

    def __init__(self) -> None:
        self._active: bool = False
        self._output_watts: float = 0.0

    def initialize(self) -> bool:
        self._active = True
        self._output_watts = 150.0
        print(f"[SolarPowerMonitor] Initialized. Output: {self._output_watts} W")
        return True

    def get_output_watts(self) -> float:
        return self._output_watts if self._active else 0.0

    def get_status(self) -> Dict[str, Any]:
        return {
            "module": "SolarPowerMonitor",
            "active": self._active,
            "output_watts": self._output_watts,
        }

    def shutdown(self) -> None:
        self._active = False
        print("[SolarPowerMonitor] Shutdown.")
