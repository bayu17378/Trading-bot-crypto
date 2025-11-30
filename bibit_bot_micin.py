import requests
import time
import numpy as np
import concurrent.futures

BYBIT = "https://api.bybit.com"

# ========= GET ALL PAIRS ==========
def get_all_pairs():
    url = f"{BYBIT}/v5/market/instruments-info?category=spot"
    r = requests.get(url, timeout=5).json()
    coins = []
    for item in r["result"]["list"]:
        if item["quoteCoin"] == "USDT":
            coins.append(item["symbol"])
    return coins


# ========= GET KLINES ==========
def get_klines(symbol):
    url = f"{BYBIT}/v5/market/kline"
    params = {
        "category": "spot",
        "symbol": symbol,
        "interval": "1m",
        "limit": 50
    }
    try:
        r = requests.get(url, params=params, timeout=2).json()
        return r["result"]["list"]
    except:
        return None


# ========= RSI ==========
def rsi(closes, period=14):
    deltas = np.diff(closes)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)

    avg_gain = np.mean(gains[:period])
    avg_loss = np.mean(losses[:period])

    for i in range(period, len(deltas)):
        avg_gain = (avg_gain*(period-1) + gains[i]) / period
        avg_loss = (avg_loss*(period-1) + losses[i]) / period

    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


# ========= CHECK BULLISH ==========
def check_symbol(symbol):
    kl = get_klines(symbol)
    if not kl:
        return None

    closes = [float(c[4]) for c in kl]
    opens = [float(c[1]) for c in kl]

    ma5 = np.mean(closes[-5:])
    ma20 = np.mean(closes[-20:])
    r = rsi(closes)

    if ma5 > ma20 and r > 50 and closes[-1] > opens[-1]:
        return symbol
    return None


# ========= MAIN ==========
print("Loading all USDT pairs...")
pairs = get_all_pairs()
print("Total pair:", len(pairs))

print("\nBot scanner turbo dimulai...\n")

while True:
    bullish = []

    # 10 thread worker
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        results = executor.map(check_symbol, pairs)

    for res in results:
        if res:
            bullish.append(res)

    if bullish:
        print("\n🔥 BULLISH TERDETEKSI 🔥")
        for b in bullish:
            print("➡️", b)
    else:
        print("Scan ulang... (tidak ada bullish)")

    time.sleep(5)