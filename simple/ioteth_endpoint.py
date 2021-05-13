#!/usr/bin/env python
from flask import Flask, request, Response
from functools import wraps
from facebook_notif import *
from bot_runner import *
from fbchat import Client as Facebook_Client
from fbchat.models import *
from okex_client import OKCoinSpot
from bitfinex_client import BitfinexTradeClient
from binance_client import *
import time
import threading

app = Flask(__name__)

market_pairs = [
    (('IOT', 'ETH'), ['Bitfinex', 'Binance'])
    #(('IOT', 'ETH'), ['Binance', 'Okex'])
]

relevant_pair = '[ETH]'
trading_pair = 'IOTETH'

binance_client = get_binance_client()
bitfinex_client = BitfinexTradeClient()
okex_client = OKCoinSpot()

rebalancing = False

# trade_threshold = 0.012
# rebalance_threshold = -0.0005
weight = 1

def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == 'admin' and password == 'CryptoBot'

def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

def run(trade_threshold, rebalance_threshold, rebalancing):
    global running

    print "Trade threshold is: " + str(trade_threshold)

    time_start = time.time()

    fb_client = Facebook_Client(secrets.FACEBOOK_USERNAME, secrets.FACEBOOK_PASSWORD)

    started_msg = relevant_pair + " Run has started."

    fb_client.send(Message(started_msg), thread_id='562431311', thread_type=ThreadType.USER)

    while running:
        try:
            best_trade = run_bot(trade_threshold, market_pairs)
            if isinstance(best_trade, dict) and rebalancing:
                rebalance_wrapper(rebalance_threshold, best_trade)
        except Exception as e:
            print(e)
            fb_client = Facebook_Client("squanchroom@gmail.com", "CryptoBot")
            fb_message = "[ERROR] "+ relevant_pair + " Run has failed:\n" \
                         "[MESSAGE]: " + str(e)
            fb_client.send(Message(fb_message), thread_id='562431311', thread_type=ThreadType.USER)
            time.sleep(20)
            pass

        time.sleep(7)
        if (time.time() - time_start) > 3600:
            facebook_notif(trading_pair, 3600)
            time_start = time.time()

    fb_message = relevant_pair + " Run has ended."

    fb_client.send(Message(fb_message), thread_id='562431311', thread_type=ThreadType.USER)

def rebalance_from_run(rebalance_threshold, best_trade):
    global running

    fb_client = Facebook_Client(secrets.FACEBOOK_USERNAME, secrets.FACEBOOK_PASSWORD)

    started_msg = relevant_pair + " Rebalance has started."

    fb_client.send(Message(started_msg), thread_id='562431311', thread_type=ThreadType.USER)

    continue_rebalancing = True
    i = 0
    time_start_rebalance = time.time()

    balances_after = update_balances(binance_client, bitfinex_client, okex_client)

    print "Rebalance threshold is: " + str(rebalance_threshold)
    print "Cheap market is: " + best_trade["cheap_exchange"]
    print "Expensive market is: " + best_trade["expensive_exchange"]

    while continue_rebalancing and running:
        try:
            continue_rebalancing = rebalance(market_pairs, best_trade, rebalance_threshold, balances_after)
        except Exception as e:
            print(e)
            fb_client = Facebook_Client("squanchroom@gmail.com", "CryptoBot")
            fb_message = "[ERROR] Rebalance for " + best_trade["pair"] + " has failed:\n" \
                                                                         "[MESSAGE]: " + str(e)
            fb_client.send(Message(fb_message), thread_id='562431311',
                           thread_type=ThreadType.USER)
            time.sleep(20)
            pass
        if (time.time() - time_start_rebalance) > 1800:
            send_rebalancing_update(best_trade, i)
            i = i + 1
            time_start_rebalance = time.time()

    fb_message = relevant_pair + " Rebalance has ended."

    fb_client.send(Message(fb_message), thread_id='562431311', thread_type=ThreadType.USER)


