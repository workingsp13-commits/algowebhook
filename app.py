from flask import Flask, request, jsonify, render_template_string
import requests
import json
import os

app = Flask(__name__)

# =========================================================
# Client Accounts List
# =========================================================
CLIENTS = [
    {
        "name": "Admin (Prasanth)",
        "client_id": "SKY62341_U",
        "secret_code": "brrHxkaGmkoALkDdbpiaHImbX3BIPx48d3LrdRqOgaLODopaapkoDjaMqNMpX4dX",
        "lots": 1
    }
]

# Sky Broking Official Quick Order Endpoint
SKY_ORDER_URL = "https://skypro.skybroking.com/NorenWClientTP/PlaceOrder"

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
        .btn-buy-pe { background: #d50000; color: white; }
        .btn-exit { background: #ff9100; color: white; }
        #status { margin-top: 15px; font-size: 12px; font-weight: bold; color: #ffea00; text-align: left; background: #111; padding: 10px; border-radius: 6px; overflow-x: auto; white-space: pre-wrap; word-break: break-all; font-family: monospace; }
    </style>
</head>
<body>
    <div class="card">
        <h2>🚀 Algo 1-Click Master</h2>
        <label>Enter Strike Price Symbol:</label>
        <input type="text" id="symbol" placeholder="E.g: NIFTY01SEP2624200PE">
        
        <button class="btn-buy-ce" onclick="sendOrder('BUY')">BUY CALL / PUT</button>
        <hr style="border-color:#333;">
        <button class="btn-exit" onclick="sendOrder('SELL')">⚠️ SAFE EXIT ALL (SQUARE OFF)</button>
        
        <div id="status">Status: Ready</div>
    </div>

    <script>
        async function sendOrder(action) {
            let symbolInput = document.getElementById('symbol').value.trim();
            if(!symbolInput) {
                alert("தயவுசெய்து Strike Price Symbol-ஐ டைப் செய்யவும்!");
                return;
            }
            
            document.getElementById('status').innerText = "Processing direct API order...";

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
        action = data.get('action')
        symbol = data.get('symbol')
        
        results = []
        for client in CLIENTS:
            qty = client['lots'] * 50
            
            # Exact Payload required by Noren Engine
            payload_data = {
                "uid": client['client_id'],
                "actid": client['client_id'],
                "exch": "NFO",
                "tsym": symbol,
                "qty": str(qty),
                "prc": "0",
                "prd": "M",
                "trantype": action,
                "prctyp": "MKT",
                "ret": "DAY"
            }
            
            body_data = f"jData={json.dumps(payload_data)}&jKey={client['secret_code']}"
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded'
            }
            
            try:
                resp = requests.post(SKY_ORDER_URL, data=body_data, headers=headers, timeout=12)
                
                # Safe Parsing to prevent JSONDecodeError crashes
                if resp.status_code == 200 and resp.text.strip():
                    try:
                        broker_res = resp.json()
                    except json.JSONDecodeError:
                        broker_res = {"status": "Failed", "raw_response": resp.text}
                else:
                    broker_res = {
                        "status_code": resp.status_code,
                        "response_text": resp.text if resp.text else "Empty response from Broker Server"
                    }
            except Exception as req_err:
                broker_res = {"error": str(req_err)}

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
