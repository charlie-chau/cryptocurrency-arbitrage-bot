#!/usr/bin/env python
from bitfinex_client import BitfinexClient
from binance_client import BinanceClient
from balance_manager import *
import json
from helpers import *

binance_client = BinanceClient().get_client()

bitfinex_client = BitfinexClient()


def main():
    balances = update_balances_real(binance_client, bitfinex_client)
    total_balances = get_total_balances(balances)
    ideal_balances = get_ideal_balances(total_balances)
    print_rebalance(balances, ideal_balances)


if __name__ == "__main__":
    main()
