import json
import sys
from binance.exceptions import BinanceAPIException
from fbchat import Client as Facebook_Client
from fbchat.models import *
import time
from helpers import *
import numpy as np



def execute_trade_test(sorted_spread, balances):

    print ("Executing trade(s)")

    best_trade = sorted_spread[0]

    pair = best_trade["pair"]

    print ("Considering " + pair)
    from_coin = pair[0:3]
    to_coin = pair[3:6]

    trade_amount = best_trade["max_amount_tradeable"]

    cheap_exchange = best_trade["cheap_exchange"]
    cheap_price = best_trade["cheap_price"]

    expensive_exchange = best_trade["expensive_exchange"]
    expensive_price = best_trade["expensive_price"]

    spread_before_fees = best_trade["spread"] * 100

    print ("TRADE:")
    print ("Buy " + str(trade_amount) + from_coin + " on " + cheap_exchange + " at " + str(
        cheap_price) + to_coin + ".")

    amount_spent_to_coin = cheap_price * trade_amount

    balances[cheap_exchange][from_coin] = balances[cheap_exchange][from_coin] + trade_amount
    balances[cheap_exchange][to_coin] = balances[cheap_exchange][to_coin] - amount_spent_to_coin

    print ("Balance updated...")
    print json.dumps(balances, indent=2, separators=(',', ': '))

    print ("Sell " + str(trade_amount) + from_coin + " on " + expensive_exchange + " at " + str(
        expensive_price) + to_coin + ".")

    amount_gained_to_coin = expensive_price * trade_amount

    balances[expensive_exchange][from_coin] = balances[expensive_exchange][from_coin] - trade_amount
    balances[expensive_exchange][to_coin] = balances[expensive_exchange][to_coin] + amount_gained_to_coin

    print ("Balance updated...")
    print json.dumps(balances, indent=2, separators=(',', ': '))

    print ("Actual profit in arbitrage: " + str(best_trade["profit_to_coin"]) + to_coin + ".")
    print ("Value of profit in AUD: " + str(best_trade["profit_USD"]) + "USD.")

    fb_client = Facebook_Client("squanchroom@gmail.com", "CryptoBot")

    fb_message = "TRADE:\n" \
                 "Buy " + str(trade_amount) + from_coin + " on " + cheap_exchange + " at " + str(
        cheap_price) + to_coin + ".\n" \
                                 "Sell " + str(trade_amount) + from_coin + " on " + expensive_exchange + " at " + str(
        expensive_price) + to_coin + ".\n" \
                                     "Spread before fees: " + str(round(spread_before_fees, 2)) + "%.\n" \
                                                                                                  "Actual profit in arbitrage: " + str(
        best_trade["profit_to_coin"]) + to_coin + ".\n" \
                                                  "Value of profit in USD: " + str(
        round(best_trade["profit_USD"], 2)) + "USD."

    fb_client.send(Message(fb_message), thread_id='562431311', thread_type=ThreadType.USER)

    return balances

