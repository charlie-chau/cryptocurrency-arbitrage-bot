import json
from fbchat import Client as Facebook_Client
from fbchat.models import *
from helpers import *


def execute_trade(sorted_spread, balances):
    print ("Executing trade(s)")

    best_trade = sorted_spread[0]

    fb_client = Facebook_Client("squanchroom@gmail.com", "CryptoBot")

    fb_message = "Spread after fees: " + str(round(best_trade['spread']*100, 2)) + "%.\n" \
                 "Value of profit in AUD (before fees): " + str(round(best_trade["profit_before_fees"], 2)) + "AUD.\n" \
                 "Value of profit in AUD (after fees): " + str(round(best_trade["profit"], 2)) + "AUD.\n" \
                 "Market_A: " + best_trade["market_a"] + ".\n" \
                 "Market_B: " + best_trade["market_b"] + ".\n" \
                 "Lower ratio coin: " + best_trade["cheap_coin"] + ".\n" \
                 "Higher ratio coin: " + best_trade["expensive_coin"] + "."
    fb_client.send(Message(fb_message), thread_id='562431311', thread_type=ThreadType.USER)

    return balances