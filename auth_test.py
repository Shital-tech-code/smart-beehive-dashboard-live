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

# ---------------- GOOGLE AUTH ----------------
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

if "GOOGLE_SERVICE_ACCOUNT_B64" in os.environ:
    decoded_bytes = base64.b64decode(os.environ["GOOGLE_SERVICE_ACCOUNT_B64"])
    service_account_info = json.loads(decoded_bytes.decode("utf-8"))
else:
    with open("service_account.json", "r", encoding="utf-8") as f:
        service_account_info = json.load(f)

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
        return jsonify({"hives": []})

    records = rows[1:]
    latest_hives = {}

    for row in records:

        if len(row) < 10:
            continue

        timestamp = row[0].strip()
        hive_id = row[1].strip()

        if (
            not hive_id or
            hive_id.lower() == "hiveid" or
            timestamp.lower() == "timestamp"
        ):
            continue

        temperature = safe_float(row[3])
        humidity = safe_float(row[4])
        weight1 = safe_float(row[5])
        weight2 = safe_float(row[6])
        total_weight = safe_float(row[7])

        if (
            temperature == 0 and
            humidity == 0 and
            weight1 == 0 and
            weight2 == 0 and
            total_weight == 0
        ):
            continue

        # ---------------- LOCATION FIX ----------------
        lat = row[8].strip()
        lon = row[9].strip()

        # ✅ ONLY Hive_2 → MGIRI
        if hive_id == "Hive_2":
            lat = "20.739964"
            lon = "78.594939"

        # ---------------- STORE DATA ----------------
        latest_hives[hive_id] = {
            "timestamp": timestamp,
            "hive_id": hive_id,

            # Existing status
            "status": row[2] if row[2] else "Active",

            # ✅ NEW BATTERY STATUS
            "battery_status": "Active",

            "temperature": temperature,
            "humidity": humidity,
            "weight1": weight1,
            "weight2": weight2,
            "total_weight": total_weight,

            "latitude": lat,
            "longitude": lon
        }

    # ---------------- SORT ----------------
    sorted_hives = sorted(
    latest_hives.values(),
    key=lambda x: int(x["hive_id"].split("_")[1])
    if "_" in x["hive_id"] and x["hive_id"].split("_")[1].isdigit()
    else 999
    )

    return jsonify({
        "total_hives": len(sorted_hives),
        "hives": sorted_hives
    })

# ---------------- RUN ----------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)