# def execute_trade(best_trade, bitfinex_client, binance_client, okex_client, rebalance=False, allout=False):
#
#     ts = time.time()
#
#     pair = best_trade["pair"]
#
#     from_coin = pair[0:3]
#     to_coin = pair[3:6]
#     if allout:
#         trade_amount = best_trade["max_amount_tradeable"]
#     else:
#         trade_amount = best_trade["weighted_amount_tradeable"]
#     if rebalance:
#         print ("Executing rebalance...")
#         print ("Considering " + pair)
#         cheap_exchange = best_trade["expensive_exchange"]
#         cheap_price = best_trade["expensive_price"]
#
#         expensive_exchange = best_trade["cheap_exchange"]
#         expensive_price = best_trade["cheap_price"]
#
#         print ("REBALANCE:")
#     else:
#         print ("Executing trade...")
#         print ("Considering " + pair)
#         cheap_exchange = best_trade["cheap_exchange"]
#         cheap_price = best_trade["cheap_price"]
#
#         expensive_exchange = best_trade["expensive_exchange"]
#         expensive_price = best_trade["expensive_price"]
#
#         print ("TRADE:")
#
#     print ("Buy " + str(trade_amount) + from_coin + " on " + cheap_exchange + " at " + str(
#         cheap_price) + to_coin + ".")
#
#     if cheap_exchange == 'Okex':
#
#         if pair == 'IOTETH':
#             okex_pair = 'iota_eth'
#         elif pair == 'IOTBTC':
#             okex_pair = 'iota_btc'
#         else:
#             okex_pair = pair
#         trade_amount_okex = cheap_price*trade_amount
#         okex_order = json.loads(okex_client.trade(okex_pair, "buy_market", price=str(trade_amount_okex)))
#         okex_success = False
#         if "result" in okex_order:
#             if okex_order["result"]:
#                 okex_success = True
#         if okex_success:
#             order_id = okex_order["order_id"]
#             okex_order_id = json.loads(okex_client.orderinfo(okex_pair, order_id))
#             traded_amount = trade_amount
#             if "result" in okex_order_id:
#                 if okex_order_id["result"]:
#                     traded_amount_rounded = np.rint(float(okex_order_id['orders'][0]['deal_amount']))
#                     traded_amount = min(traded_amount_rounded, trade_amount)
#
#             print ("Trade success!")
#             print (json.dumps(okex_order, indent=2, separators=(',', ': ')))
#             print ("Sell " + str(traded_amount) + from_coin + " on " + expensive_exchange + " at " + str(
#                 expensive_price) + to_coin + ".")
#
#             success = True
#
#             if pair == 'IOTETH':
#                 trade_pair = 'IOTAETH'
#             elif pair == 'IOTBTC':
#                 trade_pair = 'IOTABTC'
#             else:
#                 trade_pair = pair
#
#             try:
#                 binance_order = binance_client.order_market_sell(symbol=trade_pair, quantity=traded_amount)
#             except BinanceAPIException as e:
#                 fb_client = Facebook_Client("squanchroom@gmail.com", "CryptoBot")
#                 fb_message = "[ERROR] Binance API Exception raised when trying to sell:\n" \
#                              "[STATUS]: " + str(e.status_code) + "\n" \
#                              "[MESSAGE]: " + e.message + "\n" \
#                              "Manually sell " + str(traded_amount) + " of " + trade_pair
#                 print fb_message
#                 fb_client.send(Message(fb_message), thread_id='562431311', thread_type=ThreadType.USER)
#                 success = False
#                 return 1
#             if success:
#                 print ("Trade success!")
#                 print (json.dumps(binance_order, indent=2, separators=(',', ': ')))
#
#         else:
#             message = "[ERROR]: Okex buy market order\n" \
#                       "[MESSAGE]: " + okex_order
#             print message
#
#             fb_client = Facebook_Client("squanchroom@gmail.com", "CryptoBot")
#             fb_client.send(Message(message), thread_id='562431311', thread_type=ThreadType.USER)
#             return 1
#
#     elif cheap_exchange == 'Binance':
#
#         print ("TRADE:")
#         print ("Buy " + str(trade_amount) + from_coin + " on " + cheap_exchange + " at " + str(
#             cheap_price) + to_coin + ".")
#
#         success = True
#
#         if pair == 'IOTETH':
#             trade_pair = 'IOTAETH'
#         elif pair == 'IOTBTC':
#             trade_pair = 'IOTABTC'
#         else:
#             trade_pair = pair
#
#         try:
#             binance_order = binance_client.order_market_buy(symbol=trade_pair, quantity=trade_amount)
#         except BinanceAPIException as e:
#             fb_client = Facebook_Client("squanchroom@gmail.com", "CryptoBot")
#             fb_message = "[ERROR] Binance API Exception raised when trying to buy:\n" \
#                          "[STATUS]: " + str(e.status_code) + "\n" \
#                                                         "[MESSAGE]: " + e.message
#             print fb_message
#             fb_client.send(Message(fb_message), thread_id='562431311', thread_type=ThreadType.USER)
#             success = False
#             return 1
#
#         if success:
#             print ("Trade success!")
#             print (json.dumps(binance_order, indent=2, separators=(',', ': ')))
#             print ("Sell " + str(trade_amount) + from_coin + " on " + expensive_exchange + " at " + str(
#                 expensive_price) + to_coin + ".")
#
#             if pair == 'IOTETH':
#                 okex_pair = 'iota_eth'
#             elif pair == 'IOTBTC':
#                 okex_pair = 'iota_btc'
#             else:
#                 okex_pair = pair
#
#             okex_order = json.loads(okex_client.trade(okex_pair, "sell_market", amount=str(trade_amount)))
#             okex_success = False
#             if "result" in okex_order:
#                 if okex_order["result"]:
#                     okex_success = True
#             if okex_success:
#                 print ("Trade success!")
#                 print (json.dumps(okex_order, indent=2, separators=(',', ': ')))
#             else:
#                 message = "[ERROR]: Okex sell market order\n" \
#                           "[MESSAGE]: " + okex_order + "\n" \
#                                                                       "Manually sell " + str(
#                     trade_amount) + " of " + pair
#                 print message
#                 return 1
#     if not rebalance:
#         if allout:
#             print ("Projected profit in arbitrage: " + str(best_trade["profit_to_coin"]) + to_coin + ".")
#             print ("Projected value of profit in USD: " + str(best_trade["profit_USD"]) + "USD.")
#         else:
#             print ("Projected profit in arbitrage: " + str(best_trade["profit_to_coin_weighted"]) + to_coin + ".")
#             print ("Projected value of profit in USD: " + str(best_trade["profit_USD_weighted"]) + "USD.")
#
#     seconds = time.time() - ts
#
#     print ("Seconds elapsed to execute trade: " + str(seconds))
#
#     return 0

