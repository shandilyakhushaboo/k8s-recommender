from flask import Flask, jsonify
import os
import requests

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
        return jsonify({"error": "Missing NEW_RELIC_API_KEY or NEW_RELIC_ACCOUNT_ID"}), 500

    # Dummy NRQL query to verify API access
    nrql = "SELECT count(*) FROM Transaction SINCE 1 minute ago"
    url = f"https://api.newrelic.com/v1/accounts/{NEW_RELIC_ACCOUNT_ID}/query?nrql={nrql}"
    headers = {
        "X-Api-Key": NEW_RELIC_API_KEY,
        "Content-Type": "application/json"
    }

    resp = requests.get(url, headers=headers)

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
