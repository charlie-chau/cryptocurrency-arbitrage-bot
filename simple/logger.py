import time
import os
import datetime
from balance_manager import *


def log_spreads(spread_data):

    dir = os.path.dirname(__file__)
    #log_file = os.path.join(os.getcwd(),"spread_data_collected", datetime.datetime.today().strftime('%Y%m%d') + ".csv")

    #log_file = "E:\\Documents\\cryptocurrency-arbitrage-bot\\simple\\spread_data_collected\\" + datetime.datetime.today().strftime('%Y%m%d') + ".csv"

    file_name = datetime.datetime.today().strftime('%Y%m%d') + ".csv"

    log_file = os.path.join(dir, 'spread_data_collected', file_name)

    for spread in spread_data:
        list=[time.time() \
        , spread["pair"] \
        , spread["cheap_exchange"] \
        , spread["expensive_exchange"] \
        , spread["cheap_price"] \
        , spread["cheap_price_volume"] \
        , spread["expensive_price"] \
        , spread["expensive_price_volume"] \
        , spread["spread"] \
        , spread["max_amount_tradeable"] \
        , spread["weighted_amount_tradeable"] \
        , spread["profit_to_coin"] \
        , spread["profit_to_coin_weighted"] \
        , spread["profit_USD"] \
        , spread["profit_USD_weighted"]
        ]

        string_comma_delimited = ",".join(str(x) for x in list) + "\n"

        f = open(log_file, "a+")
        f.write(string_comma_delimited)
        f.close()

def log_trades(spread_data, balance, profit_coin, profit_usd, rebalance=False):
    #log_file = os.path.join(os.getcwd(),"spread_data_collected", datetime.datetime.today().strftime('%Y%m%d') + ".csv")

    #log_file = "E:\\Documents\\cryptocurrency-arbitrage-bot\\simple\\trade_data_collected\\" + datetime.datetime.today().strftime('%Y%m%d') + ".csv"

    dir = os.path.dirname(__file__)

    file_name = datetime.datetime.today().strftime('%Y%m%d') + ".csv"

    log_file = os.path.join(dir, 'trade_data_collected', file_name)

    if rebalance:
        trade_type = 'REBALANCE'
    else:
        trade_type = 'TRADE'

    total_balance = get_total_balances(balance)

    list=[time.time() \
    , trade_type
    , spread_data["pair"] \
    , spread_data["cheap_exchange"] \
    , spread_data["expensive_exchange"] \
    , spread_data["cheap_price"] \
    , spread_data["cheap_price_volume"] \
    , spread_data["expensive_price"] \
    , spread_data["expensive_price_volume"]
    , spread_data["spread"] \
    , spread_data["max_amount_tradeable"] \
    , spread_data["weighted_amount_tradeable"] \
    , spread_data["profit_to_coin"] \
    , spread_data["profit_to_coin_weighted"] \
    , spread_data["profit_USD"] \
    , spread_data["profit_USD_weighted"]
    , profit_usd
    , profit_coin
    , total_balance["BTC"]
    , total_balance["ETH"]
    , total_balance["IOT"]
    ]

    string_comma_delimited = ",".join(str(x) for x in list) + "\n"

    f = open(log_file, "a+")
    f.write(string_comma_delimited)
    f.close()