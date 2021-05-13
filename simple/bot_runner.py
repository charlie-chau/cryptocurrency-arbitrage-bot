#!/usr/bin/env python
from bitfinex_client import BitfinexTradeClient
from binance_client import *
from okex_client import OKCoinSpot
from spread_detective_simple import *
from trader import *
from balance_manager import *
from helpers import *
import time

binance_client = get_binance_client()
bitfinex_client = BitfinexTradeClient()
okex_client = OKCoinSpot()

withdraw_threshold = 0.05
weight = 1


def run_bot(trade_threshold, market_pairs):
    balances_before = update_balances(binance_client, bitfinex_client, okex_client)

    price_data, exchange_rates = get_prices(market_pairs)

    sorted_spread = get_spreads(price_data, balances_before, exchange_rates, weight)

    print "PRICES: \n" \
          + json.dumps(price_data, indent=2, separators=(',', ': '))

    print "EXCHANGE RATES: \n" \
          + json.dumps(exchange_rates, indent=2, separators=(',', ': '))

    if len(sorted_spread) > 0:
        best_trade = sorted_spread[0]
        if best_trade["spread"] > trade_threshold and best_trade["profit_USD"] > 0:
            trade_success = 1
            if best_trade["spread"] >= withdraw_threshold and best_trade["max_amount_tradeable"] >= 6:
                trade_success = execute_trade(best_trade, bitfinex_client, binance_client, okex_client, allout=True)
            elif best_trade["spread"] < withdraw_threshold and best_trade["weighted_amount_tradeable"] >= 6:
                trade_success = execute_trade(best_trade, bitfinex_client, binance_client, okex_client)
            if trade_success == 0:
                time.sleep(10)
                balances_after = update_balances(binance_client, bitfinex_client, okex_client)
                balances_delta = get_balances_delta(balances_before, balances_after)
                profit_coin, profit_usd = get_actual_profit(best_trade, balances_delta, exchange_rates)
                if best_trade["spread"] >= withdraw_threshold:
                    send_facebook_trade_update(best_trade, profit_coin, profit_usd, allout=True)
                else:
                    send_facebook_trade_update(best_trade, profit_coin, profit_usd)
                log_trades(best_trade, balances_after, profit_coin, profit_usd)

                return best_trade

    return 0


def rebalance(market_pairs, best_trade, rebalance_threshold, balances_after):
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

    if rebalance_spread > rebalance_threshold:
        max_amount_rebalance, weighted_amount_rebalance = get_amount_tradeable(
            price_data[best_trade['pair']][best_trade['expensive_exchange']]['ask'],
            best_trade['expensive_exchange'], best_trade['cheap_exchange'], best_trade['pair'],
            balances_after, weight)
        best_trade["expensive_price_volume"] = price_data[best_trade['pair']][best_trade["expensive_exchange"]]['volume_bid']
        best_trade["cheap_price_volume"] = price_data[best_trade['pair']][best_trade["cheap_exchange"]]['volume_ask']
        best_trade['max_amount_tradeable'] = max_amount_rebalance
        best_trade['weighted_amount_tradeable'] = weighted_amount_rebalance
        rebalance_success = execute_trade(best_trade, bitfinex_client, binance_client, okex_client, rebalance=True)

        if rebalance_success == 0:
            time.sleep(5)
            balance_after_rebalance = update_balances(binance_client, bitfinex_client, okex_client)
            balances_delta_rebalance = get_balances_delta(balances_after, balance_after_rebalance)
            profit_coin_rebalance, profit_usd_rebalance = get_actual_profit(best_trade, balances_delta_rebalance,
                                                                            exchange_rates)
            best_trade["spread"] = rebalance_spread
            send_facebook_trade_update(best_trade, profit_coin_rebalance, profit_usd_rebalance, rebalance=True)
            log_trades(best_trade, balance_after_rebalance, profit_coin_rebalance, profit_usd_rebalance, rebalance=True)
            return False
    else:
        return True