def force_rebalance(rebalance_threshold, cheap_market, exp_market):
    amount = 1000
    pair = trading_pair
    buy_market = cheap_market
    sell_market = exp_market

    print "Rebalance threshold is: " + str(rebalance_threshold)
    print "Cheap market is: " + buy_market
    print "Expensive market is: " + sell_market

    best_trade = {
        "max_amount_tradeable": amount,
        "weighted_amount_tradeble": amount / 2,
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

    balances_after = update_balances(binance_client, bitfinex_client, okex_client)
    i = 0

    time_start_rebalance = time.time()

    fb_client = Facebook_Client("squanchroom@gmail.com", "CryptoBot")

    started_msg = relevant_pair + " Rebalance has started."

    fb_client.send(Message(started_msg), thread_id='562431311', thread_type=ThreadType.USER)

    continue_rebalance = True

    while rebalancing_thread and continue_rebalance:
        try:
            continue_rebalance = rebalance(market_pairs, best_trade, rebalance_threshold, balances_after)
        except Exception as e:
            print(e)
            fb_client = Facebook_Client("squanchroom@gmail.com", "CryptoBot")
            fb_message = "[ERROR] " + relevant_pair + " Rebalance has failed:\n" \
                         "[MESSAGE]: " + str(e)
            fb_client.send(Message(fb_message), thread_id='562431311', thread_type=ThreadType.USER)
            time.sleep(20)
            pass

        if (time.time() - time_start_rebalance) > 1800:
            send_rebalancing_update(best_trade, i)
            i = i + 1
            time_start_rebalance = time.time()

    fb_message = relevant_pair + " Rebalance has ended."

    fb_client.send(Message(fb_message), thread_id='562431311', thread_type=ThreadType.USER)

def rebalance_wrapper(rebalance_threshold, best_trade):

    t = threading.Thread(target=rebalance_from_run, args=(rebalance_threshold, best_trade,))
    t.start()
    if t.isAlive():
        return "Rebalancing started"
    else:
        return "Rebalancing has not started"

@app.route("/get_update")
def fifteen_minute_update():
    facebook_notif(trading_pair, 180)

@app.route("/force_rebalance")
@requires_auth
def rebalance_endpoint():
    global rebalancing_thread

    rebalance_thresh_param = request.args.get('rebalance_threshold', default=-0.0005, type=float)
    cheap_market_param = request.args.get('cheap_market', default='Bitfinex')
    exp_market_param = request.args.get('expensive_market', default='Binance')

    rebalancing_thread = True
    t = threading.Thread(target=force_rebalance, args=(rebalance_thresh_param, cheap_market_param, exp_market_param,))
    t.start()
    if t.isAlive():
        return "Rebalancing started"
    else:
        return "Rebalancing has not started"

@app.route("/run_rebalance")
@requires_auth
def endpoint_with_rebalance():
    global running

    trade_thresh_param = request.args.get('trade_threshold', default=0.01, type=float)
    rebalance_thresh_param = request.args.get('rebalance_threshold', default=-0.0005, type=float)
    rebalancing = True

    running = True
    t = threading.Thread(target=run, args=(trade_thresh_param, rebalance_thresh_param, rebalancing,))
    t.start()
    if t.isAlive():
        return "Run with rebalancing started"
    else:
        return "Run with rebalancing has not started"

@app.route("/run_no_rebalance")
@requires_auth
def endpoint_without_rebalance():
    global running

    trade_thresh_param = request.args.get('trade_threshold', default=0.01, type=float)
    rebalance_thresh_param = request.args.get('rebalance_threshold', default=-0.0005, type=float)
    rebalancing = False

    print "Trade threshold received: " + str(trade_thresh_param)

    running = True
    t = threading.Thread(target=run, args=(trade_thresh_param, rebalance_thresh_param, rebalancing,))
    t.start()
    if t.isAlive():
        return "Run without rebalancing started"
    else:
        return "Run without rebalancing has not started"

@app.route("/end")
def endpoint_end_run():
    global running
    running = False
    if running:
        return "App has not been successfully ended"
    else:
        return "App has successfully ended"

@app.route("/end_rebalance")
def endpoint_end_rebalance():
    global rebalancing_thread
    rebalancing_thread = False
    if rebalancing_thread:
        return "Rebalancing has not been successfully ended"
    else:
        return "Rebalancing has been successfully ended"


if __name__ == "__main__":
    app.run(host='0.0.0.0', threading=True)
