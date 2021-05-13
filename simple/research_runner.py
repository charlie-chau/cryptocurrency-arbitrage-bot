#!/usr/bin/env python
import datetime
import requests
import time
import json
import os

trade_fees = {'Bitfinex': 0.002,
              'Binance': 0.001,
              'Huobi': 0.002,
              'Okex': 0.002
              }

def get_prices(market_pairs):
    ts = time.time()
    print ("Getting price data...")

    price_data = {}

    for market_pair in market_pairs:
        pair = market_pair[0]
        from_coin = pair[0]
        to_coin = pair[1]
        pair_name = from_coin + to_coin
        price_data[pair_name] = {}
        for market in market_pair[1]:
            price_data[pair_name][market] = {}

    try:
        bitfinex_response = requests.get("https://api.bitfinex.com/v2/tickers?symbols=tIOTBTC,tIOTETH,tBTCUSD,tETHUSD")
    except Exception as e:
        print(e)
        raise

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
                        price_data[pair_name]["Bitfinex"]['volume'] = float(pair[8])

    else:
        print ("Failed to retrieve Bitfinex prices.\n" \
               "[STATUS CODE]: " + str(bitfinex_response.status_code) + "\n" \
               "[RESPONSE]: " + str(bitfinex_response) + "\n" \
               "Exiting...")
        raise Exception

    try:
        binance_response = requests.get("https://api.binance.com/api/v1/ticker/24hr")
    except Exception as e:
        print(e)
        raise

    if binance_response.status_code == 200:
        binance_response_json = binance_response.json()
        if len(binance_response_json) > 0:
            for pair in binance_response_json:
                for pair_name in price_data:
                    if pair_name == "IOTETH":
                        matching_pair = "IOTAETH"
                    elif pair_name == "IOTBTC":
                        matching_pair = "IOTABTC"
                    elif pair_name == "ETHUSD":
                        matching_pair = "ETHUSDT"
                    elif pair_name == "BTCUSD":
                        matching_pair = "BTCUSDT"
                    else:
                        matching_pair = pair_name

                    if pair["symbol"] == matching_pair:
                        price_data[pair_name]["Binance"]['bid'] = float(pair["bidPrice"])
                        price_data[pair_name]["Binance"]['ask'] = float(pair["askPrice"])
                        price_data[pair_name]["Binance"]['volume_bid'] = float(pair["bidQty"])
                        price_data[pair_name]["Binance"]['volume_ask'] = float(pair["askQty"])
                        price_data[pair_name]["Binance"]['volume'] = float(pair["volume"])
    else:
        print ("Failed to retrieve Binance prices.\n" \
               "[STATUS CODE]: " + str(binance_response.status_code) + "\n" \
               "[RESPONSE]: " + str(binance_response) + "\n" \
               "Exiting...")
        raise Exception

    try:
        icx_eth_huobi = requests.get("http://api.huobi.pro/market/detail/merged?symbol=icxeth")
        icx_btc_huobi = requests.get("http://api.huobi.pro/market/detail/merged?symbol=icxbtc")
        ven_eth_huobi = requests.get("http://api.huobi.pro/market/detail/merged?symbol=veneth")
        ven_btc_huobi = requests.get("http://api.huobi.pro/market/detail/merged?symbol=venbtc")
        eth_usd_huobi = requests.get("http://api.huobi.pro/market/detail/merged?symbol=ethusdt")
        btc_usd_huobi = requests.get("http://api.huobi.pro/market/detail/merged?symbol=btcusdt")
    except Exception as e:
        print(e)
        raise

    if icx_eth_huobi.status_code == 200:
        icx_eth_huobi_json = icx_eth_huobi.json()
        price_data["ICXETH"]["Huobi"]["bid"] = float(icx_eth_huobi_json["tick"]["bid"][0])
        price_data["ICXETH"]["Huobi"]["ask"] = float(icx_eth_huobi_json["tick"]["ask"][0])
        price_data["ICXETH"]["Huobi"]["volume_bid"] = float(icx_eth_huobi_json["tick"]["bid"][1])
        price_data["ICXETH"]["Huobi"]["volume_ask"] = float(icx_eth_huobi_json["tick"]["ask"][1])
        price_data["ICXETH"]["Huobi"]["volume"] = float(icx_eth_huobi_json["tick"]["vol"])
    if icx_btc_huobi.status_code == 200:
        icx_btc_huobi_json = icx_btc_huobi.json()
        price_data["ICXBTC"]["Huobi"]["bid"] = float(icx_btc_huobi_json["tick"]["bid"][0])
        price_data["ICXBTC"]["Huobi"]["ask"] = float(icx_btc_huobi_json["tick"]["ask"][0])
        price_data["ICXBTC"]["Huobi"]["volume_bid"] = float(icx_btc_huobi_json["tick"]["bid"][1])
        price_data["ICXBTC"]["Huobi"]["volume_ask"] = float(icx_btc_huobi_json["tick"]["ask"][1])
        price_data["ICXBTC"]["Huobi"]["volume"] = float(icx_btc_huobi_json["tick"]["vol"])
    if ven_eth_huobi.status_code == 200:
        ven_eth_huobi_json = ven_eth_huobi.json()
        price_data["VENETH"]["Huobi"]["bid"] = float(ven_eth_huobi_json["tick"]["bid"][0])
        price_data["VENETH"]["Huobi"]["ask"] = float(ven_eth_huobi_json["tick"]["ask"][0])
        price_data["VENETH"]["Huobi"]["volume_bid"] = float(ven_eth_huobi_json["tick"]["bid"][1])
        price_data["VENETH"]["Huobi"]["volume_ask"] = float(ven_eth_huobi_json["tick"]["ask"][1])
        price_data["VENETH"]["Huobi"]["volume"] = float(ven_eth_huobi_json["tick"]["vol"])
    if ven_btc_huobi.status_code == 200:
        ven_btc_huobi_json = ven_btc_huobi.json()
        price_data["VENBTC"]["Huobi"]["bid"] = float(ven_btc_huobi_json["tick"]["bid"][0])
        price_data["VENBTC"]["Huobi"]["ask"] = float(ven_btc_huobi_json["tick"]["ask"][0])
        price_data["VENBTC"]["Huobi"]["volume_bid"] = float(ven_btc_huobi_json["tick"]["bid"][1])
        price_data["VENBTC"]["Huobi"]["volume_ask"] = float(ven_btc_huobi_json["tick"]["ask"][1])
        price_data["VENBTC"]["Huobi"]["volume"] = float(ven_btc_huobi_json["tick"]["vol"])
    if eth_usd_huobi.status_code == 200:
        eth_usd_huobi_json = eth_usd_huobi.json()
        price_data["ETHUSD"]["Huobi"]["bid"] = float(eth_usd_huobi_json["tick"]["bid"][0])
        price_data["ETHUSD"]["Huobi"]["ask"] = float(eth_usd_huobi_json["tick"]["ask"][0])
        price_data["ETHUSD"]["Huobi"]["volume_bid"] = float(eth_usd_huobi_json["tick"]["bid"][1])
        price_data["ETHUSD"]["Huobi"]["volume_ask"] = float(eth_usd_huobi_json["tick"]["ask"][1])
        price_data["ETHUSD"]["Huobi"]["volume"] = float(eth_usd_huobi_json["tick"]["vol"])
    if btc_usd_huobi.status_code == 200:
        btc_usd_huobi_json = btc_usd_huobi.json()
        price_data["BTCUSD"]["Huobi"]["bid"] = float(btc_usd_huobi_json["tick"]["bid"][0])
        price_data["BTCUSD"]["Huobi"]["ask"] = float(btc_usd_huobi_json["tick"]["ask"][0])
        price_data["BTCUSD"]["Huobi"]["volume_bid"] = float(btc_usd_huobi_json["tick"]["bid"][1])
        price_data["BTCUSD"]["Huobi"]["volume_ask"] = float(btc_usd_huobi_json["tick"]["ask"][1])
        price_data["BTCUSD"]["Huobi"]["volume"] = float(btc_usd_huobi_json["tick"]["vol"])

    try:
        icx_eth_okex = requests.get("https://www.okex.com/api/v1/ticker.do?symbol=icx_eth")
        icx_btc_okex = requests.get("https://www.okex.com/api/v1/ticker.do?symbol=icx_btc")
        iot_eth_okex = requests.get("https://www.okex.com/api/v1/ticker.do?symbol=iota_eth")
        iot_btc_okex = requests.get("https://www.okex.com/api/v1/ticker.do?symbol=iota_btc")
        eth_usd_okex = requests.get("https://www.okex.com/api/v1/ticker.do?symbol=eth_usdt")
        btc_usd_okex = requests.get("https://www.okex.com/api/v1/ticker.do?symbol=btc_usdt")
    except Exception as e:
        print(e)
        raise

    if icx_eth_okex.status_code == 200:
        icx_eth_okex_json = icx_eth_okex.json()
        price_data["ICXETH"]["Okex"]["bid"] = float(icx_eth_okex_json["ticker"]["buy"])
        price_data["ICXETH"]["Okex"]["ask"] = float(icx_eth_okex_json["ticker"]["sell"])
        price_data["ICXETH"]["Okex"]["volume_bid"] = 0
        price_data["ICXETH"]["Okex"]["volume_ask"] = 0
        price_data["ICXETH"]["Okex"]["volume"] = float(icx_eth_okex_json["ticker"]["vol"])
    if icx_btc_okex.status_code == 200:
        icx_btc_okex_json = icx_btc_okex.json()
        price_data["ICXBTC"]["Okex"]["bid"] = float(icx_btc_okex_json["ticker"]["buy"])
        price_data["ICXBTC"]["Okex"]["ask"] = float(icx_btc_okex_json["ticker"]["sell"])
        price_data["ICXBTC"]["Okex"]["volume_bid"] = 0
        price_data["ICXBTC"]["Okex"]["volume_ask"] = 0
        price_data["ICXBTC"]["Okex"]["volume"] = float(icx_btc_okex_json["ticker"]["vol"])
    if iot_eth_okex.status_code == 200:
        iot_eth_okex_json = iot_eth_okex.json()
        price_data["IOTETH"]["Okex"]["bid"] = float(iot_eth_okex_json["ticker"]["buy"])
        price_data["IOTETH"]["Okex"]["ask"] = float(iot_eth_okex_json["ticker"]["sell"])
        price_data["IOTETH"]["Okex"]["volume_bid"] = 0
        price_data["IOTETH"]["Okex"]["volume_ask"] = 0
        price_data["IOTETH"]["Okex"]["volume"] = float(iot_eth_okex_json["ticker"]["vol"])
    if iot_btc_okex.status_code == 200:
        iot_btc_okex_json = iot_btc_okex.json()
        price_data["IOTBTC"]["Okex"]["bid"] = float(iot_btc_okex_json["ticker"]["buy"])
        price_data["IOTBTC"]["Okex"]["ask"] = float(iot_btc_okex_json["ticker"]["sell"])
        price_data["IOTBTC"]["Okex"]["volume_bid"] = 0
        price_data["IOTBTC"]["Okex"]["volume_ask"] = 0
        price_data["IOTBTC"]["Okex"]["volume"] = float(iot_btc_okex_json["ticker"]["vol"])
    if eth_usd_okex.status_code == 200:
        eth_usd_okex_json = eth_usd_okex.json()
        price_data["ETHUSD"]["Okex"]["bid"] = float(eth_usd_okex_json["ticker"]["buy"])
        price_data["ETHUSD"]["Okex"]["ask"] = float(eth_usd_okex_json["ticker"]["sell"])
        price_data["ETHUSD"]["Okex"]["volume_bid"] = 0
        price_data["ETHUSD"]["Okex"]["volume_ask"] = 0
        price_data["ETHUSD"]["Okex"]["volume"] = float(eth_usd_okex_json["ticker"]["vol"])
    if btc_usd_okex.status_code == 200:
        btc_usd_okex_json = btc_usd_okex.json()
        price_data["BTCUSD"]["Okex"]["bid"] = float(btc_usd_okex_json["ticker"]["buy"])
        price_data["BTCUSD"]["Okex"]["ask"] = float(btc_usd_okex_json["ticker"]["sell"])
        price_data["BTCUSD"]["Okex"]["volume_bid"] = 0
        price_data["BTCUSD"]["Okex"]["volume_ask"] = 0
        price_data["BTCUSD"]["Okex"]["volume"] = float(btc_usd_okex_json["ticker"]["vol"])

    seconds = time.time() - ts

    print ("Seconds elapsed to get price: " + str(seconds))

    print "PRICES: \n" \
          + json.dumps(price_data, indent=2, separators=(',', ': '))

    log_prices(price_data)

    return price_data

