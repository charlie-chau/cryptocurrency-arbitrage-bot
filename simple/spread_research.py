#!/usr/bin/env python

from spread_detective_simple_research import *

market_pairs = [
    (('IOT', 'BTC'), ['Bitfinex', 'Binance']),
    (('IOT', 'ETH'), ['Bitfinex', 'Binance']),
    (('ETH', 'BTC'), ['Bitfinex', 'Binance', 'Kraken']),
    (('ETC', 'BTC'), ['Bitfinex', 'Kraken']),
    (('XRP', 'BTC'), ['Bitfinex', 'Binance', 'Kraken']),
    (('DSH', 'BTC'), ['Bitfinex', 'Binance', 'Kraken']),
    (('BCC', 'BTC'), ['Binance', 'Kraken']),
    (('QTM', 'BTC'), ['Bitfinex', 'Binance']),
    (('QTM', 'ETH'), ['Bitfinex', 'Binance']),
    (('XMR', 'BTC'), ['Binance', 'Kraken']),
    (('ETC', 'ETH'), ['Binance', 'Kraken']),
]

price_data, exchange_rates = get_prices(market_pairs)


dir = os.path.dirname(__file__)

file_name = datetime.datetime.today().strftime('%Y%m%d') + ".csv"

log_file = os.path.join(dir, 'spread_research', file_name)

print "PRICES: \n" \
          + json.dumps(price_data, indent=2, separators=(',', ': '))

for pair in price_data:
    for market in price_data[pair]:
        for other_market in price_data[pair]:
            if market != other_market:
                other_spread, spread = get_rebalance_spread(price_data, pair, market, other_market)
                list=[time.time() \
                , pair
                , market
                , other_market
                , spread
                ]

                string_comma_delimited = ",".join(str(x) for x in list) + "\n"

                f = open(log_file, "a+")
                f.write(string_comma_delimited)
                f.close()

