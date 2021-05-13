import requests
import json
import sys
from helpers import *
from logger import *
import ccxt
import secrets

def get_prices(market_pairs):
    ts = time.time()
    print ("Getting price data...")

    price_data = {}
    exchange_rates = {}

    for market_pair in market_pairs:
        pair = market_pair[0]
        from_coin = pair[0]
        to_coin = pair[1]
        pair_name = from_coin + to_coin
        price_data[pair_name] = {}
        for market in market_pair[1]:
            price_data[pair_name][market] = {}

    try:
        bitfinex_response = requests.get("https://api.bitfinex.com/v2/tickers?symbols=tETHBTC,tIOTBTC,tIOTETH,tBTCUSD,tETHUSD,tIOTUSD,tETCETH,tXRPBTC,tDSHBTC,tQTMBTC,tQTMETH,tETCBTC")
    except Exception as e:
        print(e)
        fb_client = Facebook_Client(secrets.FACEBOOK_USERNAME, secrets.FACEBOOK_PASSWORD)
        fb_message = "[ERROR] Bitfinex Price API Exception raised:\n" \
                     "[MESSAGE]: " + str(e)
        fb_client.send(Message(fb_message), thread_id='562431311', thread_type=ThreadType.USER)
        return

    if bitfinex_response.status_code == 200:
        bitfinex_response_json = bitfinex_response.json()
        if len(bitfinex_response_json) > 0:
            for pair in bitfinex_response_json:
                for pair_name in price_data:
                    matching_pair = "t" + pair_name
                    if pair[0] == matching_pair:
                        price_data[pair_name]["Bitfinex"]['bid'] = float(pair[1])
                        price_data[pair_name]["Bitfinex"]['ask'] = float(pair[3])
                if pair[0] == "tBTCUSD":
                    exchange_rates["BTC"] = float(pair[7])
                elif pair[0] == "tETHUSD":
                    exchange_rates["ETH"] = float(pair[7])
                elif pair[0] == "tIOTUSD":
                    exchange_rates["IOT"] = float(pair[7])
    else:
        print ("Failed to retrieve Bitfinex prices.\n" \
               "[STATUS CODE]: " + str(bitfinex_response.status_code) + "\n" \
               "[RESPONSE]: " + str(bitfinex_response) + "\n" \
               "Exiting...")
        sys.exit(1)

    try:
        binance_response = requests.get("https://api.binance.com/api/v1/ticker/allBookTickers")
    except Exception as e:
        print(e)
        fb_client = Facebook_Client(secrets.FACEBOOK_USERNAME, secrets.FACEBOOK_PASSWORD)
        fb_message = "[ERROR] Binance Price API Exception raised:\n" \
                     "[MESSAGE]: " + str(e)
        fb_client.send(Message(fb_message), thread_id='562431311', thread_type=ThreadType.USER)
        return


    if binance_response.status_code == 200:
        binance_response_json = binance_response.json()
        if len(binance_response_json) > 0:
            for pair in binance_response_json:
                for pair_name in price_data:
                    if "Binance" in price_data[pair_name]:
                        if pair_name == "IOTETH":
                            matching_pair = "IOTAETH"
                        elif pair_name == "IOTBTC":
                            matching_pair = "IOTABTC"
                        elif pair_name == "DSHBTC":
                            matching_pair = "DASHBTC"
                        elif pair_name == "QTMBTC":
                            matching_pair = "QTUMBTC"
                        elif pair_name == "QTMETH":
                            matching_pair = "QTUMETH"
                        else:
                            matching_pair = pair_name

                        if pair["symbol"] == matching_pair:
                            price_data[pair_name]["Binance"]['bid'] = float(pair["bidPrice"])
                            price_data[pair_name]["Binance"]['ask'] = float(pair["askPrice"])
    else:
        print ("Failed to retrieve Binance prices.\n" \
               "[STATUS CODE]: " + str(bitfinex_response.status_code) + "\n" \
               "[RESPONSE]: " + str(bitfinex_response) + "\n" \
               "Exiting...")
        sys.exit(1)

    try:
        kraken_response = requests.get("https://api.kraken.com/0/public/Ticker?pair=ETHXBT,ETCXBT,XRPXBT,DASHXBT,BCHXBT,XMRXBT,ETCETH")
    except Exception as e:
        print(e)
        fb_client = Facebook_Client(secrets.FACEBOOK_USERNAME, secrets.FACEBOOK_PASSWORD)
        fb_message = "[ERROR] Kraken Price API Exception raised:\n" \
                     "[MESSAGE]: " + str(e)
        fb_client.send(Message(fb_message), thread_id='562431311', thread_type=ThreadType.USER)
        return

    if kraken_response.status_code == 200:
        kraken_response_json = kraken_response.json()
        if len(kraken_response_json) > 0:
            for pair_name in price_data:
                if "Kraken" in price_data[pair_name]:
                    if pair_name == "ETHBTC":
                        matching_pair = "XETHXXBT"
                    elif pair_name == "ETCBTC":
                        matching_pair = "XETCXXBT"
                    elif pair_name == "XRPBTC":
                        matching_pair = "XXRPXXBT"
                    elif pair_name == "DSHBTC":
                        matching_pair = "DASHXBT"
                    elif pair_name == "BCCBTC":
                        matching_pair = "BCHXBT"
                    elif pair_name == "XMRBTC":
                        matching_pair = "XXMRXXBT"
                    elif pair_name == "ETCETH":
                        matching_pair = "XETCXETH"
                    else:
                        matching_pair = pair_name

                    price_data[pair_name]["Kraken"]['bid'] = float(kraken_response_json["result"][matching_pair]["a"][0])
                    price_data[pair_name]["Kraken"]['ask'] = float(kraken_response_json["result"][matching_pair]["b"][0])
    else:
        print ("Failed to retrieve Kraken prices.\n" \
               "[STATUS CODE]: " + str(kraken_response.status_code) + "\n" \
               "[RESPONSE]: " + str(kraken_response) + "\n" \
               "Exiting...")
        sys.exit(1)

    seconds = time.time() - ts

    print ("Seconds elapsed to get price: " + str(seconds))

    return price_data, exchange_rates

