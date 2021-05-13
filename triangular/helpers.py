trade_threshold = 10

trade_fees = {'Bitfinex': 0.002,
              'Binance': 0.001,
              'BTCMarkets': 0.0085
              }

deposit_fees = {'Binance':
                    {'LTC': 0,
                     'BTC': 0,
                     'ETH': 0
                     },
                'Bitfinex':
                    {'LTC': 0.001,
                     'BTC': 0.0005,
                     'ETH': 0.01
                     },
                'BTCMarkets':
                    {'BTC': 0,
                     'ETH': 0,
                     'LTC': 0
                    }
                }

# deposit_fees = {'Binance':
#                     {'IOT': 0,
#                      'BTC': 0,
#                      'ETH': 0
#                      },
#                'Bitfinex':
#                     {'IOT': 0,
#                      'BTC': 0,
#                      'ETH': 0
#                     }
#                 }

withdrawal_fees = {'Binance':
                       {'LTC': 0.001,
                        'BTC': 0.0005,
                        'ETH': 0.01
                        },
                   'Bitfinex':
                       {'LTC': 0.001,
                        'BTC': 0.0005,
                        'ETH': 0.01
                        },
                   'BTCMarkets':
                      {'BTC': 0.0005,
                       'ETH': 0.001,
                       'LTC': 0.01
                      }
                   }

exchange_rates = {
    'ETHAUD': 980,
    'BTCAUD': 26500,
    'IOTAUD': 4.7,
    'LTCAUD': 425
}


def get_amount_tradeable(buy_price, buy_market, sell_market, pair, balances):
    print ("Getting max amount tradeable")

    from_coin = pair[0:3]
    to_coin = pair[3:6]

    print ("From coin: " + from_coin)
    print ("To coin: " + to_coin)

    max_buy_amount = balances[buy_market][to_coin] / buy_price

    print ("Based on " + str(balances[buy_market][
                                 to_coin]) + to_coin + " in " + buy_market + ", maximum " + from_coin + " that can be bought is " + str(
        max_buy_amount))

    max_sell_amount = balances[sell_market][from_coin]

    print ("Based on " + str(balances[sell_market][
                                 from_coin]) + from_coin + " in " + sell_market + ", maximum " + from_coin + " that can be sold is " + str(
        max_sell_amount))

    max_tradeable = min(max_buy_amount, max_sell_amount)

    print ("Max tradeable is: " + str(max_tradeable) + " " + from_coin)

    return max_tradeable


def get_aud_amount(amount, coin):
    exchange_pair = coin + 'AUD'
    amount_in_AUD = exchange_rates[exchange_pair] * amount

    return amount_in_AUD


def get_movement_fees(market_a, market_b, coin, other_coin):

    coin_transfer_fees = get_aud_amount(withdrawal_fees[market_a][coin], coin) + get_aud_amount(
        deposit_fees[market_b][coin], coin)

    print ("To transfer " + coin + " from " + market_a + " to " + market_b + " will cost " + str(
        coin_transfer_fees) + "AUD.")

    other_coin_transfer_fees = get_aud_amount(withdrawal_fees[market_b][other_coin], other_coin) + get_aud_amount(
        deposit_fees[market_a][other_coin], other_coin)

    print ("To transfer " + other_coin + " from " + market_b + " to " + market_a + " will cost " + str(
        other_coin_transfer_fees) + "AUD.")

    total_transfer_fees = coin_transfer_fees + other_coin_transfer_fees

    print ("Total transfer fees: " + str(total_transfer_fees) + "AUD.")

    return total_transfer_fees


def get_max_sell_amounts(market_a, market_b, coin, other_coin, balances, price_data):

    coin_a_bal = balances[market_a][other_coin]
    coin_b_bal = balances[market_b][coin]

    amount_b_in_a = (price_data[market_b][coin]['bid'] * coin_b_bal) / price_data[market_b][other_coin]['ask']

    max_tradeable_a = min(coin_a_bal, amount_b_in_a)
    max_tradeable_b = max_tradeable_a * price_data[market_b][other_coin]['ask'] / price_data[market_b][coin]['bid']

    return max_tradeable_a, max_tradeable_b
