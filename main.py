import requests
import gspread
import json
import os
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Load creds from GitHub secret
creds_dict = json.loads(os.environ["GOOGLE_CREDS_JSON"])
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

sheet = client.open("Stock Tracker").sheet1

API_KEY = os.environ["FINNHUB_API_KEY"]
STOCKS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "JPM", "UNH", "PEP"]

# Add headers if sheet is empty
if sheet.cell(1, 1).value != "Company":
    sheet.insert_row(["Company", "Symbol", "Current Price", "Previous Close", "Daily Change", "Timestamp"], 1)

COMPANY_NAMES = {
    "AAPL": "Apple Inc.",
    "MSFT": "Microsoft Corporation",
    "GOOGL": "Alphabet Inc.",
    "AMZN": "Amazon.com, Inc.",
    "TSLA": "Tesla, Inc.",
    "META": "Meta Platforms, Inc.",
    "NVDA": "NVIDIA Corporation",
    "JPM": "JPMorgan Chase & Co.",
    "UNH": "UnitedHealth Group Inc.",
    "PEP": "PepsiCo, Inc."
}

for symbol in STOCKS:
    try:
        # Get quote data
        quote_url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={API_KEY}"

        response = requests.get(quote_url)
        data = response.json()
        print(f"{symbol} API Response: {data}")  # Debug line

        current = data.get("c", None)
        previous = data.get("pc", None)
        timestamp = data.get("t", None)

        # Ensure values are valid
        if not current or not previous:
        continue

        change = round(current - previous, 2)
        timestamp = datetime.fromtimestamp(data.get("t")).strftime("%Y-%m-%d %H:%M:%S")
        company_name = COMPANY_NAMES.get(symbol, "Unknown")

        sheet.append_row([company_name, symbol, current, previous, change, timestamp])

        # Get company name
        profile_url = f"https://finnhub.io/api/v1/stock/profile2?symbol={symbol}&token={API_KEY}"
        profile = requests.get(profile_url).json()
        company_name = profile.get("name", "Unknown")

        # Append to sheet
        sheet.append_row([company_name, symbol, current, previous, change, formatted_time])
        print(f"✅ Logged {symbol}: {current} vs {previous}")

    except Exception as e:
        print(f"❌ Error for {symbol}: {e}")
