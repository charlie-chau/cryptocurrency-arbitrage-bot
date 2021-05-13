from fbchat import Client as Facebook_Client
from fbchat.models import *
from balance_manager import *
from helpers import *
import numpy as np
import ccxt
import secrets

# market_pairs = [
#     (('IOT', 'BTC'), ['Bitfinex', 'Binance']),
#     (('IOT', 'ETH'), ['Bitfinex', 'Binance']),
#     (('ETH', 'BTC'), ['Bitfinex', 'Binance'])
# ]

trade_fees = {'Bitfinex': 0.002,
              'Binance': 0.001,
              'Okex': 0.002
              }

# deposit_fees = {'Binance':
#                     {'IOT': 0,
#                      'BTC': 0,
#                      'ETH': 0
#                      },
#                 'Bitfinex':
#                     {'IOT': 0.5,
#                      'BTC': 0.0005,
#                      'ETH': 0.01
#                      }
#                 }

deposit_fees = {'Binance':
                    {'IOT': 0,
                     'BTC': 0,
                     'ETH': 0
                     },
                'Bitfinex':
                    {'IOT': 0,
                     'BTC': 0,
                     'ETH': 0
                     }
                }

withdrawal_fees = {'Binance':
                       {'IOT': 0,
                        'BTC': 0.0005,
                        'ETH': 0.01
                        },
                   'Bitfinex':
                       {'IOT': 0.5,
                        'BTC': 0.0005,
                        'ETH': 0.01
                        }
                   }


def get_amount_tradeable(buy_price, buy_market, sell_market, pair, balances, weight):
    print ("Getting max amount tradeable")

    from_coin = pair[0:3]
    to_coin = pair[3:6]

    total_balances = get_total_balances(balances)

    print ("From coin: " + from_coin)
    print ("To coin: " + to_coin)

    binance_ccxt = ccxt.binance()
    binance_ccxt.load_markets()

    if from_coin == "IOT":
        from_coin_for_lots = "IOTA"
    else:
        from_coin_for_lots = from_coin

    pair_for_lots = from_coin_for_lots + "/" + to_coin

    max_buy_amount = balances[buy_market][to_coin] / buy_price
    weighted_buy_amount = total_balances[to_coin]*weight / buy_price

    print ("Based on " + str(balances[buy_market][to_coin]) + to_coin + " in " + buy_market + ", maximum " + from_coin + " that can be bought is " + str(max_buy_amount))
    print ("Weighted (" +str(weight*100) + "%) amount that can be bought is " + str(weighted_buy_amount))

    max_sell_amount = balances[sell_market][from_coin]

    print ("Based on " + str(balances[sell_market][from_coin]) + from_coin + " in " + sell_market + ", maximum " + from_coin + " that can be sold is " + str(max_sell_amount))

    max_tradeable = min(max_buy_amount, max_sell_amount)
    weighted_tradeable = min(weighted_buy_amount, max_tradeable)
    # trade_amount = max(0, binance_ccxt.amount_to_lots(pair_for_lots, max_tradeable) - 2)
    trade_amount = max(0, np.rint(max_tradeable) - 2)
    # weighted_trade_amount = max(0, binance_ccxt.amount_to_lots(pair_for_lots, weighted_tradeable) - 2)
    weighted_trade_amount = max(0, np.rint(weighted_tradeable) - 2)

    print ("Max tradeable is: " + str(trade_amount) + " " + from_coin)
    print ("Weighted tradeable is: " + str(weighted_trade_amount) + " " + from_coin)

    return trade_amount, weighted_trade_amount

def get_usd_amount(amount, coin, exchange_rates):
    return amount*exchange_rates[coin]

def get_movement_fees(cheap_exchange, expensive_exchange, pair, exchange_rates):
    from_coin = pair[0:3]
    to_coin = pair[3:6]

    from_coin_transfer_fees = get_usd_amount(withdrawal_fees[cheap_exchange][from_coin], from_coin, exchange_rates) + get_usd_amount(deposit_fees[expensive_exchange][from_coin], from_coin, exchange_rates)

    print ("To transfer " + from_coin + " from " + cheap_exchange + " to " + expensive_exchange + " will cost " + str(from_coin_transfer_fees) + "USD.")

    to_coin_transfer_fees = get_usd_amount(withdrawal_fees[expensive_exchange][to_coin], to_coin, exchange_rates) + get_usd_amount(deposit_fees[cheap_exchange][to_coin], to_coin, exchange_rates)

    print ("To transfer " + to_coin + " from " + expensive_exchange + " to " + cheap_exchange + " will cost " + str(to_coin_transfer_fees) + "USD.")

    total_transfer_fees = from_coin_transfer_fees + to_coin_transfer_fees

    print ("Total transfer fees: " + str(total_transfer_fees) + "USD.")

    return total_transfer_fees

