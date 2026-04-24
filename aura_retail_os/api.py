import os
import sys
import uuid
from datetime import datetime

# Add the project root to sys.path so imports work correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify
from flask_cors import CORS

from core.kiosk_factory import PharmacyKioskFactory, FoodKioskFactory, EmergencyKioskFactory
from interface.kiosk_interface import KioskInterface
from registry.central_registry import CentralRegistry

app = Flask(__name__)
CORS(app)

# Initialize all three kiosk types as per spec 3.4
pharmacy_factory = PharmacyKioskFactory()
food_factory = FoodKioskFactory()
emergency_factory = EmergencyKioskFactory()

kiosks = {
    "PHARM-001": pharmacy_factory.create_kiosk("PHARM-001", "City Hospital"),
    "FOOD-002": food_factory.create_kiosk("FOOD-002", "Metro Station"),
    "EMERG-003": emergency_factory.create_kiosk("EMERG-003", "Relief Camp Sector 7")
}

# Default active kiosk
active_kiosk_id = "PHARM-001"

def get_active_kiosk():
    return kiosks[active_kiosk_id]

def get_active_interface():
    return KioskInterface(get_active_kiosk())

@app.route("/api/kiosks", methods=["GET"])
def list_kiosks():
    return jsonify([
        {"id": k.kiosk_id, "type": k.get_kiosk_type(), "location": k.location}
        for k in kiosks.values()
    ])

@app.route("/api/kiosk/select", methods=["POST"])
def select_kiosk():
    global active_kiosk_id
    data = request.json
    kid = data.get("id")
    if kid in kiosks:
        active_kiosk_id = kid
        return jsonify({"status": "success", "active_id": active_kiosk_id})
    return jsonify({"error": "Kiosk not found"}), 404

@app.route("/api/state", methods=["GET"])
def get_state():
    kiosk = get_active_kiosk()
    interface = KioskInterface(kiosk)
    status = interface.run_diagnostics()
    history = interface.get_transaction_history()
    
    txns = []
    for t in history:
        txns.append({
            "id": str(uuid.uuid4())[:8],
            "type": "purchase" if "Purchase" in t else ("restock" if "Restock" in t else "refund"),
            "amount": 0.0,
            "desc": t,
            "time": datetime.now().strftime("%H:%M:%S")
        })

    mode_name = kiosk.mode_manager.get_current_mode()
    mode_map = {
        "ACTIVE": "active",
        "MAINTENANCE": "maintenance",
        "EMERGENCY": "emergency",
        "POWER_SAVING": "power_saving"
    }
    mode_key = mode_map.get(mode_name, "active")

    strat_key = "standard"
    if mode_key == "emergency":
        strat_key = "emergency"

    return jsonify({
        "id": kiosk.kiosk_id,
        "type": kiosk.get_kiosk_type(),
        "location": kiosk.location,
        "status": status,
        "txns": txns,
        "mode": mode_key,
        "strat": strat_key,
        "events": [],
        "mems": []
    })

@app.route("/api/inventory", methods=["GET"])
def get_inventory():
    kiosk = get_active_kiosk()
    interface = KioskInterface(kiosk)
    prods = []
    for pid, product in kiosk.inventory.all_products().items():
        info = interface.get_stock_info(pid)
        if "error" not in info:
            prods.append({
                "id": info["product_id"],
                "nm": info["name"],
                "cat": product.category,
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
    get_active_interface().set_operating_mode(mode)
    return jsonify({"status": "success", "mode": mode})


@app.route("/api/purchase", methods=["POST"])
def purchase():
    data = request.json
    pid = data.get("pid")
    qty = data.get("qty", 1)
    uid = data.get("uid", "USER001")
    
    success = get_active_interface().purchase_item(pid, qty, uid)
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
    
    success = get_active_interface().refund_transaction(tid, float(amount), pid, int(qty))
    if success:
        return jsonify({"status": "success"})
    return jsonify({"error": "Refund failed"}), 400


@app.route("/api/restock", methods=["POST"])
def restock():
    data = request.json
    pid = data.get("pid")
    qty = data.get("qty", 1)
    
    success = get_active_interface().restock_inventory(pid, int(qty))
    if success:
        return jsonify({"status": "success"})
    return jsonify({"error": "Restock failed"}), 400

@app.route("/api/undo", methods=["POST"])
def undo():
    success = get_active_interface().undo_last_command()
    if success:
        return jsonify({"status": "success"})
    return jsonify({"error": "Undo failed"}), 400

if __name__ == "__main__":
    print("\n[FLASK] Starting Aura Kiosk REST API...")
    app.run(port=5000, debug=True)