def get_spreads(price_data):

    print ("Calculating spreads...")

    spread_data = []

    for pair in price_data:
        for market in price_data[pair]:
            for other_market in price_data[pair]:
                if market != other_market:

                    spread_diff = (price_data[pair][market]['bid'] * (1 - trade_fees[market]) - price_data[pair][other_market]['ask'] * (1 + trade_fees[other_market]))
                    spread_percentage = (spread_diff / price_data[pair][other_market]['ask'])
                    cheap_price = price_data[pair][other_market]['ask']
                    expensive_price = price_data[pair][market]['bid']
                    cheaper_market_volume = price_data[pair][other_market]['volume']
                    expensive_market_volume = price_data[pair][market]['volume']

                    temp_spread_data = {}
                    temp_spread_data["pair"] = pair
                    temp_spread_data["cheap_exchange"] = other_market
                    temp_spread_data["expensive_exchange"] = market
                    temp_spread_data["cheap_price"] = cheap_price
                    temp_spread_data["expensive_price"] = expensive_price
                    temp_spread_data["expensive_market_volume"] = expensive_market_volume
                    temp_spread_data["cheap_market_volume"] = cheaper_market_volume

                    temp_spread_data["spread"] = spread_percentage

                    print json.dumps(temp_spread_data, indent=2, separators=(',', ': '))
                    spread_data.append(temp_spread_data)

    print ("Logging spreads")
    log_spreads(spread_data)

    print ("Going through spreads and identifying best in each pair")

    print ("Spreads sorted.")
    print json.dumps(spread_data, indent=2, separators=(',', ': '))


