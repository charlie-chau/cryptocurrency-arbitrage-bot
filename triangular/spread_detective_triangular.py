import requests
import json
import sys
from helpers import *

def get_prices():

    print ("Getting price data...")

    price_data = {}

    price_data = {}

    coins_list = {'BTC', 'ETH', 'LTC'}
    market_list = {'Bitfinex', 'BTCMarkets', 'Binance'}

    for market in market_list:
        price_data[market] = {}
        for coin in coins_list:
            price_data[market][coin] = {}


    try:
        bitfinex_response = requests.get("https://api.bitfinex.com/v2/tickers?symbols=tETHUSD,tBTCUSD,tLTCUSD").json()
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)
    if len(bitfinex_response) > 0:
        for pair in bitfinex_response:
            if pair[0] == "tETHUSD":
                price_data["Bitfinex"]["ETH"]['bid'] = float(pair[1])
                price_data["Bitfinex"]["ETH"]['ask'] = float(pair[3])
            elif pair[0] == "tBTCUSD":
                price_data["Bitfinex"]["BTC"]['bid'] = float(pair[1])
                price_data["Bitfinex"]["BTC"]['ask'] = float(pair[3])
            elif pair[0] == "tXRPUSD":
                price_data["Bitfinex"]["LTC"]['bid'] = float(pair[1])
                price_data["Bitfinex"]["LTC"]['ask'] = float(pair[3])

    try:
        binance_response = requests.get("https://api.binance.com/api/v1/ticker/allBookTickers").json()
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)
    #binance_response = requests.get("https://api.binance.com/api/v1/ticker/allPrices").json()
    if len(binance_response) > 0:
        for pair in binance_response:
            if pair["symbol"] == "BTCUSDT":
                price_data["Binance"]["BTC"]['bid'] = float(pair["bidPrice"])
                price_data["Binance"]["BTC"]['ask'] = float(pair["askPrice"])
            elif pair["symbol"] == "ETHUSDT":
                price_data["Binance"]["ETH"]['bid'] = float(pair["bidPrice"])
                price_data["Binance"]["ETH"]['ask'] = float(pair["askPrice"])
            elif pair["symbol"] == "LTCUSDT":
                price_data["Binance"]["LTC"]['bid'] = float(pair["bidPrice"])
                price_data["Binance"]["LTC"]['ask'] = float(pair["askPrice"])


    try:
        btcmkt_btc_response = requests.get("https://api.btcmarkets.net/market/BTC/AUD/tick").json()
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)
    price_data["BTCMarkets"]["BTC"]['bid'] = float(btcmkt_btc_response["bestBid"])
    price_data["BTCMarkets"]["BTC"]['ask'] = float(btcmkt_btc_response["bestAsk"])

    try:
        btcmkt_eth_response = requests.get("https://api.btcmarkets.net/market/ETH/AUD/tick").json()
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)
    price_data["BTCMarkets"]["ETH"]['bid'] = float(btcmkt_eth_response["bestBid"])
    price_data["BTCMarkets"]["ETH"]['ask'] = float(btcmkt_eth_response["bestAsk"])

    try:
        btcmkt_ltc_response = requests.get("https://api.btcmarkets.net/market/LTC/AUD/tick").json()
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)
    price_data["BTCMarkets"]["LTC"]['bid'] = float(btcmkt_ltc_response["bestBid"])
    price_data["BTCMarkets"]["LTC"]['ask'] = float(btcmkt_ltc_response["bestAsk"])



    print json.dumps(price_data, indent=2, separators=(',', ': '))

    return price_data

def get_spreads(price_data, balances):

    print ("Calculating spreads...")

    spread_data = []

    for market in price_data:
        for other_market in price_data:
            if market != other_market:
                for coin in price_data[market]:
                    coin_ratio = price_data[market][coin]['ask'] / price_data[other_market][coin]['bid']
                    for other_coin in price_data[market]:
                        if coin != other_coin:

                            other_coin_ratio = price_data[market][other_coin]['bid'] / price_data[other_market][other_coin]['ask']

                            if coin_ratio < other_coin_ratio:

                                spread = (other_coin_ratio - coin_ratio) / coin_ratio
                                cheap_coin = coin
                                expensive_coin = other_coin
                                market_a = market
                                market_b = other_market
                                total_movement_fees = get_movement_fees(market_a, market_b, coin, other_coin)
                                amount_sell_a, amount_sell_b = get_max_sell_amounts(market_a, market_b, coin, other_coin, balances, price_data)
                                profit_before_fees = amount_sell_a*price_data[market_a][other_coin]['bid']*spread
                                profit = profit_before_fees - total_movement_fees

                                temp_spread_data = {}

                                temp_spread_data["spread"] = spread
                                temp_spread_data["cheap_coin"] = cheap_coin
                                temp_spread_data["expensive_coin"] = expensive_coin
                                temp_spread_data["market_a"] = market_a
                                temp_spread_data["market_b"] = market_b
                                temp_spread_data["amount_sell_a"] = amount_sell_a
                                temp_spread_data["amount_sell_b"] = amount_sell_b
                                temp_spread_data["movement_fees"] = total_movement_fees
                                temp_spread_data["profit_before_fees"] = profit_before_fees
                                temp_spread_data["profit"] = profit
                                spread_data.append(temp_spread_data)

    def extract_profit(json):
        try:
            return json["profit"]
        except KeyError:
            return 0

    spread_data.sort(key=extract_profit, reverse=True)

    print ("Spreads sorted.")
    print json.dumps(spread_data, indent=2, separators=(',', ': '))
    return spread_data
