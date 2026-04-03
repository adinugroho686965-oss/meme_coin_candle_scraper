# Meme Coin Candle Scraper (define.fi)


### Description
Meme Coin Candle Scraper is a Python script used to fetch candle data (OHLCV and trading statistics) from define.fi.

## 📊 Data Explanation

All price and volume-related data in this project are represented in **USD (United States Dollar)** unless stated otherwise.

Below is the explanation for each field:

- **Timestamp**  
  The time when the candle is recorded. Each timestamp represents one candle interval.

- **Open**  
  The opening price of the asset at the beginning of the candle (in USD).

- **High**  
  The highest price reached during the candle period (in USD).

- **Low**  
  The lowest price reached during the candle period (in USD).

- **Close**  
  The closing price of the asset at the end of the candle (in USD).

- **Volume**  
  Total trading volume during the candle period (in USD).

- **VolumeNative**  
  Trading volume measured in the token's native unit (not USD).

- **Buys**  
  Total number of buy transactions during the candle period.

- **Buyers**  
  Number of unique wallets/users that performed buy transactions.

- **BuyVolume**  
  Total volume of buy transactions (in USD).

- **Sells**  
  Total number of sell transactions during the candle period.

- **Sellers**  
  Number of unique wallets/users that performed sell transactions.

- **SellVolume**  
  Total volume of sell transactions (in USD).

- **Liquidity**  
  Total liquidity available in the pool (in USD).

- **Traders**  
  Total number of unique traders (buyers + sellers) during the candle period.

- **Transactions**  
  Total number of transactions (buy + sell) during the candle period.

---
The data is processed into a pandas DataFrame and exported as an Excel (.xlsx) file.

---

## ⚙️ Installation

Clone the project and install dependencies:

```bash
pip install -r requirements.txt
```
---

## 🚀 How to Use

### 1. Get Cookies from Browser
- Open https://www.defined.fi
- Press **F12** to open Developer Tools
- Go to **Application → Cookies**
- Copy the cookie value

---

### 2. Run the Script

Basic command:

```bash
python project.py \
--coin COIN_ADDRESS \
--cookies "YOUR_COOKIE" \
--start-time "YYYY-MM-DD HH:MM:SS" \
--num-candles 100



---

## ⚙️ How the System Works

This project works by replicating the same requests used by the define.fi website to fetch candle data directly from their API.

### 🔍 Step-by-step process:

1. **User Input**
   - The user provides:
     - Token address (`--coin`)
     - Start time
     - Number of candles
     - Cookies (from browser)

2. **Cookie Authentication**
   - The script uses the provided cookies to authenticate requests.
   - This is required because define.fi restricts access without a valid session.

3. **Replicating define.fi Requests**
   - The script sends POST requests to the define.fi API endpoint.
   - It mimics the exact structure of requests used by the website (GraphQL queries).

4. **Using `curl_cffi`**
   - The script uses `curl_cffi` instead of standard requests.
   - This is important because define.fi detects browser fingerprints.
   - `curl_cffi` allows the script to impersonate a real browser (e.g., Firefox), helping bypass these restrictions.

5. **Data Fetching Flow**
   - Get `pairId` from token address
   - Fetch metadata (to get `quoteToken`)
   - Request candle data (OHLCV + trading stats)

6. **Data Processing**
   - The response is converted into a pandas DataFrame
   - Timestamp is converted to local time
   - Data is formatted and cleaned

7. **Export**
   - Final data is saved as an Excel file (`.xlsx`)

---

## ⚠️ Important Notes
- This script does NOT use an official public API
- It works by replicating internal requests from define.fi
- If define.fi changes their request structure, the script may stop working
- Valid cookies are required at all times