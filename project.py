import argparse
import os
import sys
from curl_cffi import requests
import datetime
import pandas as pd

url = "https://www.defined.fi/api"
COOKIE_FILE = "cookies.txt"

RESOLUTION_MAP = {
    "1": 60,
    "5": 300,
    "60": 3600,
    "240": 14400
}



def error_and_exit(msg):
    print(msg)
    sys.exit(1)



def save_cookies(cookies):
    try:
        with open(COOKIE_FILE, "w") as f:
            f.write(cookies)
    except Exception as e:
        error_and_exit(f"Gagal menyimpan cookies: {e}")

def load_cookies():
    if not os.path.exists(COOKIE_FILE):
        error_and_exit("Cookies file tidak ditemukan. Gunakan --cookies dulu.")
    try:
        with open(COOKIE_FILE, "r") as f:
            return f.read().strip()
    except Exception as e:
        error_and_exit(f"Gagal membaca cookies: {e}")







def local_to_utc(time_str):
    try:
        dt = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        return int(dt.timestamp())
    except Exception as e:
        error_and_exit(f"Format waktu salah: {e}")

def utc_to_local(ts):
    try:
        return datetime.datetime.fromtimestamp(ts).astimezone()
    except Exception as e:
        error_and_exit(f"Gagal convert timestamp: {e}")



def get_pairId(token_address, headers):
    payload = {
        "operationName": "FilterTokens",
        "variables": {"limit": 1, "phrase": token_address},
        "query": "query FilterTokens($phrase: String, $limit: Int){filterTokens(phrase:$phrase,limit:$limit){results{pair{id}}}}"
    }

    try:
        r = requests.post(url, headers=headers, json=payload, impersonate="firefox")

        if r.status_code != 200:
            error_and_exit(f"HTTP Error get_pairId: {r.status_code}")

        data = r.json()

        results = data.get("data", {}).get("filterTokens", {}).get("results", [])
        if not results:
            error_and_exit("Pair tidak ditemukan / token salah")

        return results[0]["pair"]["id"]

    except Exception as e:
        error_and_exit(f"Error get_pairId: {e}")


def get_metadata(pairId, headers):
    payload = {
        "operationName": "GetPairMetadata",
        "variables": {"pairId": pairId},
        "query": "query GetPairMetadata($pairId: String!){pairMetadata(pairId:$pairId){nonLiquidityToken}}"
    }

    try:
        r = requests.post(url, headers=headers, json=payload, impersonate="firefox")

        if r.status_code != 200:
            error_and_exit(f"HTTP Error get_metadata: {r.status_code}")

        data = r.json()

        meta = data.get("data", {}).get("pairMetadata")
        if not meta:
            error_and_exit("Metadata tidak ditemukan")

        if "nonLiquidityToken" not in meta:
            error_and_exit("nonLiquidityToken tidak ada")

        return meta

    except Exception as e:
        error_and_exit(f"Error get_metadata: {e}")


def get_candles(pairId, start, end, resolution, num_candles, quoteToken, headers):
    payload = {
        "operationName": "GetBars",
        "variables": {
            "from": start,
            "to": end,
            "symbol": pairId,
            "resolution": resolution,
            "currencyCode": "USD",
            "removeEmptyBars": True,
            "removeLeadingNullValues": True,
            "statsType": "FILTERED",
            "countback": num_candles,
            "quoteToken": quoteToken
        },
        "query": "query GetBars($symbol: String!, $countback: Int, $from: Int!, $to: Int!, $resolution: String!, $currencyCode: String, $quoteToken: QuoteToken, $statsType: TokenPairStatisticsType, $removeLeadingNullValues: Boolean, $removeEmptyBars: Boolean) { getBars(symbol: $symbol countback: $countback from: $from to: $to resolution: $resolution currencyCode: $currencyCode quoteToken: $quoteToken statsType: $statsType removeLeadingNullValues: $removeLeadingNullValues removeEmptyBars: $removeEmptyBars) { s o h l c t volume volumeNativeToken buys buyers buyVolume sells sellers sellVolume liquidity traders transactions __typename }}"
    }

    try:
        r = requests.post(url, headers=headers, json=payload, impersonate="firefox")

        if r.status_code != 200:
            error_and_exit(f"HTTP Error get_candles: {r.status_code}")

        data = r.json()

        candles = data.get("data", {}).get("getBars")
        if not candles:
            error_and_exit("Data candle kosong")

        required_keys = ["t", "o", "h", "l", "c"]
        for key in required_keys:
            if key not in candles:
                error_and_exit(f"Field '{key}' tidak ditemukan di candle")

        return candles

    except Exception as e:
        error_and_exit(f"Error get_candles: {e}")



def convert_to_df(data):
    try:
        df = pd.DataFrame({
            "timestamp": data["t"],
            "Open": data["o"],
            "High": data["h"],
            "Low": data["l"],
            "Close": data["c"],
            "Volume": data["volume"],
            "VolumeNative": data["volumeNativeToken"],
            "Buys": data["buys"],
            "Buyers": data["buyers"],
            "BuyVolume": data["buyVolume"],
            "Sells": data["sells"],
            "Sellers": data["sellers"],
            "SellVolume": data["sellVolume"],
            "Liqudity": data["liquidity"],
            "Traders": data["traders"],
            "Transactions": data["transactions"],
        })

        df["timestamp"] = df["timestamp"].apply(utc_to_local)
        df["timestamp"] = df["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")

        return df

    except Exception as e:
        error_and_exit(f"Error convert_to_df: {e}")



def main(args):
    try:
        
        if args.cookies:
            save_cookies(args.cookies)
            cookies = args.cookies
        else:
            cookies = load_cookies()

        headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "*/*",
        "Content-Type": "application/json",
        "Origin": "https://www.defined.fi",
        "Cookie": cookies
        }

        
        if args.resolution not in RESOLUTION_MAP:
            error_and_exit("Resolution hanya boleh: 1,5,60,240")

        if args.num_candles > 1500:
            error_and_exit("max num_candles = 1500")

        
        start_unix = local_to_utc(args.start_time)
        interval = RESOLUTION_MAP[args.resolution]
        end_unix = start_unix + (args.num_candles * interval)

        print(f"Start: {start_unix}")
        print(f"End  : {end_unix}")

        
        pairId = get_pairId(args.coin, headers)
        print("Pair:", pairId)

        meta = get_metadata(pairId, headers)
        quoteToken = meta["nonLiquidityToken"]

        candles = get_candles(
            pairId,
            start_unix,
            end_unix,
            args.resolution,
            args.num_candles,
            quoteToken,
            headers
        )

        df = convert_to_df(candles)

        
        filename = args.output if args.output else f"{args.coin}.xlsx"
        directory = args.dir if args.dir else "."

        os.makedirs(directory, exist_ok=True)

        path = os.path.join(directory, filename)
        df.to_excel(path, index=False)

        print(f"Saved to: {path}")

    except Exception as e:
        error_and_exit(f"error_and_exit error: {e}")



if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--coin", required=True)
    parser.add_argument("--cookies")
    parser.add_argument("--resolution", default="1")
    parser.add_argument("--start-time", required=True)
    parser.add_argument("--num-candles", type=int, required=True)
    parser.add_argument("--output")
    parser.add_argument("--dir")

    args = parser.parse_args()

    main(args)