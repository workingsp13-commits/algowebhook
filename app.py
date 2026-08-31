from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# =========================================================
# Sky Broking API விவரங்கள் (Image-ல் இருந்து எடுக்கப்பட்டது)
# =========================================================
CLIENT_ID = "SKY62341_U"
SECRET_CODE = "brrHxkaGmkoALkDdbpiaHImbX3BIPx48d3LrdRqOgaLODopaapkoDjaMqNMpX4dX"
REDIRECT_URL = "https://algowebhook.onrender.com/webhook"

SKY_API_ORDER_URL = "https://api.skybroking.com/v1/orders/place"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.json
        print("TradingView Signal பெறப்பட்டது:", data)
        
        action = data.get('action') # BUY அல்லது SELL
        symbol = data.get('symbol', 'NIFTY')
        
        # Sky Broking API Order Details
        order_payload = {
            "client_id": CLIENT_ID,
            "symbol": symbol,
            "transaction_type": action, # BUY / SELL
            "quantity": 50,             # 1 Lot Nifty = 50
            "order_type": "MARKET",
            "product": "MIS"            # Intraday
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {SECRET_CODE}"
        }
        
        # Sky Broking-க்கு Order Request அனுப்புதல்
        response = requests.post(SKY_API_ORDER_URL, json=order_payload, headers=headers)
        res_data = response.json()
        
        print("Broker Response:", res_data)
        return jsonify({"status": "success", "broker_response": res_data}), 200

    except Exception as e:
        print("Error:", str(e))
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
