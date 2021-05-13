#!/usr/bin/env python
from spread_detective_simple import *
from bitfinex_client import BitfinexClient, BitfinexTradeClient
from binance_client import *
from trader import *
from balance_manager import *
from helpers import *
import secrets

binance_client = get_binance_client()
bitfinex_client = BitfinexTradeClient()

market_pairs = [
    (('IOT', 'BTC'), ['Bitfinex', 'Binance']),
    (('IOT', 'ETH'), ['Bitfinex', 'Binance']),
    (('ETH', 'BTC'), ['Bitfinex', 'Binance'])
]

trade_threshold = 0.01
rebalance_threshold = -0.0005
weight = 0.5

amount = 566.0
pair = "IOTBTC"
buy_market = "Binance"
sell_market = "Bitfinex"

best_trade = {
    "max_amount_tradeable": amount,
    "weighted_amount_tradeable": amount/2,
    "expensive_exchange": sell_market,
    "profit_to_coin": 1,
    "profit_to_coin_weighted": 1,
    "profit_USD": 1,
    "profit_USD_weighted": 1,
    "cheap_price": 1,
    "spread": 1,
    "pair": pair,
    "expensive_price": 1,
    "cheap_exchange": buy_market
  }

balances_after = update_balances(binance_client, bitfinex_client)

rebalance_spread = -1
sub_reb_spread = -1
i = 0
time_start_rebalance = time.time()
while rebalance_spread < rebalance_threshold:
    try:
        print ("Finding the right spread to rebalance...")
        time.sleep(10)
        price_data, exchange_rates = get_prices(market_pairs)
        subsequent_spread, rebalance_spread = get_rebalance_spread(price_data, best_trade["pair"],
                                                                   best_trade["expensive_exchange"],
                                                                   best_trade["cheap_exchange"])
        sub_reb_spread = rebalance_spread + subsequent_spread
        print ("Rebalance: " + str(rebalance_spread))
        print ("Opportunity Cost Spread: " + str(subsequent_spread))
        print ("Diff: " + str(sub_reb_spread))
        if (time.time() - time_start_rebalance) > 1800:
            send_rebalancing_update(best_trade, i)
            i = i + 1
            time_start_rebalance = time.time()
    except Exception as e:
        print(e)
        fb_client = Facebook_Client(secrets.FACEBOOK_USERNAME, secrets.FACEBOOK_PASSWORD)
        fb_message = "[ERROR] Rebalance for " + best_trade["pair"] + " has failed:\n" \
                                                                     "[MESSAGE]: " + str(e)
        fb_client.send(Message(fb_message), thread_id='562431311',
                       thread_type=ThreadType.USER)
        time.sleep(20)
        pass
max_amount_rebalance, weighted_amount_rebalance = get_amount_tradeable(
                        price_data[best_trade['pair']][best_trade['expensive_exchange']]['ask'],
                        best_trade['expensive_exchange'], best_trade['cheap_exchange'], best_trade['pair'],
                        balances_after, weight)
best_trade['max_amount_tradeable'] = max_amount_rebalance
best_trade['weighted_amount_tradeable'] = weighted_amount_rebalance
rebalance_success = execute_trade(best_trade, bitfinex_client, binance_client, rebalance=True)
if rebalance_success == 0:
    time.sleep(10)
    balance_after_rebalance = update_balances(binance_client, bitfinex_client)
    balances_delta_rebalance = get_balances_delta(balances_after, balance_after_rebalance)
    profit_coin_rebalance, profit_usd_rebalance = get_actual_profit(best_trade, balances_delta_rebalance,
                                                                    exchange_rates)
    best_trade["spread"] = rebalance_spread
    send_facebook_trade_update(best_trade, profit_coin_rebalance, profit_usd_rebalance, rebalance=True)
    log_trades(best_trade, balance_after_rebalance, profit_coin_rebalance, profit_usd_rebalance, rebalance=True)