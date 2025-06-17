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

    

    # NRQL query
    nrql = "SELECT count(*) FROM Transaction SINCE 5 minutes ago"
    url = "https://api.newrelic.com/graphql"
    headers = {
        "API-Key": NEW_RELIC_API_KEY,
        "Content-Type": "application/json"
    }
    query = {
        "query": f"""
        {{
          actor {{
            account(id: {NEW_RELIC_ACCOUNT_ID}) {{
              nrql(query: "{nrql}") {{
                results
              }}
            }}
          }}
        }}
        """
    }

      resp = requests.post(url, headers=headers, json=query)

    if resp.status_code == 200:
        data = resp.json()
        results = data.get("data", {}).get("actor", {}).get("account", {}).get("nrql", {}).get("results", [])
        logging.info(f"✅ NRQL Query Results: {results}")
        return jsonify({"message": "Successfully connected to New Relic", "results": results}), 200
    else:
        logging.error(f"❌ Failed to connect to New Relic: {resp.status_code} - {resp.text}")
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
