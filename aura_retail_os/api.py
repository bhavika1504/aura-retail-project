import os
import sys
import uuid
from datetime import datetime

# Add the project root to sys.path so imports work correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify
from flask_cors import CORS

from core.kiosk_factory import PharmacyKioskFactory
from interface.kiosk_interface import KioskInterface
from registry.central_registry import CentralRegistry

app = Flask(__name__)
CORS(app)

# Initialize the system exactly like main.py
factory = PharmacyKioskFactory()
kiosk = factory.create_kiosk("PHARM-001", "City Hospital")
registry = CentralRegistry()
registry.register_kiosk("PHARM-001", kiosk)
interface = KioskInterface(kiosk)

@app.route("/api/state", methods=["GET"])
def get_state():
    status = interface.run_diagnostics()
    history = interface.get_transaction_history()
    
    # Map raw history strings into frontend txn objects
    txns = []
    for t in history:
        txns.append({
            "id": str(uuid.uuid4())[:8],
            "type": "purchase" if "Purchase" in t else ("restock" if "Restock" in t else "refund"),
            "amount": 0.0,  # Could parse it if needed
            "desc": t,
            "time": datetime.now().strftime("%H:%M:%S")
        })

    # Try to map Python state class to frontend mode key
    mode_name = kiosk.mode_manager.get_current_mode()
    mode_map = {
        "ACTIVE": "active",
        "MAINTENANCE": "maintenance",
        "EMERGENCY": "emergency",
        "POWER_SAVING": "power_saving"
    }
    mode_key = mode_map.get(mode_name, "active")

    # The PricingStrategy in python does not perfectly map to the React hardcoded ones unless we infer it by name
    strat_key = "standard"
    if mode_key == "emergency":
        strat_key = "emergency"

    return jsonify({
        "status": status,
        "txns": txns,
        "mode": mode_key,
        "strat": strat_key,
        "events": [], # EventBus doesn't natively cache across requests in this design without a hook
        "mems": []    # Memento caretaker has backups, but we don't expose them directly in the Facade yet
    })

@app.route("/api/inventory", methods=["GET"])
def get_inventory():
    prods = []
    for pid, product in kiosk.inventory.all_products().items():
        info = interface.get_stock_info(pid)
        if "error" not in info:
            prods.append({
                "id": info["product_id"],
                "nm": info["name"],
                "cat": product.category,  # Map to React's 'cat'
                "qty": product.quantity,
                "res": info["reserved"],
                "hw": info["hw_faulted"],
                "price": info["base_price"],
                "max": 100
            })
    return jsonify(prods)


@app.route("/api/mode", methods=["POST"])
def set_mode():
    data = request.json
    mode = data.get("mode")
    interface.set_operating_mode(mode)
    return jsonify({"status": "success", "mode": mode})


@app.route("/api/purchase", methods=["POST"])
def purchase():
    data = request.json
    pid = data.get("pid")
    qty = data.get("qty", 1)
    uid = data.get("uid", "USER001")
    
    success = interface.purchase_item(pid, qty, uid)
    if success:
        return jsonify({"status": "success"})
    return jsonify({"error": "Purchase failed or denied by constraints"}), 400


@app.route("/api/refund", methods=["POST"])
def refund():
    data = request.json
    tid = data.get("tid", "SYS-TID")
    amount = data.get("amount", 0.0)
    pid = data.get("pid")
    qty = data.get("qty", 1)
    
    success = interface.refund_transaction(tid, float(amount), pid, int(qty))
    if success:
        return jsonify({"status": "success"})
    return jsonify({"error": "Refund failed"}), 400


@app.route("/api/restock", methods=["POST"])
def restock():
    data = request.json
    pid = data.get("pid")
    qty = data.get("qty", 1)
    
    success = interface.restock_inventory(pid, int(qty))
    if success:
        return jsonify({"status": "success"})
    return jsonify({"error": "Restock failed"}), 400

if __name__ == "__main__":
    print("\n[FLASK] Starting Aura Kiosk REST API...")
    app.run(port=5000, debug=True)
