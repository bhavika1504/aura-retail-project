
import csv
import json
import os
from datetime import datetime
from typing import Any, Dict, List


class PersistenceManager:
  

    def __init__(self, data_dir: str = "data") -> None:
        self._data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)

   
    # Inventory  (JSON)
    def save_inventory(self, kiosk_id: str, products: Dict[str, Any]) -> None:
        path = self._path(f"inventory_{kiosk_id}.json")
        data = {pid: p.to_dict() for pid, p in products.items()}
        with open(path, "w") as fh:
            json.dump(data, fh, indent=2)
        print(f"[Persistence] Inventory saved → {path}")

    def load_inventory(self, kiosk_id: str) -> Dict[str, Any]:
        path = self._path(f"inventory_{kiosk_id}.json")
        if not os.path.exists(path):
            return {}
        with open(path) as fh:
            return json.load(fh)

 
    # Transaction log  (CSV — append only)

    def log_transaction(self, record: Dict[str, Any]) -> None:
        path = self._path("transactions.csv")
        file_exists = os.path.exists(path)
        with open(path, "a", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(record.keys()))
            if not file_exists:
                writer.writeheader()
            writer.writerow(record)

    def load_transactions(self) -> List[Dict[str, Any]]:
        path = self._path("transactions.csv")
        if not os.path.exists(path):
            return []
        with open(path) as fh:
            return list(csv.DictReader(fh))

   
    # System config  (JSON)
    
    def save_config(self, config: Dict[str, Any]) -> None:
        path = self._path("config.json")
        with open(path, "w") as fh:
            json.dump(config, fh, indent=2)

    def load_config(self) -> Dict[str, Any]:
        path = self._path("config.json")
        if not os.path.exists(path):
            return {}
        with open(path) as fh:
            return json.load(fh)

  
    # Internal helper
    
    def _path(self, filename: str) -> str:
        return os.path.join(self._data_dir, filename)
