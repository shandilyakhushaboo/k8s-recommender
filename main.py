from flask import Flask, request, jsonify
import vertexai
from vertexai.generative_models import GenerativeModel
import requests
import os

app = Flask(__name__)

# Init Vertex AI
gcp_project = os.environ.get("GCP_PROJECT")
vertexai.init(project=gcp_project, location="us-central1")
gemini = GenerativeModel("gemini-1.5-pro-002")

# Environment vars
NEW_RELIC_API_KEY = os.environ.get("NEW_RELIC_API_KEY")
NEW_RELIC_ACCOUNT_ID = os.environ.get("NEW_RELIC_ACCOUNT_ID")

def fetch_newrelic_usage(service_name):
    nrql = f"SELECT average(cpuPercent) as cpu, average(memoryUsedBytes) as memory FROM ProcessSample WHERE processDisplayName='{service_name}' SINCE 30 minutes ago"
    url = f"https://api.newrelic.com/v1/accounts/{NEW_RELIC_ACCOUNT_ID}/query?nrql={nrql}"
    headers = {
        "X-Api-Key": NEW_RELIC_API_KEY,
        "Content-Type": "application/json"
    }
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        raise Exception("New Relic query failed")
    data = resp.json()
    results = data.get("results", [{}])[0]
    return {
        "cpu": results.get("cpu", 150),
        "memory_mb": round(results.get("memory", 500_000_000) / (1024 * 1024), 2)
    }

def generate_recommendation(service_name, cpu, memory):
    prompt = f"""
    For the service '{service_name}', with average CPU usage of {cpu} millicores and memory usage of {memory} MB over the last 30 minutes,
    what Kubernetes resource requests and limits (in millicores and MiB) would you recommend for stable operation?
    Provide only the values.
    """
    response = gemini.generate_content(prompt)
    return response.text.strip()

@app.route("/recommend", methods=["POST"])
def recommend():
    data = request.get_json()
    service = data.get("service")
    if not service:
        return jsonify({"error": "Missing 'service' in request"}), 400

    try:
        usage = fetch_newrelic_usage(service)
        rec = generate_recommendation(service, usage["cpu"], usage["memory_mb"])
        return jsonify({
            "service": service,
            "cpu_usage": usage["cpu"],
            "memory_usage_mb": usage["memory_mb"],
            "recommended_settings": rec
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=8080)