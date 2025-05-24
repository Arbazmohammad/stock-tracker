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

API_KEY = "d0p0oqhr01qr8ds0pkogd0p0oqhr01qr8ds0pkp0"
STOCKS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "JPM", "UNH", "PEP"]

# Add headers if sheet is empty
if sheet.cell(1, 1).value != "Company":
    sheet.insert_row(["Company", "Symbol", "Current Price", "Previous Close", "Daily Change", "Timestamp"], 1)

for symbol in STOCKS:
    try:
        # Get current quote
        quote_url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={API_KEY}"
        quote = requests.get(quote_url).json()
        
        current = quote.get("c", 0)
        previous = quote.get("pc", 0)

        if current == 0 or previous == 0:
            print(f"⚠️ No data for {symbol}, skipping.")
            continue

        # Get company profile (name)
        profile_url = f"https://finnhub.io/api/v1/stock/profile2?symbol={symbol}&token={API_KEY}"
        profile = requests.get(profile_url).json()
        company_name = profile.get("name", "Unknown")

        change = round(current - previous, 2)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Append row
        sheet.append_row([company_name, symbol, current, previous, change, timestamp])
        print(f"✅ {symbol} logged.")

    except Exception as e:
        print(f"❌ Error for {symbol}: {e}")
