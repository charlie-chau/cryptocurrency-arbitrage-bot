import json
import time
import sys
from binance.exceptions import *
from fbchat import Client as Facebook_Client
from fbchat.models import *
from helpers import *
import secrets


def update_balances(binance_client, bitfinex_client, okex_client):
    ts = time.time()

    print ("Retrieving balances...")

    balances = {'Bitfinex': {}, 'Binance': {}, 'Okex': {}}

    okex_balances = {};
    try:
        okex_balances = json.loads(okex_client.userinfo())
    except Exception as e:
        print e
        fb_client = Facebook_Client(secrets.FACEBOOK_USERNAME, secrets.FACEBOOK_PASSWORD)
        fb_message = "[ERROR] Okex API Exception raised while retrieving balances:\n" \
                     "[MESSAGE]: " + str(e)+ "\n" + json.dumps(okex_balances, indent=2, separators=(',', ': '))

        fb_client.send(Message(fb_message), thread_id='562431311', thread_type=ThreadType.USER)
        return 1

    if okex_balances['result']:
        balances['Okex']['ETH'] = float(okex_balances['info']['funds']['free']['eth'])
        balances['Okex']['BTC'] = float(okex_balances['info']['funds']['free']['btc'])
        balances['Okex']['IOT'] = float(okex_balances['info']['funds']['free']['iota'])
    else:
        fb_client = Facebook_Client(secrets.FACEBOOK_USERNAME, secrets.FACEBOOK_PASSWORD)
        fb_message = "[ERROR] Okex API Exception raised while retrieving balances:\n" \
                     "[MESSAGE]: " + json.dumps(okex_balances, indent=2, separators=(',', ': '))

        fb_client.send(Message(fb_message), thread_id='562431311', thread_type=ThreadType.USER)
        return 1

    try:
        bitfinex_balances = bitfinex_client.balances()
    except Exception as e:
        print e
        fb_client = Facebook_Client(secrets.FACEBOOK_USERNAME, secrets.FACEBOOK_PASSWORD)
        fb_message = "[ERROR] Bitfinex API Exception raised while retrieving balances:\n" \
                     "[MESSAGE]: " + str(e)+ "\n" + json.dumps(bitfinex_balances, indent=2, separators=(',', ': '))

        fb_client.send(Message(fb_message), thread_id='562431311', thread_type=ThreadType.USER)
        return 1

    if len(bitfinex_balances) <= 1:
        print ("Failed to retrieve bitfinex balances.\n" \
               "[RESPONSE]: " + str(bitfinex_balances) + "\n" \
               "Exiting...")
        return

    else:
        for balance in bitfinex_balances:
            if balance['currency'] == "eth":
                balances['Bitfinex']['ETH'] = float(balance['available'])
            elif balance['currency'] == "btc":
                balances['Bitfinex']['BTC'] = float(balance['available'])
            elif balance['currency'] == "iot":
                balances['Bitfinex']['IOT'] = float(balance['available'])

    try:
        binance_balances = binance_client.get_account(recvWindow=6000000)['balances']
    except BinanceAPIException as e:
        print e.status_code
        print e.message
        fb_client = Facebook_Client(secrets.FACEBOOK_USERNAME, secrets.FACEBOOK_PASSWORD)
        fb_message = "[ERROR] Binance API Exception raised while retrieving balances:\n" \
                     "[STATUS]: " + str(e.status_code) + "\n" \
                     "[MESSAGE]: " + e.message
        fb_client.send(Message(fb_message), thread_id='562431311', thread_type=ThreadType.USER)
        return 1
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


def get_total_balances(balances):
    total_balances = {
        'IOT': 0,
        'ETH': 0,
        'BTC': 0
    }

    markets = ['Bitfinex', 'Binance', 'Okex']

    for market in markets:
        total_balances['IOT'] = total_balances['IOT'] + balances[market]['IOT']
        total_balances['ETH'] = total_balances['ETH'] + balances[market]['ETH']
        total_balances['BTC'] = total_balances['BTC'] + balances[market]['BTC']

    print json.dumps(total_balances, indent=2, separators=(',', ': '))
    return total_balances


def get_balances_delta(balance_before, balance_after):
    print ("Getting delta in balances...")

    total_balance_before = get_total_balances(balance_before)
    total_balance_after = get_total_balances(balance_after)

    balance_delta = {'IOT': total_balance_after['IOT'] - total_balance_before['IOT'],
                     'ETH': total_balance_after['ETH'] - total_balance_before['ETH'],
                     'BTC': total_balance_after['BTC'] - total_balance_before['BTC']}

    print json.dumps(balance_delta, indent=2, separators=(',', ': '))

    print ("Change in delta calculated.")

    return balance_delta


def print_rebalance(balances, ideal_balances):
    coin_list = {'IOT', 'ETH', 'BTC'}

    for coin in coin_list:
        if balances['Bitfinex'][coin] > balances['Binance'][coin]:
            to_transfer = balances['Bitfinex'][coin] - ideal_balances['Bitfinex'][coin]
            print ("[" + coin + "] Bitfinex --> Binance: " + str(to_transfer))
        else:
            to_transfer = balances['Binance'][coin] - ideal_balances['Binance'][coin]
            print ("[" + coin + "] Binance --> Bitfinex: " + str(to_transfer))

