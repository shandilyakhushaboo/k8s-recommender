from flask import Flask, jsonify
import os
import requests
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

app = Flask(__name__)

# Load env vars
NEW_RELIC_API_KEY = os.environ.get("NEW_RELIC_API_KEY")
NEW_RELIC_ACCOUNT_ID = os.environ.get("NEW_RELIC_ACCOUNT_ID")

@app.route("/")
def hello():
    return "Hello, world from Cloud Run!", 200

@app.route("/check-newrelic")
def check_newrelic():
    if not NEW_RELIC_API_KEY or not NEW_RELIC_ACCOUNT_ID:
        logging.warning("❌ Missing API key or Account ID")
        return jsonify({"error": "Missing NEW_RELIC_API_KEY or NEW_RELIC_ACCOUNT_ID"}), 500
   
    logging.info("✅ API key & Account ID exists")

    

    nrql = "SELECT count(*) FROM Transaction SINCE 5 minutes ago"
    url = "https://insights-api.newrelic.com/v1/accounts/{}/query".format(NEW_RELIC_ACCOUNT_ID)
    headers = {
        "X-Query-Key": NEW_RELIC_API_KEY,
        "Accept": "application/json"
    }
    params = {
        "nrql": nrql
    }

    resp = requests.get(url, headers=headers, params=params)

    if resp.status_code == 200:
        return jsonify({"message": "Successfully connected to New Relic"}), 200
    else:
        return jsonify({
            "error": "Failed to connect to New Relic",
            "status_code": resp.status_code,
            "response": resp.text
        }), 500

@app.route("/healthz")
def health():
    return "ok", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
