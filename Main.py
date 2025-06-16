from telegram import Bot
import requests
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import MACD, SMAIndicator
from threading import Thread
from flask import Flask
import time

# Your credentials
TOKEN = "7769640970:AAGG7QI-h2k6amBJcjAsafGutprwG5clR-A"
CHAT_ID = "-1002552555211"
bot = Bot(token=TOKEN)

# Flask for keep alive
app = Flask(__name__)
@app.route('/')
def home():
    return "✅ Bot is running!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# Fetch historical price data
def fetch_data(coin):
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coin}/market_chart?vs_currency=usd&days=2&interval=hourly"
        data = requests.get(url).json()
        prices = [i[1] for i in data['prices']]
        df = pd.DataFrame(prices, columns=['close'])
        return df
    except Exception as e:
        print(f"Data fetch error for {coin}: {e}")
        return None

# Strategy logic
def calculate_signals(df):
    df['rsi'] = RSIIndicator(df['close']).rsi()
    macd = MACD(df['close'])
    df['macd'] = macd.macd()
    df['macd_signal'] = macd.macd_signal()
    df['sma'] = SMAIndicator(df['close'], window=20).sma_indicator()
    latest = df.iloc[-1]

    if latest['rsi'] < 30 and latest['macd'] > latest['macd_signal'] and latest['close'] > latest['sma']:
        return "💹 STRONG BUY"
    elif latest['rsi'] > 70 and latest['macd'] < latest['macd_signal'] and latest['close'] < latest['sma']:
        return "🔻 STRONG SELL"
    else:
        return "📊 HOLD"

# Send message to Telegram
def send_signal(coin):
    df = fetch_data(coin)
    if df is not None:
        signal = calculate_signals(df)
        current_price = df['close'].iloc[-1]
        message = f"""
🪙 *{coin.upper()}*
💰 Price: ${current_price:.2f}
📈 Signal: {signal}
🧠 Strategy: RSI + MACD + SMA
        """
        bot.send_message(chat_id=CHAT_ID, text=message, parse_mode='Markdown')

# 25 Strong Coins
coins = [
    "bitcoin", "ethereum", "binancecoin", "solana", "cardano",
    "xrp", "dogecoin", "polkadot", "chainlink", "litecoin",
    "tron", "avalanche-2", "uniswap", "stellar", "vechain",
    "aptos", "arbitrum", "the-graph", "injective-protocol", "kaspa",
    "optimism", "algorand", "hedera-hashgraph", "near", "tezos"
]

# Run
keep_alive()
while True:
    for coin in coins:
        try:
            send_signal(coin)
            time.sleep(2)  # small delay between requests
        except Exception as e:
            bot.send_message(chat_id=CHAT_ID, text=f"⚠️ {coin.upper()} Error: {e}")
    time.sleep(300)  # wait 5 mins before next round
