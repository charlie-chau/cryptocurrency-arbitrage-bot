import requests
import json
import sys
from helpers import *
from logger import *
import ccxt
import numpy as np
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
        bitfinex_response = requests.get("https://api.bitfinex.com/v2/tickers?symbols=tETHBTC,tIOTBTC,tIOTETH,tBTCUSD,tETHUSD,tIOTUSD")
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
                        price_data[pair_name]["Bitfinex"]['volume_bid'] = float(pair[2])
                        price_data[pair_name]["Bitfinex"]['volume_ask'] = float(pair[4])
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
        return

    # try:
    #     if pair_name == "IOTETH":
    #         iot_eth_okex = requests.get("https://www.okex.com/api/v1/ticker.do?symbol=iota_eth")
    #         if iot_eth_okex.status_code == 200:
    #             iot_eth_okex_json = iot_eth_okex.json()
    #             price_data[pair_name]["Okex"]["bid"] = float(iot_eth_okex_json["ticker"]["buy"])
    #             price_data[pair_name]["Okex"]["ask"] = float(iot_eth_okex_json["ticker"]["sell"])
    #             price_data[pair_name]["Okex"]["volume_bid"] = 0
    #             price_data[pair_name]["Okex"]["volume_ask"] = 0
    #             price_data[pair_name]["Okex"]["volume"] = float(iot_eth_okex_json["ticker"]["vol"])
    #     if pair_name == "IOTBTC":
    #         iot_btc_okex = requests.get("https://www.okex.com/api/v1/ticker.do?symbol=iota_btc")
    #         if iot_btc_okex.status_code == 200:
    #             iot_btc_okex_json = iot_btc_okex.json()
    #             price_data[pair_name]["Okex"]["bid"] = float(iot_btc_okex_json["ticker"]["buy"])
    #             price_data[pair_name]["Okex"]["ask"] = float(iot_btc_okex_json["ticker"]["sell"])
    #             price_data[pair_name]["Okex"]["volume_bid"] = 0
    #             price_data[pair_name]["Okex"]["volume_ask"] = 0
    #             price_data[pair_name]["Okex"]["volume"] = float(iot_btc_okex_json["ticker"]["vol"])
    # except Exception as e:
    #     print(e)
    #     raise

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
                    if pair_name == "IOTETH":
                        matching_pair = "IOTAETH"
                    elif pair_name == "IOTBTC":
                        matching_pair = "IOTABTC"
                    else:
                        matching_pair = pair_name

                    if pair["symbol"] == matching_pair:
                        price_data[pair_name]["Binance"]['bid'] = float(pair["bidPrice"])
                        price_data[pair_name]["Binance"]['ask'] = float(pair["askPrice"])
                        price_data[pair_name]["Binance"]['volume_bid'] = float(pair["bidQty"])
                        price_data[pair_name]["Binance"]['volume_ask'] = float(pair["askQty"])
    else:
        print ("Failed to retrieve Binance prices.\n" \
               "[STATUS CODE]: " + str(binance_response.status_code) + "\n" \
               "[RESPONSE]: " + str(binance_response) + "\n" \
               "Exiting...")
        return

    seconds = time.time() - ts

    print ("Seconds elapsed to get price: " + str(seconds))

    return price_data, exchange_rates

def get_rebalance_spread(price_data, pair, buy_market, sell_market):

    spread_diff_subsequent = (
            price_data[pair][buy_market]['bid'] * (1 - trade_fees[buy_market]) - price_data[pair][sell_market][
        'ask'] * (
                    1 + trade_fees[sell_market]))
    spread_percentage_subsequent = (spread_diff_subsequent / price_data[pair][sell_market]['ask'])

    spread_diff_rebalance = (
            price_data[pair][sell_market]['bid'] * (1 - trade_fees[sell_market]) - price_data[pair][buy_market]['ask'] * (
            1 + trade_fees[buy_market]))
    spread_percentage_rebalance = (spread_diff_rebalance / price_data[pair][buy_market]['ask'])

    return spread_percentage_subsequent, spread_percentage_rebalance


def get_spreads(price_data, balances, exchange_rates, weight):

    print ("Calculating spreads...")

    binance_ccxt = ccxt.binance()
    binance_ccxt.load_markets()

    spread_data = []

    for pair in price_data:
        from_coin = pair[0:3]
        to_coin = pair[3:6]
        for market in price_data[pair]:
            for other_market in price_data[pair]:
                if market != other_market:

                    if from_coin == "IOT":
                        from_coin_for_lots = "IOTA"
                    else:
                        from_coin_for_lots = from_coin

                    pair_for_lots = from_coin_for_lots + "/" + to_coin

                    spread_diff = (price_data[pair][market]['bid'] * (1 - trade_fees[market]) - price_data[pair][other_market]['ask'] * (1 + trade_fees[other_market]))
                    spread_percentage = (spread_diff / price_data[pair][other_market]['ask'])
                    cheap_price = price_data[pair][other_market]['ask']
                    # cheap_price_volume = binance_ccxt.amount_to_lots(pair_for_lots, price_data[pair][other_market]['volume_ask'])
                    cheap_price_volume = np.rint(price_data[pair][other_market]['volume_ask'])
                    expensive_price = price_data[pair][market]['bid']
                    # expensive_price_volume = binance_ccxt.amount_to_lots(pair_for_lots, price_data[pair][market]['volume_bid'])
                    expensive_price_volume = np.rint(price_data[pair][market]['volume_bid'])
                    # total_movement_fees = get_movement_fees(other_market, market, pair, exchange_rates)
                    total_movement_fees = 0
                    trade_amount, weighted_trade_amount = get_amount_tradeable(cheap_price, other_market, market,
                                                            pair, balances, weight)
                    #trade_amount = binance_ccxt.amount_to_lots(pair_for_lots, max_trade_amount)
                    profit_in_to_coin = spread_diff * trade_amount
                    profit_in_to_coin_weighted = spread_diff * weighted_trade_amount
                    profit_in_usd = get_usd_amount(profit_in_to_coin, to_coin,
                                                   exchange_rates)
                    profit_in_usd_weighted = get_usd_amount(profit_in_to_coin_weighted,to_coin,exchange_rates)

                    temp_spread_data = {}
                    temp_spread_data["pair"] = pair
                    temp_spread_data["cheap_exchange"] = other_market
                    temp_spread_data["expensive_exchange"] = market
                    temp_spread_data["cheap_price"] = cheap_price
                    temp_spread_data["cheap_price_volume"] = cheap_price_volume
                    temp_spread_data["expensive_price"] = expensive_price
                    temp_spread_data["expensive_price_volume"] = expensive_price_volume
                    temp_spread_data["spread"] = spread_percentage
                    temp_spread_data["max_amount_tradeable"] = trade_amount
                    temp_spread_data["weighted_amount_tradeable"] = weighted_trade_amount
                    temp_spread_data["profit_to_coin"] = profit_in_to_coin
                    temp_spread_data["profit_to_coin_weighted"] = profit_in_to_coin_weighted
                    temp_spread_data["profit_USD"] = profit_in_usd
                    temp_spread_data["profit_USD_weighted"] = profit_in_usd_weighted

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
