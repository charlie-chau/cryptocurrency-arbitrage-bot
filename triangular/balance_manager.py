import json
import time
from helpers import *


def update_balances_real(binance_client, bitfinex_client):

    ts = time.time()

    print ("Retrieving balances...")

    balances = {'Bitfinex': {}, 'Binance': {}}

    bitfinex_balances = bitfinex_client.get_balances()

    for balance in bitfinex_balances:
        if balance[1] == "ETH":
            balances['Bitfinex']['ETH'] = float(balance[2])
        elif balance[1] == "BTC":
            balances['Bitfinex']['BTC'] = float(balance[2])
        elif balance[1] == "IOT":
            balances['Bitfinex']['IOT'] = float(balance[2])

    binance_balances = binance_client.get_account(recvWindow=6000000)['balances']

    for balance in binance_balances:
        if balance['asset'] == 'IOTA':
            balances['Binance']['IOT'] = float(balance['free'])
        elif balance['asset'] == 'ETH':
            balances['Binance']['ETH'] = float(balance['free'])
        elif balance['asset'] == 'BTC':
            balances['Binance']['BTC'] = float(balance['free'])

    print json.dumps(balances, indent=2, separators=(',', ': '))

    seconds = time.time() - ts
    print ("Balances retrieved in " + str(seconds))

    return balances

def update_balances():

    balances = {
                  "Binance": {
                    "ETH": 1.6,
                    "BTC": 0.06,
                    "LTC": 3.5
                  },
                  "Bitfinex": {
                    "ETH": 1.6,
                    "BTC": 0.06,
                    "LTC": 3.5
                  },
                  "BTCMarkets": {
                    "ETH": 1.6,
                    "BTC": 0.06,
                    "LTC": 3.5
                  }
                }

    return balances

def get_total_balances(balances):

    total_balances = {
        'ETH': 0,
        'BTC': 0
    }

    markets = ['Bitfinex', 'Binance']

    for market in markets:
        total_balances['ETH'] = total_balances['ETH'] + balances[market]['ETH']
        total_balances['BTC'] = total_balances['BTC'] + balances[market]['BTC']

    print json.dumps(total_balances, indent=2, separators=(',', ': '))
    return total_balances

def get_balances_delta(balance_before, balance_after):

    print ("Getting delta in balances...")
    balance_delta = {'ETH': balance_after['ETH'] - balance_before['ETH'],
                     'BTC': balance_after['BTC'] - balance_before['BTC']}

    print json.dumps(balance_delta, indent=2, separators=(',', ': '))

    print ("Change in delta calculated.")

    return balance_delta

def get_ideal_balances(total_balances):

    print ("Getting ideal balances...")
    ideal_balances = {'IOT': total_balances['IOT'] / 2, 'ETH': total_balances['ETH'] / 2,
                      'BTC': total_balances['BTC'] / 2}

    final_ideal_balances = {'Bitfinex': ideal_balances, 'Binance': ideal_balances}

    print json.dumps(final_ideal_balances, indent=2, separators=(',', ': '))

    print ("Ideal balances calculated")

    return final_ideal_balances

def print_rebalance(balances, ideal_balances):

    coin_list = {'IOT', 'ETH', 'BTC'}

    for coin in coin_list:
        if balances['Bitfinex'][coin] > balances['Binance'][coin]:
            to_transfer = balances['Bitfinex'][coin] - ideal_balances['Bitfinex'][coin]
            print ("["+coin+"] Bitfinex --> Binance: " + str(to_transfer))
        else:
            to_transfer = balances['Binance'][coin] - ideal_balances['Binance'][coin]
            print ("["+coin+"] Binance --> Bitfinex: " + str(to_transfer))
