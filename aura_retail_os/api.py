import os
import sys
import uuid
from datetime import datetime

# Add the project root to sys.path so imports work correctly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

from core.kiosk_factory import PharmacyKioskFactory, FoodKioskFactory, EmergencyKioskFactory
from interface.kiosk_interface import KioskInterface
from registry.central_registry import CentralRegistry

app = Flask(__name__)
CORS(app, origins=["*"])

# Serve frontend static files
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'frontend')

@app.route('/')
def serve_frontend():
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/src/<path:path>')
def serve_src(path):
    return send_from_directory(os.path.join(FRONTEND_DIR, 'src'), path)

@app.route('/<path:path>')
def serve_static(path):
    try:
        return send_from_directory(FRONTEND_DIR, path)
    except:
        return send_from_directory(FRONTEND_DIR, 'index.html')

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
    try:
        kiosk = get_active_kiosk()
        interface = KioskInterface(kiosk)
        status = interface.run_diagnostics()
        history = interface.get_transaction_history()
        
        txns = []
        for t in history:
            # Extract amount from description string like "... @ rs.20.00"
            amt = 0.0
            if "@ rs." in t:
                try:
                    amt = float(t.split("@ rs.")[-1].split()[0])
                except:
                    pass
            
            txns.append({
                "id": str(uuid.uuid4())[:8],
                "type": "purchase" if "Purchase" in t else ("restock" if "Restock" in t else "refund"),
                "amount": amt,
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

        # Dynamically determine the strategy key from the actual strategy object
        current_strat_name = kiosk.mode_manager.get_pricing_strategy().get_name()
        if "Discount" in current_strat_name:
            strat_key = "discount"
        elif "Emergency" in current_strat_name:
            strat_key = "emergency"
        else:
            strat_key = "standard"

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
    except Exception as e:
        print(f"[ERROR] /api/state: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/inventory", methods=["GET"])
def get_inventory():
    try:
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
    except Exception as e:
        print(f"[ERROR] /api/inventory: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/mode", methods=["POST"])
def set_mode():
    try:
        data = request.json
        mode = data.get("mode")
        print(f"[API] Setting mode to '{mode}' for kiosk '{active_kiosk_id}'")
        get_active_interface().set_operating_mode(mode)
        return jsonify({"status": "success", "mode": mode})
    except Exception as e:
        print(f"[ERROR] /api/mode: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/strategy", methods=["POST"])
def set_strategy():
    try:
        from inventory.pricing_strategies import StandardPricing, DiscountPricing, EmergencyPricing
        data = request.json
        strat_key = data.get("strat")
        kiosk = get_active_kiosk()
        
        strat_map = {
            "standard": StandardPricing(),
            "discount": DiscountPricing(discount_rate=0.20), # Match frontend 20%
            "emergency": EmergencyPricing()
        }
        
        if strat_key in strat_map:
            kiosk.mode_manager.switch_pricing_strategy(strat_map[strat_key])
            print(f"[API] Strategy changed to '{strat_key}' for kiosk '{active_kiosk_id}'")
            return jsonify({"status": "success", "strat": strat_key})
        return jsonify({"error": "Unknown strategy"}), 400
    except Exception as e:
        print(f"[ERROR] /api/strategy: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/purchase", methods=["POST"])
def purchase():
    try:
        data = request.json
        pid = data.get("pid")
        qty = int(data.get("qty", 1))
        uid = data.get("uid", "USER001")
        
        print(f"[API] Purchase request: {qty}x {pid} for user {uid}")
        success = get_active_interface().purchase_item(pid, qty, uid)
        
        if success:
            print(f"[API] Purchase SUCCESS: {pid}")
            return jsonify({"status": "success"})
        
        print(f"[API] Purchase FAILED: {pid} (rejected by business logic or hardware)")
        return jsonify({"error": "Purchase failed or denied by constraints"}), 400
    except Exception as e:
        print(f"[ERROR] /api/purchase: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/refund", methods=["POST"])
def refund():
    try:
        data = request.json
        tid = data.get("tid", "SYS-TID")
        amount = float(data.get("amount", 0.0))
        pid = data.get("pid")
        qty = int(data.get("qty", 1))
        
        success = get_active_interface().refund_transaction(tid, amount, pid, qty)
        if success:
            return jsonify({"status": "success"})
        return jsonify({"error": "Refund failed"}), 400
    except Exception as e:
        print(f"[ERROR] /api/refund: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/restock", methods=["POST"])
def restock():
    try:
        data = request.json
        pid = data.get("pid")
        qty = int(data.get("qty", 1))
        
        success = get_active_interface().restock_inventory(pid, qty)
        if success:
            return jsonify({"status": "success"})
        return jsonify({"error": "Restock failed"}), 400
    except Exception as e:
        print(f"[ERROR] /api/restock: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/undo", methods=["POST"])
def undo():
    try:
        success = get_active_interface().undo_last_command()
        if success:
            return jsonify({"status": "success"})
        return jsonify({"error": "Undo failed"}), 400
    except Exception as e:
        print(f"[ERROR] /api/undo: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n[FLASK] starting Aura Kiosk REST API on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=False)
