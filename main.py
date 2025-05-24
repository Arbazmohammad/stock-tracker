import os
import json
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import time

# Write the creds.json file from GitHub secret
with open("creds.json", "w") as f:
    f.write(os.environ["GOOGLE_CREDS_JSON"])

# Authenticate with Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open("Stock Tracker").sheet1

# Finnhub API setup
API_KEY = os.environ.get("FINNHUB_API_KEY")
if not API_KEY:
    raise ValueError("Missing FINNHUB_API_KEY environment variable.")

STOCKS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "META", "NVDA", "JPM", "UNH", "PEP"]
URL = "https://finnhub.io/api/v1/quote?symbol={}&token=" + API_KEY

# Fetch and append data
for symbol in STOCKS:
    try:
        response = requests.get(URL.format(symbol))
        data = response.json()
        current_price = data.get("c", 0)
        prev_close = data.get("pc", 0)
        change = round(current_price - prev_close, 2)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sheet.append_row([timestamp, symbol, current_price, prev_close, change])
        print(f"{symbol} logged at {timestamp}")
        time.sleep(1)  # To respect API rate limits
    except Exception as e:
        print(f"Error for {symbol}: {e}")
