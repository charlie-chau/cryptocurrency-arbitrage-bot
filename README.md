# cryptocurrency-arbitrage-bot
Previously operational arbitrage bot. Built during the 2017 bull market.

## Exchanges
- Binance
- Bitfinex
- OKex

## Currencies
- ETH
- BTC
- IOT

### Sophisticated arbitrage bot with:
- Automated arbitrage detection and trade execution
  - Simple -> exchange 1 and exchange 2 have price discrepancy for same exchange pair
  - Triangular -> opportunity found via 3 different currencies (2 exchange pairs)
- Automated rebalancing mechanism. E.g. Selling 1 ETH in Bitfinex, and buying 1 ETH in Binance for arbitrage purposes. Assuming that in Bitfinex, the ETH balance is now 0 - there is no way to arbitrage by selling again in Bitfinex. When opportunity arises, 1 ETH is bought in Bitfinex, and 1 ETH is sold in Binance for break even.
- Notification system hooked into Facebook chat


### Code base also contains:
- Run scripts to deploy on cloud server
- Research scripts to identify further arbitrage opportunities
- Helper scripts for operating or manual intervention scenario