def log_prices(price_data):
    dir = os.path.dirname(__file__)

    file_name = datetime.datetime.today().strftime('%Y%m%d') + ".csv"

    log_file = os.path.join(dir, 'price_data_collected', file_name)

    for pair in price_data:
        for market in price_data[pair]:
            to_log = price_data[pair][market]
            list=[time.time() \
                , pair
                , market
                , to_log["ask"] \
                , to_log["volume_ask"]
                , to_log["bid"] \
                , to_log["volume_bid"] \
                , to_log["volume"] \
                  ]

            string_comma_delimited = ",".join(str(x) for x in list) + "\n"

            f = open(log_file, "a+")
            f.write(string_comma_delimited)
            f.close()

def log_spreads(spread_data):

    dir = os.path.dirname(__file__)

    file_name = datetime.datetime.today().strftime('%Y%m%d') + ".csv"

    log_file = os.path.join(dir, 'spread_data_collected', file_name)

    for spread in spread_data:
        list=[time.time() \
        , spread["pair"] \
        , spread["cheap_exchange"] \
        , spread["expensive_exchange"] \
        , spread["cheap_price"] \
        , spread["expensive_price"] \
        , spread["cheap_market_volume"] \
        , spread["expensive_market_volume"] \
        , spread["spread"]
        ]

        string_comma_delimited = ",".join(str(x) for x in list) + "\n"

        f = open(log_file, "a+")
        f.write(string_comma_delimited)
        f.close()

def run_research():
    market_pairs = [
        (('IOT', 'ETH'), ['Bitfinex', 'Binance', 'Okex']),
        (('IOT', 'BTC'), ['Bitfinex', 'Binance', 'Okex']),
        (('VEN', 'ETH'), ['Huobi', 'Binance']),
        (('VEN', 'BTC'), ['Huobi', 'Binance']),
        (('ICX', 'ETH'), ['Huobi', 'Binance', 'Okex']),
        (('ICX', 'BTC'), ['Huobi', 'Binance', 'Okex']),
        (('BTC', 'USD'), ['Huobi', 'Bitfinex', 'Binance', 'Okex']),
        (('ETH', 'USD'), ['Huobi', 'Bitfinex', 'Binance', 'Okex'])
    ]

    while True:
        try:
            price_data = get_prices(market_pairs)
            get_spreads(price_data)
            time.sleep(7)
        except Exception as e:
            print(e)
            time.sleep(20)
            pass


if __name__ == "__main__":
    run_research()