def get_rebalance_spread(price_data, pair, buy_market, sell_market):

    spread_diff_subsequent = (
            price_data[pair][buy_market]['bid'] * (1 - trade_fees[buy_market]) - price_data[pair][sell_market][
        'ask'] * (1 + trade_fees[sell_market]))
    spread_percentage_subsequent = (spread_diff_subsequent / price_data[pair][sell_market]['ask'])

    spread_diff_rebalance = (
            price_data[pair][sell_market]['bid'] * (1 - trade_fees[sell_market]) - price_data[pair][buy_market]['ask'] * (
            1 + trade_fees[buy_market]))
    spread_percentage_rebalance = (spread_diff_rebalance / price_data[pair][buy_market]['ask'])

    return spread_percentage_subsequent, spread_percentage_rebalance


def get_spreads(price_data, balances, exchange_rates):

    print ("Calculating spreads...")

    spread_data = []

    for pair in price_data:
        from_coin = pair[0:3]
        to_coin = pair[3:6]
        for market in price_data[pair]:
            for other_market in price_data[pair]:
                if market != other_market:

                    spread_diff = (price_data[pair][market]['bid'] * (1 - trade_fees[market]) - price_data[pair][other_market]['ask'] * (1 + trade_fees[other_market]))
                    spread_percentage = (spread_diff / price_data[pair][other_market]['ask'])
                    cheap_price = price_data[pair][other_market]['ask']
                    expensive_price = price_data[pair][market]['bid']
                    # total_movement_fees = get_movement_fees(other_market, market, pair, exchange_rates)
                    total_movement_fees = 0
                    max_trade_amount = get_amount_tradeable(cheap_price, other_market, market,
                                                            pair, balances)
                    profit_in_to_coin = spread_diff * max_trade_amount
                    profit_in_usd = get_usd_amount(profit_in_to_coin, to_coin,
                                                   exchange_rates) - total_movement_fees

                    temp_spread_data = {}
                    temp_spread_data["pair"] = pair
                    temp_spread_data["cheap_exchange"] = other_market
                    temp_spread_data["expensive_exchange"] = market
                    temp_spread_data["cheap_price"] = cheap_price
                    temp_spread_data["expensive_price"] = expensive_price
                    temp_spread_data["spread"] = spread_percentage
                    temp_spread_data["max_amount_tradeable"] = max_trade_amount
                    temp_spread_data["profit_to_coin"] = profit_in_to_coin
                    temp_spread_data["profit_USD"] = profit_in_usd

                    spread_data.append(temp_spread_data)
    print ("Logging spreads")
    log_spreads(spread_data)

    print ("Going through spreads and identifying best in each pair")

    def extract_profit(json):
        try:
            return json["profit_USD"]
        except KeyError:
            sys.exit(1)
            return 0

    spread_data.sort(key=extract_profit, reverse=True)

    print ("Spreads sorted.")
    print json.dumps(spread_data, indent=2, separators=(',', ': '))
    return spread_data
