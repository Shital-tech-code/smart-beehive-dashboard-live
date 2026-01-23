import os
import json
import base64
import gspread
from flask import Flask, jsonify, render_template
from flask_cors import CORS
from oauth2client.service_account import ServiceAccountCredentials

print("🐝 Starting Smart Beehive App...")

# ---------------- APP ----------------
app = Flask(__name__, template_folder="templates")
CORS(app)

# ---------------- AUTH ----------------
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

# Cloud (Render)
if "GOOGLE_SERVICE_ACCOUNT_B64" in os.environ:
    print("🔐 Using Render credentials")

    # ✅ FIX: DO NOT decode to UTF-8
    decoded_bytes = base64.b64decode(
        os.environ["GOOGLE_SERVICE_ACCOUNT_B64"]
    )

    service_account_info = json.loads(decoded_bytes)

# Local (Windows PC)
else:
    print("🔐 Using local service_account.json")

    with open("service_account.json", "r", encoding="utf-8") as f:
        service_account_info = json.load(f)

# ---------------- GOOGLE AUTH ----------------
creds = ServiceAccountCredentials.from_json_keyfile_dict(
    service_account_info, scope
)
client = gspread.authorize(creds)

# ---------------- GOOGLE SHEET ----------------
SHEET_ID = "1gjlu4F-iNqhjrT57mpU7vGQOgXtjMer6i2Z3dDRbrFo"
sheet = client.open_by_key(SHEET_ID).sheet1
print("✅ Google Sheet connected")

# ---------------- ROUTES ----------------
@app.route("/")
def dashboard():
    return render_template("index.html")

@app.route("/data")
def data():
    rows = sheet.get_all_values()

    if len(rows) < 2:
        return jsonify({"error": "No data found"})

    latest = rows[-1]

    return jsonify({
        "timestamp": latest[0],
        "hive_id": latest[1],
        "status": latest[2],
        "temperature": latest[3],
        "humidity": latest[4],
        "weight1": latest[5],
        "weight2": latest[6],
        "total_weight": latest[7],
        "latitude": latest[8],
        "longitude": latest[9]
    })

# ---------------- RUN ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
