import requests  # pip install requests
import json
import base64
import hashlib
import hmac
import time #for nonce
import secrets

class BitfinexClient(object):
    BASE_URL = "https://api.bitfinex.com/"
    KEY=secrets.BITFINEX_KEY
    SECRET=secrets.BITFINEX_SECRET

    def _nonce(self):
        """
        Returns a nonce
        Used in authentication
        """
        return str(int(round(time.time() * 1000)))

    def _headers(self, path, nonce, body):

        signature = "/api/" + path + nonce + body
        print "Signing: " + signature
        h = hmac.new(self.SECRET, signature, hashlib.sha384)
        signature = h.hexdigest()

        return {
            "bfx-nonce": nonce,
            "bfx-apikey": self.KEY,
            "bfx-signature": signature,
            "content-type": "application/json"
        }

    def active_orders(self):
        """
        Fetch active orders
        """
        nonce = self._nonce()
        body = {}
        rawBody = json.dumps(body)
        path = "v2/auth/r/orders"


        print(self.BASE_URL + path)
        print(nonce)


        headers = self._headers(path, nonce, rawBody)

        print(headers)
        print(rawBody)


        print("requests.post("+self.BASE_URL + path + ", headers=" + str(headers) + ", data=" + rawBody + ", verify=True)")
        r = requests.post(self.BASE_URL + path, headers=headers, data=rawBody, verify=True)

        if r.status_code == 200:
          return r.json()
        else:
          print r.status_code
          print r
          return ''

    def get_balances(self):

      nonce = self._nonce()
      body = {}
      rawBody = json.dumps(body)
      path = "v2/auth/r/wallets"


      print(self.BASE_URL + path)
      print(nonce)


      headers = self._headers(path, nonce, rawBody)

      print(headers)
      print(rawBody)


      print("requests.post("+self.BASE_URL + path + ", headers=" + str(headers) + ", data=" + rawBody + ", verify=True)")
      r = requests.post(self.BASE_URL + path, headers=headers, data=rawBody, verify=True)


      if r.status_code == 200:
        return r.json()
      else:
        print r.status_code
        print r
        return ''
