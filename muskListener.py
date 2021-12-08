import requests
import json
import validators
import tweepy
import hmac
import hashlib
import datetime

base = "https://api.binance.com/api/v3/order"
check = "https://api.binance.com/api/v3/ticker/price"
get_coins = "https://api.binance.com/api/v3/account"

sKey = "TqM4GT2V8uivZSUEqil4lsqJH7iQyaP6TuBetGZ0hsK8qabFDsjljswAct9rFRvQ"
TWITTER_APP_KEY = "oZPKBIcEg2D7sRB46ROQ6TLgH"
TWITTER_APP_SECRET = "iIl7ttDAJqfNLswPu9lQ6RwlD0etHMBdGFn8cxWxyAeGdEp3Ci"

TWITTER_KEY = "2933016428-qEFVr8FXNafqTlWWocrhMirMVVQdqSTJvej3Mzo"
TWITTER_SECRET = "WUKVLm4WSagvlvA7nJp1WshhaFDllE2fCjlwW4RQQSrGs"

def pushbullet_message(title, body):
    msg = {"type": "note", "title": title, "body": body}
    TOKEN = 'o.iBQDhyN2kyM7m6mu002pAmAHCuJ6cpHO'
    resp = requests.post('https://api.pushbullet.com/v2/pushes',
                         data=json.dumps(msg),
                         headers={'Authorization': 'Bearer ' + TOKEN,
                                  'Content-Type': 'application/json'})
    if resp.status_code != 200:
        raise Exception('Error',resp.status_code)
    else:
        print ('Message sent')

def signature(query):
    signature = hmac.new(sKey.encode('utf-8'), query.encode('utf-8'), digestmod=hashlib.sha256).hexdigest()
    return signature

def api_price():
    x = requests.get(check + "?symbol=DOGEBTC", headers={'X-MBX-APIKEY':'fgSGjuzIHwlqgOpn7MJRHRhgTXCEuzPqjlUL2B3MNWZJyFAnWo2JOyf2MfzkBxqj'})
    data = x.json()
    return data["price"]

def api_coins():
    y = int(datetime.datetime.now().timestamp() * 1000)
    dataQueryString = "recvWindow=50000&timestamp=" + str(y)
    a_signature = signature(dataQueryString)
    x = requests.get(get_coins +"?"+ dataQueryString+"&signature="+a_signature, headers={'X-MBX-APIKEY':'fgSGjuzIHwlqgOpn7MJRHRhgTXCEuzPqjlUL2B3MNWZJyFAnWo2JOyf2MfzkBxqj'})
    print(x)
    data = x.json()
    for i in data["balances"]:
        if i["asset"] == "BTC":
            print("free btc = ", i["free"])
            return i["free"]

def api_order(buying_string, a_signature):
    print("hello")
    x = requests.post(base +"?"+ buying_string+"&signature="+a_signature, headers={'X-MBX-APIKEY':'fgSGjuzIHwlqgOpn7MJRHRhgTXCEuzPqjlUL2B3MNWZJyFAnWo2JOyf2MfzkBxqj'})
    data = x.json()
    print("bought:", data)

def buy_doge():
    try:
        y = int(datetime.datetime.now().timestamp() * 1000)
        dataQueryString = "recWindow=2000&timestamp=" + str(y)
        a_signature = hmac.new(sKey.encode('utf-8'), dataQueryString.encode('utf-8'), digestmod=hashlib.sha256).hexdigest()
        balance = api_coins()
        price = api_price()
        test_amount = float(balance) * 0.95
        buying_amount = round(test_amount / float(price))
        #buying_amount = 200
        date = int(datetime.datetime.now().timestamp() * 1000)
        buying_string = "symbol=DOGEBTC&side=BUY&type=MARKET&quantity=" + str(buying_amount) +"&timestamp=" + str(date)
        a_signature = signature(buying_string)
        print("buying=", buying_amount)
        pushbullet_message("Bought Doge", "bought " + str(buying_amount) +" Doge")
        api_order(buying_string, a_signature)
        
    except Exception as e:
        pushbullet_message("Error occured", e.message)

class StreamListener(tweepy.StreamListener):
    def on_status(self, status):
        if (status.user.screen_name == "elonmusk"):
            buy_doge()
    def on_error(self, status_code):
        print("Error occured " + str(status_code))
        pushbullet_message("Error occured", str(status_code))
def start_stream(api):
    while True:
        try:
            stream_listener = StreamListener()
            stream = tweepy.Stream(auth=api.auth, listener=stream_listener)
            stream.filter(track=["doge", "DOGE", "Doge"])
        except Exception as e:
            pushbullet_message("Error occured", str(e))
            continue
if __name__ == "__main__":
    auth = tweepy.OAuthHandler(TWITTER_APP_KEY, TWITTER_APP_SECRET)
    auth.set_access_token(TWITTER_KEY, TWITTER_SECRET)
    api = tweepy.API(auth)

    start_stream(api)
    print("stream started")

