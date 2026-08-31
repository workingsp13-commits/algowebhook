from flask import Flask, request, jsonify, render_template_string
import requests
import os

app = Flask(__name__)

CLIENTS = [
    {
        "name": "Admin (Prasanth)",
        "client_id": "SKY62341_U",
        "secret_code": "brrHxkaGmkoALkDdbpiaHImbX3BIPx48d3LrdRqOgaLODopaapkoDjaMqNMpX4dX",
        "lots": 1
    }
]

# Sky Broking / GoPocket Noren API Endpoint
SKY_API_ORDER_URL = "https://skypro.skybroking.com/NorenWClientTP/QuickOrder"

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>1-Click Algo Master</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial, sans-serif; background: #121212; color: white; text-align: center; padding: 20px; }
        .card { background: #1e1e1e; max-width: 480px; margin: auto; padding: 20px; border-radius: 12px; box-shadow: 0 4px 10px rgba(0,0,0,0.5); }
        input { width: 90%; padding: 12px; margin: 10px 0; border-radius: 6px; border: 1px solid #333; background: #2a2a2a; color: #fff; font-size: 16px; text-align: center; }
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
        
        <button class="btn-buy-ce" onclick="sendOrder('BUY')">BUY CALL (CE)</button>
        <button class="btn-buy-pe" onclick="sendOrder('BUY')">BUY PUT (PE)</button>
        <hr style="border-color:#333;">
        <button class="btn-exit" onclick="sendOrder('SELL')">⚠️ SAFE EXIT ALL (SQUARE OFF)</button>
        
        <div id="status">Status: Waiting for action...</div>
    </div>

    <script>
        async function sendOrder(action) {
            let symbolInput = document.getElementById('symbol').value.trim();
            if(!symbolInput) {
                alert("தயவுசெய்து Strike Price Symbol-ஐ டைப் செய்யவும்!");
                return;
            }
            
            document.getElementById('status').innerText = "Processing request...";

            try {
                let response = await fetch('/manual-order', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ action: action, symbol: symbolInput })
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
            
            order_payload = {
                "uid": client['client_id'],
                "actid": client['client_id'],
                "exch": "NFO",
                "tsym": symbol,
                "qty": str(qty),
                "prc": "0",
                "prd": "M",
                "trantype": "B" if action == "BUY" else "S",
                "prctyp": "MKT",
                "ret": "DAY"
            }
            
            headers = {
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            try:
                # Transmit as form payload for SkyBroking Noren server
                response = requests.post(SKY_API_ORDER_URL, data=f"jData={jsonify(order_payload).get_data(as_text=True)}&jKey={client['secret_code']}", headers=headers, timeout=10)
                
                try:
                    res_data = response.json()
                except Exception:
                    res_data = {
                        "http_code": response.status_code,
                        "raw_body": response.text[:200] if response.text else "Empty Response"
                    }
            except Exception as req_err:
                res_data = {"error_details": str(req_err)}

            results.append({
                "client": client['name'],
                "response": res_data
            })
            
        return jsonify({"status": "Executed", "data": results}), 200

    except Exception as e:
        return jsonify({"status": "Error", "message": str(e)}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
