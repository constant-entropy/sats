import ccxt
import time, datetime
import pandas as pd
from store import DBConn
import requests

def any_upbit_listing():
    proxies = {'http': "socks5://127.0.0.1:1080", 'https': "socks5://127.0.0.1:1080"}
    response = requests.get('https://upbit.com/service_center/notice', proxies=proxies)
    print (response.status_code)
    #print (response.content)
    print(response.content.find('거래'))

class DataFetcher():

    def __init__(self):
        self.bitmex = ccxt.bitmex({
            'options': {
                'api-expires': 10,
            }
        })
        self.bitmex.proxies = {"http": "socks5h://127.0.0.1:1080", "https": "socks5h://127.0.0.1:1080"}
        self.bitmex.apiKey = 'your api key'
        self.bitmex.secret = 'your api secret'

        """Connect MongoDB
        """
        #self.dbconn = DBConn()
        #self.dbconn.connect()
        #self.settings_json = self.dbconn.read_web_setting()

    def fetch_ohlcv(self, name, sd, tf):
        try:
            dt_obj = datetime.datetime.strptime(sd, "%Y-%m-%d")
            since = int(time.mktime(dt_obj.timetuple()) * 1000)
            data = self.bitmex.fetch_ohlcv(name + '/USD', timeframe=tf, since=since)
            return data
        except ccxt.NetworkError as e:
            print(self.bitmex.id, 'fetch_ohlcv failed due to a network error:', str(e))
        except ccxt.ExchangeError as e:
            print(self.bitmex.id, 'fetch_ohlcv failed due to exchange error:', str(e))
            # retry or whatever
            # ...
        except Exception as e:
            print(self.bitmex.id, 'fetch_ohlcv failed with:', str(e))
            # retry or whatever
            # ...

    def get_df(self, name, sd, tf):
        dt_obj = datetime.datetime.strptime(sd, "%Y-%m-%d")
        since = int(time.mktime(dt_obj.timetuple()) * 1000)
        data = self.bitmex.fetch_ohlcv(name + '/USD', timeframe=tf, since=since, limit=500)
        columns = ['t', 'O', 'H', 'L', 'C', 'V']
        index = ['t']
        df = pd.DataFrame(data=data, columns=columns)
        df = df.set_index(index)
        #print(df)
        return df

    def fetch_positions(self):
        try:
            return self.bitmex.fetch_positions()
        except ccxt.NetworkError as e:
            print(self.bitmex.id, 'fetch_positions failed due to a network error:', str(e))
            return None
        except ccxt.ExchangeError as e:
            print(self.bitmex.id, 'fetch_positions failed due to exchange error:', str(e))
            # retry or whatever
            # ...
        except Exception as e:
            print(self.bitmex.id, 'fetch_positions failed with:', str(e))
            # retry or whatever
            # ...

    def get_open_orders(self):
        try:
            return self.bitmex.fetch_open_orders()
        except ccxt.NetworkError as e:
            print(self.bitmex.id, 'fetch_open_orders failed due to a network error:', str(e))
            return None
        except ccxt.ExchangeError as e:
            print(self.bitmex.id, 'fetch_open_orders failed due to exchange error:', str(e))
            # retry or whatever
            # ...
        except Exception as e:
            print(self.bitmex.id, 'fetch_open_orders failed with:', str(e))
            # retry or whatever
            # ...

    def place_limit_order(self, name, size, price):
        try:
            side = 'Sell' if size < 0 else 'Buy'
            params = {'execInst': 'ParticipateDoNotInitiate'}
            return self.bitmex.create_limit_order(name + '/USD', side, abs(size), price, params=params)
        except ccxt.NetworkError as e:
            print(self.bitmex.id, 'create_limit_order failed due to a network error:', str(e))
        except ccxt.ExchangeError as e:
            print(self.bitmex.id, 'create_limit_order failed due to exchange error:', str(e))
            # retry or whatever
            # ...
        except Exception as e:
            print(self.bitmex.id, 'create_limit_order failed with:', str(e))
            # retry or whatever
            # ...

    def cancel_all_orders(self, name):
        try:
            return self.bitmex.cancel_all_orders(name+'/USD')
        except ccxt.NetworkError as e:
            print(self.bitmex.id, 'cancel_all_orders failed due to a network error:', str(e))
        except ccxt.ExchangeError as e:
            print(self.bitmex.id, 'cancel_all_orders failed due to exchange error:', str(e))
            # retry or whatever
            # ...
        except Exception as e:
            print(self.bitmex.id, 'cancel_all_orders failed with:', str(e))
            # retry or whatever
            # ...buy_at_best_bid

    def buy_at_best_bid(self, name, size):
        try:
            """Sample data
            {'symbol': 'BCH/USD', 'bids': [[448.3, 107.0], [448.25, 498.0], [448.2, 754.0], 
             [448.15, 26.0], [448.1, 189.0]], 'asks': [[448.7, 31.0], [448.85, 394.0], [448.9, 118.0], 
             [449.0, 71.0], [449.05, 111.0]], 'timestamp': None, 'datetime': None, 'nonce': None}
            """
            symbol = name+'/USD'
            ob = self.bitmex.fetch_order_book(symbol,limit=5)
            #print(ob)
            bb = ob['bids'][0][0]
            return self.place_limit_order(name, size, bb)
        except ccxt.NetworkError as e:
            print(self.bitmex.id, 'buy_at_best_bid failed due to a network error:', str(e))
        except ccxt.ExchangeError as e:
            print(self.bitmex.id, 'buy_at_best_bid failed due to exchange error:', str(e))
            # retry or whatever
            # ...
        except Exception as e:
            print(self.bitmex.id, 'buy_at_best_bid failed with:', str(e))
            # retry or whatever
            # ...
    def sell_at_best_ask(self, name, size):
        try:
            """Sample data
            {'symbol': 'BCH/USD', 'bids': [[448.3, 107.0], [448.25, 498.0], [448.2, 754.0], 
             [448.15, 26.0], [448.1, 189.0]], 'asks': [[448.7, 31.0], [448.85, 394.0], [448.9, 118.0], 
             [449.0, 71.0], [449.05, 111.0]], 'timestamp': None, 'datetime': None, 'nonce': None}
            """
            symbol = name+'/USD'
            ob = self.bitmex.fetch_order_book(symbol,limit=5)
            #print(ob)
            ba = ob['asks'][0][0]
            return self.place_limit_order(name, -size, ba)
        except ccxt.NetworkError as e:
            print(self.bitmex.id, 'sell_at_best_ask failed due to a network error:', str(e))
        except ccxt.ExchangeError as e:
            print(self.bitmex.id, 'sell_at_best_ask failed due to exchange error:', str(e))
            # retry or whatever
            # ...
        except Exception as e:
            print(self.bitmex.id, 'sell_at_best_ask failed with:', str(e))
            # retry or whatever
            # ...

    def get_total_balances(self):
        try:
            """
            {'info': [{'account': '1786200', 'currency': 'XBt', 'riskLimit': '1000000000000', 'prevState': '', 'state': '', 'action': '', 'amount': '198174', 'pendingCredit': '0', 'pendingDebit': '0', 'confirmedDebit': '0', 'prevRealisedPnl': '-2658', 'prevUnrealisedPnl': '0', 'grossComm': '-390', 'grossOpenCost': '210775', 'grossOpenPremium': '0', 'grossExecCost': '103644', 'grossMarkValue': '1115956', 'riskValue': '1326731', 'taxableMargin': '0', 'initMargin': '2320', 'maintMargin': '42960', 'sessionMargin': '0', 'targetExcessMargin': '0', 'varMargin': '0', 'realisedPnl': '6247', 'unrealisedPnl': '2115', 'indicativeTax': '0', 'unrealisedProfit': '0', 'syntheticMargin': None, 'walletBalance': '204421', 'marginBalance': '206536', 'marginBalancePcnt': '0.1851', 'marginLeverage': '5.40320331564473', 'marginUsedPcnt': '0.2192', 'excessMargin': '161256', 'excessMarginPcnt': '0.1445', 'availableMargin': '161256', 'withdrawableMargin': '161256', 'grossLastValue': '1115956', 'commission': None, 'makerFeeDiscount': None, 'takerFeeDiscount': None, 'timestamp': '2021-12-17T03:21:30.898Z'}, {'account': '1786200', 'currency': 'USDt', 'riskLimit': '500000000000000', 'prevState': '', 'state': '', 'action': '', 'amount': '0', 'pendingCredit': '0', 'pendingDebit': '0', 'confirmedDebit': '0', 'prevRealisedPnl': '0', 'prevUnrealisedPnl': '0', 'grossComm': '0', 'grossOpenCost': '0', 'grossOpenPremium': '0', 'grossExecCost': '0', 'grossMarkValue': '0', 'riskValue': '0', 'taxableMargin': '0', 'initMargin': '0', 'maintMargin': '0', 'sessionMargin': '0', 'targetExcessMargin': '0', 'varMargin': '0', 'realisedPnl': '0', 'unrealisedPnl': '0', 'indicativeTax': '0', 'unrealisedProfit': '0', 'syntheticMargin': None, 'walletBalance': '0', 'marginBalance': '0', 'marginBalancePcnt': '1', 'marginLeverage': '0', 'marginUsedPcnt': '0', 'excessMargin': '0', 'excessMarginPcnt': '1', 'availableMargin': '0', 'withdrawableMargin': '0', 'grossLastValue': '0', 'commission': None, 'makerFeeDiscount': None, 'takerFeeDiscount': None, 'timestamp': '2021-12-15T05:00:00.057Z'}], 'BTC': {'free': 0.00161256, 'used': 0.0004528, 'total': 0.00206536}, 'USDT': {'free': 0.0, 'used': 0.0, 'total': 0.0}, 'free': {'BTC': 0.00161256, 'USDT': 0.0}, 'used': {'BTC': 0.0004528, 'USDT': 0.0}, 'total': {'BTC': 0.00206536, 'USDT': 0.0}}
            """
            balance = self.bitmex.fetch_balance()
            #print(balance)
            assets = balance['info']
            XBt_balance = ''
            for a in assets:
                if a['currency'] == 'XBt':
                    XBt_balance = a['walletBalance']
            return XBt_balance
        except ccxt.NetworkError as e:
            print(self.bitmex.id, 'get_total_balances failed due to a network error:', str(e))
        except ccxt.ExchangeError as e:
            print(self.bitmex.id, 'get_total_balances failed due to exchange error:', str(e))
            # retry or whatever
            # ...
        except Exception as e:
            print(self.bitmex.id, 'get_total_balances failed with:', str(e))
            # retry or whatever
            # ...

    def get_today_trades(self,count=10):
        try:
            """
            [{'info': {}}, {'info': {}}]
            """
            #since = '2021-12-21T21:05:11Z'
            trades = []
            trade_history = self.bitmex.fetch_my_trades(limit=count, params={'reverse': 'true'})
            for trade in trade_history:
                _trade = trade['info']
                trades.append(_trade)
            #print(trade_history)
            return trades
        except ccxt.NetworkError as e:
            print(self.bitmex.id, 'get_today_trades failed due to a network error:', str(e))
        except ccxt.ExchangeError as e:
            print(self.bitmex.id, 'get_today_trades failed due to exchange error:', str(e))
            # retry or whatever
            # ...
        except Exception as e:
            print(self.bitmex.id, 'get_today_trades failed with:', str(e))
            # retry or whatever
            # ...
    
    def get_price_of(self, name):
        try:
            """Sample data
            {'symbol': 'BCH/USD', 'bids': [[448.3, 107.0], [448.25, 498.0], [448.2, 754.0], 
             [448.15, 26.0], [448.1, 189.0]], 'asks': [[448.7, 31.0], [448.85, 394.0], [448.9, 118.0], 
             [449.0, 71.0], [449.05, 111.0]], 'timestamp': None, 'datetime': None, 'nonce': None}
            """
            symbol = name+'/USD'
            ob = self.bitmex.fetch_order_book(symbol,limit=5)
            #print(ob)
            ba = ob['asks'][0][0]
            bb = ob['bids'][0][0]
            timestamp = ob['timestamp']
            return (ba+bb) / 2, timestamp
        except ccxt.NetworkError as e:
            print(self.bitmex.id, 'get_price_of failed due to a network error:', str(e))
        except ccxt.ExchangeError as e:
            print(self.bitmex.id, 'get_price_of failed due to exchange error:', str(e))
            # retry or whatever
            # ...
        except Exception as e:
            print(self.bitmex.id, 'get_price_of failed with:', str(e))
            # retry or whatever
            # ...
