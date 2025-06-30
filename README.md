# OANDA Trade Logger with Google Sheets Integration

This Python script connects to your OANDA trading account and automatically logs open trades to a Google Sheet. It also monitors for closed trades, updates their P&L, and tracks performance statistics (win rate and average P&L).

## Features

- Logs open trades to Google Sheets in real-time
- Monitors for closed trades and updates relevant columns
- Tracks win percentage and average profit/loss
- Works with both live and practice OANDA accounts
- Designed for hands-off trade tracking

## Requirements

- A Google Cloud service account with Sheets API access
- A Google Sheet with a tab named as configured
- An OANDA API key and account ID

## Setup

1. **Google Sheets API:**
   - Create a Google Cloud project
   - Enable the Sheets API
   - Create a service account and download the JSON key file
   - Share the target Google Sheet with the service account email

2. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```


(NOTE: The script expects the following column headers starting in row 2:

Trade ID | Instrument | Open Time | Units | Open Price | Closed Price | P&L | Notes

A summary of statistics (Win %, Avg P&L) is written to cell A1. 

The script will override will override the data in these cells with the headers and data if not formatted accordingly)