def execute_trade(best_trade, bitfinex_client, binance_client, okex_client, rebalance=False, allout=False):

    ts = time.time()

    pair = best_trade["pair"]

    from_coin = pair[0:3]
    to_coin = pair[3:6]
    if allout:
        trade_amount = best_trade["max_amount_tradeable"]
    else:
        trade_amount = best_trade["weighted_amount_tradeable"]
    if rebalance:
        print ("Executing rebalance...")
        print ("Considering " + pair)
        cheap_exchange = best_trade["expensive_exchange"]
        cheap_price = best_trade["expensive_price"]

        expensive_exchange = best_trade["cheap_exchange"]
        expensive_price = best_trade["cheap_price"]

        print ("REBALANCE:")
    else:
        print ("Executing trade...")
        print ("Considering " + pair)
        cheap_exchange = best_trade["cheap_exchange"]
        cheap_price = best_trade["cheap_price"]

        expensive_exchange = best_trade["expensive_exchange"]
        expensive_price = best_trade["expensive_price"]

        print ("TRADE:")

    print ("Buy " + str(trade_amount) + from_coin + " on " + cheap_exchange + " at " + str(
        cheap_price) + to_coin + ".")

    if cheap_exchange == 'Bitfinex':
        bitfinex_order = bitfinex_client.place_order(str(trade_amount), str(cheap_price), 'buy', 'exchange market',
                                                     pair.lower())

        if 'order_id' in bitfinex_order:
            print ("Trade success!")
            print (json.dumps(bitfinex_order, indent=2, separators=(',', ': ')))
            print ("Sell " + str(trade_amount) + from_coin + " on " + expensive_exchange + " at " + str(
                expensive_price) + to_coin + ".")

            success = True

            if pair == 'IOTETH':
                trade_pair = 'IOTAETH'
            elif pair == 'IOTBTC':
                trade_pair = 'IOTABTC'
            else:
                trade_pair = pair

            try:
                binance_order = binance_client.order_market_sell(symbol=trade_pair, quantity=trade_amount)
            except BinanceAPIException as e:
                fb_client = Facebook_Client("squanchroom@gmail.com", "CryptoBot")
                fb_message = "[ERROR] Binance API Exception raised when trying to sell:\n" \
                             "[STATUS]: " + str(e.status_code) + "\n" \
                             "[MESSAGE]: " + e.message + "\n" \
                             "Manually sell " + str(trade_amount) + " of " + trade_pair
                print fb_message
                fb_client.send(Message(fb_message), thread_id='562431311', thread_type=ThreadType.USER)
                success = False
                return 1
            if success:
                print ("Trade success!")
                print (json.dumps(binance_order, indent=2, separators=(',', ': ')))

        else:
            message = "[ERROR]: Bitfinex buy market order\n" \
                      "[MESSAGE]: " + bitfinex_order['message']
            print message

            fb_client = Facebook_Client("squanchroom@gmail.com", "CryptoBot")
            fb_client.send(Message(message), thread_id='562431311', thread_type=ThreadType.USER)
            return 1

    elif cheap_exchange == 'Binance':

        print ("TRADE:")
        print ("Buy " + str(trade_amount) + from_coin + " on " + cheap_exchange + " at " + str(
            cheap_price) + to_coin + ".")

        success = True

        if pair == 'IOTETH':
            trade_pair = 'IOTAETH'
        elif pair == 'IOTBTC':
            trade_pair = 'IOTABTC'
        else:
            trade_pair = pair

        try:
            binance_order = binance_client.order_market_buy(symbol=trade_pair, quantity=trade_amount)
        except BinanceAPIException as e:
            fb_client = Facebook_Client("squanchroom@gmail.com", "CryptoBot")
            fb_message = "[ERROR] Binance API Exception raised when trying to buy:\n" \
                         "[STATUS]: " + str(e.status_code) + "\n" \
                                                        "[MESSAGE]: " + e.message
            print fb_message
            fb_client.send(Message(fb_message), thread_id='562431311', thread_type=ThreadType.USER)
            success = False
            return 1

        if success:
            print ("Trade success!")
            print (json.dumps(binance_order, indent=2, separators=(',', ': ')))
            print ("Sell " + str(trade_amount) + from_coin + " on " + expensive_exchange + " at " + str(
                expensive_price) + to_coin + ".")

            bitfinex_order = bitfinex_client.place_order(str(trade_amount), str(cheap_price), 'sell', 'exchange market',
                                                         pair.lower())

            if 'order_id' in bitfinex_order:
                print ("Trade success!")
                print (json.dumps(bitfinex_order, indent=2, separators=(',', ': ')))
            else:
                message = "[ERROR]: Bitfinex sell market order\n" \
                          "[MESSAGE]: " + bitfinex_order['message'] + "\n" \
                                                                      "Manually sell " + str(
                    trade_amount) + " of " + pair
                print message
                return 1
    if not rebalance:
        if allout:
            print ("Projected profit in arbitrage: " + str(best_trade["profit_to_coin"]) + to_coin + ".")
            print ("Projected value of profit in USD: " + str(best_trade["profit_USD"]) + "USD.")
        else:
            print ("Projected profit in arbitrage: " + str(best_trade["profit_to_coin_weighted"]) + to_coin + ".")
            print ("Projected value of profit in USD: " + str(best_trade["profit_USD_weighted"]) + "USD.")

    seconds = time.time() - ts

    print ("Seconds elapsed to execute trade: " + str(seconds))

    return 0