def send_facebook_trade_update(best_trade, profit_coin, profit_usd, rebalance=False, allout=False):


    print ("Sending facebook message re: successful trade...")

    pair = best_trade["pair"]

    from_coin = pair[0:3]
    to_coin = pair[3:6]

    if allout:
        trade_amount = best_trade["max_amount_tradeable"]
    else:
        trade_amount = best_trade["weighted_amount_tradeable"]

    cheap_exchange = best_trade["cheap_exchange"]
    cheap_price = best_trade["cheap_price"]

    expensive_exchange = best_trade["expensive_exchange"]
    expensive_price = best_trade["expensive_price"]

    spread_before_fees = best_trade["spread"] * 100

    fb_client = Facebook_Client(secrets.FACEBOOK_USERNAME, secrets.FACEBOOK_PASSWORD)

    if rebalance:
        fb_message = "REBALANCE:\n" \
                     "Buy " + str(trade_amount) + from_coin + " on " + expensive_exchange + " at " + str(expensive_price) + to_coin + ".\n" \
                     "Sell " + str(trade_amount) + from_coin + " on " + cheap_exchange + " at " + str(cheap_price) + to_coin + ".\n" \
                     "Spread: " + str(round(spread_before_fees, 2)) + "%.\n" \
                     "Actual profit in crypto: " + str(profit_coin) + to_coin + ".\n" \
                     "Actual profit in USD: " + str(round(profit_usd, 2)) + "USD."
    else:
        fb_message = "TRADE:\n" \
                     "Buy " + str(trade_amount) + from_coin + " on " + cheap_exchange + " at " + str(cheap_price) + to_coin + ".\n" \
                     "Sell " + str(trade_amount) + from_coin + " on " + expensive_exchange + " at " + str(expensive_price) + to_coin + ".\n" \
                     "Spread: " + str(round(spread_before_fees, 2)) + "%.\n" \
                     "Projected profit in crypto: " + str(best_trade["profit_to_coin"]) + to_coin + ".\n" \
                     "Projected profit in USD: " + str(round(best_trade["profit_USD"], 2)) + "USD" + ".\n" \
                     "Actual profit in crypto: " + str(profit_coin) + to_coin + ".\n" \
                     "Actual profit in USD: " + str(round(profit_usd, 2)) + "USD."

    fb_client.send(Message(fb_message), thread_id='562431311', thread_type=ThreadType.USER)

def get_actual_profit(best_trade, balance_delta, exchange_rates):

    pair = best_trade["pair"]
    from_coin = pair[0:3]
    to_coin = pair[3:6]

    profit_coin = balance_delta[to_coin]
    profit_usd = get_usd_amount(profit_coin, to_coin, exchange_rates) + get_usd_amount(balance_delta[from_coin], from_coin, exchange_rates)
    return profit_coin, profit_usd

def automatic_withdrawal(bitfinex_client, binance_client, best_trade, profit_coin):

    pair = best_trade["pair"]

    from_coin = pair[0:3]
    to_coin = pair[3:6]

    trade_amount = best_trade["max_amount_tradeable"]
    cheap_exchange = best_trade["cheap_exchange"]
    expensive_exchange = best_trade["expensive_exchange"]
    to_transfer = profit_coin

    fb_message = "WITHDRAW: \n" \
                 "Send " + str(trade_amount) + from_coin + " from " + cheap_exchange + " to " + expensive_exchange + ".\n" \
                 "Send " + str(round(to_transfer, 2)) + to_coin + " from " + expensive_exchange + " to " + cheap_exchange + "."
    fb_client = Facebook_Client(secrets.FACEBOOK_USERNAME, secrets.FACEBOOK_PASSWORD)
    fb_client.send(Message(fb_message), thread_id='562431311', thread_type=ThreadType.USER)

def send_rebalancing_update(best_trade, i):

    pair = best_trade["pair"]

    trade_amount = best_trade["max_amount_tradeable"]
    cheap_exchange = best_trade["cheap_exchange"]
    expensive_exchange = best_trade["expensive_exchange"]

    fb_message = pair + " REBALANCING ROUND " + str(i) + ": \n" \
                 "SELL on " + cheap_exchange + ".\n" \
                 "BUY on " + expensive_exchange + "."
    fb_client = Facebook_Client(secrets.FACEBOOK_USERNAME, secrets.FACEBOOK_PASSWORD)
    fb_client.send(Message(fb_message), thread_id='562431311', thread_type=ThreadType.USER)
