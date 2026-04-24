from typing import Dict, Any

class CentralRegistry:
    """
    PATTERN: Singleton + Registry
    
    Section 3.3: Stores global system information such as 
    configuration and system status.
    """
    _instance = None
    _kiosks = {}
    _config = {
        "city_node": "ZEPHYRUS-CORE-01",
        "emergency_threshold": 0.8,
        "logging_level": "VERBOSE"
    }

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CentralRegistry, cls).__new__(cls)
        return cls._instance

    def register_kiosk(self, kiosk_id: str, kiosk_obj: Any):
        self._kiosks[kiosk_id] = kiosk_obj
        print(f"[Registry] Registered kiosk: {kiosk_id}")

    def get_kiosk(self, kiosk_id: str) -> Any:
        return self._kiosks.get(kiosk_id)

    def get_all_kiosks(self) -> Dict[str, Any]:
        return self._kiosks

    def update_config(self, key: str, value: Any):
        self._config[key] = value

    def get_config(self, key: str) -> Any:
        return self._config.get(key)
