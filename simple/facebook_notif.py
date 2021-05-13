from fbchat import Client as Facebook_Client
from fbchat.models import *
import time
import datetime
import pandas as pd
import os
import secrets

def facebook_notif(pair, window):

    fb_client = Facebook_Client(secrets.FACEBOOK_USERNAME, secrets.FACEBOOK_PASSWORD)

    if window == 3600:
        window_type = "HOURLY"
    else:
        window_type = "ON-DEMAND"

    if pair =='IOTBTC':

        df_IOTBTC_bitfinex, df_IOTBTC_binance = get_df(pair, window)

        bitfinex_IOTBTC_max = df_IOTBTC_bitfinex['spread'].max()
        bitfinex_IOTBTC_min = df_IOTBTC_bitfinex['spread'].min()
        bitfinex_IOTBTC_mean = df_IOTBTC_bitfinex['spread'].mean()
        bitfinex_IOTBTC_median = df_IOTBTC_bitfinex['spread'].median()

        binance_IOTBTC_max = df_IOTBTC_binance['spread'].max()
        binance_IOTBTC_min = df_IOTBTC_binance['spread'].min()
        binance_IOTBTC_mean = df_IOTBTC_binance['spread'].mean()
        binance_IOTBTC_median = df_IOTBTC_binance['spread'].median()

        fb_message = "[IOTBTC " + window_type + " SPREAD REPORT]: \n" \
                     "--[Bitfinex]-- \n" \
                     "High = " + str(round(bitfinex_IOTBTC_max*100, 2)) + "%\n" \
                     "Low = " + str(round(bitfinex_IOTBTC_min*100, 2)) + "%\n" \
                     "Ave = " + str(round(bitfinex_IOTBTC_mean*100, 2)) + "%\n" \
                     "Med = " + str(round(bitfinex_IOTBTC_median*100, 2)) + "%\n" \
                     "--[Binance]-- \n" \
                     "High = " + str(round(binance_IOTBTC_max * 100, 2)) + "%\n" \
                     "Low = " + str(round(binance_IOTBTC_min * 100, 2)) + "%\n" \
                     "Ave = " + str(round(binance_IOTBTC_mean * 100, 2)) + "%\n" \
                     "Med = " + str(round(binance_IOTBTC_median * 100, 2)) + "%\n"
    if pair == 'IOTETH':
        df_IOTETH_bitfinex, df_IOTETH_binance = get_df(pair, window)

        bitfinex_IOTETH_max = df_IOTETH_bitfinex['spread'].max()
        bitfinex_IOTETH_min = df_IOTETH_bitfinex['spread'].min()
        bitfinex_IOTETH_mean = df_IOTETH_bitfinex['spread'].mean()
        bitfinex_IOTETH_median = df_IOTETH_bitfinex['spread'].median()

        binance_IOTETH_max = df_IOTETH_binance['spread'].max()
        binance_IOTETH_min = df_IOTETH_binance['spread'].min()
        binance_IOTETH_mean = df_IOTETH_binance['spread'].mean()
        binance_IOTETH_median = df_IOTETH_binance['spread'].median()

        fb_message = "[IOTETH " + window_type + " SPREAD REPORT]: \n" \
                     "--[Bitfinex]-- \n" \
                     "High = " + str(round(bitfinex_IOTETH_max*100, 2)) + "%\n" \
                     "Low = " + str(round(bitfinex_IOTETH_min*100, 2)) + "%\n" \
                     "Ave = " + str(round(bitfinex_IOTETH_mean*100, 2)) + "%\n" \
                     "Med = " + str(round(bitfinex_IOTETH_median*100, 2)) + "%\n" \
                     "--[Binance]-- \n" \
                     "High = " + str(round(binance_IOTETH_max * 100, 2)) + "%\n" \
                     "Low = " + str(round(binance_IOTETH_min * 100, 2)) + "%\n" \
                     "Ave = " + str(round(binance_IOTETH_mean * 100, 2)) + "%\n" \
                     "Med = " + str(round(binance_IOTETH_median * 100, 2)) + "%\n"


    fb_client.send(Message(fb_message), thread_id='562431311', thread_type=ThreadType.USER)

def get_df(pair, window):

    today = datetime.datetime.today().strftime('%Y%m%d')
    dir = os.path.dirname(__file__)
    file_name = today + ".csv"
    file_path = os.path.join(dir, 'spread_data_collected', file_name)
    column_names = ['time', 'pair', 'cheap_exchange', 'expensive_exchange', 'cheap_price', 'cheap_price_volume',
                    'expensive_price', 'expensive_price_volume', 'spread', 'max_amount_tradeable',
                    'weighted_amount_tradeable', 'profit_to_coin', 'profit_to_coin_weighted', 'profit_USD',
                    'profit_USD_weighted']

    df = pd.read_csv(file_path)
    df.columns = column_names
    df_last_window = df[df['time'] > (time.time() - window)]

    df_pair = df_last_window[df_last_window['pair'] == pair]

    df_bitfinex = df_pair[df_pair['cheap_exchange'] == 'Bitfinex']
    df_binance = df_pair[df_pair['cheap_exchange'] == 'Binance']

    return df_bitfinex, df_binance

if __name__ == "__main__":
    facebook_notif()
