#!/usr/bin/env python
from bitfinex_client import BitfinexClient
from binance_client import BinanceClient
from spread_detective_triangular import *
from trader import *
from balance_manager import *
from helpers import *
import time


binance_client = BinanceClient().get_client()
#
bitfinex_client = BitfinexClient()

def main():
    ts = time.time()

    price_data = get_prices()

    seconds = time.time() - ts

    print ("Seconds elapsed to get price: " + str(seconds))

    #balances = update_balances_real(binance_client, bitfinex_client)
    balances = update_balances()

    sorted_spread = get_spreads(price_data, balances)

    if len(sorted_spread) > 0:
        total_balances_before_trade = get_total_balances(balances)
        balances = execute_trade(sorted_spread, balances)
        total_balances_after_trade = get_total_balances(balances)
        balances_delta = get_balances_delta(total_balances_before_trade, total_balances_after_trade)


if __name__ == "__main__":
    main()
