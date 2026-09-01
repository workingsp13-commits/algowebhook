from flask import Flask, request, jsonify, render_template_string
import requests
import json
import os

app = Flask(__name__)

# =========================================================
# Client Accounts Configuration
# =========================================================
CLIENTS = [
    {
        "name": "Admin (Prasanth)",
        "client_id": "SKY62341_U",
        "password": "Good@123",
        "factor2": "10071998",
        "app_key": "brrHxkaGmkoALkDdbpiaHImbX3BIPx48d3LrdRqOgaLODopaapkoDjaMqNMpX4dX",
        "lots": 1
    }
]

# Sky Broking Endpoints
SKY_BASE_URL = "https://skypro.skybroking.com/NorenWClientTP"

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>1-Click Algo Master</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; background: #121212; color: white; text-align: center; padding: 20px; }
        .card { background: #1e1e1e; max-width: 480px; margin: auto; padding: 20px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.5); }
        input { width: 90%; padding: 12px; margin: 10px 0; border-radius: 6px; border: 1px solid #333; background: #2a2a2a; color: #fff; font-size: 16px; text-align: center; text-transform: uppercase; }
        button { width: 95%; padding: 15px; margin: 10px 0; border: none; border-radius: 8px; font-size: 18px; font-weight: bold; cursor: pointer; }
        .btn-buy-ce { background: #00c853; color: white; }
        .btn-exit { background: #ff9100; color: white; }
        #status { margin-top: 15px; font-size: 12px; font-weight: bold; color: #ffea00; text-align: left; background: #111; padding: 10px; border-radius: 6px; overflow-x: auto; white-space: pre-wrap; word-break: break-all; font-family: monospace; }
    </style>
</head>
<body>
    <div class="card">
        <h2>🚀 Algo 1-Click Master</h2>
        <label>Enter Strike Price Symbol:</label>
        <input type="text" id="symbol" placeholder="E.g: NIFTY01SEP26C24100">
        
        <button class="btn-buy-ce" onclick="sendOrder('B')">BUY ORDER</button>
        <hr style="border-color:#333;">
        <button class="btn-exit" onclick="sendOrder('S')">⚠️ SAFE EXIT ALL (SELL)</button>
        
        <div id="status">Status: Ready</div>
    </div>

    <script>
        async function sendOrder(action) {
            let symbolInput = document.getElementById('symbol').value.trim();
            if(!symbolInput) {
                alert("தயவுசெய்து Trading Symbol-ஐ டைப் செய்யவும்!");
                return;
            }
            
            document.getElementById('status').innerText = "Authenticating & Executing Order...";

            try {
                let response = await fetch('/manual-order', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ action: action, symbol: symbolInput.toUpperCase() })
                });

                let res = await response.json();
                document.getElementById('status').innerText = JSON.stringify(res, null, 2);
            } catch (err) {
                document.getElementById('status').innerText = "Network Error: " + err.message;
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_PAGE)

@app.route('/manual-order', methods=['POST'])
def manual_order():
    try:
        data = request.json
        action = data.get('action') # 'B' or 'S'
        symbol = data.get('symbol')
        
        results = []
        
        for client in CLIENTS:
            qty = client['lots'] * 50
            
            # Using Session to retain headers & cookies properly
            http_session = requests.Session()
            http_session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Content-Type': 'application/x-www-form-urlencoded'
            })

            # STEP 1: Authenticate and get Token via QuickLogin
            login_payload = {
                "uid": client['client_id'],
                "pwd": client['password'],
                "factor2": client['factor2'],
                "vc": client['client_id'],
                "appkey": client['app_key'],
                "imei": "abc1234",
                "source": "API"
            }
            
            login_data_str = f"jData={json.dumps(login_payload)}"
            login_url = f"{SKY_BASE_URL}/QuickAuth"
            
            login_resp = http_session.post(login_url, data=login_data_str, timeout=10)
            
            try:
                login_json = login_resp.json()
            except Exception:
                login_json = {}

            token = login_json.get('token') or client['app_key']

            # STEP 2: Place Order using the Authenticated Session Token
            order_payload = {
                "uid": client['client_id'],
                "actid": client['client_id'],
                "exch": "NFO",
                "tsym": symbol,
                "qty": str(qty),
                "prc": "0",
                "prd": "M",
                "trantype": action,
                "prctyp": "MKT",
                "ret": "DAY",
                "ordersource": "API"
            }
            
            order_data_str = f"jData={json.dumps(order_payload)}&jKey={token}"
            order_url = f"{SKY_BASE_URL}/PlaceOrder"
            
            order_resp = http_session.post(order_url, data=order_data_str, timeout=10)
            
            try:
                broker_res = order_resp.json()
            except Exception:
                broker_res = {
                    "http_status": order_resp.status_code,
                    "response_text": order_resp.text,
                    "login_attempt_response": login_json
                }
            
            results.append({
                "client": client['name'],
                "broker_response": broker_res
            })
            
        return jsonify({"status": "Completed", "details": results}), 200

    except Exception as e:
        return jsonify({"status": "Error", "message": str(e)}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
