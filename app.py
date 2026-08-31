from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.json
        print("TradingView Signal வந்தாச்சு:", data)
        
        # Signal வந்தவுடன் என்ன செய்ய வேண்டும் என்ற விவரம்
        action = data.get('action')  # BUY அல்லது SELL
        symbol = data.get('symbol')  # NIFTY
        
        # ---------------------------------------------------
        # இங்கே உங்கள் Sky Broking API Order Code இயங்கும்
        # ---------------------------------------------------
        
        return jsonify({"status": "success", "message": f"{symbol} - {action} Signal received!"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
