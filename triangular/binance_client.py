from binance.client import Client
import secrets

class BinanceClient(object):

    def get_client():
        api_key = secrets.BINANCE_KEY
        api_secret = secrets.BINANCE_SECRET
        return Client(api_key, api_secret)

