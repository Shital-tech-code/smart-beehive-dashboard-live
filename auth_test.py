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

if "GOOGLE_SERVICE_ACCOUNT_B64" in os.environ:
    print("🔐 Using Render credentials")
    decoded_bytes = base64.b64decode(os.environ["GOOGLE_SERVICE_ACCOUNT_B64"])
    service_account_info = json.loads(decoded_bytes.decode("utf-8"))
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

# ---------------- HELPERS ----------------
def safe_float(val):
    try:
        return float(val)
    except:
        return 0.0

# ---------------- ROUTES ----------------
@app.route("/")
def dashboard():
    return render_template("index.html")

@app.route("/data")
def data():
    rows = sheet.get_all_values()

    if len(rows) < 2:
        return jsonify({"error": "No data found"})

    records = rows[1:]  # skip header
    hives = {}

    for row in records:
        hive_id = row[1]
        timestamp = row[0]

        # Always keep the latest record per hive
        hives[hive_id] = {
            "timestamp": timestamp,
            "hive_id": hive_id,
            "status": row[2],
            "temperature": safe_float(row[3]),
            "humidity": safe_float(row[4]),
            "weight1": safe_float(row[5]),
            "weight2": safe_float(row[6]),
            "total_weight": safe_float(row[7]),
            "latitude": row[8],
            "longitude": row[9],

            # For future map / UI
            "location_name": "Fetching location..."
        }

    return jsonify({
        "total_hives": len(hives),
        "hives": list(hives.values())
    })

# ---------------- RUN ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
