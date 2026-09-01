from flask import Flask, request, jsonify, render_template_string
import os
from NorenRestApiPy.NorenApi import NorenApi

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
        "vc": "SKY62341_U_VC",
        "app_key": "brrHxkaGmkoALkDdbpiaHImbX3BIPx48d3LrdRqOgaLODopaapkoDjaMqNMpX4dX",
        "imei": "abc1234",
        "lots": 1
    }
]

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
            
            document.getElementById('status').innerText = "Logging in & Executing Order...";

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
            
            # API Initialization using exact host path required by Sky Broking
            api = NorenApi(
                host='https://skypro.skybroking.com/NorenWClientTP',
                websocket='wss://skypro.skybroking.com/NorenWClientTPWS/'
            )
            
            login_res = None
            try:
                # Proper Noren API login
                login_res = api.login(
                    userid=client['client_id'],
                    password=client['password'],
                    twoFA=client['factor2'],
                    vendor_code=client['vc'],
                    api_secret=client['app_key'],
                    imei=client['imei']
                )
            except Exception as log_err:
                login_res = {"stat": "Not_Ok", "emsg": str(log_err)}

            # If login succeeded
            if login_res and isinstance(login_res, dict) and login_res.get('stat') == 'Ok':
                try:
                    order_res = api.place_order(
                        buy_or_sell=action,
                        product_type='M', 
                        exchange='NFO',
                        tradingsymbol=symbol,
                        quantity=qty,
                        discloseqty=0,
                        price_type='MKT',
                        price=0,
                        trigger_price=None,
                        retention='DAY',
                        remarks='AlgoOrder'
                    )
                except Exception as ord_err:
                    order_res = {"stat": "Not_Ok", "emsg": str(ord_err)}

                results.append({
                    "client": client['name'],
                    "login_status": "Success",
                    "broker_response": order_res
                })
            else:
                results.append({
                    "client": client['name'],
                    "login_status": "Failed",
                    "broker_response": login_res
                })
            
        return jsonify({"status": "Completed", "details": results}), 200

    except Exception as e:
        return jsonify({"status": "Error", "message": str(e)}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
