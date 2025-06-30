import time
import threading
import gspread
from google.oauth2.service_account import Credentials
import oandapyV20
import oandapyV20.endpoints.trades as trades

# ------------------ CONFIG ------------------
OANDA_API_KEY = "<your-oanda-api-key>"
OANDA_ACCOUNT_ID = "<your-account-id>"
ENVIRONMENT = "live"  # use "practice" if on demo
GOOGLE_CREDS_FILE = "<path-to-service-account-json>"
SHEET_NAME = "<google-sheet-name>"
WORKSHEET_NAME = "<worksheet-tab-name>"
POLL_INTERVAL_SECONDS = 10
# --------------------------------------------


def log_open_trades():
    global logged_trade_ids
    r = trades.OpenTrades(accountID=OANDA_ACCOUNT_ID)
    oanda.request(r)
    for trade in r.response.get("trades", []):
        trade_id = str(trade['id'])
        if trade_id not in logged_trade_ids:
            logged_trade_ids.add(trade_id)
            instrument = trade['instrument']
            units = trade['currentUnits']
            open_time = trade['openTime']
            price = trade['price']

            sheet.insert_row([
                trade_id,
                instrument,
                open_time,
                units,
                price,
                "", "", ""  # closed price, P&L, notes
            ], index=3)  # Insert directly under the header


def update_statistics():
    try:
        records = sheet.get_all_records(head = 2)
        closed_pls = []

        for row in records:
            pl_str = str(row.get('P&L', '')).strip()
            if pl_str:
                try:
                    pl = float(pl_str)
                    closed_pls.append(pl)
                except ValueError:
                    continue

        if closed_pls:
            wins = [pl for pl in closed_pls if pl > 0]
            win_rate = round(len(wins) / len(closed_pls) * 100, 2)
            avg_pl = round(sum(closed_pls) / len(closed_pls), 2)
        else:
            win_rate = avg_pl = 0.0

        # Write to summary row
        sheet.update("A1", [["Win %", f"{win_rate}%", "Avg P&L", avg_pl]])
        print(f"Updated stats: Win % = {win_rate}%, Avg P&L = {avg_pl}")

    except Exception as e:
        print(f"Error updating stats: {e}")







def monitor_closed_trades():
    while True:
        try:
            records = sheet.get_all_records(head = 2)
            for idx, row in enumerate(records, start=3):
                trade_id = str(row['Trade ID'])

                if str(row.get('Closed Price')).strip() != "" and str(row.get('P&L')).strip() != "":
                    continue  # Already updated

                try:
                    r = trades.TradeDetails(accountID=OANDA_ACCOUNT_ID, tradeID=trade_id)
                    oanda.request(r)
                    trade = r.response['trade']

                    if trade['state'] == 'CLOSED':
                        closed_price = trade.get('price', 'N/A')
                        realized_pl = trade.get('realizedPL', '0.0')

                        sheet.update_cell(idx, col_index("Closed Price"), closed_price)
                        sheet.update_cell(idx, col_index("P&L"), realized_pl)
                        print(f"Closed trade updated: {trade_id}")
                        update_statistics()
                except Exception as e:
                    print(f"Error for trade {trade_id}: {e}")

        except Exception as e:
            print(f"Error in monitor thread: {e}")
        time.sleep(30)





if __name__ == '__main__':

    # Connect to OANDA
    oanda = oandapyV20.API(access_token=OANDA_API_KEY, environment=ENVIRONMENT)

    # Connect to Google Sheets
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_file(GOOGLE_CREDS_FILE, scopes=scope)
    client = gspread.authorize(creds)
    sheet = client.open(SHEET_NAME).worksheet(WORKSHEET_NAME)

    # Track known trades
    logged_trade_ids = set()

    # Get header row to map column names
    header = sheet.row_values(2)
    col_index = lambda name: header.index(name) + 1  # Convert to 1-based index

    print("Trade Logger started.")
    threading.Thread(target=monitor_closed_trades, daemon=True).start()

    while True:
        try:
            log_open_trades()
        except KeyboardInterrupt:
            print("Stopping")
            break
        except Exception as e:
            print(f"Error checking trades: {e}")
        time.sleep(POLL_INTERVAL_SECONDS)


